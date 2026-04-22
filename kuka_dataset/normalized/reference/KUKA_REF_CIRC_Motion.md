---
id: KUKA_REF_CIRC_Motion
title: KRL CIRC Motion Instruction
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [416, 557]
  section: "9.4 Motion type CIRC; 11.5 Motion programming"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_SPLINE_Block, ONE_motion_termination, ONE_motion_blending, ONE_spline_orientation, ONE_status_turn, ONE_singularities]
difficulty: intermediate
tags: [motion, circ, cartesian, cp-motion, circular-arc]
---

# KRL CIRC Motion Instruction

## Summary

`CIRC` moves the tool center point along a circular arc in Cartesian space. The arc is defined by the current position, an auxiliary point (which the TCP passes through unless a circular angle is specified), and an end point. Use `CIRC` for curved process paths — fillet welds around a radius, dispensing around a corner, circular deburring.

## Syntax / Specification

```krl
CIRC <aux_point>, <end_point>                 ; full arc from current through aux to end
CIRC <aux_point>, <end_point>, CA <angle>     ; partial / extended arc by circular angle
CIRC <aux_point>, <end_point> C_DIS           ; with blending
```

Target types for `aux_point` and `end_point`: `POS`, `E6POS`, or `FRAME`. Axis-space targets are not valid.

`CA <angle>` (circular angle) lets the end point be computed from the geometry rather than being exactly reached; positive values extend the arc beyond the programmed end, negative values shorten it. Useful when the physical end point is constrained by the workpiece and the programmer wants a specific arc length.

## Semantics / Behavior

- **Three-point circle.** Start = current position (from the preceding motion). Aux = programmed through-point. End = programmed end point. The three points define the plane of the arc.
- **TCP passes through the auxiliary point** when `CA` is not used. With `CA`, aux still defines the plane but the TCP may not visit aux exactly.
- **Orientation control.** Default orientation interpolation carries from start to end; KSS 8.7 extends this with aux-point orientation modes `#INTERPOLATE`, `#IGNORE`, `#CONSIDER`, `#EXTRAPOLATE` (applicable to spline `SCIRC`; classic `CIRC` supports a subset). See `ONE_spline_orientation` for the full matrix.
- **Singularities.** Same constraints as `LIN`: the controller plans the full Cartesian path and rejects traversals that cross a wrist singularity.
- **Velocity.** Uses the same Cartesian velocity/acceleration system variables as LIN (`$VEL.CP`, `$VEL.ORI1/2`, `$ACC.CP`).
- **Degenerate geometry.** If the three points are collinear (or nearly so) the controller cannot define a unique circle and raises an error. Offset the aux point enough that the arc's radius is well-defined.

## Common Pitfalls

- **Collinear aux/start/end** → controller error. Always check by sketching in the active `$BASE`.
- **Aux point where the tool collides** — the TCP physically reaches aux unless `CA` is used; verify clearance.
- **Copying `CIRC` blocks across cells** where the `$BASE` rotated — the arc plane rotates with the base, which usually (but not always) is what you want.
- **Using `CIRC` for small blends** — a `C_DIS` blend on a `LIN` is often simpler and faster than a two-segment LIN+CIRC+LIN.
- **Orientation surprises at high speed** — with long arcs the orientation interpolation can make the wrist rotate faster than intuited; monitor `$VEL.ORI1/2`.

## Worked Example

Quarter-circle between two straight segments (fillet around a corner):

```krl
DEF circ_corner()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   $VEL.CP = 0.2
   $ACC.CP = 1.0

   LIN P_line1_end C_DIS
   CIRC P_corner_aux, P_corner_end C_DIS
   LIN P_line2_end

END
```

With circular angle to overshoot the geometric end by 10°:

```krl
CIRC P_aux, P_end, CA 10
```

## Related Entries

- `KUKA_REF_LIN_Motion` — straight-line counterpart.
- `KUKA_REF_SPLINE_Block` — `SCIRC` inside a spline block is usually preferable for multi-segment process paths.
- `ONE_motion_termination` — blending types applicable.
- `ONE_spline_orientation` — auxiliary-point orientation modes.
- `ONE_singularities` — singular configurations block CIRC planning.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Section 9.4 "Motion type CIRC" (pp. 416–417); Chapter 11.5 motion programming (pp. 555–557).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`. Summary in our own words.
