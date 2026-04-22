---
id: KUKA_REF_LIN_Motion
title: KRL LIN Motion Instruction
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [416, 557]
  section: "9.3 Motion type LIN; 11.5 Motion programming"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_SPLINE_Block, KUKA_REF_Velocity_Acceleration, KUKA_REF_Tool_Base_Frames, ONE_motion_termination, ONE_motion_blending, ONE_status_turn, ONE_singularities]
difficulty: intermediate
tags: [motion, lin, cartesian, cp-motion, straight-line]
---

# KRL LIN Motion Instruction

## Summary

`LIN` moves the tool center point along a straight line in Cartesian space from the current position to the target. Orientation is interpolated separately (quaternion-like) between start and end. Use `LIN` whenever the TCP path shape matters: welding, gluing, dispensing, pick/place where the approach must clear obstacles, and any process constrained to a straight line.

## Syntax / Specification

```krl
LIN <target>                    ; fine positioning (exact stop)
LIN <target> C_DIS              ; blended, Cartesian distance criterion
LIN <target> C_ORI              ; blended, orientation criterion
LIN <target> C_VEL              ; blended, velocity criterion
```

Target types:

- `POS` / `E6POS` — Cartesian target with Status/Turn.
- `FRAME` — Cartesian target without Status/Turn; current configuration retained.
- Axis-space targets are **not** valid for `LIN`.

Examples:

```krl
LIN {X 800, Y 0, Z 500, A 0, B 90, C 0}
LIN P_approach C_DIS
LIN P_weld_start
```

## Semantics / Behavior

- **Cartesian straight-line TCP path** between start and end, measured in the active `$BASE` frame, with the active `$TOOL` applied.
- **Orientation interpolation** runs in parallel with translation. For CP motion the orientation mode is controlled by `$ORI_TYPE` (`#CONSTANT`, `#VAR`, `#JOINT`). See `ONE_spline_orientation` for details applicable to spline; similar principles govern LIN.
- **Velocity source.** Path velocity is set by `$VEL.CP` (Cartesian path velocity, m/s) and `$VEL.ORI1`/`$VEL.ORI2` (angular). Acceleration by `$ACC.CP`, `$ACC.ORI1`, `$ACC.ORI2`.
- **Singularity behavior.** Because LIN plans the straight TCP path before moving, wrist singularities along that path cause a planning stop (`KSS15004` or similar). Options: reroute via an intermediate point, switch to PTP for that segment, or enable `$SINGUL_POS[]` handling where available.
- **Termination types.** `C_DIS`, `C_ORI`, and `C_VEL` each define when the blending region begins. `C_FINE` (exact stop) is the default if no termination is given; a bare `LIN` means exact stop. See `ONE_motion_termination`.
- **Status/Turn changes.** A LIN motion cannot cross a S/T discontinuity. If the target's S/T differs from the current configuration, the controller raises an error rather than silently reconfiguring mid-line.

## Common Pitfalls

- **Assuming LIN will "find a way through" a singularity** — it will not; the programmer must break the motion into segments.
- **Setting `$VEL.CP` too high** for short segments — the robot never reaches programmed speed and cycle time is dominated by acceleration.
- **Forgetting the TCP is in `$TOOL`** — wrong tool selection shifts the programmed path by the tool offset.
- **Hard-coded Cartesian points copied across customers** — Cartesian targets are `$BASE`-relative; moving a program to a new cell without updating `$BASE` is a common integration bug.
- **Mixing LIN and PTP blending** without understanding that the blend geometry differs — approximate PTP→LIN and LIN→PTP blends are Cartesian, but the preceding or following segment may still deviate in axis space.

## Worked Example

Straight-line approach and retract around a pick point:

```krl
DEF lin_pick()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   $VEL.CP = 0.5                ; 0.5 m/s Cartesian
   $ACC.CP = 2.0
   $APO.CDIS = 50               ; blending distance for C_DIS

   ; Position above pick
   PTP P_approach C_PTP

   ; Straight descent to pick
   LIN P_pick

   ; (gripper close happens here)

   ; Straight retract
   LIN P_retract C_DIS

   ; Transit
   PTP P_place_approach C_PTP

END
```

## Related Entries

- `KUKA_REF_PTP_Motion` — axis-space alternative; faster but no path guarantee.
- `KUKA_REF_CIRC_Motion` — Cartesian circular motion.
- `KUKA_REF_SPLINE_Block` — preferred modern CP motion for multi-segment paths.
- `KUKA_REF_Velocity_Acceleration` — `$VEL.CP`, `$ACC.CP` system variables.
- `ONE_motion_termination` — `C_DIS` / `C_ORI` / `C_VEL` termination semantics.
- `ONE_singularities` — why LIN can fail near wrist singularities.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Section 9.3 "Motion type LIN" (p. 416); Chapter 11.5 motion programming (pp. 555–557).
- KUKA College, Robot Programming 2 lecture — Chapter 11.4 "CP motion, LIN" (T1 training).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`. Summary in our own words; no verbatim reproduction.
