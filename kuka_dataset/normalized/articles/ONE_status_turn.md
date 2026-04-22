---
id: ONE_status_turn
title: Status and Turn (S/T) — Robot Configuration in Cartesian Targets
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [444, 447]
  section: "9.7 Status and Turn"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, ONE_singularities]
difficulty: advanced
tags: [motion, status, turn, configuration, inverse-kinematics]
---

# Status and Turn (S/T) — Robot Configuration in Cartesian Targets

## Summary

A six-axis articulated robot can usually reach the same Cartesian pose in multiple axis configurations — elbow up or down, wrist flipped or not, A4/A6 turning one direction or the other. Status (S) and Turn (T) disambiguate which configuration the controller uses when a Cartesian target is commanded via PTP. They are integer bit fields that encode the configuration explicitly. Omitting S/T means "keep the current configuration," which is usually fine but occasionally causes silent mid-program reorientation.

## Status (S)

Status is a 3-bit field encoding three kinematic choices:

| Bit | Meaning |
|-----|---------|
| Bit 0 | Basic position: overhead vs. basic (shoulder configuration). |
| Bit 1 | Elbow: positive vs. negative value of A3. |
| Bit 2 | Wrist: flipped vs. not (sign of A5). |

Written as an integer 0..7 (or more in 8.x, as reserved bits may appear). `S 2` means bit 1 set, bits 0 and 2 clear.

## Turn (T)

Turn is a 6-bit field, one bit per axis, indicating whether the axis value is in its negative or positive half-revolution from the mastering zero. Relevant for axes that can physically rotate past ±180°; the Turn bit tells the controller which side of the discontinuity to solve to.

`T 35` in binary is `100011` — axis 1 bit set, axis 2 set, axis 6 set (the bit ordering is axis 1 = LSB in the P2 training workbook; confirm against KSS 8.7 manual figure for your version).

## When S/T Matters

- **PTP with Cartesian target.** The controller solves inverse kinematics; S/T disambiguate the solution.
- **Teach points stored as `POS` or `E6POS`.** The teach-pendant records S/T at teach time; playback reproduces the taught configuration.
- **Program restart / BCO.** After a stop, the controller checks the stored S/T against the actual configuration; mismatch yields an error at BCO rather than a silent move.
- **LIN does not change S/T.** LIN motions are continuous in Cartesian space; the controller cannot cross a S/T discontinuity mid-LIN. If your target has a different S/T, a LIN fails and a PTP is required.

## When S/T Does Not Matter

- **Axis-space targets (`AXIS`, `E6AXIS`).** Axis values fully specify the configuration; S/T are meaningless.
- **FRAME targets.** Omit S/T entirely; the controller retains current configuration.

## Common Pitfalls

- **Copy-pasting Cartesian points without S/T** — the controller picks "current" configuration; two teach pendants, two different answers.
- **Mixing robots of different kinematic families** — S/T semantics are specific to the robot model; copied points may not translate.
- **Forcing a S/T change with LIN** — will not work; use PTP to reconfigure.
- **Ignoring turn** — for long, twisted programs, the same Cartesian pose at "T 0" vs. "T 32" wraps differently; subsequent LIN motions can then unwrap unexpectedly.
- **Relying on teach-pendant defaults** — always inspect S/T after teaching, especially for clearance and home positions.

## Worked Example

Teaching a point with explicit S/T:

```krl
DECL POS p_approach = {X 1000, Y 0, Z 1500, A 0, B 90, C 0, S 2, T 2}
DECL POS p_pick     = {X 1000, Y 0, Z 1200, A 0, B 90, C 0, S 2, T 2}
DECL POS p_elbow_up = {X 1000, Y 0, Z 1200, A 0, B 90, C 0, S 6, T 2}   ; different elbow

PTP p_approach               ; establish configuration
LIN p_pick                   ; LIN works — same S/T
PTP p_elbow_up               ; must be PTP — S differs
```

## Related Entries

- `KUKA_REF_PTP_Motion` — PTP is the motion that consumes S/T.
- `KUKA_REF_LIN_Motion` — why LIN rejects S/T changes.
- `ONE_singularities` — singularity handling intersects with S/T (wrist flip at A5 = 0).

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.7 "Status and Turn" (pp. 444–447).
- KUKA College, Robot Programming 2 lecture — Chapter 11.7 Status and Turn (T1).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
