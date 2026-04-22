# Setup Guide — KUKA Agentic Workspace Template

Step-by-step instructions to take this template from zip-file to a functioning agentic workspace.

---

## 0. Prerequisites

| Tool | Why | Install |
|------|-----|---------|
| **Git + Git LFS** | Versioning + large binary handling for PDFs | `git` via OS package manager; `git lfs install --system` |
| **Cursor IDE** | Primary host for in-file editing and Cursor subagents | https://cursor.sh |
| **Claude Desktop (Cowork)** | Orchestration host | https://claude.ai/download |
| **Python 3.11+** | Runs the MCP servers | https://www.python.org |
| **uv** *(recommended)* or **pip** | Fast Python package install | `pip install uv` |
| **Ollama** *(optional, recommended)* | Local embeddings + local LLM for evals | https://ollama.com |

---

## 1. Copy the Template to Your New Workspace

The template is designed to be copied wholesale to a new location outside the repository it currently lives in. Do not fork-in-place unless you intend to work inside the parent repository.

```bash
# Example — Windows
xcopy /E /I /H "C:\path\to\KUKA_Agentic_Workspace_Template" "C:\path\to\MyKUKA_Workspace"

# Example — macOS/Linux
cp -R /path/to/KUKA_Agentic_Workspace_Template /path/to/MyKUKA_Workspace
```

Then in the new location:

```bash
cd /path/to/MyKUKA_Workspace
git init
git lfs install
git add .
git commit -m "Initial scaffold from KUKA Agentic Workspace Template"
```

---

## 2. Rename and Adjust

Open and edit the following to match your organization:

| File | What to change |
|------|----------------|
| `README.md` | Organization name, project title |
| `AGENTS.md` | "The Way Automation LLC" → your org; customer list section |
| `CLAUDE.md` | Same |
| `LICENSE` | Your copyright holder |
| `*.code-workspace` | Display name |
| `customer_programs/PROGRAM_REPOSITORY_INDEX.md` | Your customer list |
| `customer_programs/_manifest.json` | Your customer list (machine-readable) |

---

## 3. Add Your KUKA PDFs

Drop all KUKA-related PDFs into `kuka_dataset/raw_sources/`. Recommended organization:

```
kuka_dataset/raw_sources/
├─ vendor_manuals/        # KUKA official manuals
├─ application_notes/     # KUKA application notes
├─ training/              # KUKA College / Academy material
├─ error_codes/           # Error/alarm references
└─ third_party/           # Integrator notes, community compilations
```

These files are LFS-tracked automatically via `.gitattributes`.

**Copyright reminder:** Do not publish `raw_sources/` to a public repo unless you own the copyright or have permission. The normalization pipeline is designed to summarize and cite, not extract verbatim.

---

## 4. Install the MCP Servers

The template ships three local MCP servers. Install each:

```bash
cd mcp_servers/kuka_knowledge
uv pip install -e .
# or: pip install -e .

cd ../program_repository
uv pip install -e .

cd ../safety_lint
uv pip install -e .
```

*(Optional, recommended)* Install Ollama and pull an embedding model so `kuka_knowledge` works fully offline and keeps KUKA content local:

```bash
ollama pull nomic-embed-text
# or for higher quality:
ollama pull mxbai-embed-large
```

---

## 5. Register the MCP Servers with Cursor and Claude Desktop

### Cursor

1. Open Cursor → Settings → MCP.
2. Copy the contents of `mcp_servers/mcp.example.json` into your Cursor MCP config.
3. Update absolute paths to point at this workspace.
4. Restart Cursor. The MCP panel should show three green dots.

### Claude Desktop (Cowork)

1. Open Claude Desktop → Settings → Developer → Edit Config.
2. Merge the same three server blocks from `mcp.example.json`.
3. Restart Claude Desktop.

**Troubleshooting:** If a server fails to start, run it manually from the command line (`python -m kuka_knowledge.server`) to see the error. Common causes: missing Python 3.11, missing Ollama (if embeddings configured for Ollama), or wrong `cwd` in the MCP config.

---

## 6. Open the Workspace

### In Cursor

Open the `.code-workspace` file. Cursor will:
- Auto-apply `.cursor/rules/workspace-context.mdc` (marked `alwaysApply: true`).
- Apply glob-scoped rules as you open `.src`, `.dat`, `SAFETY_*.md` files.
- Make `.cursor/skills/` available via the skills system.
- Make `.cursor/agents/<role>.md` available as system-prompt bodies for subagents spawned via the `Task` tool.

### In Claude Desktop (Cowork)

- Add this workspace folder to Claude Desktop's project list.
- Claude will read `CLAUDE.md` and `AGENTS.md` on session start.
- A machine-specific runbook (Ollama, eval harness, Cursor/Claude MCP locations, Claude Project copy-paste text) is available in [COWORK_CLAUDE_DESKTOP.md](COWORK_CLAUDE_DESKTOP.md) when you maintain a filled-in copy in your repo or notes.

---

## 7. Run the Ingestion Pipeline

With MCP servers running and PDFs in place:

1. In Cursor, open any file in the workspace.
2. Invoke the skill: `@.cursor/skills/ingest-pdf-to-normalized/SKILL.md`
3. Follow the skill's instructions; it will walk an agent through extracting, chunking, frontmatter-tagging, and emitting normalized files.
4. Each normalized file is validated against `cowork/schemas/dataset_entry.schema.json` by the QA agent.

After ingestion:
- `kuka_dataset/normalized/` is populated.
- `DATASET_INDEX.md` is updated with topic → file mappings.
- `_manifest.json` lists every entry with frontmatter.
- The `kuka_knowledge` MCP server indexes on next call.

---

## 8. Run the Deep Research

To fill gaps not covered by your PDFs:

1. Open `research/RESEARCH_PROMPT_KUKA_KRL.md`.
2. Paste into Claude (Research mode recommended for multi-source citation).
3. Claude will emit additional normalized entries with `source_urls` and access dates.
4. Claude also updates `research/RESEARCH_TRACKING.md` to show remaining taxonomy coverage gaps.
5. Repeat until coverage is satisfactory.

---

## 9. Verify with the Eval Harness

```bash
cd evals
python runner.py --list                         # see available cases (ships with one: smoke_task_state)
python runner.py --case smoke_task_state --schema-only
python runner.py --all --schema-only            # run full suite in schema-only mode
```

The template ships with a single smoke test (`smoke_task_state`) that validates the `task_state.json` template against its schema. Add your own cases under `evals/cases/` and corresponding goldens under `evals/golden/` as you develop.

The eval harness is intentionally small; add more cases as you develop against real customer work.

---

## 10. Start Working

From this point, typical workflows are:

| Task | Entry point |
|------|-------------|
| Generate a new KRL program | `cowork/workflows/program_generation.md` |
| Review an existing program | `cowork/workflows/code_review.md` |
| Onboard a new customer | `cowork/workflows/customer_onboarding.md` |
| Ingest more documentation | `cowork/workflows/knowledge_ingestion.md` |
| Audit safety of a program | `cowork/workflows/safety_audit.md` |

Each workflow document names the agents involved, the schemas exchanged, and the MCP tools used.

---

## Common Problems

| Symptom | Cause | Fix |
|---------|-------|-----|
| MCP server red in Cursor | Path typo or Python version | Run manually: `python -m kuka_knowledge.server` |
| `kuka_knowledge.search` returns nothing | Index not built | Call `kuka_knowledge.reindex()` or delete `.cache/` and retry |
| Agent ignores dataset | `workspace-context.mdc` not set to `alwaysApply: true` | Check rule frontmatter |
| Ingestion skips PDFs | PDF is image-only (no text layer) | OCR the PDF first (e.g., `ocrmypdf`) |
| Schema validation fails constantly | Agent prompt drift | Run eval harness to diagnose; update `.cursor/agents/<role>.md` |

---

## Getting Help

- Agent roster and confer-graph: `.cursor/agents/_ROSTER.md`
- Handoff protocol: `AGENTS.md` § Handoff Protocol
- Dataset organization: `kuka_dataset/DATASET_README.md`
- Ingestion schema: `kuka_dataset/INGESTION_SCHEMA.md`
- Deep-research prompt: `research/RESEARCH_PROMPT_KUKA_KRL.md`
