---
id: KUKA_REF_PTP_Motion
title: KRL PTP Motion Instruction
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [415, 557]
  section: "9.2 Motion type PTP; 11.5 Motion programming"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_SPLINE_Block, KUKA_REF_Tool_Base_Frames, KUKA_REF_Velocity_Acceleration, ONE_motion_termination, ONE_motion_blending, ONE_status_turn, ONE_singularities, EG_PTP_Hello]
difficulty: intermediate
tags: [motion, ptp, asynchronous, axis-interpolated]
---

# KRL PTP Motion Instruction

## Summary

`PTP` is the point-to-point motion instruction in KRL. The robot moves all axes simultaneously from the current position to the target; each axis starts and ends at the same time, but the slowest axis dominates the move. The tool center point (TCP) path is not planned in Cartesian space and is generally curved. PTP is the fastest way to move between two points when the exact path shape does not matter.

## Syntax / Specification

Canonical forms:

```krl
PTP <target>                    ; fine positioning (exact stop)
PTP <target> C_PTP              ; approximate positioning (blended, axis space)
PTP <target> C_DIS              ; approximate positioning (Cartesian distance criterion)
```

Target types:

- `POS` / `E6POS` — Cartesian target with Status/Turn (`S`, `T`). The controller solves inverse kinematics at planning time.
- `AXIS` / `E6AXIS` — axis-space target (A1..A6, plus E1..E6 for external axes). No inverse kinematics.
- `FRAME` — Cartesian target without Status/Turn; the controller reuses the current S/T.

Examples:

```krl
PTP {X 1000, Y 0, Z 1200, A 0, B 90, C 0, S 2, T 2}
PTP {A1 0, A2 -90, A3 90, A4 0, A5 0, A6 0}
PTP XHOME                       ; named point from $config.dat
PTP P1 C_PTP                    ; blended move to P1
```

## Semantics / Behavior

- **Asynchronous axis motion.** All axes reach the target simultaneously; no Cartesian path control. Useful for gross repositioning, pick/place approach moves, and avoiding singularities where Cartesian motion would fail.
- **Velocity source.** PTP speed is governed by `$VEL_AXIS[1..6]` (percentage of maximum per axis). Acceleration by `$ACC_AXIS[1..6]`.
- **Status and Turn.** For Cartesian targets with S/T specified, the controller resolves the inverse kinematics to the exact configuration (elbow up/down, wrist flipped, turn values). If S/T are omitted, the controller uses the current configuration. `S/T` mismatches between consecutive Cartesian PTP points can trigger a stop.
- **Approximate vs. exact.** A bare `PTP` ends with the axes at rest at the programmed target (fine positioning). `PTP <target> C_PTP` blends into the next motion; the programmed target is not reached exactly. See `ONE_motion_termination`.
- **First motion of the program.** The first PTP after an advance-run gap (or after program start) must be a fully defined point — axis target or Cartesian target with S/T — so the controller can synchronize its internal position tracking with the mechanics.
- **No path planning.** Do not use PTP when the TCP must follow a straight or circular path (e.g., welding, gluing, cutting); use `LIN` or `CIRC` instead.

## Common Pitfalls

- **Missing S/T on Cartesian PTP** after a program restart or BCO move, causing the controller to pick an unintended configuration.
- **Blended PTP across a singularity** — approximate positioning can fail or deform unexpectedly near wrist singularities; see `ONE_singularities`.
- **Assuming inherited `$VEL_AXIS`** — always set velocity explicitly in a program prologue; do not rely on prior-program state.
- **Using `PTP` where `LIN` is required** — a PTP move between two close points can still deviate from a straight line enough to collide with fixtures.
- **Reading `$POS_ACT` immediately after a blended PTP** — the reported position is a sampled runtime value, not the programmed target, and will vary with override.

## Worked Example

Minimal safe PTP move with explicit frame, velocity, and termination:

```krl
DEF ptp_demo()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   $VEL_AXIS[1] = 30
   $VEL_AXIS[2] = 30
   $VEL_AXIS[3] = 30
   $VEL_AXIS[4] = 30
   $VEL_AXIS[5] = 30
   $VEL_AXIS[6] = 30
   $ACC_AXIS[1] = 50

   ; Exact stop at home (BCO point)
   PTP XHOME

   ; Blended approach into pick
   PTP {X 500, Y 200, Z 400, A 180, B 0, C 180, S 2, T 2} C_PTP

   ; Fine pick position
   PTP {X 500, Y 200, Z 250, A 180, B 0, C 180, S 2, T 2}

END
```

See `EG_PTP_Hello` for the minimal program with interrupts; see `EG_Palletizing_Skeleton` for a realistic production structure.

## Related Entries

- `KUKA_REF_LIN_Motion` — Cartesian straight-line motion; use where path shape matters.
- `KUKA_REF_CIRC_Motion` — Cartesian circular motion.
- `KUKA_REF_SPLINE_Block` — modern spline block with richer blending.
- `KUKA_REF_Velocity_Acceleration` — speed/accel system variables referenced by PTP.
- `KUKA_REF_Tool_Base_Frames` — required frame setup before any motion.
- `ONE_motion_termination` — `C_PTP` vs. `C_DIS` vs. `C_FINE` semantics.
- `ONE_status_turn` — how Status/Turn disambiguate Cartesian targets.
- `ONE_singularities` — configurations where PTP blending becomes risky.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Section 9.2 "Motion type PTP" (p. 415); Chapter 11.5 "Programming motions PTP / LIN / CIRC" (pp. 555–557). Publication date 2023-07-07.
- KUKA College, Robot Programming 2 lecture workbook (KSS 8.x) — Chapter 11 motion recap (T1, training).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator. Raw source: `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`. Summarized in our own words per copyright policy; no verbatim reproduction of tables or figures.
