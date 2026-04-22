# MCP Servers

Three Model Context Protocol (MCP) servers bundled with this workspace. MCP is an open specification for LLM hosts (Cursor, Claude Desktop, Zed, Windsurf) to plug into external tools, resources, and prompts via a local JSON-RPC protocol.

https://modelcontextprotocol.io

## Why MCP

- **Portable.** Same server works across any MCP-capable host.
- **Scoped.** Each server owns a narrow surface; agents call typed tools instead of raw files.
- **Indexed.** Servers maintain their own caches (embeddings, manifests, rule catalogs).
- **Citation-aware.** Every tool response carries provenance.
- **Stable.** Schema of tool inputs/outputs is machine-verifiable; prompt drift does not break integration.

## Shipped Servers

| Server | Purpose | Key Tools |
|--------|---------|-----------|
| [`kuka_knowledge/`](./kuka_knowledge/) | Semantic + keyword search over `kuka_dataset/normalized/` | `search`, `get`, `list_by_tag`, `related`, `reindex` |
| [`program_repository/`](./program_repository/) | Query customer programs | `list_customers`, `get_program`, `search`, `diff` |
| [`safety_lint/`](./safety_lint/) | Static safety / convention checks on `.src` | `lint_src`, `list_rules`, `explain_rule` |

## Quick Install

```bash
# from workspace root, with a Python 3.11+ venv active
pip install uv

cd mcp_servers/kuka_knowledge && uv pip install -e . && cd ../..
cd mcp_servers/program_repository && uv pip install -e . && cd ../..
cd mcp_servers/safety_lint && uv pip install -e . && cd ../..
```

## Register with Cursor

Open Cursor → Settings → MCP → Edit Configuration. Merge in the contents of [`mcp.example.json`](./mcp.example.json). Replace `${workspaceFolder}` with absolute paths if your Cursor version does not interpolate.

## Register with Claude Desktop

Settings → Developer → Edit Config. Merge the same `mcpServers` blocks. Absolute paths required.

## Ollama (optional, for local embeddings)

The `kuka_knowledge` server can embed text locally via Ollama, avoiding API calls and keeping KUKA content on your machine.

```bash
ollama pull nomic-embed-text
# optional, higher quality:
# ollama pull mxbai-embed-large
```

Then set `EMBEDDING_BACKEND=ollama` and `EMBEDDING_MODEL=nomic-embed-text` in the server config (see `mcp.example.json`).

## Developing Your Own MCP Server

1. Follow the stub pattern in any of the three bundled servers.
2. Use the official Python `mcp` SDK (`pip install mcp`).
3. Each server is a Python module with a `server.py` exposing `@server.tool()` handlers.
4. Register stdio transport (default) or SSE.
5. Add a block to `mcp.example.json`.
6. Document new tools here.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Server shows red in Cursor | Run the module manually: `python -m <server_name>.server`. Read stderr. |
| `mcp` import error | `pip install mcp` in the venv that Cursor's config points at. |
| Ollama calls time out | Ensure `ollama serve` is running; `curl http://localhost:11434/api/tags`. |
| Tool "not found" | Did you restart the host after editing MCP config? |
