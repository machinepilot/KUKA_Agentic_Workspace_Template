---
name: ingest-pdf-to-normalized
description: Ingest KUKA PDFs (manuals, application notes, training material, error code refs) from kuka_dataset/raw_sources/ into normalized knowledge entries under kuka_dataset/normalized/. Use when new PDFs are added or when re-ingesting after schema updates.
---

# Ingest PDF to Normalized

Turn a directory of raw KUKA PDFs into typed, schema-validated knowledge entries the agent cell can reliably cite.

## When to Use

- New PDFs added to `kuka_dataset/raw_sources/`.
- `kuka_dataset/INGESTION_SCHEMA.md` changed (re-ingest to conform).
- `kuka_knowledge` MCP search quality is poor (gap indicates missing normalization).

## Prerequisites

- Python 3.11+ with `pdfplumber` or `pypdf` installed (for text extraction).
- Optional: `ocrmypdf` if any PDF is image-only.
- `kuka_dataset/INGESTION_SCHEMA.md` read in context.
- `cowork/schemas/dataset_entry.schema.json` read in context.
- `cowork/templates/INGESTION_ENTRY_TEMPLATE.md` read in context.

## Steps

### 1. Inventory

List every PDF in `kuka_dataset/raw_sources/` with its current file name and size. For each PDF, determine:

- **Document kind** — `vendor_manual`, `application_note`, `training`, `error_code_ref`, `white_paper`, `third_party_integrator`, `community`.
- **Platform** — KR C4, KR C5, KR C2 (legacy), iiQKA, Sunrise.
- **KSS version(s)** — from title page or metadata.
- **Primary topic(s)** — motion, safety, fieldbus, KRL programming, KAREL-equivalent, etc.

Output this inventory to `kuka_dataset/_ingestion_log.md` as a table.

### 2. Extract Text

For each PDF, extract text per page. Preserve page numbers — they are needed for citation. If a PDF is image-only, OCR it first:

```bash
ocrmypdf input.pdf output.pdf
```

Keep extracted text in a scratch directory (`kuka_dataset/raw_sources/_scratch/`, gitignored).

### 3. Chunk

Per `kuka_dataset/INGESTION_SCHEMA.md`:

- One concept per file. Chunks should be coherent units (e.g., "PTP Motion Instruction," not the entire motion chapter).
- Max ~400 lines per normalized file. Split longer chunks.
- Preserve section hierarchy in markdown headings.

### 4. Categorize

For each chunk, decide the target subdirectory:

- `articles/` — conceptual explanations, how-to. Prefix `ONE_<topic>_<slug>.md`.
- `reference/` — syntax, instruction reference, parameter tables. Prefix `KUKA_REF_<topic>.md`.
- `examples/` — code examples with context. Prefix `EG_<scenario>.md`.
- `protocols/` — fieldbus, EKI, RSI, mxAutomation. Prefix `KUKA_<protocol>_<aspect>.md`.
- `safety/` — safety content only. Prefix `KUKA_SAFETY_<topic>.md`.

### 5. Emit Normalized Entries

For each chunk, write a file under the chosen subdirectory with:

**YAML frontmatter** (required; see `INGESTION_SCHEMA.md` for full spec):

```yaml
---
id: KUKA_REF_PTP_Motion
title: KRL PTP Motion Instruction
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.3, KSS 8.6]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.x Operating and Programming Instructions"
  tier: T1
  pages: [412, 418]
  access_date: 2026-04-21
license: reference-only
revision_date: 2026-04-21
related: [KUKA_REF_LIN_Motion, ONE_motion_termination]
difficulty: intermediate
tags: [motion, ptp, asynchronous]
---
```

**Body** — summary first, syntax/details next, examples last. Cite by page range. Do NOT reproduce more than a short quote verbatim — summarize in your own words.

### 6. Validate

For each file, validate the frontmatter block against `cowork/schemas/dataset_entry.schema.json`. If a field is missing or typed wrong, fix and re-validate.

### 7. Update Manifests

- Append an entry to `kuka_dataset/_manifest.json` with the file's `id`, path, frontmatter summary.
- Add a row to `kuka_dataset/DATASET_INDEX.md` under the appropriate topic section.

### 8. Reindex

Trigger `kuka_knowledge.reindex()` via the MCP tool so new entries are searchable.

### 9. QA Gate

Hand every new entry to the QA agent for validation:
- Frontmatter schema-valid?
- Citations present and correct?
- No verbatim copyright violation?
- Topic / category correct?

QA issues a `REVIEW_ingestion_<date>.md`. Fix any findings before declaring the ingestion done.

### 10. Log

Update `kuka_dataset/_ingestion_log.md` with which PDFs produced which normalized entries, date, and agent.

## Notes

- Raw PDFs stay in `raw_sources/` and remain git-lfs tracked. Normalized entries are the citable product.
- When a PDF is updated (new KSS version), produce a *new* normalized entry with incremented `revision_date`; keep the old for provenance if still relevant.
- The Architect and Motion agents will cite normalized entries via `kuka_knowledge.search`; a good normalization schema means they find the right entry on the first search.
