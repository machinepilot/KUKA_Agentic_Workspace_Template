---
id: EG_Tool_Base_Calibration_Flow
title: Tool and Base Calibration Procedure (4-Point / 3-Point / XYZ-Reference)
topic: mastering
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: N/A
source:
  type: training
  title: "KUKA College — Robot Programming 2 Exercises Ch 3: Tool + Base Calibration"
  tier: T1
  pages: [9, 18]
  section: "Exercise 3"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_Tool_Base_Frames, ONE_structured_programming]
difficulty: intermediate
tags: [example, calibration, tool, base, tcp, 4-point, 3-point, xyz-2-point, abc-2-point]
---

# Tool and Base Calibration Procedure

## Summary

End-to-end procedure for calibrating `$TOOL` (tool frame / TCP) and `$BASE` (work-piece frame) on a KR C4 / KR C5 controller using the teach pendant. Covers: 4-point XYZ method for TCP position, ABC 2-point method for TCP orientation, 3-point method for base frame, and the companion XYZ-reference method for pre-measured fixtures. Presented as a flow the integrator follows step-by-step; outputs populate `tool_data[i]` and `base_data[i]` arrays used by every motion program.

## Prerequisites

- Robot mastered (axis encoders referenced via EMT).
- Tool physically mounted on flange. For TCP calibration, select a sharp, rigid feature on the tool (weld tip, probe stylus, gripper center pin) as the nominal TCP.
- Fixed reference point available in the cell — e.g., a precision cone mounted on a pedestal. The reference must be rigid; any flex during calibration shows up as TCP error.
- Operating mode T1 (manual reduced).

## Tool Calibration

### 4-Point XYZ Method (TCP position)

Goal: determine the (X, Y, Z) offset of the TCP from the A6 flange.

1. On the pendant, navigate `Start-up → Measure → Tool → XYZ 4-Point`.
2. Select the tool number (1..16). Give it a name (`gripper_A`).
3. Jog the robot so the TCP touches the reference point with the tool in an approach pose.
4. Teach Point 1.
5. Repeat 3–4 three more times, each time from a visibly different orientation (rotate wrist ~ 45–60° between points). The four orientations must span a 3D cone; coplanar points yield a singular solution.
6. The pendant computes the TCP offset by solving for the common point in flange coordinates. Accept if the residual error is below tolerance (typical: ≤ 1 mm for a well-mastered robot).
7. Save to `tool_data[i]`.

Result: `tool_data[i].X/Y/Z` populated. Orientation (A/B/C) is still default (zero); do ABC next.

### ABC 2-Point or ABC World Method (TCP orientation)

Two methods; pick the one your tool geometry supports.

**ABC 2-Point:**

1. Navigate `Measure → Tool → ABC 2-Point`.
2. With the TCP held at the reference point, orient the tool so that the tool's intended +X axis points toward a second reference feature. Teach.
3. Move the tool so its intended +X-Y plane is visible (a co-planar feature). Teach.
4. Pendant computes A/B/C (tool rotation relative to flange).

**ABC World:**

1. Navigate `Measure → Tool → ABC World`.
2. Orient the tool so that the tool's coordinate axes are parallel to world-frame axes (visually, or using a jig).
3. Teach.
4. Pendant computes A/B/C directly.

### Load Data

Pair each tool with its load:

1. `Start-up → Measure → Tool → Tool load data`.
2. Enter mass (kg), center of mass offset from the flange (X, Y, Z), and principal moments of inertia if known.
3. Save to `load_data[i]` — same index as the tool.
4. Assign in code: `$LOAD = load_data[i]` when `$TOOL = tool_data[i]`.

## Base Calibration

### 3-Point Method (most common)

Goal: define the workpiece frame origin, X direction, and XY plane.

1. Navigate `Measure → Base → 3-Point`.
2. Select the base number (1..32). Name it (`fixture_A`).
3. Jog TCP to the origin of the new base frame (corner of the fixture, fiducial hole). Teach Point 1.
4. Jog TCP along the intended +X direction, far enough that the line is well-defined (≥ 100 mm). Teach Point 2.
5. Jog TCP into the +XY plane (any point on the +Y side of the X axis). Teach Point 3.
6. Pendant computes the frame and saves to `base_data[i]`.

### XYZ-Reference Method (pre-measured fixture)

If the fixture's location relative to an existing base is known (CAD or laser-measured):

1. `Measure → Base → Indirect`.
2. Enter reference base number.
3. Enter the known offset (translation + A/B/C rotation).
4. Save.

## Verification

Always verify before committing:

1. Set `$TOOL = tool_data[i]` and `$BASE = base_data[j]` in a test program.
2. Jog the TCP to a known point on the fixture using Cartesian jog (`Cartesian` mode).
3. Rotate the tool about the TCP using `Tool` jog mode — the TCP should stay on the reference point; if it wanders, recalibrate.
4. Move along `$BASE` +X; the TCP should slide along the fixture's +X edge.

## Common Pitfalls

- **Coplanar XYZ points.** Pendant accepts it but the solution is poor. Use visibly different wrist orientations.
- **Load mismatch.** Calibrating a tool but forgetting to pair its load data; trajectories accurate, dynamics wrong.
- **Fixture flex.** A wobbly calibration block propagates error into every program. Use a rigid reference.
- **Confusing tool index with program.** `$TOOL = 3` is not legal; use `$TOOL = tool_data[3]`.
- **Recalibrating base without re-teaching points.** Points stored against the old base are now invalid.
- **Skipping verification.** A few minutes of jog test catches gross errors before a full cycle damages parts.

## Related Entries

- `KUKA_REF_Tool_Base_Frames` — system-variable reference.
- `ONE_structured_programming` — where to assign `$TOOL` / `$BASE` in program code.

## Citations

- KUKA College, Robot Programming 2 Exercise Book — Chapter 3 (pp. 9–18).
- KUKA College, Robot Programming 2 lecture — Chapter 3.
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — Chapter 6 "Configuration / Measurement".

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf` + `KSS_87_SI_en.pdf`.
