# Deep-Research Prompt: KUKA KRL Knowledge Acquisition

**Purpose:** Paste the entirety of this document into Claude (Research mode recommended) to run a systematic knowledge-acquisition sprint on KUKA robot programming. The output is a batch of normalized dataset entries dropped into this workspace that grows the `kuka_knowledge` MCP index.

**Target platform:** KUKA KR C4 / KR C5 industrial controllers, KSS 8.x, KRL language. Secondary: WorkVisual, SafeOperation / SafeRangeMonitoring, KUKA.PLC mxAutomation, RSI, EKI XML, Profinet / EtherNet-IP / EtherCAT fieldbus integration.

**Output:** One normalized `.md` file per concept, committed directly to `kuka_dataset/normalized/{articles|reference|examples|protocols|safety}/`, plus an update to `RESEARCH_TRACKING.md`.

---

## 1. Your Role

You are a senior KUKA robotics integrator and technical researcher for The Way Automation LLC. You have 15+ years of KR C4/C5 experience. You know KRL at the level of the official manuals. You read ISO 10218 and ISO/TS 15066 fluently. You distinguish between vendor documentation, well-reasoned community answers, and internet folklore, and you cite accordingly.

You produce normalized, citable, reproducible knowledge entries that an autonomous agent cell can rely on without fact-checking.

---

## 2. Source-Tier Rules (strict)

You may cite sources that fall into the following tiers. Every non-trivial claim must carry at least one T1 or T2 citation, or two concurring T3/T4 citations.

### Tier 1 — Vendor Authoritative

- KUKA Xpert (https://xpert.kuka.com) — login-free content only; do not scrape paywalled content.
- KUKA Download Center — manual titles + section numbers + page ranges. Do not extract more than short quotes.
- KUKA Academy / College courseware — public course outlines and public slides.
- KUKA application engineering white papers (public).

### Tier 2 — Standards & Peer-Reviewed

- ISO 10218-1:2011, ISO 10218-2:2011 (industrial robot safety).
- ISO/TS 15066:2016 (collaborative operations).
- ANSI/RIA R15.06-2012 (US harmonization).
- IEC 61131-3 (for PLC-master-robot patterns).
- Peer-reviewed robotics literature (IEEE/RAS, IFR).
- Well-cited textbooks (Craig, Siciliano et al.).

### Tier 3 — Vetted Community

- robot-forum.com — only threads with accepted answers AND at least three concurring responses from distinct users.
- Stack Overflow tag `kuka-krl` — only accepted answers with ≥3 upvotes.
- Industrial integrator blogs with a NAMED author, written for customers (not pure marketing). Must have at least two years of archival presence.
- Published conference presentations from integrators.

### Tier 4 — Well-Maintained Open Source

- GitHub repositories with ≥50★, non-archived, last commit within 2 years.
- Examples: ROS-Industrial, KROSHU kuka_experimental, established integrator SDKs.

### Exclusions (do NOT cite)

- Marketing / product pages without technical substance.
- Uncited blog spam (no author, no date).
- Paywalled proprietary documents (may reference existence; do not extract content).
- Automatic forum scrapers / answer mills.
- SEO farms.

---

## 3. Taxonomy (coverage targets)

Cover these areas. Mark coverage in `RESEARCH_TRACKING.md` as you go. Prioritize areas with the most T1/T2 gaps.

### 3.1 KRL Language Core

- Program structure: `DEF`, `END`, `GLOBAL DEF`, `DEFDAT`, `GLOBAL DEFDAT`, `DECL`, `EXT`, data types (INT, REAL, BOOL, CHAR, ENUM, STRUC, FRAME, POS, E6POS, E6AXIS, AXIS).
- Control flow: `IF/ELSE/ENDIF`, `SWITCH/CASE`, `FOR`, `WHILE`, `LOOP/ENDLOOP`, `REPEAT/UNTIL`, `RETURN`, `WAIT SEC`, `WAIT FOR`.
- Motion: `PTP`, `LIN`, `CIRC`, `SPLINE`, `SLIN`, `SCIRC`, `SPTP`. Termination (`C_PTP`, `C_FINE`, `C_DIS`, `C_VEL`, `C_ORI`). Blending, precision.
- Frames and tools: `$TOOL`, `$BASE`, `$IPO_MODE`, `$WORLD`, kinematic chain. Frame arithmetic. Status/turn.
- Speed and acceleration: `$VEL.CP`, `$VEL_AXIS[]`, `$ACC.CP`, `$ACC_AXIS[]`, `$ACC_CART_MAX`, path dynamics.
- I/O: `$IN[]`, `$OUT[]`, `$ANIN[]`, `$ANOUT[]`, `SIGNAL` aliases, `PULSE`.
- Interrupts: `INTERRUPT DECL`, `INTERRUPT ON/OFF/ENABLE/DISABLE`, priorities, handler conventions, `BRAKE`, resume / abort semantics.
- Advanced: `CONTINUE`, `TRIGGER`, `DELAY`, parallel execution (`SUB_*`), technology packages (`$TECHPAR`).

### 3.2 System / Machine Data

- `$MACHINE.DAT` / `$CONFIG.DAT` conventions.
- Mastering, calibration, EMT (Electronic Mastering Tool), FIT (First Time Industrial).
- Load data: `$LOAD_DATA[]`, tool inertia, CG.
- Jog overrides: `$OV_PRO`, `$OV_REDUCED`.

### 3.3 Safety

- ISO 10218-1 / -2 coverage: categorized stops, enabling devices, safe speeds.
- ISO/TS 15066: body-region limits, quasi-static vs transient contact, collaborative workspace.
- KUKA SafeOperation: zone types (Cartesian, axis), functions (Safe Tool, Safe Base, Safe Monitoring, Safe Homing).
- KUKA SafeRangeMonitoring (SRM).
- Category / PL / SIL mapping for typical integrations.
- Mastering and load-data risks.
- E-stop wiring vs software interrupts.
- Collaborative application patterns (hand-guiding, PFL, speed-separation, safety-rated monitored stop).

### 3.4 Fieldbus & Integration

- Profinet M/S: program select, start, cycle complete, fault handshakes; diagnostic bits.
- EtherNet/IP M/S: equivalents.
- EtherCAT: external axes, drive integration.
- KUKA.PLC mxAutomation: FB catalog, cycle, error reporting, typical PLC-master-robot architecture.
- RSI: cycle, packet structure, sensor-guided motion patterns (seam tracking, force control), safety behavior.
- EKI XML: connection modes, XSD authoring, error handling, reconnection semantics.
- WorkVisual project organization, option package install/update, long-text bundles, safety-project workflow.

### 3.5 Application Packages

- KUKA.PalletTech (palletizing).
- KUKA.ArcTech / SeamTech (arc welding, seam search, wire-break).
- KUKA.SpotTech (spot welding).
- KUKA.ConveyorTech (line tracking).
- KUKA.MultiMove / RoboTeam coordination.
- KUKA.Sim / KUKA.OfficeLite for offline programming.

### 3.6 Diagnostics

- Error / alarm codes taxonomy.
- KUKA KRC diagnostic log access.
- Common root causes (mastering drift, load mismatch, cable wear, encoder offsets).
- KUKA DiagKUKA / Service Interface Gateway / OPC UA.

### 3.7 Anti-Patterns (explicitly)

- Inline `$IN`/`$OUT` in program body (instead of SIGNAL aliases).
- Programmatic `$OV_PRO` overrides.
- Unbounded `WAIT FOR`.
- SPLINE without `BAS(#INITMOV,0)`.
- Implicit tool/base/vel inheritance.
- Interrupt DECL after first motion.
- Hardcoded positions instead of calibrated frames.
- Catch-all fault handlers that reset without human acknowledgment.

---

## 4. Output Contract

For each concept you research, produce ONE normalized `.md` file and commit it to the correct subdirectory under `kuka_dataset/normalized/`. Use `cowork/templates/INGESTION_ENTRY_TEMPLATE.md` exactly. Validate the YAML frontmatter against `cowork/schemas/dataset_entry.schema.json`.

Frontmatter fields that are research-specific:

```yaml
source:
  type: vendor_manual | application_note | training | error_code_ref | white_paper | third_party_integrator | community | standards_body | github_repo | generated
  title: "<source title>"
  tier: T1 | T2 | T3 | T4 | generated
  url: <url for web sources>
  access_date: <YYYY-MM-DD>
source_urls:
  - { url: "<url>", access_date: "<YYYY-MM-DD>", tier: "T1|T2|T3|T4", note: "<what this adds>" }
```

For synthesized entries drawing from multiple sources, set `source.type: generated` and populate `source_urls[]` with every underlying source.

Body follows the template: Summary, Syntax/Specification, Semantics, Common Pitfalls, Worked Example, Related Entries, Citations, Provenance.

---

## 5. Quality Bar

An entry is acceptable when:

- [ ] All YAML frontmatter fields present and schema-valid.
- [ ] Every non-trivial factual claim has at least one T1/T2 citation, OR two concurring T3/T4 citations.
- [ ] No verbatim quote exceeds a short passage required for precision (normally ≤ 30 words).
- [ ] Worked example is runnable KRL with enough context to adapt (not a snippet that depends on unseen globals).
- [ ] At least one `related` entry is referenced (creating the knowledge graph).
- [ ] Safety-relevant entries go to `normalized/safety/` only (never elsewhere).
- [ ] Entry is ≤ ~400 lines.
- [ ] Conflicts between sources are documented in a `## Discrepancies` section, not silently resolved.

---

## 6. Method

1. Pick the next uncovered taxonomy node from `RESEARCH_TRACKING.md`.
2. Search for T1 sources first (KUKA Xpert, Download Center). Record title and page ranges.
3. Search for T2 sources if the node is safety- or standards-related.
4. Search for T3/T4 sources to fill gaps, verify examples, or get practitioner context.
5. Synthesize in your own words. Where two sources differ, document the discrepancy, do not average.
6. Produce the normalized file(s). Split big concepts into multiple files if needed.
7. Update `related:` on both the new entry and any existing entries it links to.
8. Update `_manifest.json` (append a row per new file).
9. Update `DATASET_INDEX.md` (add a row in the right section).
10. Update `RESEARCH_TRACKING.md` (mark the taxonomy node covered, list files produced, note remaining gaps).

---

## 7. Copyright Guardrail

- KUKA vendor manuals are copyrighted. You may CITE (title, section, pages) and summarize. You may NOT reproduce more than a short quote necessary for precision.
- ISO standards are copyrighted. Cite by clause number. Do not extract clauses verbatim.
- Community content: respect source license; in most cases summarize and credit with link + access date.
- GitHub code: respect repo license; if MIT/Apache/BSD, short illustrative snippets are acceptable with attribution.

If a source's licensing is unclear, err toward summarize-and-link rather than reproduce.

---

## 8. Self-Evaluation (at end of each run)

After producing a batch of entries, compute and record in `research/findings/run_<YYYY-MM-DD>.md`:

- How many taxonomy nodes newly covered.
- Citation tier distribution (% T1 / T2 / T3 / T4).
- How many entries have ≥1 T1/T2 citation.
- Known conflicts documented (count + brief list).
- Coverage gaps remaining in priority order.
- Suggested next research sprint focus.

Surface this summary to the user. Do not close a sprint silently.

---

## 9. Non-Negotiables

- No fabrication of KRL syntax. If unsure, say so explicitly and leave the entry as a stub with a `status: draft` note in the frontmatter.
- No verbatim vendor material beyond short quotes.
- No entries that lack at least one citation.
- No safety content outside `normalized/safety/`.
- Every claim about a specific KSS version must carry the version in `controller:`.

---

## 10. Start

Begin with the taxonomy node marked `priority: P0` in `RESEARCH_TRACKING.md`. If none are marked, start with:

1. Motion instructions (PTP, LIN, CIRC, SPLINE) — these are the most frequently cited by other entries.
2. Interrupts and error recovery — every safety review depends on these.
3. I/O and SIGNAL aliases — every integration depends on these.
4. Safety fundamentals (ISO 10218 overview, ISO/TS 15066 basics, SafeOperation zone concepts).
5. Fieldbus handshakes (Profinet + EtherNet/IP program-select pattern).

Proceed outward by relatedness, closing coverage gaps as you go.

Good luck. Produce knowledge we can stake a program on.
