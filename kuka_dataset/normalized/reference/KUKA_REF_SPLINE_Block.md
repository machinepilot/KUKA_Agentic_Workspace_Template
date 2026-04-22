---
id: KUKA_REF_SPLINE_Block
title: KRL SPLINE Block (SPLINE / SPTP / SLIN / SCIRC)
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [421, 590]
  section: "9.5 SPLINE motion; 11.6 Spline programming"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, ONE_spline_vs_ptp_lin, ONE_spline_orientation, ONE_motion_termination, ONE_motion_blending, EG_SPLINE_Basic_Block]
difficulty: advanced
tags: [motion, spline, cp-motion, sptp, slin, scirc]
---

# KRL SPLINE Block (SPLINE / SPTP / SLIN / SCIRC)

## Summary

SPLINE is KUKA's modern motion model. A `SPLINE` block groups one or more spline segments (`SLIN`, `SCIRC`, and optionally `SPL`) into a single planned path; `SPTP` is the axis-space analog. Compared to classical PTP/LIN/CIRC with `C_*` blending, spline motion plans the whole block as a single trajectory: smoother velocity, fewer blending approximations, more predictable cycle time, and cleaner orientation control.

## Syntax / Specification

Two block types:

```krl
SPLINE                          ; Cartesian spline block
   SLIN P_a
   SCIRC P_aux, P_b
   SLIN P_c
ENDSPLINE

SPTP                            ; axis-space spline block (PTP-style)
   SPTP P_1
   SPTP P_2
   SPTP P_3
ENDSPLINE
```

Segment instructions:

| Instruction | Meaning |
|-------------|---------|
| `SLIN <point>` | Straight-line segment in Cartesian space. |
| `SCIRC <aux>, <end>` | Circular segment in Cartesian space. |
| `SPL <point>` | Spline-interpolated (polynomial) segment; controller fits a smooth curve through the point. |
| `SPTP <point>` | Axis-space segment (only inside `SPTP` block). |

Optional per-segment modifiers: `WITH ...` clauses for per-segment velocity, acceleration, and orientation control (e.g., `WITH $VEL.CP = 0.3`).

## Semantics / Behavior

- **Whole-block planning.** The controller computes the trajectory across the entire spline block before starting motion. This enables true smoothing between segments — no `C_*` approximation needed.
- **Continuous velocity.** Velocity is generally continuous across segment boundaries (no deceleration to zero between segments), which shortens cycle time and reduces wear.
- **Orientation modes.** `SCIRC` supports four aux-point orientation modes — `#INTERPOLATE` (orientation passes through aux), `#IGNORE` (aux orientation ignored), `#CONSIDER` (aux orientation used but TCP does not visit it), `#EXTRAPOLATE` (derived from line through aux). See `ONE_spline_orientation`.
- **Triggers.** Spline blocks support path-related triggers (`TRIGGER WHEN PATH = <offset> ...`) that fire at a defined distance before/after a point — not covered in this pass-1 entry.
- **Stop and resume.** A spline block stopped mid-execution can be resumed; the advance run pointer tracks position within the block.
- **Compatibility.** Spline blocks cannot be mixed freely with classical motions on the same advance-run step; wrap each logical segment group in its own `SPLINE` block with PTP transitions between.
- **When not to use SPLINE.** For a single straight-line move or a single circular arc, classical `LIN`/`CIRC` are simpler and have identical path. SPLINE earns its weight when you have 3+ chained CP segments.

## Common Pitfalls

- **Empty SPLINE block** — controller error. A block needs at least one segment.
- **Using `SLIN` outside a `SPLINE` block** — syntax error; `SLIN`/`SCIRC`/`SPL` are valid only inside a block.
- **Expecting `C_DIS` inside a spline** — spline blends are automatic; do not add classical termination clauses to segments.
- **Copy-pasting from classical motions** — the variables controlling speed inside a spline may require `WITH` overrides to take effect on specific segments.
- **Aux point with insufficient offset on `SCIRC`** — same collinearity constraint as classical `CIRC`.
- **Confusing `SPL` (polynomial through the point) with `SLIN` (straight line)** — `SPL` smooths and may deviate from geometry the programmer expects.

## Worked Example

Three-segment Cartesian spline (approach → arc → retract):

```krl
DEF spline_demo()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   $VEL.CP = 0.4
   $ACC.CP = 2.0

   PTP P_home C_PTP

   SPLINE
      SLIN P_approach
      SCIRC P_arc_aux, P_arc_end
      SLIN P_retract
   ENDSPLINE

   PTP P_home
END
```

See `EG_SPLINE_Basic_Block` for an example with segment-local `WITH` overrides.

## Related Entries

- `ONE_spline_vs_ptp_lin` — decision guide for choosing spline vs. classical motion.
- `ONE_spline_orientation` — `#INTERPOLATE` / `#IGNORE` / `#CONSIDER` / `#EXTRAPOLATE` on `SCIRC` aux.
- `KUKA_REF_LIN_Motion`, `KUKA_REF_CIRC_Motion`, `KUKA_REF_PTP_Motion` — classical counterparts.
- `ONE_motion_blending` — why spline usually outperforms `C_DIS`/`C_ORI`.
- `EG_SPLINE_Basic_Block` — worked example.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.5 "SPLINE motion" (pp. 421–435); Chapter 11.6 "Spline programming" (pp. 565–590).
- KUKA College, Robot Programming 2 lecture — Chapter 12 "SPLINE motion" (T1 training).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`. Summarized in our own words; no table or figure reproduction.
