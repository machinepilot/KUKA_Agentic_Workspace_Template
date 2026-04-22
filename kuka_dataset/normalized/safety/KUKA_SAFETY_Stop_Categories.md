---
id: KUKA_SAFETY_Stop_Categories
title: "Stop Categories & Triggers (KSS and VSS)"
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [33, 34]
  section: "3.4–3.5 Stop categories and triggers"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_Operating_Modes, KUKA_SAFETY_SafeOp_Overview, EG_Interrupt_Safety_Shutdown]
difficulty: intermediate
tags: [safety, stop-categories, stop0, stop1, stop2, iso-10218, en-60204]
---

# Stop Categories & Triggers (KSS and VSS)

## Summary

KUKA implements three stop categories aligned with EN 60204-1 / EN ISO 13850: Stop 0 (immediate power removal), Stop 1 (controlled stop followed by power removal), Stop 2 (controlled stop, drives remain energized). These apply across the Kuka Safety System (KSS, robot safety) and, where configured, the Visual Safety System (VSS, additional monitoring). Integrators need to know which trigger produces which stop to design handlers and recovery correctly.

## The Three Categories

### Stop 0

- **Action:** Drives de-energized immediately; mechanical brakes engage.
- **TCP behavior:** Leaves programmed path; deceleration is whatever the mechanical brakes provide.
- **When used:** Severe safety violations — safety-rated E-stop hardware latch, encoder implausibility, safety bus failure.
- **Equivalent:** KRL `BRAKE F`, but invoked by the safety system, not the program.

### Stop 1

- **Action:** Controlled deceleration along the planned path; drives de-energized at rest.
- **TCP behavior:** Stays on programmed trajectory during deceleration.
- **When used:** Operator E-stop button, light curtain break, safeguard open.
- **Equivalent:** KRL `BRAKE` followed by program halt.

### Stop 2

- **Action:** Controlled deceleration along the planned path; drives remain energized at rest.
- **TCP behavior:** Stays on programmed trajectory; can resume immediately on acknowledgment.
- **When used:** Program-pause, operator-requested hold, Safe-Stop 2 (SS2) monitored via SafeOperation, reduced-speed override transitions.
- **Equivalent:** KRL program pause.

## Triggers

Representative triggers by category; confirm against the cell's safety acceptance document:

| Trigger | Typical category |
|---------|------------------|
| Safety-rated E-stop button (latched) | Stop 1 (Cat 1) — operator-actuated safeguards |
| Drive fault / encoder fault | Stop 0 |
| Safety bus loss | Stop 0 |
| Light curtain break | Stop 1 |
| Safeguard door open (in AUT) | Stop 1 |
| SafeOperation zone violation | Depends on zone config — typically Stop 1 |
| Program pause (operator) | Stop 2 |
| Deadman released (T1) | Stop 2 or Stop 1 depending on config |
| Mastering lost | Stop 0 (no trusted position) |

## Recovery by Category

- **Stop 0 recovery:** Clear the fault, reset the drive, re-enable, re-home. Often requires mastering verification because the TCP is off-path.
- **Stop 1 recovery:** Clear the fault, acknowledge, resume. TCP is on-path so restart is clean.
- **Stop 2 recovery:** Acknowledge; drives still energized, robot can continue.

## Common Pitfalls

- **Assuming any BRAKE is Cat-1.** `BRAKE F` (software) is an immediate mechanical brake — functionally Cat 0 but not safety-rated. The safety system must still evaluate the safety signal independently.
- **Latching E-stops as Cat 0.** Local codes may require Cat 1 (controlled stop) for operator-actuated safeguards; don't configure them as Cat 0 without a hazard analysis.
- **Skipping re-home after Stop 0.** The TCP is off path; continuing assumes it isn't.
- **Treating program pause (Stop 2) as a safety function.** It isn't — it's program control. Safety stops must come from safety-rated signals.

## Related Entries

- `KUKA_SAFETY_Operating_Modes` — mode-dependent stop behavior (T1 / T2 / AUT / AUT EXT).
- `KUKA_SAFETY_SafeOp_Overview` — SafeOperation zone violations and their stop categories.
- `EG_Interrupt_Safety_Shutdown` — KRL-level pattern complementing safety-rated stops.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 3.4–3.5 "Stop categories and triggers" (pp. 33–34).
- EN 60204-1:2018 and EN ISO 13850:2015 — the underlying category definitions.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
