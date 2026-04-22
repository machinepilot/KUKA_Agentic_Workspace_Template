---
id: ONE_singularities
title: "Singularities: Overhead, Extended, and Wrist"
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [448, 450]
  section: "9.8 Singularities"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_PTP_Motion, ONE_status_turn]
difficulty: advanced
tags: [motion, singularity, kinematics, wrist, overhead, extended]
---

# Singularities: Overhead, Extended, and Wrist

## Summary

A singularity is a robot configuration where the Jacobian of the forward kinematics loses rank — intuitively, the robot can no longer move the TCP in at least one Cartesian direction without infinite joint velocity. For CP motions (LIN, CIRC, spline) this matters because the controller cannot plan a straight-line path through a singularity without violating axis-velocity limits. KUKA 6-axis robots exhibit three singularity families: **overhead**, **extended position**, and **wrist**.

## The Three Singularities

### Overhead singularity

Tool center point on or near the axis-1 axis (the vertical through the base). A1 rotation around this axis produces no TCP motion — the robot can spin around A1 without moving the tool. Detection: `$SINGUL_POS[1]` (confirm variable name/index against your KSS version) flags proximity.

### Extended position singularity

A3 very close to 0°: the arm is fully stretched out, so small changes in A3 produce large changes in end effector position. Jacobian rank drops; motion through the arm-stretched zone becomes unstable. Detection: `$SINGUL_POS[2]`.

### Wrist singularity

A5 close to 0° with A4 and A6 collinear. Infinite pairs of (A4, A6) produce the same wrist orientation; the controller cannot decide how to split rotation between the two axes. LIN through a wrist singularity raises a planning error. Detection: `$SINGUL_POS[3]`.

## Why This Matters

- **LIN / CIRC fail** when the planned Cartesian path crosses a singularity. The controller refuses to move rather than produce unpredictable joint motion.
- **PTP may succeed** because PTP is axis-space; the controller picks joint trajectories without requiring the Jacobian to be well-conditioned. A common fix is to break a problematic LIN into LIN→PTP→LIN, using the PTP to cross the singular region.
- **Blending effects** — approximate positioning can accidentally route through a near-singularity that the original exact trajectory avoided.
- **Palletizing-style tools** that work near the A1 axis frequently encounter overhead singularities; process layout matters.

## Mitigation Patterns

1. **Reroute the path.** Offset the fixture so the TCP never crosses A1.
2. **Split CP motions with a PTP.** Short PTP through the singular neighborhood.
3. **Use `$SINGUL_POS[]` detection + `INTERRUPT`** to log approaches in diagnostic programs.
4. **Adjust A5 range.** If the process tolerates a small change in tool orientation, raising A5 a few degrees may avoid the wrist singularity.
5. **Pick a different robot model.** Some applications simply do not fit a serial-6 robot's workspace; consider adding an external axis.

## Common Pitfalls

- **Expecting LIN to "push through" a singularity.** It will not.
- **Assuming PTP is safe everywhere near singularities.** PTP planning is robust, but axis velocities can still spike; limit `$VEL_AXIS[i]` in sensitive regions.
- **Relying on simulation alone.** Singularity behavior depends on model-specific geometry; confirm on hardware at reduced speed.
- **Blended transitions that cross a near-singular pose.** The blended path may approach the singularity even if the programmed points avoid it.

## Worked Example

Splitting a LIN that fails wrist-singularity planning:

```krl
; Original (fails planning):
; LIN P_end

; Replacement:
LIN  P_before_singularity
PTP  P_through_singularity     ; axis-space crossing
LIN  P_after_singularity
LIN  P_end
```

Diagnostic monitoring with an interrupt:

```krl
INTERRUPT DECL 80 WHEN $SINGUL_POS[3] == TRUE DO log_wrist_singularity()
INTERRUPT ON 80
```

## Related Entries

- `ONE_status_turn` — wrist flip at A5 = 0 is tightly related to Status bit 2.
- `KUKA_REF_LIN_Motion` — LIN is the motion most affected by singularities.
- `KUKA_REF_PTP_Motion` — PTP is the usual escape hatch.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 9.8 "Singularities" (pp. 448–450).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
