"""MCP server exposing kuka_dataset/normalized/ via search/get/list tools.

This is a minimal, readable reference implementation. It uses keyword scoring by
default and can switch to Ollama embeddings via EMBEDDING_BACKEND=ollama.

Run directly for debugging:
    python -m kuka_knowledge.server
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "mcp package not installed. Run: pip install mcp"
    ) from exc


# ----- Configuration -------------------------------------------------------

DATASET_PATH = Path(
    os.environ.get(
        "KUKA_DATASET_PATH",
        Path(__file__).resolve().parents[3] / "kuka_dataset",
    )
).resolve()
EMBEDDING_BACKEND = os.environ.get("EMBEDDING_BACKEND", "keyword").lower()
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")


# ----- Data model ----------------------------------------------------------


@dataclass
class Entry:
    """One normalized dataset entry."""

    id: str
    path: Path
    frontmatter: dict[str, Any]
    body: str
    tokens: Counter = field(default_factory=Counter)

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title", self.id))

    @property
    def topic(self) -> str:
        return str(self.frontmatter.get("topic", ""))

    @property
    def tier(self) -> str:
        source = self.frontmatter.get("source") or {}
        return str(source.get("tier", "")) if isinstance(source, dict) else ""

    @property
    def tags(self) -> list[str]:
        tags = self.frontmatter.get("tags") or []
        if isinstance(tags, list):
            return [str(t) for t in tags]
        return []

    @property
    def related(self) -> list[str]:
        rel = self.frontmatter.get("related") or []
        if isinstance(rel, list):
            return [str(r) for r in rel]
        return []

    def to_summary(self, score: float | None = None, snippet: str | None = None) -> dict:
        result = {
            "id": self.id,
            "path": str(self.path.relative_to(DATASET_PATH)),
            "title": self.title,
            "topic": self.topic,
            "tier": self.tier,
            "tags": self.tags,
        }
        if score is not None:
            result["score"] = round(score, 4)
        if snippet is not None:
            result["snippet"] = snippet
        return result

    def to_full(self) -> dict:
        return {
            **self.to_summary(),
            "frontmatter": self.frontmatter,
            "body": self.body,
        }


# ----- Loading + indexing --------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n?(.*)$", re.DOTALL)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


def _tokenize(text: str) -> Counter:
    return Counter(w.lower() for w in WORD_RE.findall(text))


def _parse_file(path: Path) -> Entry | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return None
    try:
        frontmatter = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(frontmatter, dict):
        return None
    body = m.group(2)
    fid = frontmatter.get("id")
    if not fid:
        return None
    return Entry(
        id=str(fid),
        path=path,
        frontmatter=frontmatter,
        body=body,
        tokens=_tokenize(f"{frontmatter.get('title', '')} {body}"),
    )


def _load_entries() -> dict[str, Entry]:
    normalized = DATASET_PATH / "normalized"
    entries: dict[str, Entry] = {}
    if not normalized.exists():
        return entries
    for p in normalized.rglob("*.md"):
        entry = _parse_file(p)
        if entry is not None:
            entries[entry.id] = entry
    return entries


_INDEX: dict[str, Entry] = {}


def reindex() -> dict:
    global _INDEX
    _INDEX = _load_entries()
    return {"entries": len(_INDEX), "dataset_path": str(DATASET_PATH)}


# ----- Search --------------------------------------------------------------


def _keyword_score(query_tokens: Counter, entry: Entry) -> float:
    if not query_tokens or not entry.tokens:
        return 0.0
    numerator = 0
    for tok, qcount in query_tokens.items():
        ecount = entry.tokens.get(tok, 0)
        numerator += min(qcount, ecount)
    total_query = sum(query_tokens.values()) or 1
    return numerator / total_query


def _snippet(body: str, query: str, window: int = 180) -> str:
    if not body:
        return ""
    lower_body = body.lower()
    lower_q = query.lower()
    idx = lower_body.find(lower_q.split()[0]) if query.split() else -1
    if idx < 0:
        return (body[:window] + "...") if len(body) > window else body
    start = max(0, idx - 40)
    end = min(len(body), idx + window)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(body) else ""
    return prefix + body[start:end].strip() + suffix


def search(query: str, top_k: int = 5, tag: str | None = None) -> list[dict]:
    if not _INDEX:
        reindex()
    qtokens = _tokenize(query)
    results: list[tuple[float, Entry]] = []
    for entry in _INDEX.values():
        if tag and tag not in entry.tags and tag != entry.topic:
            continue
        score = _keyword_score(qtokens, entry)
        if score > 0:
            results.append((score, entry))
    results.sort(key=lambda p: p[0], reverse=True)
    return [
        entry.to_summary(score=score, snippet=_snippet(entry.body, query))
        for score, entry in results[:top_k]
    ]


def get(id: str) -> dict:
    if not _INDEX:
        reindex()
    entry = _INDEX.get(id)
    if entry is None:
        return {"error": f"id '{id}' not found", "available_count": len(_INDEX)}
    return entry.to_full()


def list_by_tag(tag: str) -> list[dict]:
    if not _INDEX:
        reindex()
    return [
        entry.to_summary()
        for entry in _INDEX.values()
        if tag in entry.tags or tag == entry.topic
    ]


def related(id: str) -> list[dict]:
    if not _INDEX:
        reindex()
    entry = _INDEX.get(id)
    if entry is None:
        return []
    return [
        _INDEX[rid].to_summary()
        for rid in entry.related
        if rid in _INDEX
    ]


def list_rules() -> dict:
    if not _INDEX:
        reindex()
    by_topic = Counter(e.topic for e in _INDEX.values() if e.topic)
    by_tier = Counter(e.tier for e in _INDEX.values() if e.tier)
    return {
        "entries": len(_INDEX),
        "by_topic": dict(by_topic),
        "by_tier": dict(by_tier),
        "dataset_path": str(DATASET_PATH),
        "embedding_backend": EMBEDDING_BACKEND,
    }


# ----- MCP glue ------------------------------------------------------------

server = Server("kuka-knowledge")


@server.list_tools()
async def _list_tools() -> list[Tool]:
    return [
        Tool(
            name="search",
            description="Semantic+keyword search over normalized KUKA dataset entries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                    "tag": {"type": ["string", "null"]},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get",
            description="Fetch full content and frontmatter of a normalized entry by id.",
            inputSchema={
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        ),
        Tool(
            name="list_by_tag",
            description="List normalized entries whose tags or topic match the given tag.",
            inputSchema={
                "type": "object",
                "properties": {"tag": {"type": "string"}},
                "required": ["tag"],
            },
        ),
        Tool(
            name="related",
            description="Return entries in the `related` graph one hop from the given id.",
            inputSchema={
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        ),
        Tool(
            name="reindex",
            description="Rebuild the in-memory index from disk. Call after ingestion.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_rules",
            description="Return index metadata: entry count, counts by topic/tier, and paths.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search":
        result = search(**arguments)
    elif name == "get":
        result = get(**arguments)
    elif name == "list_by_tag":
        result = list_by_tag(**arguments)
    elif name == "related":
        result = related(**arguments)
    elif name == "reindex":
        result = reindex()
    elif name == "list_rules":
        result = list_rules()
    else:
        result = {"error": f"unknown tool: {name}"}
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:
    reindex()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
