# KUKA Dataset Ingestion Log

Raw PDFs live in `kuka_dataset/raw_sources/` (Git LFS). Normalized, citable entries are emitted under `kuka_dataset/normalized/`.

## Current inventory (PDFs)

| File | Size (bytes) | Document kind | Platform | KSS / notes | Primary topic(s) |
|------|--------------|---------------|----------|-------------|------------------|
| _(none — only `.gitkeep` present)_ | — | — | — | — | — |

**Action:** Add vendor PDFs to `kuka_dataset/raw_sources/`, then run the `ingest-pdf-to-normalized` skill (extract → chunk → emit normalized entries with frontmatter; validate; update manifest and `DATASET_INDEX.md`; reindex `kuka_knowledge`).

## Runs

| Date | PDF / batch | Normalized files produced | Agent / notes |
|------|-------------|---------------------------|---------------|
| 2026-04-21 | _n/a_ | _n/a_ | Workspace unbundled from `FANUC_dev`; `git` + LFS initialized. No raw PDFs yet. |
