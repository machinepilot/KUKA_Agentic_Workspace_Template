---
id: ONE_motion_blending
title: Blending and Continuous Path (CP) Motion in KRL
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
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_SPLINE_Block, ONE_motion_termination, ONE_spline_vs_ptp_lin]
difficulty: intermediate
tags: [motion, blending, continuous-path, cycle-time, smoothing]
---

# Blending and Continuous Path (CP) Motion in KRL

## Summary

"Blending" (KUKA terminology: *approximate positioning*) is the act of skipping the stop at a programmed intermediate target and smoothly transitioning into the next motion. Done right, it eliminates unnecessary decelerations, reduces cycle time, and is gentler on mechanics. Done wrong, it silently changes the TCP path, risking collisions and process faults. This article covers the classical `C_*` family, why spline blocks are usually the better modern choice, and how to reason about blend geometry.

## Classical Blending with `C_*`

Classical motion instructions (`PTP`, `LIN`, `CIRC`) accept one termination clause that switches exact-stop behavior to approximate:

- `C_PTP` — axis-space approximation. The blend region is defined by `$APO.CPTP` (% of remaining path).
- `C_DIS` — Cartesian distance. Blend begins within `$APO.CDIS` mm.
- `C_ORI` — orientation angle. Blend begins within `$APO.CORI` ° of target orientation.
- `C_VEL` — when path velocity has dropped to `$APO.CVEL` % of programmed.

For CP-to-CP transitions the blend shape is a smoothed curve through the neighborhood of the programmed target. For PTP-to-LIN or LIN-to-PTP transitions the controller blends in Cartesian space, but the preceding or following PTP segment may deviate in axis space beyond the blend zone.

The programmed target **is not reached**; the TCP passes through a region in the neighborhood. If your process logic depends on exact position, do not blend.

## Spline Blocks

Spline blocks (`SPLINE`/`ENDSPLINE`, `SPTP`/`ENDSPLINE`) plan the whole block as one trajectory. Benefits over classical blending:

- **Continuous velocity by construction.** No need to tune `$APO.*`.
- **Deterministic geometry.** The path is a spline through the segment endpoints; reviewers can reason about shape without simulating the blend math.
- **Cleaner orientation.** `SCIRC` aux-orientation modes make orientation behavior explicit.
- **Triggers (path-related) work predictably** relative to segment endpoints.

For three or more chained CP segments, prefer spline.

## Reasoning About Blend Zones

A few rules that save debugging time:

1. **Blend radius scales with velocity and acceleration.** Higher `$VEL.CP` and lower `$ACC.CP` enlarge the actual blend region beyond `$APO.CDIS`. The `$APO.*` values are *minimum* criteria, not a geometric radius.
2. **Short segments may swallow the blend.** If a LIN segment is shorter than the blend region of its neighbors, the TCP never reaches programmed velocity and the blend curve deforms.
3. **Approximate positioning changes stop feedback.** `$POS_ACT` at the moment of the "target" is not the target; it is wherever the TCP is when the controller moves on.
4. **Signals should be path-triggered.** `TRIGGER WHEN PATH = <offset>...` fires at a programmable distance before/after a point; this is the correct tool for coordinating signals with blended motion.

## Common Pitfalls

- **Blending a clearance point** — the TCP cuts inside the programmed clearance. Always verify blended paths against fixture boundaries (simulation or slow run).
- **`C_VEL` on a short segment** — the velocity target may not be reached; blending starts immediately.
- **Mixing blend criteria across a transition** — `LIN P1 C_DIS` followed by `LIN P2 C_ORI` uses different blend geometry at P1 vs. P2; consistency matters for predictable cycle time.
- **Leaving classical blending in a spline block** — not permitted; segments accept `WITH ...` overrides, not `C_*`.

## Worked Example

Classical blending for a simple L-shape:

```krl
$APO.CDIS = 50

LIN P_corner_approach C_DIS
LIN P_corner_exit                   ; exact at the exit

; vs. spline for a three-segment curve
SPLINE
   SLIN P_seg1_end
   SCIRC P_arc_aux, P_arc_end
   SLIN P_seg3_end
ENDSPLINE
```

## Related Entries

- `ONE_motion_termination` — the full list of `C_*` clauses.
- `KUKA_REF_SPLINE_Block` — syntax of the block.
- `ONE_spline_vs_ptp_lin` — choosing spline vs. classical.
- `KUKA_REF_Velocity_Acceleration` — `$APO.*` values.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.6 "Motion termination / approximate positioning" (pp. 417–420); Chapter 9.5 "SPLINE motion" for block-level blending.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
