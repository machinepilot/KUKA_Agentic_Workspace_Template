---
name: register-mcp-servers
description: Register the three bundled MCP servers (kuka_knowledge, program_repository, safety_lint) with Cursor and Claude Desktop. Use when setting up a fresh machine or after adding a new MCP server.
---

# Register MCP Servers

Make the bundled Model Context Protocol servers visible to Cursor and Claude Desktop so agents can call their tools.

## When to Use

- First-time setup on a machine (also covered by `kuka-workspace-setup` SKILL).
- After installing a new MCP server.
- After re-locating the workspace (paths in MCP configs need updating).
- When an MCP server's stdio transport is failing and you need to diagnose.

## Prerequisites

- Servers installed (`uv pip install -e .` in each `mcp_servers/<name>/`).
- Python venv path known.
- Absolute path to each server module known.
- Cursor and/or Claude Desktop installed.

## Steps

### 1. Read `mcp_servers/mcp.example.json`

It contains three server blocks:

```json
{
  "mcpServers": {
    "kuka-knowledge": {
      "command": "python",
      "args": ["-m", "kuka_knowledge.server"],
      "cwd": "${workspaceFolder}/mcp_servers/kuka_knowledge",
      "env": {
        "KUKA_DATASET_PATH": "${workspaceFolder}/kuka_dataset",
        "EMBEDDING_BACKEND": "ollama",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "EMBEDDING_MODEL": "nomic-embed-text"
      }
    },
    "program-repository": {
      "command": "python",
      "args": ["-m", "program_repository.server"],
      "cwd": "${workspaceFolder}/mcp_servers/program_repository",
      "env": {
        "CUSTOMER_PROGRAMS_PATH": "${workspaceFolder}/customer_programs"
      }
    },
    "safety-lint": {
      "command": "python",
      "args": ["-m", "safety_lint.server"],
      "cwd": "${workspaceFolder}/mcp_servers/safety_lint"
    }
  }
}
```

### 2. Cursor Registration

1. Cursor → Settings (Ctrl/Cmd+,) → search "MCP" or open the MCP panel directly.
2. Click "Edit Configuration."
3. Paste or merge the three server blocks.
4. Replace `${workspaceFolder}` with the absolute path if Cursor does not interpolate it.
5. Ensure `command` points at your Python (may need absolute path to `.venv/bin/python` or `.venv\Scripts\python.exe`).
6. Save.
7. Restart Cursor.
8. Open the MCP panel; each server should appear with a green indicator within a few seconds. A red indicator means the server crashed on start — see "Diagnose a Red Indicator" below.

### 3. Claude Desktop Registration

1. Claude Desktop → Settings → Developer → Edit Config.
2. The file is JSON. Merge the three server blocks into the top-level `mcpServers` object.
3. Use absolute paths (Claude Desktop does not have a workspace concept).
4. Save.
5. Fully quit and relaunch Claude Desktop.
6. In a chat, ask Claude to list available MCP tools; the tools from the three servers should be enumerable.

### 4. Verify Each Server

Ask an agent to call:

- `kuka_knowledge.list_by_tag("motion")` — returns list (may be empty until ingestion runs).
- `program_repository.list_customers()` — returns customer list.
- `safety_lint.list_rules()` — returns rule catalog.

All three should succeed. If any fails, diagnose.

## Diagnose a Red Indicator

1. **Run the server directly**:
   ```bash
   cd mcp_servers/<name>
   python -m <name>.server
   ```
   Stdin should be open; press Enter and see if the server logs anything useful to stderr. `Ctrl+C` to exit.

2. **Check Python version**: `python --version` — must be 3.11+.

3. **Check install**: `pip show mcp` and `pip show <name>` — both present?

4. **Check paths** in the MCP config — `${workspaceFolder}` interpolation, absolute paths correct?

5. **Check Ollama** (for `kuka_knowledge`): `curl http://localhost:11434/api/tags` returns success?

6. **Check ports**: stdio servers do not bind ports; an HTTP+SSE variant would. Default template uses stdio.

## Adding a New MCP Server

1. Create `mcp_servers/<new_name>/` with a `pyproject.toml` and `server.py` following the existing stubs.
2. Install: `uv pip install -e .`
3. Add a block to `mcp.example.json`.
4. Re-register in Cursor and Claude Desktop.
5. Document the new tools in `mcp_servers/README.md`.
6. Add to `AGENTS.md` § MCP Tools if broadly useful.

## Close the Loop

Commit any change to `mcp.example.json`. Local-only overrides go in `mcp.local.json` (gitignored).
