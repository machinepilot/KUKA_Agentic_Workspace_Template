# Cowork + Cursor + Ollama — runbook (this machine)

Single source of truth for how this **KUKA Agentic Workspace** is wired on Windows. Portable template details stay in [SETUP.md](SETUP.md) and [mcp_servers/mcp.example.json](mcp_servers/mcp.example.json); **absolute paths** live in the config files below (not committed as one file; use `mcp.example.json` as the pattern on a new clone).

## Machine paths (reference)

| Role | Path |
|------|------|
| Workspace root | `C:\Users\tripp\KUKA_Agentic_Workspace_Template` |
| Python (MCP) | `C:\Users\tripp\KUKA_Agentic_Workspace_Template\.venv\Scripts\python.exe` |
| Cursor MCP (global) | `C:\Users\tripp\.cursor\mcp.json` |
| Claude Desktop MCP | `C:\Users\tripp\AppData\Roaming\Claude\claude_desktop_config.json` |
| Ollama | `C:\Users\tripp\AppData\Local\Programs\Ollama` (daemon `http://127.0.0.1:11434`) |

`kuka-knowledge` env includes `EMBEDDING_BACKEND=ollama`, `EMBEDDING_MODEL=nomic-embed-text`, `OLLAMA_BASE_URL=http://localhost:11434` (or `127.0.0.1`).

After editing Claude’s JSON, **fully quit and restart** Claude Desktop.

## Ollama models (pulled for this stack)

- `nomic-embed-text` — embeddings for `kuka_knowledge` MCP
- `qwen2.5-coder:7b` — default for `evals` **replay** mode (`EVAL_MODEL`)
- You may also have `llama3:latest` (works for the same HTTP `/api/chat` smoke)

Keep the Ollama tray app / service running when using search with embeddings or eval replay.

## Claude Project (one-time in Claude UI)

The app cannot be scripted. Do this once per machine:

1. In Claude Desktop, create a **Project** (e.g. “KUKA Agentic Workspace”).
2. **Custom instructions** — paste the block below (workspace path is already spelled out in the last line for this machine).
3. Optional: add small “Project knowledge” uploads (`AGENTS.md`, `CLAUDE.md`) *or* rely on @ / attach from disk to avoid duplicate stale copies.

**Custom instructions to paste**

```text
You are the Orchestrator (Cowork) for the KUKA Agentic Workspace. The tool split is: this chat (Claude) plans and writes specs, handoffs, reviews, and task state; Cursor IDE edits production KRL and customer program files. One folder on disk is the source of truth.

On every new conversation, do this in order:
1) Open and read: C:\Users\tripp\KUKA_Agentic_Workspace_Template\AGENTS.md
2) Then read: C:\Users\tripp\KUKA_Agentic_Workspace_Template\CLAUDE.md
3) Skim: C:\Users\tripp\KUKA_Agentic_Workspace_Template\.cursor\agents\_ROSTER.md
4) If the user names a task, load that task’s task_state.json (or ask where it lives) before planning.

You own writing/updating: cowork/**, PROGRAM_SPEC_*.md, HANDOFF_*.md, REVIEW_*.md, SAFETY_REVIEW_*.md, task_state.json, and research/tracking per workflow. You do not write production .src or .dat when Cursor is available—produce handoff artifacts instead.

Use MCP tools first: kuka_knowledge (Ollama embeddings at http://127.0.0.1:11434, nomic-embed-text), program_repository, safety_lint. If an MCP call errors, say so; do not invent KRL.

Workspace root: C:\Users\tripp\KUKA_Agentic_Workspace_Template
```

**First message template** (optional, each new session)

```text
Session start for KUKA Agentic Workspace. Same folder for Cursor and this Project. Read AGENTS.md, then CLAUDE.md, then .cursor/agents/_ROSTER.md, then help load or create task_state. I want to: <one sentence>.
```

## Eval harness

From the workspace root, with the repo venv active:

```powershell
cd C:\Users\tripp\KUKA_Agentic_Workspace_Template
.\.venv\Scripts\python.exe evals\runner.py --all --schema-only
```

- **CI-style check:** `--schema-only` (no LLM; validates `golden/*.json` against schemas). This should **exit 0**.

**Ollama replay** (local LLM + `.cursor/agents/<agent>.md` as system prompt):

```powershell
$env:EVAL_BACKEND="ollama"
$env:EVAL_MODEL="qwen2.5-coder:7b"
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
.\.venv\Scripts\python.exe evals\runner.py --case smoke_task_state --replay
```

Replay may **SCHEMA_FAIL** or **DIFF** even when the stack is fine: the model output is not guaranteed to match the committed golden. Use replay for **development**; rely on **schema-only** for a stable pass/fail bar unless you have tuned cases and models.

## Optional: Ollama as a model inside Cursor

In Cursor, open **Settings → Models** (or **Cursor Settings →** search “Ollama”): add the Ollama base URL `http://127.0.0.1:11434` and select a local model (e.g. `qwen2.5-coder:7b`) for optional offline or cheap subagent runs. This is independent of MCP; MCP still uses the venv `python` processes above.

## Operations checklist

- **MCP health:** [`.cursor/skills/register-mcp-servers/SKILL.md`](.cursor/skills/register-mcp-servers/SKILL.md) — verify `list_rules` / `list_customers` / `search` / `reindex` after path changes.
- **New normalized entries:** run `kuka_knowledge.reindex` (MCP) or restart the server after large dataset changes.
- **Handoff contract:** [AGENTS.md](AGENTS.md) — schema-validated documents between Cowork and Cursor.

## Related

- [SETUP.md](SETUP.md) — first-time install from the template
- [research/RESEARCH_TRACKING.md](research/RESEARCH_TRACKING.md) — research sprint coverage
- [kuka_dataset/_ingestion_log.md](kuka_dataset/_ingestion_log.md) — raw PDF → normalized pipeline log
