# Workflow: Knowledge Ingestion

Turn raw KUKA PDFs (and research findings) into normalized, citable knowledge entries.

**Who runs this:** Orchestrator coordinating an Ingestion subagent + QA.
**Duration:** depends on volume (hours per ~100 pages for the first pass).

## Overview

```mermaid
flowchart LR
  PDFs[raw_sources/*.pdf] --> Inventory
  Inventory --> Extract[text extraction + OCR]
  Extract --> Chunk[chunk per schema]
  Chunk --> Categorize[articles | reference | examples | protocols | safety]
  Categorize --> Emit[emit normalized/*.md]
  Emit --> Validate[schema validation]
  Validate --> Manifest[update _manifest.json + DATASET_INDEX.md]
  Manifest --> Reindex[kuka_knowledge.reindex]
  Reindex --> QA[QA: citations + license + frontmatter]
  QA --> Log[update _ingestion_log.md]
```

## Inputs

- PDFs dropped into `kuka_dataset/raw_sources/` (LFS-tracked).
- Optional: research findings under `research/findings/` (already normalized format).

## Outputs

- New or revised entries under `kuka_dataset/normalized/{articles,reference,examples,protocols,safety}/`.
- Updated `kuka_dataset/_manifest.json`.
- Updated `kuka_dataset/DATASET_INDEX.md` topic table.
- Updated `kuka_dataset/_ingestion_log.md`.
- `REVIEW_ingestion_<date>.md` from QA.

## Steps

### Step 1 — Invoke Skill

Orchestrator invokes `.cursor/skills/ingest-pdf-to-normalized/SKILL.md`. Subagent executes that skill end-to-end.

### Step 2 — Schema Validation

Every emitted file's YAML frontmatter validates against `cowork/schemas/dataset_entry.schema.json`. Files that fail are rejected and returned to the ingestion subagent.

### Step 3 — Manifest Update

Ingestion subagent appends one entry per file to `_manifest.json`. Entry structure:

```json
{
  "id": "KUKA_REF_PTP_Motion",
  "path": "reference/KUKA_REF_PTP_Motion.md",
  "topic": "motion",
  "tier": "T1",
  "source": { "...": "..." },
  "revision_date": "2026-04-21"
}
```

And a row to `DATASET_INDEX.md` in the relevant topic section.

### Step 4 — Reindex

Orchestrator calls `kuka_knowledge.reindex()` (the MCP server re-embeds new/changed entries).

### Step 5 — QA Gate

Orchestrator spawns QA with the list of new entries. QA checks:

- Frontmatter complete and schema-valid.
- `source` block has `tier`, `pages` (for PDFs), `access_date`.
- No verbatim extract exceeding a short quote.
- Correct category (article vs reference vs example vs protocol vs safety).
- Related entries reference valid ids.

Produces `REVIEW_ingestion_<date>.md`. Any findings → return to ingestion for fixup.

### Step 6 — Log

Append an entry to `kuka_dataset/_ingestion_log.md`:

| Date | Agent | PDFs Ingested | Entries Produced | Review Verdict |
|------|-------|---------------|------------------|----------------|
| 2026-04-21 | Ingestion | KUKA_KRL_RefGuide.pdf | 23 | pass |

### Step 7 — Commit

Commit the normalized files, manifest, index, and log in a single commit: "Ingest `<source>`: `<N>` entries."

## Re-ingestion

When a PDF is superseded (new KSS version, new manual revision):

1. Do NOT delete the old normalized entry unless the new content is strictly superset.
2. Create new entries with updated `revision_date` and `kss_version`.
3. Set `related:` in both old and new to cross-reference.
4. Mark the old entry's frontmatter with `superseded_by: <new_id>` (optional).

## Exit Criteria

- All new entries schema-valid.
- Manifest and index updated.
- Reindex called.
- QA verdict `pass` or `conditional`.
- Log entry written.
