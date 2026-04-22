---
id: EG_Collision_Detection_Setup
title: Collision Detection Setup for Jog and Program Mode
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 Exercises Ch 4: Collision Detection"
  tier: T1
  pages: [19, 22]
  section: "Exercise 4"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_Stop_Categories, KUKA_REF_INTERRUPT_DECL]
difficulty: intermediate
tags: [example, collision-detection, torque-monitoring, safety, tuning]
---

# Collision Detection Setup for Jog and Program Mode

## Summary

Collision detection uses the robot's axis torque model to detect unexpected resistance — a crash into a fixture, an unexpected workpiece, an operator error. On KR C4 / KR C5 the feature is configured per program and per jog mode, with separate thresholds because motion profiles differ. This example walks through the pendant configuration and the KRL code that enables / disables monitoring and handles a collision event.

## Concept

The controller maintains an internal dynamic model of the robot (mass, inertia, joint friction). For each commanded motion it predicts axis torques. The *residual* — actual torque minus predicted — indicates an unmodeled load. A residual that exceeds the per-axis threshold for the configured duration trips the collision detector, which raises a stop condition and (optionally) fires a user interrupt.

## Pendant Configuration

On KR C5 / KRC4 pendants the menu path is typically `Configure → Miscellaneous → Collision detection` (exact path varies by KSS revision):

1. **Enable monitoring.** Toggle on.
2. **Per-axis tolerances.** Values are percentages (default 200 = baseline tolerance). Lowering reduces false positives but increases sensitivity.
3. **Program-mode threshold.** Separate tolerance block for program execution.
4. **Jog-mode threshold.** Usually *higher* (less sensitive) because jog is operator-driven and deliberately involves interaction.
5. **Response mode.** Stop only / stop + interrupt / log only.

After initial set-up, run the program at normal speed in a crash-free cycle and adjust thresholds upward until false positives disappear, then down ~10% as safety margin.

## KRL Interaction

Monitoring is on by default once configured. In code you can enable / disable it temporarily and handle the event:

```krl
; Disable during a deliberate contact move (e.g., probing, press-fit)
$COLL_ENABLE = FALSE
LIN P_press_contact
$COLL_ENABLE = TRUE

; Raise an interrupt on collision
INTERRUPT DECL 50 WHEN $COLLISION_DETECT == TRUE DO collision_handler()
INTERRUPT ON 50

; Handler
GLOBAL DEF collision_handler()
   BRAKE                       ; controlled stop
   fault_collision = TRUE
   RESUME
END
```

Variable names (`$COLL_ENABLE`, `$COLLISION_DETECT`) are representative; confirm against your KSS version's system-variable reference.

## Tuning Procedure

1. With default thresholds, run the program in T1 at 10% override for one cycle.
2. Record any false-positive stops (check message log for axis + torque value).
3. If false positives, raise that axis's threshold by 20% and retry.
4. After a clean T1 cycle at 100%, repeat in T2/AUT at program speed.
5. Lower thresholds 10% at a time until a deliberate light touch at reduced speed reliably triggers detection — that's the working margin.
6. Document thresholds in the cell runbook; record why each axis has a non-default value.

## Jog-Mode vs. Program-Mode

- **Jog.** Operator moves the robot manually; accelerations and loads vary. Thresholds higher to avoid nuisance stops when contacting known fixtures during teach.
- **Program.** Motions are deterministic; residuals should be small. Thresholds can be much tighter.

Never enable identical thresholds in both modes — the program-mode sensitivity that catches a crash will trip constantly during teach.

## Common Pitfalls

- **Thresholds left at default.** Either too sensitive (nuisance trips) or too loose (missed crashes).
- **Tuning with the wrong load.** Ensure `$LOAD` matches the physically mounted tool and workpiece; bad load data makes the torque model wrong and yields false positives.
- **Disabling monitoring and forgetting to re-enable.** Use a `TRY ... ENDTRY` pattern or a deliberate `$COLL_ENABLE = TRUE` at the end of the disabled section.
- **Tuning in an empty cell.** Residuals depend on the process. Tune in the actual operating configuration.
- **Mistaking collision detection for safety-rated stop.** Collision detection is a KRL feature, not SafeOperation-rated. For safety-rated response, you must still have hardware safety signals + proper safety configuration.

## Related Entries

- `KUKA_SAFETY_Stop_Categories` — stop categories, which collision-stop implements at category 1.
- `KUKA_REF_INTERRUPT_DECL` — interrupt syntax used by the handler.

## Citations

- KUKA College, Robot Programming 2 Exercise Book — Chapter 4 (pp. 19–22).
- KUKA College, Robot Programming 2 lecture — Chapter 4 "Collision detection".
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — collision monitoring system variables.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf`.
