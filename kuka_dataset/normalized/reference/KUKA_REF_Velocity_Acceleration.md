---
id: KUKA_REF_Velocity_Acceleration
title: Velocity and Acceleration System Variables ($VEL, $ACC, $VEL_AXIS, $VEL.CP)
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [551, 600]
  section: "Chapter 9 motion preparation; Chapter 11 motion programming; Chapter 11.11 system variables"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_SPLINE_Block, ONE_motion_termination]
difficulty: intermediate
tags: [motion, velocity, acceleration, system-variables, override]
---

# Velocity and Acceleration System Variables

## Summary

KUKA separates motion speeds by motion type. PTP uses per-axis percentages (`$VEL_AXIS[i]`, `$ACC_AXIS[i]`). CP motions (LIN, CIRC, spline) use Cartesian path velocity and orientation angular velocity (`$VEL.CP`, `$VEL.ORI1`, `$VEL.ORI2` and the matching `$ACC`). Program speed is further scaled at runtime by the program override `$OV_PRO` and the user-facing override `$OV_RED`. Pick the right variable for the motion type and do not attempt to substitute one for another.

## Syntax / Specification

Axis-space (PTP):

```krl
$VEL_AXIS[1] = 50       ; percent of max velocity for axis 1 (0..100)
$ACC_AXIS[1] = 50       ; percent of max acceleration
```

Cartesian path (LIN, CIRC, spline):

```krl
$VEL.CP    = 0.5        ; m/s  — path velocity for the TCP
$VEL.ORI1  = 100        ; deg/s — swivel angle velocity
$VEL.ORI2  = 100        ; deg/s — rotation angle velocity
$ACC.CP    = 2.0        ; m/s²
$ACC.ORI1  = 100        ; deg/s²
$ACC.ORI2  = 100
```

Blending-related:

```krl
$APO.CDIS  = 50         ; mm  — default distance for C_DIS
$APO.CORI  = 50         ; deg — default for C_ORI
$APO.CVEL  = 100        ; %   — default for C_VEL
$APO.CPTP  = 100        ; %   — approximate-PTP blending size
```

Runtime overrides:

```krl
$OV_PRO    = 100        ; %   — program override (never set in customer program code)
$OV_RED    = 100        ; %   — reduced-speed override for T1 / safety-reduced modes
```

## Semantics / Behavior

- **PTP is axis-percentage.** `$VEL_AXIS[i]` is a percentage (0..100) of the manufacturer-defined maximum axis velocity. `$ACC_AXIS[i]` is a percentage of maximum acceleration.
- **CP is absolute units.** `$VEL.CP` is in m/s, angular velocities in deg/s. Valid ranges are finite — setting `$VEL.CP = 10` on a small robot will be clipped silently.
- **Per-segment override (`WITH`).** Spline segments accept `WITH $VEL.CP = 0.2` etc., overriding block-level values for just that segment.
- **Blending defaults.** If a motion uses `C_DIS` but `$APO.CDIS` is 0, the blend radius effectively collapses to fine-position behavior. Always set `$APO.*` matching the motion family in use.
- **`$OV_PRO` is a system override.** Setting it in user code is disallowed by QA — it masks operator speed control and is a safety anti-pattern. Use `$OV_RED` (reduced override) only for controlled commissioning or teach-mode helpers that are removed before release.
- **Effect at runtime.** Effective velocity = programmed × (`$OV_PRO` / 100) × (`$OV_RED` / 100) × (pendant override / 100). Multiple knobs compose; if a program feels slow, check all four.
- **T1 speed cap.** Regardless of `$VEL.CP`, TCP speed in T1 is limited to 250 mm/s by safety. See `KUKA_SAFETY_Operating_Modes`.

## Common Pitfalls

- **Using `$VEL_AXIS` on a `LIN`** — has no effect; `LIN` uses `$VEL.CP`.
- **Using `$VEL.CP` on a `PTP`** — has no effect; `PTP` uses `$VEL_AXIS[i]`.
- **Setting `$OV_PRO` in production code** — silently overrides operator safety control.
- **Leaving `$APO.*` at teach-time values** — inherited defaults from another program may produce unexpected blend radii.
- **Assuming m vs. mm for `$VEL.CP`** — it is m/s, not mm/s. `$VEL.CP = 500` would be 500 m/s nominally, clipped in practice, and a sign of a copy/paste bug from FANUC where units are mm/s.
- **Scaling velocity but not acceleration** — commanding high `$VEL.CP` with low `$ACC.CP` never reaches programmed speed on short segments.

## Worked Example

```krl
DEF speed_setup()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   ; --- PTP speeds ---
   $VEL_AXIS[1] = 40
   $VEL_AXIS[2] = 40
   $VEL_AXIS[3] = 40
   $VEL_AXIS[4] = 50
   $VEL_AXIS[5] = 50
   $VEL_AXIS[6] = 50
   $ACC_AXIS[1] = 50

   ; --- CP speeds ---
   $VEL.CP    = 0.3       ; 300 mm/s path
   $VEL.ORI1  = 150
   $VEL.ORI2  = 150
   $ACC.CP    = 1.5
   $ACC.ORI1  = 200
   $ACC.ORI2  = 200

   ; --- Blending defaults ---
   $APO.CDIS  = 50
   $APO.CORI  = 50
   $APO.CVEL  = 100
   $APO.CPTP  = 75

   ; Now PTP and LIN both behave predictably
   PTP XHOME C_PTP
   LIN P1 C_DIS
   LIN P2
END
```

## Related Entries

- `KUKA_REF_PTP_Motion`, `KUKA_REF_LIN_Motion`, `KUKA_REF_CIRC_Motion`, `KUKA_REF_SPLINE_Block` — motion instructions that consume these variables.
- `ONE_motion_termination` — `$APO.*` controls the size of `C_*` blend regions.
- `KUKA_SAFETY_Operating_Modes` — T1 250 mm/s cap.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Motion preparation (Chapter 9); system-variable references across Chapter 11.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
