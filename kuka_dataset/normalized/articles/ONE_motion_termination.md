---
id: ONE_motion_termination
title: "Motion Termination Types: C_PTP, C_DIS, C_VEL, C_ORI, C_FINE"
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [417, 420]
  section: "9.6 Motion termination / approximate positioning"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_SPLINE_Block, KUKA_REF_Velocity_Acceleration, ONE_motion_blending]
difficulty: intermediate
tags: [motion, termination, blending, c_ptp, c_dis, c_ori, c_vel, c_fine]
---

# Motion Termination Types: C_PTP, C_DIS, C_VEL, C_ORI, C_FINE

## Summary

Every KRL motion ends in one of two ways: **fine positioning** (the robot reaches the programmed target exactly and stops) or **approximate positioning** (the motion blends into the next without stopping). The termination clause on the motion instruction chooses which, and for approximate motions, which criterion defines the blending zone. Choosing the right termination is one of the highest-leverage cycle-time optimizations in a KUKA program.

## Key Concepts

### Fine positioning (default)

A motion without a termination clause ends with all axes at rest at the exact programmed target. This is sometimes written `C_FINE` for clarity.

```krl
LIN P1                  ; fine positioning implicit
LIN P1 C_FINE           ; same thing, explicit
```

Fine positioning is required when the next action depends on being physically at the target — pick/place, gripper close, probe touch.

### Approximate positioning

A motion with an approximation clause starts decelerating before the programmed target so that the transition into the next motion is smooth. The target is never physically reached; the TCP passes through a blending region. The criterion chooses what "approximate" means.

| Clause | Applies to | Criterion |
|--------|------------|-----------|
| `C_PTP` | PTP | Axis-space: blending begins when axes are within `$APO.CPTP` % of the remaining path. |
| `C_DIS` | CP (LIN, CIRC) | Cartesian distance: blending begins within `$APO.CDIS` mm of the target. |
| `C_ORI` | CP | Orientation angle: blending begins within `$APO.CORI` ° of the target orientation. |
| `C_VEL` | CP | Velocity: blending begins when path velocity has dropped to `$APO.CVEL` % of programmed. |

For CP motions the controller picks the most-restrictive criterion that is active — if both `C_DIS` and `C_ORI` are set, whichever triggers first starts the blend.

### Spline blocks

Inside a `SPLINE` block, blending is automatic and you do not add `C_*` clauses. Blending between spline segments is geometric and continuous in velocity.

## Decision Guide

- **Need to reach this exact point?** Fine positioning. Examples: pick, place, process-start, clearance point.
- **Intermediate approach / retract / transit?** Approximate. Pick the criterion the path requires:
  - Linear motion through a free region → `C_DIS`.
  - Orientation must be within a tolerance but position can vary → `C_ORI`.
  - Constant-velocity streaming (dispensing, gluing) → `C_VEL`.
  - Axis-level blend (PTP transit) → `C_PTP`.

## Common Pitfalls

- **Chained fine positionings** — a long sequence of `LIN` without termination stops the robot at every point, inflating cycle time. Audit teach-pendant-generated code for this.
- **`C_DIS` with `$APO.CDIS = 0`** — effectively fine positioning; the blending zone has zero radius.
- **`C_PTP` on a safety-critical clearance point** — the programmed clearance is approximate; the actual trajectory cuts inside. Verify the blended path clears fixtures.
- **Mixing approximate transitions with heavy blending distances** — two consecutive blends can overlap, yielding an unexpectedly direct path. Use spline blocks for multi-segment curves.
- **Process signals timed to fine position** — `TRIGGER WHEN DISTANCE ...` is usually better than waiting for `$POS_ACT` equality after a blended motion.

## Worked Example

Pallet pattern: fine at pick/place, approximate at approach/retract/transit:

```krl
LIN P_approach_pick   C_DIS        ; approach is approximate
LIN P_pick                          ; pick is exact (grip here)

LIN P_retract_pick    C_DIS
PTP P_transit         C_PTP
LIN P_approach_place  C_DIS
LIN P_place                         ; place is exact (release here)

LIN P_retract_place   C_DIS
PTP P_home            C_PTP
```

## Related Entries

- `KUKA_REF_PTP_Motion`, `KUKA_REF_LIN_Motion`, `KUKA_REF_CIRC_Motion` — motion instructions that accept termination clauses.
- `KUKA_REF_SPLINE_Block` — spline blocks have automatic blending.
- `KUKA_REF_Velocity_Acceleration` — `$APO.*` variables.
- `ONE_motion_blending` — deeper treatment of blending geometry and timing.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.6 "Motion termination / approximate positioning" (pp. 417–420).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
