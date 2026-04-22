# KUKA Research Coverage Tracker

Companion to [`RESEARCH_PROMPT_KUKA_KRL.md`](./RESEARCH_PROMPT_KUKA_KRL.md). Every research sprint updates this file.

## Legend

- `status`: `empty` → no entries yet. `draft` → entries exist but not QA-passed. `covered` → at least one QA-passed entry with a T1 or T2 citation. `rich` → ≥3 entries with cross-citations.
- `priority`: `P0` urgent (blocks other work), `P1` high, `P2` normal, `P3` nice-to-have.

## Sprint Log

| Date | Agent/Researcher | Entries Added | Net Coverage Delta | Notes |
|------|------------------|---------------|--------------------|-------|
| 2026-04-21 | setup | _pending_ | _n/a_ | Copied to standalone folder; `git`+LFS initialized; no PDFs in `raw_sources/`. **Next:** run a deep-research sprint using the full text of [`RESEARCH_PROMPT_KUKA_KRL.md`](./RESEARCH_PROMPT_KUKA_KRL.md) in Claude (Research mode) **or** ingest PDFs first — both paths grow the normalized dataset. |
| _template_ | _n/a_ | _n/a_ | _n/a_ | Initial scaffold; no entries yet. |

## Taxonomy Coverage

### 3.1 KRL Language Core

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| Program structure (DEF/END/DEFDAT) | P0 | empty |  | Need T1 for scoping rules. |
| Data types (INT, REAL, BOOL, STRUC, FRAME, POS, E6POS, E6AXIS) | P0 | empty |  |  |
| Control flow (IF/SWITCH/FOR/WHILE/LOOP/REPEAT) | P1 | empty |  |  |
| Motion: PTP | P0 | draft | EG_PTP_Hello | Needs KUKA_REF_PTP_Motion with T1 page citation. |
| Motion: LIN | P0 | empty |  |  |
| Motion: CIRC | P1 | empty |  |  |
| Motion: SPLINE / SLIN / SCIRC / SPTP | P1 | empty |  | Cover BAS init requirement. |
| Motion termination (C_PTP/C_FINE/C_DIS/C_VEL/C_ORI) | P1 | empty |  |  |
| Frames and tools ($TOOL/$BASE/$IPO_MODE/$WORLD) | P0 | empty |  |  |
| Speed/accel ($VEL.CP, $VEL_AXIS[], $ACC.CP) | P1 | empty |  |  |
| I/O ($IN/$OUT/$ANIN/$ANOUT/SIGNAL) | P0 | empty |  |  |
| Interrupts (INTERRUPT DECL/ON/OFF, BRAKE) | P0 | empty |  |  |
| Advanced (TRIGGER, CONTINUE, DELAY, SUB_*) | P2 | empty |  |  |

### 3.2 System / Machine Data

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| $MACHINE.DAT / $CONFIG.DAT conventions | P1 | empty |  |  |
| Mastering / EMT / FIT | P1 | empty |  |  |
| Load data ($LOAD_DATA[]) | P1 | empty |  |  |
| Jog overrides ($OV_PRO, $OV_REDUCED) | P2 | empty |  |  |

### 3.3 Safety

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| ISO 10218-1/-2 overview | P0 | empty |  |  |
| ISO/TS 15066 body-region limits | P0 | empty |  |  |
| SafeOperation zones (Cartesian + axis) | P0 | empty |  |  |
| SafeRangeMonitoring (SRM) | P1 | empty |  |  |
| Cat/PL/SIL mapping | P1 | empty |  |  |
| E-stop wiring vs software interrupts | P0 | empty |  |  |
| Collaborative patterns (PFL, SSM, hand-guide, SRMS) | P1 | empty |  |  |

### 3.4 Fieldbus & Integration

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| Profinet program-select / start / fault handshake | P0 | empty |  |  |
| EtherNet/IP equivalents | P1 | empty |  |  |
| EtherCAT drive integration | P2 | empty |  |  |
| mxAutomation FB catalog | P1 | empty |  |  |
| RSI cycle / packet / sensor-guided | P1 | empty |  |  |
| EKI XML authoring + reconnection | P1 | empty |  |  |
| WorkVisual project organization | P1 | empty |  |  |

### 3.5 Application Packages

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| KUKA.PalletTech | P2 | empty |  |  |
| KUKA.ArcTech / SeamTech | P2 | empty |  |  |
| KUKA.SpotTech | P3 | empty |  |  |
| KUKA.ConveyorTech | P2 | empty |  |  |
| MultiMove / RoboTeam | P3 | empty |  |  |
| KUKA.Sim / OfficeLite | P3 | empty |  |  |

### 3.6 Diagnostics

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| Error/alarm code taxonomy | P1 | empty |  |  |
| KRC diagnostic log access | P2 | empty |  |  |
| Common root causes | P1 | empty |  |  |
| OPC UA / Service Interface Gateway | P2 | empty |  |  |

### 3.7 Anti-Patterns

| Node | Priority | Status | Entry IDs | Gaps |
|------|----------|--------|-----------|------|
| Inline $IN/$OUT vs SIGNAL | P1 | empty |  |  |
| Programmatic $OV_PRO | P1 | empty |  |  |
| Unbounded WAIT FOR | P0 | empty |  |  |
| SPLINE without BAS init | P1 | empty |  |  |
| Implicit tool/base/vel inheritance | P1 | empty |  |  |
| Late INTERRUPT DECL | P1 | empty |  |  |
| Hardcoded positions | P2 | empty |  |  |
| Catch-all fault handlers | P1 | empty |  |  |

## Source Tier Distribution

Updated per sprint.

| Tier | Count | % of Citations |
|------|-------|----------------|
| T1   | 0     | 0%             |
| T2   | 0     | 0%             |
| T3   | 0     | 0%             |
| T4   | 0     | 0%             |

## Open Questions / Conflicts

Track here any source conflicts, ambiguities, or TODOs for later sprints.

- _none yet_

## Next-Sprint Focus

Derived from gaps above. Populated at the end of each sprint's self-evaluation.

- Start: motion taxonomy (PTP/LIN/CIRC/SPLINE) with T1 KUKA manual page citations.
- Then: interrupts + BRAKE + error recovery.
- Then: I/O + SIGNAL aliases.
- Then: safety fundamentals (ISO 10218 / ISO/TS 15066 / SafeOperation).
- Then: fieldbus program-select handshakes (Profinet, EtherNet/IP).
