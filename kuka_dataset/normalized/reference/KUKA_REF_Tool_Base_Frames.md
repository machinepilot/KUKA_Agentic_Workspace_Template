---
id: KUKA_REF_Tool_Base_Frames
title: "$TOOL / $BASE Frame Assignment"
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [551, 560]
  section: "Chapter 6 Configuration; Chapter 9/11 motion preparation"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, KUKA_REF_CIRC_Motion, KUKA_REF_Velocity_Acceleration, EG_Tool_Base_Calibration_Flow]
difficulty: intermediate
tags: [frames, tool, base, ipo-mode, tcp]
---

# $TOOL / $BASE Frame Assignment

## Summary

`$TOOL` and `$BASE` are the active tool and base frames used for every Cartesian motion. `$TOOL` defines the tool center point (TCP) and tool orientation relative to the flange (A6 face). `$BASE` defines the workpiece/fixture frame relative to `$WORLD`. Every Cartesian motion is interpreted as "move the TCP defined by `$TOOL` to this target expressed in `$BASE`." Assign both explicitly at the start of every program.

## Syntax / Specification

```krl
; Assignment via pre-populated arrays (standard KUKA pattern)
$TOOL = tool_data[1]
$BASE = base_data[1]

; Direct assignment
$TOOL = {X 0, Y 0, Z 120, A 0, B 0, C 0}
$BASE = {X 1000, Y 500, Z 0, A 0, B 0, C 0}

; Interpolation mode — CP motion
$IPO_MODE = #BASE              ; TCP follows $BASE (standard)
$IPO_MODE = #TCP               ; Base frame moves relative to TCP (mounted-part workflow)
```

Associated system arrays in `$config.dat` / `$machine.dat`:

- `tool_data[1..16]` — up to 16 named tool frames.
- `base_data[1..32]` — up to 32 named base frames.
- `load_data[1..16]` — tool load data (mass, center-of-mass, inertia) paired with tools.

## Semantics / Behavior

- **`$TOOL` interpretation.** Six values: `X/Y/Z` offset of the TCP from the A6 flange, `A/B/C` (Z-Y-X Euler) orientation of the tool frame. In millimeters and degrees.
- **`$BASE` interpretation.** Six values expressing the base frame relative to `$WORLD`. Cartesian targets in motion instructions are implicitly relative to `$BASE`.
- **Load must match tool.** `$LOAD` (mass, CoM, inertia tensor) should be set to the physically mounted tool's load data when `$TOOL` is changed. Wrong load values degrade trajectory accuracy, cause torque faults, and can damage gearboxes.
- **`#BASE` vs. `#TCP` IPO modes.** The common case is `#BASE`: the tool moves, the base stays. For part-in-gripper processes (stationary torch or dispenser with the workpiece carried by the robot), use `#TCP`: the external tool is then expressed in `$TOOL`, and the workpiece frame becomes `$BASE` — terminology is inverted but the math is symmetric.
- **Changing frames mid-program.** Assign `$TOOL` / `$BASE` only during stationary periods; assigning during a blended motion yields undefined path. Put assignments between `C_FINE` motions or at program start.
- **Persistence.** `$TOOL` and `$BASE` are system variables in `$robcor.dat`; they survive program end. Every program prologue should re-assert them.

## Common Pitfalls

- **Forgetting to set `$LOAD`** when `$TOOL` changes — most common cause of "following error" stops on heavy tools.
- **Mixing up the index** — `tool_data[5]` vs. `$TOOL = 5` (the latter is a syntax error; `$TOOL` takes a `FRAME`).
- **Using absolute `$WORLD` coordinates** to "save time" — points become non-portable across cells.
- **Calibrating `$BASE` with the wrong tool** — tool and base calibration must be consistent; recalibrate base after any tool change.
- **Assuming `INI` sets `$TOOL` / `$BASE`** — the default `INI` macro does not guarantee it; always assign explicitly.
- **Switching `$IPO_MODE` inside a `SPLINE` block** — not supported; set it before the block.

## Worked Example

Standard prologue for any program that will do Cartesian motion:

```krl
DEF cartesian_prologue()
   INI

   ; --- Frames ---
   $TOOL = tool_data[1]         ; gripper, calibrated 4-point
   $LOAD = load_data[1]         ; mass + CoM of gripper + typical workpiece
   $BASE = base_data[2]         ; "pick fixture" calibrated 3-point
   $IPO_MODE = #BASE

   ; --- Speeds (see KUKA_REF_Velocity_Acceleration) ---
   $VEL.CP = 0.3
   $ACC.CP = 2.0

   ; Now Cartesian motion is well-defined
   PTP XHOME
   LIN P_above_pick
   LIN P_pick
END
```

See `EG_Tool_Base_Calibration_Flow` for the procedure used to populate `tool_data[i]` / `base_data[i]` interactively on the teach pendant.

## Related Entries

- `EG_Tool_Base_Calibration_Flow` — 4-point tool, 3-point base, XYZ-2-point, ABC-2-point procedures.
- `KUKA_REF_Velocity_Acceleration` — the CP velocity variables that depend on a valid `$TOOL`.
- `KUKA_REF_PTP_Motion`, `KUKA_REF_LIN_Motion`, `KUKA_REF_CIRC_Motion` — all Cartesian motions consume `$TOOL` / `$BASE`.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 6 "Configuration" (tool and base calibration); Chapter 11 "Motion programming" — assignment conventions at top of example programs (p. ~551).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`. Summary in our own words.
