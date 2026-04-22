# Evals

A lightweight harness to keep agent behavior measurable as prompts drift.

## What It Does

- Loads case files from `cases/`.
- For each case: validates the input, invokes the named agent (or a schema-only validator), compares the output to `golden/<case_id>.json`.
- Reports per-case verdict (`PASS` / `SCHEMA_FAIL` / `DIFF` / `ERROR`) + a summary.

## Philosophy

- **Schema-first.** The fastest, cheapest eval just checks that an agent's output still validates against its `schema_out`. Run on every prompt edit.
- **Golden diff.** Capture a known-good output once, assert equivalence over time.
- **Cheap models for replay.** Evals should cost pennies. Use Ollama local or small cloud models for CI.
- **Human review before new goldens.** `--update-golden` requires a diff review.

## Layout

```
evals/
├─ README.md           (this file)
├─ runner.py           (CLI entry point)
├─ cases/              (input cases; one JSON per case)
│  └─ *.json
├─ golden/             (expected outputs)
│  └─ *.json
└─ results/            (runtime outputs; gitignored)
   └─ <timestamp>/
```

## Case File

```json
{
  "case_id": "architect_press_brake_basic",
  "agent": "architect",
  "description": "Architect receives a press-brake-tending intake and produces a valid program_spec.",
  "input": {
    "program_intake": { "...": "..." }
  },
  "expected_schema": "../cowork/schemas/program_spec.schema.json",
  "expected_keys": ["modules", "variables", "motion_blocks"],
  "golden_path": "golden/architect_press_brake_basic.json",
  "notes": "If this diffs, check if the motion_blocks list was reordered."
}
```

## CLI

```bash
# List available cases
python runner.py --list

# Run one
python runner.py --case architect_press_brake_basic

# Run all
python runner.py --all

# Update a golden after reviewing the diff
python runner.py --case <id> --update-golden

# Schema-only validation (fast; doesn't invoke the agent)
python runner.py --case <id> --schema-only
```

## Agent Invocation

`runner.py` supports three modes:

1. **Schema-only** (default for CI) — no LLM call; validates that `golden/<case>.json` is itself schema-valid. Useful for stability testing on the schema files themselves.
2. **Replay** — re-invoke an agent (Ollama, OpenAI, or Anthropic) with the case's system prompt (`.cursor/agents/<agent>.md`) + input. Compare to golden.
3. **Manual** — prompt you to paste agent output; run schema + golden diff. Useful when you're iterating manually.

See `runner.py` for configuration (env vars `EVAL_BACKEND`, `EVAL_MODEL`, etc.).

## Bootstrapping

The template ships with one smoke case that exercises the loader without requiring an LLM. Add real cases as you develop real agent behavior.

## Adding a Case

1. Capture a real input (e.g., a `program_intake` that came through Intake).
2. Run the target agent and capture the output.
3. Review the output; if acceptable, save as `golden/<case_id>.json`.
4. Create `cases/<case_id>.json` with the input + golden reference.
5. Commit both files.

## Exit Codes

- `0` — all cases pass.
- `1` — one or more cases diverged or schema-failed.
- `2` — runner error.
