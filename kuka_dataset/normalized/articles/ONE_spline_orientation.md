---
id: ONE_spline_orientation
title: Orientation Control for SPLINE (SCIRC aux modes)
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [436, 442]
  section: "9.5.x SCIRC orientation"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_SPLINE_Block, KUKA_REF_CIRC_Motion, ONE_spline_vs_ptp_lin]
difficulty: advanced
tags: [motion, spline, scirc, orientation, interpolate, ignore, consider, extrapolate]
---

# Orientation Control for SPLINE (SCIRC aux modes)

## Summary

In a `SCIRC` segment inside a SPLINE block, the robot's position follows a circle defined by start, auxiliary, and end points — but orientation is controlled independently. KSS 8.7 exposes four aux-point orientation modes that let the programmer decide what role the aux point plays for tool orientation: `#INTERPOLATE`, `#IGNORE`, `#CONSIDER`, `#EXTRAPOLATE`. Picking the right mode is essential for CP processes where tool orientation relative to the workpiece matters (welding, dispensing, mill/deburr).

## The Four Modes

Assume a `SCIRC` segment whose aux point has orientation `O_aux` and whose end point has orientation `O_end`, starting from `O_start`.

### `#INTERPOLATE` (default for most welders' intent)

The TCP orientation passes through `O_aux` on the way from `O_start` to `O_end`. Orientation is interpolated via the aux — the aux contributes a middle keyframe. Use when the tool must actually be at a specific orientation mid-arc.

### `#IGNORE`

The aux point's orientation is ignored; orientation interpolates directly from `O_start` to `O_end`. Use when aux is only a geometric through-point and its recorded orientation is incidental (e.g., jogged to clear a fixture).

### `#CONSIDER`

The aux's orientation influences the path of orientation through the arc but the TCP does not pass through `O_aux` exactly. The controller computes a curve that "considers" the aux and may reach it only approximately. Use when `#INTERPOLATE` produces too-aggressive orientation changes and `#IGNORE` produces a path that clips a fixture.

### `#EXTRAPOLATE`

Orientation is extrapolated from a line through the aux — the aux defines the orientation trajectory's direction, not a keyframe. Use for process paths where orientation must change at a predictable rate and the aux is chosen to anchor that rate.

## How to Select the Mode

```krl
SPLINE
   WITH $VEL.CP = 0.2
   SCIRC P_aux, P_end, CA 90, $SPL_ORI_TYPE = #INTERPOLATE
ENDSPLINE
```

The mode variable name and exact binding may vary by KSS minor version — in the P2 training workbook the modes appear as parameters of the `SCIRC` instruction itself. Confirm against the controller in use by checking the inline-form help on the pendant.

## Common Pitfalls

- **Leaving the default `#INTERPOLATE`** when the aux orientation was never intentionally taught. The tool does a surprise mid-arc orientation change.
- **Using `#IGNORE` for a long arc through a narrow gap** — orientation interpolates start→end on a straight-line rotation, which may rotate through a fixture.
- **Mixing `#CONSIDER` and `#EXTRAPOLATE` in back-to-back SCIRCs** without understanding both. Behavior is correct per segment but the overall orientation profile becomes hard to reason about.
- **Copy-pasting SCIRC segments without re-teaching aux orientation** — the aux point's orientation is part of its record and survives copy.

## Worked Example

A dispensing arc where the tool must be perpendicular to the surface at the midpoint:

```krl
SPLINE
   WITH $VEL.CP = 0.1
   SLIN P_dispense_start
   SCIRC P_arc_mid, P_arc_end, #INTERPOLATE     ; tool vertical at arc_mid
   SLIN P_dispense_end
ENDSPLINE
```

Same arc where the mid-point orientation is incidental:

```krl
SPLINE
   SLIN P_dispense_start
   SCIRC P_arc_mid, P_arc_end, #IGNORE          ; straight orientation interpolation
   SLIN P_dispense_end
ENDSPLINE
```

## Related Entries

- `KUKA_REF_SPLINE_Block` — spline syntax, segment instructions.
- `KUKA_REF_CIRC_Motion` — classical CIRC (fewer orientation options).
- `ONE_spline_vs_ptp_lin` — when to reach for spline in the first place.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). SCIRC orientation modes (pp. 436–442).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
