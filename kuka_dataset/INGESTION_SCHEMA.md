# Ingestion Schema

Authoritative rules for turning raw KUKA material (PDFs, web pages, slides) into normalized dataset entries.

This document is the prose companion to `cowork/schemas/dataset_entry.schema.json`. Read both.

---

## 1. File Anatomy

Every normalized entry is a single Markdown file with:

1. **YAML frontmatter** (`---` ... `---`) conforming to `dataset_entry.schema.json`.
2. **Markdown body** following the section order in the template.

Path: `kuka_dataset/normalized/<category>/<id>.md` where `<category>` is one of: `articles`, `reference`, `examples`, `protocols`, `safety`.

Use `cowork/templates/INGESTION_ENTRY_TEMPLATE.md` as the starting point.

---

## 2. ID Rules

Stable, human-readable ids. Prefix encodes the category:

| Prefix | Category | Example |
|--------|----------|---------|
| `KUKA_REF_` | reference/ | `KUKA_REF_PTP_Motion` |
| `ONE_` | articles/ | `ONE_motion_termination` |
| `EG_` | examples/ | `EG_PTP_Hello` |
| `KUKA_SAFETY_` | safety/ | `KUKA_SAFETY_ISO_10218_Overview` |
| `KUKA_<proto>_` | protocols/ | `KUKA_Profinet_Handshake` |

Lowercase `ONE_` / `EG_` prefixes intentionally; uppercase `KUKA_` signals "authoritative class." These are conventions; the schema `pattern` enforces the basic shape.

Ids are immutable once referenced. If content changes materially, create a new id with an incremented version in the name (e.g., `KUKA_REF_PTP_Motion_v2`) and set `superseded_by` on the old.

---

## 3. Chunking Rules

One concept per file. Good chunking is the highest-leverage decision in ingestion.

| Rule | Why |
|------|-----|
| ≤ ~400 lines per file | Fits in a single retrieval hit; agent can cite precisely. |
| One KRL instruction per `reference/` entry | Clean lookup by syntax. |
| One pattern per `examples/` entry | Reusable without trimming. |
| One concept per `articles/` entry | Clean semantic search. |
| One protocol topic per `protocols/` entry | (e.g., "Profinet program-select handshake," not "all Profinet") |
| Safety content only in `safety/` | Every agent knows where to look. |

If a PDF chapter covers multiple concepts, produce multiple normalized entries from it.

---

## 4. Frontmatter Field Guide

All required fields must be populated. See `dataset_entry.schema.json` for exact enums.

### `source`

```yaml
source:
  type: vendor_manual
  title: "KUKA System Software 8.x Operating and Programming Instructions"
  tier: T1
  pages: [412, 418]
  section: "5.4 Motion Instructions"
  access_date: 2026-04-21
  url: null
```

- For PDF content: `type`, `title`, `tier`, `pages` are required. `url` null.
- For web content: `type`, `title`, `tier`, `url`, `access_date` required. `pages` null.
- For generated content (from research synthesizing multiple sources): additional `source_urls:` array.

### `tier`

- **T1** — KUKA Xpert, KUKA Download Center, KUKA Academy.
- **T2** — ISO standards, peer-reviewed robotics literature, vetted textbooks.
- **T3** — Robot-Forum 3+-accepted-answer threads, named-author integrator blogs, reputable community.
- **T4** — GitHub repos ≥50★ non-archived, recent.
- **generated** — synthesized in the agent pipeline (still cites underlying T1..T4 via `source_urls`).

### `license`

- `reference-only` — derived from KUKA or other vendor copyrighted material. Summarize only; short quotes only; no full-page reproduction.
- `open` — derivative of open/public-domain source.
- Any SPDX identifier for fully open-licensed material.

### `related`

List of other dataset ids that help an agent follow the topic graph. Both sides should reference each other; the ingestion skill enforces bidirectionality.

---

## 5. Body Structure

The body mirrors `cowork/templates/INGESTION_ENTRY_TEMPLATE.md`:

1. **Summary** — 2–4 sentences. First paragraph is what the agent reads when previewing a search result.
2. **Syntax / Specification** — precise; include a minimal canonical snippet.
3. **Semantics / Behavior** — preconditions, postconditions, side effects, parameter semantics.
4. **Common Pitfalls** — bullet list of mistakes.
5. **Worked Example** — minimal-but-complete example with enough context to copy-paste with only renames.
6. **Related Entries** — cross-references with a one-line "why."
7. **Citations** — source + tier + pages / url.
8. **Provenance** — ingestion agent / date / raw source path (for local provenance only — do NOT leak file system paths in generated outputs).

---

## 6. Copyright / Fair-Use Guardrails

Normalized entries must:

- Summarize in our own words. Think "explain to a colleague," not "paste the manual."
- Quote verbatim only when precision requires (specific keyword, exact grammar clause, exact numerical limit). Keep quotes short.
- Always cite (title + page) so a reader can verify.
- Never embed full tables of proprietary values (payload envelopes, safety limits) — describe and reference.

If a PDF contains figures critical to understanding, describe the figure in words; do NOT embed scanned images.

When in doubt, err toward shorter quotes and more citation.

---

## 7. Quality Bar

An entry is ready to commit when it:

- [ ] Passes `dataset_entry.schema.json` validation.
- [ ] Has a `source` block with the correct tier.
- [ ] Is ≤ ~400 lines.
- [ ] Has a summary that answers "what is this?" in one read.
- [ ] Has at least one worked example OR one canonical snippet.
- [ ] Cites every non-trivial claim.
- [ ] Lists at least one `related` entry (unless genuinely standalone — a single-entry island indicates missed connections).
- [ ] Reviewed by the QA agent post-ingestion.

---

## 8. Revision and Supersession

When KSS / controller / manual version changes the behavior:

- Create a new id with version suffix.
- Set the old entry's `superseded_by` to the new id.
- Do NOT delete the old entry — someone may still work on the old KSS.
- Update `DATASET_INDEX.md` with both rows and a note.

---

## 9. The `_manifest.json` Catalog

Machine-readable catalog. Every ingested entry adds a line. Structure:

```json
{
  "version": 1,
  "entries": [
    {
      "id": "KUKA_REF_PTP_Motion",
      "path": "reference/KUKA_REF_PTP_Motion.md",
      "topic": "motion",
      "tier": "T1",
      "kuka_platform": ["KR C4", "KR C5"],
      "kss_version": ["KSS 8.3", "KSS 8.6"],
      "revision_date": "2026-04-21",
      "tags": ["motion", "ptp", "asynchronous"]
    }
  ]
}
```

Schema: `_manifest.schema.json`.

The `kuka_knowledge` MCP server reads this manifest to build its search index.

---

## 10. When to Consult This Document

- Whenever you produce a normalized entry (human or agent).
- Whenever you add a new category (rare; requires schema update too).
- Whenever you review ingestion output (QA agent).
- Whenever the deep-research prompt gets a finding to commit.
