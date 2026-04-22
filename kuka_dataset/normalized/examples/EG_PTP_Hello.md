---
id: EG_PTP_Hello
title: Minimal PTP Hello Example
topic: motion
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.3, KSS 8.6]
language: KRL
source:
  type: generated
  title: "KUKA Agentic Workspace Template — seed example"
  tier: generated
  pages: null
  section: "template scaffold"
  access_date: "2026-04-21"
  url: null
license: open
revision_date: "2026-04-21"
related: [KUKA_REF_PTP_Motion, ONE_motion_termination]
difficulty: beginner
tags: [motion, ptp, example, beginner, template]
---

# Minimal PTP Hello Example

## Summary

A minimal, complete KRL program that initializes the robot, declares an E-stop interrupt, moves to a home position via PTP, and returns. This example is a seed placeholder shipped with the template — it exists so the dataset is non-empty on day one and so tests of the retrieval pipeline (`kuka_knowledge.search`) have something to return. Ingest real content to replace/augment.

## Syntax / Specification

The PTP instruction moves all axes simultaneously to a target. Travel time is determined by the slowest axis; path shape is not specified (axis-interpolated). Use PTP for rapid moves when path shape does not matter.

## Worked Example

File: `hello.src`

```krl
DEF hello()
   ; -------------------------------------------------------------
   ; Minimal Hello program. Move to HOME via PTP.
   ;   Dataset: EG_PTP_Hello
   ;   See also: KUKA_REF_PTP_Motion, ONE_motion_termination
   ; -------------------------------------------------------------

   INI

   ; --- Interrupts (declared before first motion) ---
   INTERRUPT DECL 3 WHEN $IN[1]==FALSE DO estop_handler()
   INTERRUPT ON 3

   ; --- Frame setup ---
   $TOOL = tool_data[1]       ; gripper tool
   $BASE = base_data[1]       ; cell base
   $IPO_MODE = #BASE

   ; --- Speed setup ---
   $VEL_AXIS[1] = 50          ; axis 1 velocity percentage
   $VEL_AXIS[2] = 50
   $VEL_AXIS[3] = 50
   $VEL_AXIS[4] = 50
   $VEL_AXIS[5] = 50
   $VEL_AXIS[6] = 50
   $ACC_AXIS[1] = 50

   ; --- Motion ---
   PTP XHOME                  ; declared globally in $config.dat
   WAIT SEC 0.5
   PTP XHOME                  ; return to home

END
```

Companion interrupt handler (`estop_handler.src`, minimal):

```krl
GLOBAL DEF estop_handler()
   ; E-stop handler. Bring the robot to rest and latch a fault.
   BRAKE                      ; controlled stop (Category 1)
   ; Customer-specific: set alarm, turn off end effector, etc.
END
```

## Semantics / Behavior

- `INI` macro (from `$config.dat`) initializes default frames, velocities, and interrupt state.
- `INTERRUPT DECL` before first motion is mandatory for safety-relevant interrupts. Priority 3 is a common house convention for E-stop — confirm per customer.
- `$TOOL`, `$BASE`, `$IPO_MODE` set explicitly — never rely on inherited state.
- `$VEL_AXIS[]` sets axis-wise velocity percentage for PTP. Cartesian motion uses `$VEL.CP`.
- PTP is asynchronous: all axes finish at the same time; the slowest axis dominates cycle time.
- `WAIT SEC` is a simple timed wait; for signal-driven waits prefer `WAIT FOR <expr>` with a timeout interrupt.

## Common Pitfalls

- Omitting `$TOOL` / `$BASE` setup — uses whatever inherited state exists, unsafe.
- Declaring `INTERRUPT DECL` after first motion — window where interrupt is not armed.
- Using `$OV_PRO` overrides in program code — removes human operator speed control. Disallowed by QA.
- Hard-coded `$IN[1]` / `$OUT[n]` — should be aliased via `SIGNAL` in `$config.dat`.

## Related Entries

- `KUKA_REF_PTP_Motion` — full PTP reference (populate via ingestion).
- `ONE_motion_termination` — termination types (C_PTP, C_FINE, etc.).

## Citations

- Source: KUKA Agentic Workspace Template seed (generated). Replace with a vendor-manual-backed example once ingestion runs.

## Provenance

Produced by the template scaffold for initial testing of the retrieval pipeline. Replace with ingested content as soon as PDFs are normalized.
