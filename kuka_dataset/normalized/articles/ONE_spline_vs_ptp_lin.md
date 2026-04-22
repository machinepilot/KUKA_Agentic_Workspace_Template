---
id: ONE_spline_vs_ptp_lin
title: When to Use SPLINE vs. PTP / LIN / CIRC
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [421, 435]
  section: "9.5 SPLINE motion; 12.1 Spline vs. classical motion"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_SPLINE_Block, KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, ONE_motion_blending, ONE_spline_orientation, EG_SPLINE_Basic_Block]
difficulty: intermediate
tags: [motion, spline, decision-guide, path-planning]
---

# When to Use SPLINE vs. PTP / LIN / CIRC

## Summary

KUKA offers two motion models: the classical PTP / LIN / CIRC (introduced with KR C2-era KRL, still present for compatibility) and the modern SPLINE block (KR C4 onward, preferred). Both are fully supported in KSS 8.x; choosing between them is a recurring decision point in program design. The short rule: **use SPLINE for any continuous-path process with more than one planned CP segment; use PTP/LIN/CIRC for gross repositioning and for short one-shot CP motions.**

## When to Prefer SPLINE

- **Multi-segment process paths.** Welds, dispensing beads, cutting contours, deburring — anywhere the TCP follows a designed path. Spline blocks plan the full path as one trajectory; velocity is continuous; orientation is coordinated.
- **Tight cycle time.** Spline eliminates the micro-decelerations that `C_*` blending leaves in place.
- **Predictable stop-and-resume.** Advance-run behavior inside a block is cleaner than across a string of classical motions.
- **When orientation control matters.** `SCIRC` aux-orientation modes (`#INTERPOLATE`, `#IGNORE`, `#CONSIDER`, `#EXTRAPOLATE`) expose exactly how orientation is handled; classical CIRC does not.
- **Path-related triggers.** `TRIGGER WHEN PATH = ...` is cleaner inside a spline block.

## When to Prefer Classical PTP / LIN / CIRC

- **Single motion.** One PTP to home, one LIN to pick, one CIRC around a fillet — no reason to wrap a single segment in a SPLINE block.
- **Gross repositioning.** PTP excels here; SPLINE is for CP paths.
- **Legacy programs.** When maintaining a customer program written entirely in the classical style, stay consistent; mixing adds review burden.
- **Teach-pendant inline forms.** The operator UI still emits classical motions; if a program is designed to be edited on the pendant, spline may force developers back to a text editor.
- **When readers of the code are more familiar with classical motions.** Simpler is better if the process doesn't need spline's features.

## Hybrid Patterns

It is perfectly normal to mix:

```krl
PTP P_home C_PTP
PTP P_safe_approach C_PTP

SPLINE
   SLIN P_process_start
   SCIRC P_arc_aux, P_arc_end
   SLIN P_process_end
ENDSPLINE

PTP P_retract C_PTP
PTP P_home
```

Transitions between classical and spline require a planned stop unless both motions fit into the same advance-run window — the simplest rule is "end the classical motion fine (or `C_PTP`) before the SPLINE block, and start the classical motion after the block."

## Common Pitfalls

- **Wrapping everything in SPLINE.** A single-segment spline block is overhead without benefit.
- **Ignoring `$VEL.CP` inside a spline.** Without explicit velocity, block cycle time is dominated by the slowest segment's defaults; set `$VEL.CP` before the block or use `WITH $VEL.CP = ...` per segment.
- **Mixing `C_DIS` with spline segments.** Not permitted.
- **Treating spline as a drop-in LIN replacement** in tight spaces. Spline may deviate slightly from a classical LIN between two points; for tool entry into a tight feature, test path before committing.

## Worked Example

Fillet-weld path as spline block (preferred) vs. classical chain (legacy style):

```krl
; --- Modern spline ---
SPLINE
   WITH $VEL.CP = 0.15
   SLIN P_weld_lead_in
   SLIN P_corner_1
   SCIRC P_corner_aux, P_corner_end
   SLIN P_weld_lead_out
ENDSPLINE

; --- Legacy classical with blending ---
$VEL.CP = 0.15
$APO.CDIS = 20
LIN  P_weld_lead_in C_DIS
LIN  P_corner_1     C_DIS
CIRC P_corner_aux, P_corner_end C_DIS
LIN  P_weld_lead_out
```

See `EG_SPLINE_Basic_Block` for a full worked example with `WITH` overrides.

## Related Entries

- `KUKA_REF_SPLINE_Block` — spline syntax reference.
- `KUKA_REF_LIN_Motion`, `KUKA_REF_CIRC_Motion`, `KUKA_REF_PTP_Motion` — classical counterparts.
- `ONE_spline_orientation` — orientation behavior that is difficult to match with classical CIRC.
- `ONE_motion_blending` — classical blending concepts.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.5 "SPLINE motion" (pp. 421–435); spline-vs-classical discussion (Chapter 12.1 in P2 lecture).
- KUKA College, Robot Programming 2 lecture — Chapter 12.1 (T1 training).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf` + `WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf`.
