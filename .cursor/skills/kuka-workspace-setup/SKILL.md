---
name: kuka-workspace-setup
description: First-run setup walkthrough for a freshly copied KUKA Agentic Workspace (git, LFS, Python venv, MCP servers, Ollama, Cursor registration). Use when bootstrapping the workspace on a new machine.
---

# KUKA Workspace Setup

Bootstrap a fresh copy of the KUKA Agentic Workspace on a new machine.

## When to Use

- First time opening the workspace after copying the template.
- Setting up a teammate's machine.
- After a major template upgrade.

## Prerequisites

- Git and Git LFS installed and on PATH.
- Python 3.11+ on PATH (`python --version` or `python3 --version`).
- Cursor IDE installed.
- Claude Desktop installed.
- (Optional) Ollama installed: https://ollama.com

## Steps

### 1. Git + LFS

```bash
cd <workspace-root>
git init
git lfs install
git lfs track "kuka_dataset/raw_sources/**/*.pdf"
git add .gitattributes .gitignore
git add .
git commit -m "Initial scaffold"
```

### 2. Python Environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Unix:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install uv
```

### 3. Install MCP Servers

```bash
cd mcp_servers/kuka_knowledge
uv pip install -e .

cd ../program_repository
uv pip install -e .

cd ../safety_lint
uv pip install -e .

cd ../..
```

### 4. Ollama (Recommended)

```bash
# Install Ollama if not already:  https://ollama.com
ollama pull nomic-embed-text
# optional higher quality embeddings:
# ollama pull mxbai-embed-large
```

Verify Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

### 5. Configure `kuka_knowledge` Embeddings Backend

Edit `mcp_servers/kuka_knowledge/server.py` (or its config file) to point at Ollama:

```python
EMBEDDING_BACKEND = "ollama"  # or "openai"
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
```

### 6. Register MCP Servers with Cursor

Open Cursor → Settings → MCP → Add configuration.

Copy the contents of `mcp_servers/mcp.example.json`. Adjust absolute paths for your machine. Save. Restart Cursor.

Verify: Cursor's MCP panel should show three green indicators.

### 7. Register with Claude Desktop (Cowork)

Open Claude Desktop → Settings → Developer → Edit Config. Merge the same server blocks from `mcp.example.json`. Save. Restart Claude Desktop.

### 8. Smoke-Test MCP Servers

In Cursor, ask the agent to run:
- `kuka_knowledge.list_rules()` (should return built-in list even with empty dataset)
- `program_repository.list_customers()` (should return empty list or the `_example_customer`)
- `safety_lint.list_rules()` (should return the seed rule catalog)

### 9. Verify Rules and Agents

Open any `.src` file (even a blank test one). Cursor's rule indicator should show:
- `workspace-context` (always)
- `kuka-krl-conventions` (glob match on `*.src`)
- `kuka-safety` (glob match)

Open `.cursor/agents/_ROSTER.md` and verify all eight agent files are present.

### 10. Run Eval Harness (Smoke)

```bash
cd evals
python runner.py --list
```

Should list available cases (even if empty on a fresh setup).

### 11. Ingest PDFs (when ready)

Drop PDFs into `kuka_dataset/raw_sources/` and invoke `.cursor/skills/ingest-pdf-to-normalized/SKILL.md`.

### 12. Run Deep Research (when ready)

Paste `research/RESEARCH_PROMPT_KUKA_KRL.md` into Claude (Research mode).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP server "red" in Cursor | Run `python -m <package>.server` manually; check stderr |
| `kuka_knowledge.search` returns nothing | Reindex: `kuka_knowledge.reindex()` — or check dataset is non-empty |
| Ollama embedding call fails | Confirm `ollama serve` is running; `ollama list` shows the model |
| Rules not activating | Rule frontmatter `globs:` correct? File path matches glob? |
| Schema validation always fails | Check schema version matches `$schema` URL in produced JSON |
