# KUKA Agentic Workspace Template

A copy-and-go workspace template for KUKA industrial robot programming with Cursor IDE + Cowork (Claude Desktop), built around a multi-agent "robot cell" topology.

**Target platform:** KUKA KR C4 / KR C5 controllers, KSS 8.x, KRL language.
**Primary users:** Industrial integrators, controls engineers, automation OEMs.
**Philosophy:** Every piece is either a prompt, a schema, or a Model Context Protocol (MCP) tool — no bespoke runtime, no vendor lock-in, portable across Cursor / Claude Desktop / Zed / Windsurf.

---

## What's in the Box

| Path | Purpose |
|------|---------|
| `AGENTS.md` | Master instruction file read by both Cursor and Cowork |
| `CLAUDE.md` | Cowork-specific orchestration instructions |
| `.cursor/rules/` | Glob-scoped coding rules (KRL conventions, safety, fieldbus, etc.) |
| `.cursor/agents/` | Per-role agent system prompts (Orchestrator, Architect, Motion, Safety, QA, etc.) |
| `.cursor/skills/` | Procedural skills (PDF ingestion, lint, eval harness, setup) |
| `cowork/templates/` | Document templates (program specs, reviews, handoffs) |
| `cowork/schemas/` | JSON Schemas (Draft 2020-12) for every inter-agent handoff |
| `cowork/workflows/` | Multi-agent workflow scripts (program generation, code review, etc.) |
| `kuka_dataset/` | Normalized KUKA knowledge base (ingested from your PDFs + research) |
| `customer_programs/` | Production backups per customer (kept separate from dataset) |
| `mcp_servers/` | Model Context Protocol servers: knowledge retrieval, repo query, safety lint |
| `evals/` | Lightweight eval harness to keep agent behavior measurable |
| `research/` | Deep-research prompt + coverage tracker for filling dataset gaps |

---

## The Multi-Agent "Robot Cell"

The agents are organized the way a real robot cell is organized:

| Agent | Robot-Cell Analog | What it Does |
|-------|------------------|--------------|
| **Orchestrator** | Cell PLC / Supervisor | Routes work, owns `task_state.json`, enforces schemas |
| **Intake** | Perception | Parses user request into a structured spec |
| **Architect** | Task planner | Designs program structure, allocates variables |
| **Motion Synthesis** | Trajectory planner | Generates KRL motion modules |
| **Integration** | I/O layer | Maps Profinet / EtherNet-IP / discrete signals |
| **Safety** | Safety PLC | Applies ISO 10218, SafeOperation, SRM rules |
| **QA** | Diagnostics | Runs lint + judgment review |
| **Documentation** | HMI / logging | Emits handoffs and operator docs |

See `.cursor/agents/_ROSTER.md` for the complete confer-graph.

---

## Getting Started

Read `SETUP.md` for the full walkthrough. Quick version:

1. Copy this entire folder to a new location outside any existing repo.
2. `git init && git lfs install` in the new location.
3. Drop your KUKA PDFs into `kuka_dataset/raw_sources/`.
4. Install MCP servers (see `mcp_servers/README.md`).
5. Register MCP servers in Cursor Settings (copy `mcp_servers/mcp.example.json`).
6. Open this workspace in Cursor. Both `AGENTS.md` and the `.cursor/rules/` take effect automatically.
7. Run the `ingest-pdf-to-normalized` skill to populate `kuka_dataset/normalized/`.
8. Run the deep-research prompt in `research/RESEARCH_PROMPT_KUKA_KRL.md` via Claude Research to fill remaining gaps.

---

## Design Principles

1. **Dataset is the authority.** Customer programs are context, not truth. Normalized dataset entries are truth. Vendor PDFs are source.
2. **Every handoff is schema-validated.** If the Architect emits something that fails `program_spec.schema.json`, the Orchestrator rejects it — that is the agentic equivalent of a compile error.
3. **Deterministic where possible, probabilistic where necessary.** Safety lint is code. Architecture is LLM. Combining them is QA.
4. **Small surface, clear edges.** Each agent has a single job, a typed input, a typed output, and an explicit list of agents it may confer with.
5. **Copyright-safe.** Raw vendor material stays in LFS-tracked `raw_sources/`, never leaks verbatim into normalized or ingested outputs.

---

## Credit & Provenance

This template is derived from patterns proven in the FANUC_dev workspace at The Way Automation LLC, generalized and extended with agent role definitions, MCP integration, JSON-schema handoffs, and an eval harness.
