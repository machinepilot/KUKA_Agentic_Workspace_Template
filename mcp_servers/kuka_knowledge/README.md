# kuka_knowledge MCP Server

Exposes the normalized KUKA dataset (`kuka_dataset/normalized/`) as a set of MCP tools: semantic search, lookup, listing by tag, related-graph walk, and reindex.

## Install

```bash
pip install uv
uv pip install -e .
# for local embeddings:
uv pip install -e ".[embeddings]"
```

## Configure

Environment variables:

| Var | Default | Purpose |
|-----|---------|---------|
| `KUKA_DATASET_PATH` | `../../kuka_dataset` | Absolute or relative path to the dataset root |
| `EMBEDDING_BACKEND` | `keyword` | `keyword` · `ollama` · `openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Model name (for ollama) |
| `OPENAI_API_KEY` | — | For `openai` backend |

## Tools

### `search(query: str, top_k: int = 5, tag: str | None = None) -> list[Result]`

Semantic + keyword search. Returns `[{ id, path, title, topic, tier, score, snippet }]`.

### `get(id: str) -> Entry`

Fetch a single entry's full content + frontmatter.

### `list_by_tag(tag: str) -> list[Summary]`

List entries matching a tag (from frontmatter `tags:` or `topic:` or category).

### `related(id: str) -> list[Summary]`

Walk the `related:` graph one hop from a given entry.

### `reindex() -> dict`

Rebuild the in-memory index from disk. Call after ingestion.

### `list_rules() -> dict`

Return metadata about which categories / tiers are in the index. Useful as a smoke test.

## Implementation Notes

This is a deliberately simple implementation intended to be readable and forkable:

- Keyword mode uses inverted-index scoring (Python only, no dependencies beyond mcp + pyyaml).
- Ollama embedding mode calls `/api/embeddings` per chunk and caches to `~/.cache/kuka_knowledge/`.
- All responses include a `citation` block with path, title, tier, and (when available) source pages / URL.

Grow this into a production retrieval stack as needed (FAISS / sqlite-vec / pgvector).
