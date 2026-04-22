# KUKA Dataset Ingestion Log

Raw PDFs live in `kuka_dataset/raw_sources/` (Git LFS). Normalized, citable entries are emitted under `kuka_dataset/normalized/`.

## Current inventory (PDFs)

All files under `kuka_dataset/raw_sources/vendor_manuals/`. Relocated from workspace root on 2026-04-22.

| File | Size (MB) | Pages | Document kind | Platform | KSS / version | Issued | Primary topic(s) |
|------|-----------|-------|---------------|----------|---------------|--------|------------------|
| `0012401208_EN.pdf` | 0.4 | 1 | vendor_manual (product datasheet) | KR C4, KR C5 | n/a | 2023-ish | external axis — KL 5000 RV3 linear unit |
| `KR C5 Quick Start.pdf` | 2.4 | 19 | vendor_manual (Xpert quick-start) | KR C5 | any KSS on KR C5 | 2026-01 (Xpert export) | cabinet installation, transport, initial commissioning |
| `KSS_87_SI_en.pdf` | 31.8 | 761 | vendor_manual (System Integrator guide) | KR C4, KR C5 | KSS 8.7 | 2023-07-07 | KRL programming, motion, variables, I/O, interrupts, safety overview, system config, diagnostics |
| `KST_SafeOperation_36_en.pdf` | 6.2 | 307 | vendor_manual (system technology option) | KR C4, KR C5 | KSS 8.7 + SafeOp 3.6 | 2024-02-07 | safety-rated motion monitoring — zones, velocity, SRM, reference switches, brake test |
| `KST_WorkVisual_60_en.pdf` | 10.9 | 280 | vendor_manual (system technology tool) | KR C4, KR C5 | KSS 8.2 / 8.3 / 8.5 / 8.6 / 8.7; VW 8.2 / 8.3 / 8.6 / 8.7 | 2025-03-27 | WorkVisual project engineering, fieldbus mapping (Profinet/EtherNetIP/EtherCAT), safety config, KRL deployment |
| `KUKA_KR_C5_EN.pdf` | 1.9 | 2 | vendor_manual (product datasheet) | KR C5 | n/a | 2021-03 | KR C5 controller spec sheet |
| `MA_KR_C5_Cabinet_en.pdf` | 15.2 | 230 | vendor_manual (assembly instructions) | KR C5 (dualcab/triplecab/quadcab) | n/a | 2025-04-02 | cabinet mechanical install, interfaces, cooling, power, REACH |
| `MA_KR_C5_basiccab_en.pdf` | 7.9 | 206 | vendor_manual (assembly instructions) | KR C5 (basiccab) | n/a | 2025-11-23 | cabinet mechanical install, interfaces, cooling, power, REACH (basiccab variant) |
| `WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf` | 16.9 | 337 | training (KUKA College, Robot Programming 2 — lecture) | KR C4 | KSS 8.5 (content applies to 8.x) | 2019-07-31 | advanced KRL — structured programming, variables, subprograms, interrupts, motion blending, SPLINE, technology packages |
| `WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf` | 4.3 | 105 | training (KUKA College, Robot Programming 2 — exercises) | KR C4 | KSS 8.5 | 2019-07-31 | paired exercise book for the P2 course — worked palletizing program, variable declarations, collision detection, SPLINE exercises |

### Notes on the inventory

- **All PDFs are KUKA copyright.** `license: reference-only` applies to every derived normalized entry. Summarize in our own words; short quotes only.
- **Cabinet manual overlap.** `MA_KR_C5_Cabinet_en.pdf` and `MA_KR_C5_basiccab_en.pdf` share substantial content (install, cooling, REACH) with variant-specific differences. Chunking will produce shared-concept entries that cite both, plus variant-specific entries where they diverge.
- **WorkVisual covers KSS 8.2–8.7 + VW 8.2–8.7.** Normalized entries will list all supported controllers in `kuka_platform` / `controller` fields.
- **P2 training predates KSS 8.7.** Content is authored for KSS 8.5 but the KRL constructs remain valid through 8.7; entries will declare `controller: [KSS 8.5]` and cross-reference the SI manual for 8.7 confirmation where relevant.
- **`0012401208_EN` is a rail-axis datasheet**, not a KRL topic — it belongs to a (new) `external_axis` topic in the category taxonomy.
- **Training material (`PROG P2` pair) is the highest-leverage source for `articles/` and `examples/`** because it was written for human learners and is already chunked pedagogically. Ingest the lecture as articles, the exercise book as examples.

## Proposed category breakdown (pre-chunking estimate)

| Category | Est. entries | Primary sources |
|----------|--------------|-----------------|
| `reference/` | ~30 | KSS 8.7 SI (KRL instructions, system variables, data types), cabinet specs, KL 5000 |
| `articles/` | ~40 | KSS 8.7 SI conceptual sections, P2 Training lecture, WorkVisual concepts, SafeOperation concepts |
| `examples/` | ~20 | P2 Exercise Book (palletizing, pick/place, collision detect, structured programs, SPLINE) |
| `protocols/` | ~10 | WorkVisual fieldbus chapters, KR C5 interface sheet |
| `safety/` | ~25 | SafeOperation 3.6 (zones, velocity, SRM, ref switches, brake test), KSS 8.7 safety chapter |
| **Total (rough)** | **~125** | |

## Runs

| Date | PDF / batch | Normalized files produced | Agent / notes |
|------|-------------|---------------------------|---------------|
| 2026-04-21 | _n/a_ | _n/a_ | Workspace unbundled from `FANUC_dev`; `git` + LFS initialized. No raw PDFs yet. |
| 2026-04-22 | 10-PDF triage (all vendor_manuals) | 0 (triage stage) | Cowork Orchestrator; PDFs relocated root → `raw_sources/vendor_manuals/`; outlines + first-3 pages extracted to `raw_sources/_scratch/`. Awaiting triage approval before chunking/ingestion. |
| 2026-04-22 | Pass-1 emission (Option 2 / batch) across all 10 PDFs | 33 new normalized entries (34 total incl. prior `EG_PTP_Hello`) | Cowork Orchestrator; emitted `reference/` ×8, `articles/` ×10, `examples/` ×5, `protocols/` ×4, `safety/` ×6. All entries schema-valid against `cowork/schemas/dataset_entry.schema.json`; cross-references clean (0 orphan `related:` ids). `_manifest.json` regenerated; `DATASET_INDEX.md` populated across Motion, I/O, Interrupts, Frames, Structured-Programming, Safety, Fieldbus, WorkVisual, Mastering, Application sections. Schema fixes in pass: (a) quoted ISO-date fields to satisfy YAML-string typing; (b) renamed `KUKA_KRC5_Bus_Interfaces` → `KUKA_Fieldbus_KRC5_Interfaces` to match id regex. Copyright guardrail respected — summaries in own words; page-citation ranges on every vendor-manual entry. MCP `kuka_knowledge.reindex()` not available in this Cowork session; reindex deferred to next Cursor-side run. |
