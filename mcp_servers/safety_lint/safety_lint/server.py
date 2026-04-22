"""MCP server for deterministic safety + convention linting of KRL .src files."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as exc:  # pragma: no cover
    raise SystemExit("mcp package not installed. Run: pip install mcp") from exc

from .rules import RULES, RuleDef


def _read_lines(path: str) -> list[str] | dict:
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {path}"}
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return {"error": f"read failed: {exc}"}


def lint_src(path: str) -> list[dict]:
    lines = _read_lines(path)
    if isinstance(lines, dict):
        return [lines]
    results: list[dict] = []
    for rule in RULES:
        if rule.matcher is None:
            continue
        for lineno, column, message, fix_hint in rule.matcher(lines):
            results.append(
                {
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "category": rule.category,
                    "file": path,
                    "line": lineno,
                    "column": column,
                    "message": message,
                    "fix_hint": fix_hint,
                }
            )
    return results


def list_rules() -> list[dict]:
    return [
        {
            "rule_id": r.rule_id,
            "severity": r.severity,
            "category": r.category,
            "description": r.description,
        }
        for r in RULES
    ]


def explain_rule(rule_id: str) -> dict:
    for r in RULES:
        if r.rule_id == rule_id:
            return {
                "rule_id": r.rule_id,
                "severity": r.severity,
                "category": r.category,
                "description": r.description,
                "rationale": r.rationale,
                "normative_refs": r.normative_refs,
            }
    return {"error": f"unknown rule_id: {rule_id}"}


server = Server("safety-lint")


@server.list_tools()
async def _list_tools() -> list[Tool]:
    return [
        Tool(
            name="lint_src",
            description="Run static safety and convention checks on a KRL .src file. Returns list of findings.",
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        ),
        Tool(
            name="list_rules",
            description="Return the full rule catalog.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="explain_rule",
            description="Return rationale and normative citations for a single rule id.",
            inputSchema={
                "type": "object",
                "properties": {"rule_id": {"type": "string"}},
                "required": ["rule_id"],
            },
        ),
    ]


@server.call_tool()
async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "lint_src":
        result = lint_src(**arguments)
    elif name == "list_rules":
        result = list_rules()
    elif name == "explain_rule":
        result = explain_rule(**arguments)
    else:
        result = {"error": f"unknown tool: {name}"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
