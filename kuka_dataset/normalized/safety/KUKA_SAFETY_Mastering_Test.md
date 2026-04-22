---
id: KUKA_SAFETY_Mastering_Test
title: Mastering Test Procedure
topic: mastering
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.SafeOperation 3.6 Operating and Programming Instructions"
  tier: T1
  pages: [131, 147]
  section: "7.7 Mastering test"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_SafeOp_Overview, KUKA_SAFETY_Brake_Test, EG_Tool_Base_Calibration_Flow]
difficulty: advanced
tags: [safety, safeoperation, mastering, srm, reference-switch, encoder, periodic-test]
---

# Mastering Test Procedure

## Summary

The mastering test verifies that the robot's axis-encoder values are still consistent with an external reference — a safety-rated check that the robot "knows where it is." It is required for SafeOperation certification: if the safety CPU is computing safe zones and safe velocities, those calculations depend on trustworthy encoder data. The test is part of the commissioning acceptance and must be repeated periodically (interval set by the safety acceptance; commonly every 12 months) and after any event that could shift the encoder reference.

## Why Mastering Can Drift

Mastering is the zero-reference for each axis. It can drift or become invalid through:

- Encoder battery depletion on axes without absolute encoders (older designs).
- Physical impact that slips the cart encoder or shifts a resolver.
- Service that breaks the encoder chain (motor replacement, resolver replacement).
- Cart-axis collision on a rail.
- Firmware update that clears the stored master position (rare but happens).

SafeOperation assumes mastering is valid; if the test fails, the controller must not compute safe monitoring until mastering is re-established and re-tested.

## Test Procedure Outline

The detailed procedure is in the SafeOperation manual (Chapter 7.7); summarized here for reference:

1. **Ensure cell is safe** — cell closed, operator outside, keys controlled.
2. **Operating mode T1**. Enabling switch ready.
3. **Select Mastering Test** on the pendant (safety menu).
4. **Move each axis to its reference switch position.** The reference switch is a safety-rated limit-switch-like device installed per axis during commissioning (a cam engages the switch at a known angular position).
5. **For each axis**, the controller records the encoder reading at switch actuation and compares against the stored reference. Difference must be within tolerance (typically < 0.1°).
6. **If in tolerance** — axis passes. Repeat for remaining axes.
7. **If out of tolerance** — re-master that axis (EMT or dial-gauge method), then re-run the test.
8. **Record results** in the cell's mastering-test log with operator signature, date, and axis-by-axis reading.

## Required Equipment

- Safety-rated reference switches installed per axis (part of the initial SafeOperation commissioning).
- EMT (Electronic Mastering Tool) or dial gauge for re-mastering if needed.
- Cell's mastering test log (paper or electronic).

## Acceptance Criteria

Per-axis tolerance and frequency are set in the cell's safety acceptance document. Typical values:

| Parameter | Typical value |
|-----------|---------------|
| Tolerance | 0.1° per axis |
| Frequency | Annual (or per local regulation) |
| After service | Always |
| After collision | Always |
| After firmware update | Always |

## Common Pitfalls

- **Skipping the test after a near-miss collision.** If the robot hit anything, re-master and re-test. Close calls still count.
- **Using the wrong reference position.** The reference switch must engage at the stored reference angle, not whatever angle the cam happens to be at.
- **Signing off without the log entry.** No signed record = no certification. If audited, missing logs are a compliance finding.
- **Re-mastering without re-running the test.** Re-master moves the reference; re-test confirms the new reference is stable.
- **Ignoring an axis that "passed but was close."** If an axis is at 80% of tolerance, investigate — it's on its way to failing.
- **Treating cart (external) axes as optional.** If the cart has a safety-rated encoder chain (required for SafeOperation on rails), it must be tested too.

## Related Entries

- `KUKA_SAFETY_SafeOp_Overview` — why mastering matters for zone monitoring.
- `KUKA_SAFETY_Brake_Test` — companion periodic test.
- `EG_Tool_Base_Calibration_Flow` — tool/base calibration assumes valid mastering as prerequisite.

## Citations

- KUKA.SafeOperation 3.6 Operating and Programming Instructions (T1). Chapter 7.7 "Mastering test" (pp. 131–147).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_SafeOperation_36_en.pdf`. Summary only — exact procedure is safety-critical and must be followed from the manual, not from this entry.
