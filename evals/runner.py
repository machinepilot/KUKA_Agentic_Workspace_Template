"""Eval harness for KUKA agentic workspace.

Deliberately small. Modes:

- schema-only: validate golden files against their schemas (no LLM).
- replay: re-invoke an agent backend (Ollama / OpenAI / Anthropic) with the case's
  system prompt + input, then diff against golden. Requires the corresponding
  environment variables.
- manual: prompt user to paste agent output.

Usage:
    python runner.py --list
    python runner.py --case <id> [--schema-only|--replay|--manual] [--update-golden]
    python runner.py --all [--schema-only]

Exit codes:
    0 = all pass
    1 = at least one failure
    2 = runner error
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
CASES_DIR = ROOT / "cases"
GOLDEN_DIR = ROOT / "golden"
RESULTS_DIR = ROOT / "results"


# ---------- Optional dependency: jsonschema ----------


def _validate_schema(data: Any, schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return [
            "jsonschema not installed; skipping schema validation. `pip install jsonschema` to enable."
        ]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Failed to read schema {schema_path}: {exc}"]
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in validator.iter_errors(data)]


# ---------- Case model ----------


@dataclass
class Case:
    case_id: str
    agent: str
    input: dict
    expected_schema: Path | None
    golden_path: Path
    description: str = ""
    notes: str = ""

    @classmethod
    def from_path(cls, path: Path) -> "Case":
        raw = json.loads(path.read_text(encoding="utf-8"))
        schema = raw.get("expected_schema")
        schema_path = (ROOT / schema).resolve() if schema else None
        golden = raw.get("golden_path", f"golden/{raw['case_id']}.json")
        return cls(
            case_id=raw["case_id"],
            agent=raw.get("agent", "unknown"),
            input=raw.get("input", {}),
            expected_schema=schema_path,
            golden_path=(ROOT / golden).resolve(),
            description=raw.get("description", ""),
            notes=raw.get("notes", ""),
        )


def _load_cases() -> list[Case]:
    if not CASES_DIR.exists():
        return []
    return [Case.from_path(p) for p in sorted(CASES_DIR.glob("*.json"))]


# ---------- Backends ----------


def _run_replay(case: Case) -> dict:
    backend = os.environ.get("EVAL_BACKEND", "").lower()
    if backend == "ollama":
        return _run_ollama(case)
    if backend == "openai":
        return _run_openai(case)
    if backend == "anthropic":
        return _run_anthropic(case)
    return {"_error": f"EVAL_BACKEND not set (tried replay). set to ollama|openai|anthropic"}


def _agent_system_prompt(agent: str) -> str | None:
    p = WORKSPACE / ".cursor" / "agents" / f"{agent}.md"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def _run_ollama(case: Case) -> dict:
    try:
        import httpx  # type: ignore
    except ImportError:
        return {"_error": "httpx not installed; pip install httpx"}
    sys_prompt = _agent_system_prompt(case.agent) or ""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("EVAL_MODEL", "qwen2.5-coder:7b")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": json.dumps(case.input, indent=2)},
        ],
        "stream": False,
        "format": "json",
    }
    try:
        resp = httpx.post(f"{base_url}/api/chat", json=payload, timeout=120.0)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"ollama call failed: {exc}"}
    text = resp.json().get("message", {}).get("content", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_error": "ollama response was not valid JSON", "raw": text}


def _run_openai(case: Case) -> dict:
    return {"_error": "openai backend not implemented in this stub; add via openai python SDK"}


def _run_anthropic(case: Case) -> dict:
    return {"_error": "anthropic backend not implemented in this stub; add via anthropic python SDK"}


# ---------- Comparison ----------


def _json_diff(a: Any, b: Any) -> list[str]:
    a_text = json.dumps(a, indent=2, sort_keys=True).splitlines()
    b_text = json.dumps(b, indent=2, sort_keys=True).splitlines()
    return list(difflib.unified_diff(a_text, b_text, fromfile="golden", tofile="actual", lineterm=""))


# ---------- Runner ----------


def _run_case(case: Case, mode: str, update_golden: bool) -> dict:
    result: dict[str, Any] = {"case_id": case.case_id, "agent": case.agent}

    # Produce actual output
    if mode == "schema-only":
        if not case.golden_path.exists():
            return {**result, "verdict": "ERROR", "reason": "no golden to schema-check"}
        actual = json.loads(case.golden_path.read_text(encoding="utf-8"))
    elif mode == "replay":
        actual = _run_replay(case)
        if "_error" in actual:
            return {**result, "verdict": "ERROR", "reason": actual["_error"]}
    elif mode == "manual":
        print(f"[{case.case_id}] Paste agent output as JSON (end with EOF / Ctrl-D):")
        try:
            actual = json.loads(sys.stdin.read())
        except json.JSONDecodeError as exc:
            return {**result, "verdict": "ERROR", "reason": f"invalid JSON: {exc}"}
    else:
        return {**result, "verdict": "ERROR", "reason": f"unknown mode: {mode}"}

    # Schema check
    schema_errors: list[str] = []
    if case.expected_schema and case.expected_schema.exists():
        schema_errors = _validate_schema(actual, case.expected_schema)
        if schema_errors and not any("jsonschema not installed" in e for e in schema_errors):
            return {**result, "verdict": "SCHEMA_FAIL", "schema_errors": schema_errors}

    # Update golden?
    if update_golden:
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        case.golden_path.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8")
        return {**result, "verdict": "GOLDEN_UPDATED", "path": str(case.golden_path.relative_to(ROOT))}

    # Golden diff
    if not case.golden_path.exists():
        return {**result, "verdict": "NO_GOLDEN", "hint": "run with --update-golden after reviewing output"}

    golden = json.loads(case.golden_path.read_text(encoding="utf-8"))
    if golden == actual:
        return {**result, "verdict": "PASS", "schema_notes": schema_errors}
    diff = _json_diff(golden, actual)
    return {**result, "verdict": "DIFF", "diff": "\n".join(diff), "schema_notes": schema_errors}


def _write_results(results: list[dict]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = RESULTS_DIR / datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="KUKA agentic workspace eval harness")
    parser.add_argument("--list", action="store_true", help="List cases")
    parser.add_argument("--case", help="Run one case by id")
    parser.add_argument("--all", action="store_true", help="Run all cases")
    parser.add_argument(
        "--mode",
        choices=["schema-only", "replay", "manual"],
        default="schema-only",
        help="How to produce actual output",
    )
    parser.add_argument("--schema-only", action="store_true", help="Shortcut for --mode schema-only")
    parser.add_argument("--replay", action="store_true", help="Shortcut for --mode replay")
    parser.add_argument("--manual", action="store_true", help="Shortcut for --mode manual")
    parser.add_argument("--update-golden", action="store_true", help="Save actual output as new golden")
    args = parser.parse_args()

    if args.schema_only:
        args.mode = "schema-only"
    elif args.replay:
        args.mode = "replay"
    elif args.manual:
        args.mode = "manual"

    cases = _load_cases()
    if args.list:
        if not cases:
            print("(no cases found in evals/cases/)")
            return 0
        for c in cases:
            print(f"  {c.case_id:40}  agent={c.agent}  desc={c.description}")
        return 0

    if args.case:
        target = next((c for c in cases if c.case_id == args.case), None)
        if target is None:
            print(f"case '{args.case}' not found", file=sys.stderr)
            return 2
        selected = [target]
    elif args.all:
        selected = cases
    else:
        parser.print_help()
        return 2

    if not selected:
        print("No cases to run. Add files under evals/cases/.")
        return 0

    results = []
    any_fail = False
    for c in selected:
        r = _run_case(c, args.mode, args.update_golden)
        results.append(r)
        verdict = r.get("verdict", "?")
        if verdict not in ("PASS", "GOLDEN_UPDATED"):
            any_fail = True
        print(f"[{verdict}] {c.case_id} ({c.agent})")
        if verdict == "DIFF":
            print(r.get("diff", ""))
        elif verdict in ("SCHEMA_FAIL", "ERROR"):
            print(f"  {r.get('reason') or r.get('schema_errors')}")

    run_dir = _write_results(results)
    print(f"\nResults: {run_dir.relative_to(ROOT)}")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
