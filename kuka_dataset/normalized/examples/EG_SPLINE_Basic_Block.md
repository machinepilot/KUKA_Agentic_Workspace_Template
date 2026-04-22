---
id: EG_SPLINE_Basic_Block
title: Basic SPLINE Block with SLIN and SCIRC
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 Exercises Ch 12: SPLINE"
  tier: T1
  pages: [67, 68]
  section: "Exercise 12"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_SPLINE_Block, ONE_spline_vs_ptp_lin, ONE_spline_orientation]
difficulty: advanced
tags: [example, spline, slin, scirc, motion, cp-motion]
---

# Basic SPLINE Block with SLIN and SCIRC

## Summary

A minimal-but-realistic spline program that runs a lead-in, a circular segment, and a lead-out as one planned trajectory. Demonstrates: block structure, segment-level `WITH` overrides for velocity, the `SCIRC` aux-orientation hint, and the classical-to-spline transition pattern. Use as a starting point for any multi-segment CP process path.

## File

`spline_demo.src` — single module.

## Source

```krl
&ACCESS RVP
DEF spline_demo()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   ; Block-level defaults
   $VEL.CP   = 0.3
   $ACC.CP   = 2.0
   $APO.CPTP = 75

   ; Transit to the lead-in position — classical PTP, fine at last point
   PTP P_home C_PTP
   PTP P_pre_lead_in

   ; --- Spline block ---
   SPLINE
      SLIN P_lead_in
         WITH $VEL.CP = 0.15         ; slower on lead-in
      SCIRC P_arc_aux, P_arc_end, #INTERPOLATE    ; orient through aux
         WITH $VEL.CP = 0.10         ; slower through arc
      SLIN P_lead_out
         WITH $VEL.CP = 0.2          ; faster lead-out
   ENDSPLINE
   ; --- End spline block ---

   PTP P_retract C_PTP
   PTP P_home
END
```

Companion data file sketch (abbreviated):

```krl
DEFDAT spline_demo PUBLIC
   DECL GLOBAL POS P_home        = {X 1000, Y   0, Z 1500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_pre_lead_in = {X  800, Y 100, Z  700, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_lead_in     = {X  800, Y 100, Z  500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_arc_aux     = {X  850, Y 150, Z  500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_arc_end     = {X  900, Y 100, Z  500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_lead_out    = {X  950, Y 100, Z  500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS P_retract     = {X  950, Y 100, Z  700, A 0, B 90, C 0, S 2, T 2}
ENDDAT
```

## Key Points

- **Block is framed by a fine-position point on each side.** `PTP P_pre_lead_in` (no blending) enters the block cleanly; `PTP P_retract` after the block is likewise exact. This is the safest classical-to-spline transition.
- **`WITH $VEL.CP = ...`** scopes the override to a single segment. Without `WITH`, the block-level `$VEL.CP` applies throughout.
- **`SCIRC` orientation mode** is declared inline (`#INTERPOLATE`). Try the example with `#IGNORE` to see the visible difference in orientation profile at the aux point.
- **No `C_*` clauses inside the block.** Spline segments blend automatically.
- **Segment endpoints are `POS` with S/T.** Spline supports `FRAME` too, but including S/T is cleaner for reproducibility.

## Variations to Try

1. **`#IGNORE` vs. `#INTERPOLATE`** on `SCIRC` — observe the difference in wrist motion.
2. **Remove the middle `WITH`** — the arc runs at the block-level speed (`$VEL.CP = 0.3`); observe cycle time.
3. **Replace the classical `PTP P_pre_lead_in`** with a second spline block containing a `SPTP P_pre_lead_in` — see whether the transition is smoother.
4. **Add a `SPL P_fillet_through`** between `SLIN` and `SCIRC` for polynomial smoothing — compare geometry.

## Common Pitfalls

- **Trying `C_DIS` inside the block.** Not permitted.
- **Empty block body.** Compile error.
- **Teaching all points at once on the pendant** — pendant-generated code mixes folds and inline forms; clean up before committing.
- **Starting block while still moving** — if the preceding motion is blended, advance-run may be inside the spline before the block begins; use `C_FINE` or a `PTP` without termination to be safe.

## Related Entries

- `KUKA_REF_SPLINE_Block` — syntax reference.
- `ONE_spline_vs_ptp_lin` — decision guide.
- `ONE_spline_orientation` — aux-orientation modes explained.

## Citations

- KUKA College, Robot Programming 2 Exercise Book — Chapter 12 exercise (pp. 67–68).
- KUKA College, Robot Programming 2 lecture — Chapter 12.2 "SPLINE basics" (pp. 200–204).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf`.
