"""MCP server exposing customer_programs/ via list/get/search/diff tools."""

from __future__ import annotations

import difflib
import json
import os
import re
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as exc:  # pragma: no cover
    raise SystemExit("mcp package not installed. Run: pip install mcp") from exc


REPO_PATH = Path(
    os.environ.get(
        "CUSTOMER_PROGRAMS_PATH",
        Path(__file__).resolve().parents[3] / "customer_programs",
    )
).resolve()


def _manifest() -> dict:
    p = REPO_PATH / "_manifest.json"
    if not p.exists():
        return {"customers": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"customers": []}


def list_customers() -> list[dict]:
    return list(_manifest().get("customers", []))


def _customer_dir(customer_id: str) -> Path:
    return REPO_PATH / customer_id


def _resolve_program(customer_id: str, name: str, backup: str | None) -> Path | None:
    cdir = _customer_dir(customer_id)
    if not cdir.exists():
        return None
    candidates: list[Path] = []
    for system_dir in [d for d in cdir.iterdir() if d.is_dir()]:
        if backup:
            target = system_dir / backup / name
            if target.exists():
                candidates.append(target)
        else:
            # pick latest dated backup dir (YYYY-MM-DD_*) or system_dir root
            dated = sorted(
                [d for d in system_dir.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)],
                reverse=True,
            )
            for d in dated:
                target = d / name
                if target.exists():
                    candidates.append(target)
                    break
            target = system_dir / name
            if target.exists():
                candidates.append(target)
    return candidates[0] if candidates else None


def get_program(customer_id: str, name: str, backup: str | None = None) -> dict:
    path = _resolve_program(customer_id, name, backup)
    if path is None:
        return {"error": f"program '{name}' not found for customer '{customer_id}'"}
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"error": f"read failed: {exc}"}
    return {
        "customer_id": customer_id,
        "name": name,
        "backup": backup,
        "path": str(path.relative_to(REPO_PATH)),
        "content": content,
        "lines": content.count("\n") + 1,
    }


def list_files(customer_id: str, system: str | None = None) -> list[str]:
    cdir = _customer_dir(customer_id)
    if not cdir.exists():
        return []
    root = cdir / system if system else cdir
    if not root.exists():
        return []
    return [
        str(p.relative_to(REPO_PATH))
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in (".src", ".dat", ".sub")
    ]


def search(regex: str, scope: str | None = None, file_glob: str = "**/*.src") -> list[dict]:
    root = REPO_PATH
    if scope:
        root = (REPO_PATH / scope).resolve()
        if not str(root).startswith(str(REPO_PATH)):
            return [{"error": "scope escapes customer_programs"}]
    try:
        pattern = re.compile(regex)
    except re.error as exc:
        return [{"error": f"bad regex: {exc}"}]

    hits: list[dict] = []
    for path in root.glob(file_glob):
        if not path.is_file():
            continue
        try:
            for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                if pattern.search(line):
                    hits.append(
                        {
                            "path": str(path.relative_to(REPO_PATH)),
                            "line": lineno,
                            "text": line.rstrip(),
                        }
                    )
        except OSError:
            continue
    return hits


def diff(path_a: str, path_b: str) -> dict:
    pa = (REPO_PATH / path_a).resolve()
    pb = (REPO_PATH / path_b).resolve()
    for p in (pa, pb):
        if not str(p).startswith(str(REPO_PATH)):
            return {"error": f"path '{p}' escapes customer_programs"}
        if not p.exists():
            return {"error": f"path '{p.relative_to(REPO_PATH)}' not found"}
    a_lines = pa.read_text(encoding="utf-8", errors="replace").splitlines()
    b_lines = pb.read_text(encoding="utf-8", errors="replace").splitlines()
    diff_lines = list(
        difflib.unified_diff(a_lines, b_lines, fromfile=str(path_a), tofile=str(path_b), lineterm="")
    )
    added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
    return {
        "a": path_a,
        "b": path_b,
        "added": added,
        "removed": removed,
        "diff": "\n".join(diff_lines),
    }


server = Server("program-repository")


@server.list_tools()
async def _list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_customers",
            description="Return all customers from customer_programs/_manifest.json.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_program",
            description="Fetch a .src/.dat/.sub file from a customer/system (latest backup by default).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "name": {"type": "string"},
                    "backup": {"type": ["string", "null"]},
                },
                "required": ["customer_id", "name"],
            },
        ),
        Tool(
            name="list_files",
            description="Enumerate program files for a customer (optionally a system).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "system": {"type": ["string", "null"]},
                },
                "required": ["customer_id"],
            },
        ),
        Tool(
            name="search",
            description="Regex search within customer_programs/. scope may be 'customer_id' or 'customer_id/system'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "regex": {"type": "string"},
                    "scope": {"type": ["string", "null"]},
                    "file_glob": {"type": "string", "default": "**/*.src"},
                },
                "required": ["regex"],
            },
        ),
        Tool(
            name="diff",
            description="Unified diff of two program files. Paths relative to customer_programs/.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path_a": {"type": "string"},
                    "path_b": {"type": "string"},
                },
                "required": ["path_a", "path_b"],
            },
        ),
    ]


@server.call_tool()
async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_customers":
        result = list_customers()
    elif name == "get_program":
        result = get_program(**arguments)
    elif name == "list_files":
        result = list_files(**arguments)
    elif name == "search":
        result = search(**arguments)
    elif name == "diff":
        result = diff(**arguments)
    else:
        result = {"error": f"unknown tool: {name}"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
