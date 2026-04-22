---
id: KUKA_SAFETY_Brake_Test
title: Brake Test Procedure
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.SafeOperation 3.6 Operating and Programming Instructions"
  tier: T1
  pages: [148, 166]
  section: "7.8 Brake test"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_SafeOp_Overview, KUKA_SAFETY_Mastering_Test, KUKA_SAFETY_Stop_Categories]
difficulty: advanced
tags: [safety, safeoperation, brake-test, periodic-test, holding-brakes, pl-d]
---

# Brake Test Procedure

## Summary

The brake test verifies that each axis's mechanical holding brake is still strong enough to stop and hold the axis under its worst-case load. SafeOperation relies on holding brakes to implement Stop 0 — if a brake has worn or lost torque, Stop 0 becomes ineffective and the safety argument collapses. The test is part of the SafeOperation acceptance and must be repeated periodically, typically every 12 months and always after any service that could affect a brake.

## Why Brakes Need Periodic Testing

Axis holding brakes are consumable:

- Friction material wears with every brake engagement.
- Brake dust accumulates and reduces friction.
- Environmental contamination (oil mist, grit) degrades performance.
- Spring-applied brakes can lose spring tension over long service.

A brake that holds 100% of rated torque when new may hold only 70% after years of service. The test catches this before a safety event relies on it.

## Test Procedure Outline

Detailed procedure in the SafeOperation manual (Chapter 7.8); summary:

1. **Ensure cell is safe.** T1 mode, cell closed, operator has keys.
2. **Select Brake Test** on the pendant (safety menu). The controller will drive each axis against its engaged brake to measure holding torque.
3. **Per axis**:
   - The controller drives the axis with its brake engaged, applying a defined torque.
   - Measures whether the axis moves (brake insufficient) or holds (brake OK).
   - Repeats from multiple positions if the cell's safety acceptance requires it (loaded vs. unloaded).
4. **Evaluate results.** Each axis's holding torque must exceed the per-axis acceptance threshold set at commissioning.
5. **Record results** — date, per-axis torque values, operator signature, test status (pass/fail).

A failed axis requires brake service (replacement or adjustment) before the cell may return to production.

## Related Variables and Safety Implications

- **Without a valid brake test, SafeOperation must not certify Stop 0 functionality.** Zones that depend on Stop 0 become unsafe.
- **Some KRL behaviors interact with brake state:**
  - `$BRAKE_TEST_OK` (or equivalent) indicates current test validity.
  - `BRAKE` (controlled stop) uses drive deceleration, not brakes primarily.
  - `BRAKE F` (fast stop) does engage brakes immediately — its effectiveness depends directly on brake health.

## Test Frequency

Per-cell safety acceptance; typical values:

| Trigger | Required |
|---------|----------|
| Commissioning | Always |
| Annual re-acceptance | Always |
| After brake service | Always |
| After E-stop-triggered Stop 0 | Recommended (brake just slammed) |
| After extended idle (>3 months) | Recommended |
| After collision | Always |

## Required Equipment

- Pendant with SafeOperation installed.
- Test log — brake-test results must be signed and retained for regulatory compliance (typically 5 years).
- Payload matching the production configuration (test under worst-case load).

## Common Pitfalls

- **Testing without production load.** Brakes hold an empty tool easily; the test must reflect real worst-case.
- **Skipping after Stop 0.** An E-stop-triggered Stop 0 engages brakes at speed — the most stressful operation. Re-test.
- **Running test in AUT.** Test is T1-only; running it otherwise could inject motion with a weak brake.
- **Signing off without capturing per-axis numbers.** "Passed" alone is insufficient; specific torque values matter when diagnosing drift.
- **Deferring a failed axis.** A borderline brake is a live risk; replace before returning to production.
- **Assuming drive deceleration substitutes for brakes.** It doesn't — Stop 0 removes drive power; at that moment, only brakes hold the axis.

## Related Entries

- `KUKA_SAFETY_SafeOp_Overview` — why brake test matters for the safety argument.
- `KUKA_SAFETY_Mastering_Test` — companion periodic test (same commissioning/acceptance flow).
- `KUKA_SAFETY_Stop_Categories` — Stop 0 depends on brakes.

## Citations

- KUKA.SafeOperation 3.6 Operating and Programming Instructions (T1). Chapter 7.8 "Brake test" (pp. 148–166).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_SafeOperation_36_en.pdf`. Summary only — procedure is safety-critical; follow the manual, not this entry.
