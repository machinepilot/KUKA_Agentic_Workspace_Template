# KUKA Dataset

Normalized, citable knowledge that the agent cell treats as authoritative.

## Structure

```
kuka_dataset/
├─ DATASET_README.md              # this file
├─ DATASET_INDEX.md               # topic → file lookup (human-readable)
├─ INGESTION_SCHEMA.md            # frontmatter spec + chunking rules
├─ _manifest.json                 # machine-readable catalog
├─ _manifest.schema.json          # schema for the manifest
├─ _ingestion_log.md              # chronological log of ingestion runs (grows over time)
├─ normalized/
│  ├─ articles/        # ONE_<topic>_<slug>.md — conceptual pieces
│  ├─ reference/       # KUKA_REF_<topic>.md — syntax reference
│  ├─ examples/        # EG_<scenario>.md — worked examples
│  ├─ protocols/       # KUKA_<protocol>_*.md — fieldbus, mxAutomation, RSI, EKI
│  └─ safety/          # KUKA_SAFETY_<topic>.md — safety content (never elsewhere)
└─ raw_sources/                   # LFS-tracked PDFs — ignored by Cursor index
```

## What Goes Where

| Subdir | Goes Here | Does NOT Go Here |
|--------|-----------|------------------|
| `articles/` | "How PTP differs from LIN," "When to use SPLINE" | Full syntax tables |
| `reference/` | Full syntax tables, parameter enums, instruction reference | Conceptual discussion |
| `examples/` | Pick/place blocks, palletizing patterns, welding seams | Unexplained code dumps |
| `protocols/` | Fieldbus handshakes, mxAutomation FBs, RSI contract, EKI XML schema | Generic I/O |
| `safety/` | ISO 10218, ISO/TS 15066, SafeOp, SRM, collab analysis | General motion |

## Authoring Rules

Every file under `normalized/`:

- Starts with YAML frontmatter conforming to `cowork/schemas/dataset_entry.schema.json`.
- Has a unique `id` with the correct prefix.
- Cites `source` with tier (T1..T4) and page range (for PDFs) or URL + access_date (for web).
- Has `license: reference-only` when derived from copyrighted vendor material (default for KUKA PDFs).
- Is at most ~400 lines. If the concept is larger, split it.
- Contains no verbatim copyrighted text longer than a short quote required for precision.
- Cross-references related entries in `related:`.

The `ingest-pdf-to-normalized` skill automates most of this.

## Retrieval

Agents retrieve dataset content via the `kuka_knowledge` MCP server:

- `kuka_knowledge.search(query)` — semantic, primary.
- `kuka_knowledge.get(id)` — fetch by id.
- `kuka_knowledge.list_by_tag(tag)` — enumerate.
- `kuka_knowledge.related(id)` — follow the `related:` graph.

Human browsing: start at `DATASET_INDEX.md` for a topic-organized table.

## Raw Sources

`raw_sources/` holds the source PDFs that are LFS-tracked and `.cursorignored`. Don't cite `raw_sources/` in agent output — always cite normalized entries. When a PDF is the underlying source, the normalized entry's `source.title` + `pages` is sufficient provenance.

## Copyright

- KUKA vendor PDFs remain KUKA's property. `raw_sources/` is private to your workspace; do NOT publish.
- Normalized entries summarize in our own words with short quotes only where precision requires.
- Community / open sources ingested from the web get `source.url` and `source.access_date`.
- When in doubt about a source's tier or license, ask the Architect or user; don't guess.

## Growth

This dataset is expected to grow over time via:

1. **Ingestion** — dropping new PDFs into `raw_sources/` and running `ingest-pdf-to-normalized`.
2. **Deep research** — running `research/RESEARCH_PROMPT_KUKA_KRL.md` via Claude Research and committing findings.
3. **On-the-job capture** — when an agent discovers a gap (noted in `research/RESEARCH_TRACKING.md`), a research sprint fills it.

Each growth path ends with a QA review and a reindex.
