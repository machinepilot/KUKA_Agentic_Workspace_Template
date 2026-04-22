---
id: EG_Interrupt_Safety_Shutdown
title: Interrupt + BRAKE Safety Shutdown Example
topic: interrupts
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 Exercises Ch 14: Interrupt + BRAKE"
  tier: T1
  pages: [73, 78]
  section: "Exercise 14"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_INTERRUPT_DECL, ONE_interrupt_programming]
difficulty: advanced
tags: [example, interrupt, brake, safety, shutdown, recovery]
---

# Interrupt + BRAKE Safety Shutdown Example

## Summary

A worked example of a production-grade interrupt pattern: two simultaneous safety inputs (E-stop and light curtain), controlled stop via `BRAKE`, explicit fault latch, and a deliberate recovery path that requires operator acknowledgment before resuming work. The pattern is built on the P2 course exercise but extended for cell-level realism — distinct priorities, signal aliases via `SIGNAL`, and an operator-ack loop for safe restart.

## Files

- `safety_shutdown.src` — main program, handlers.
- `safety_shutdown.dat` — signal aliases, state.
- `$config.dat` — `SIGNAL` declarations (shown in the example comments; live in the standard file).

## Signal Aliases (in `$config.dat`)

```krl
SIGNAL sig_estop       $IN[1]       ; wired NC — FALSE when pressed
SIGNAL sig_light_curtn $IN[2]       ; wired NC — FALSE when broken
SIGNAL sig_reset       $IN[3]       ; TRUE when operator presses Reset
SIGNAL sig_fault_lamp  $OUT[10]     ; fault indicator
```

## `safety_shutdown.dat`

```krl
DEFDAT safety_shutdown PUBLIC
   DECL GLOBAL BOOL fault_estop       = FALSE
   DECL GLOBAL BOOL fault_lightcurtn  = FALSE
   DECL GLOBAL BOOL cycle_ok          = TRUE
ENDDAT
```

## `safety_shutdown.src`

```krl
&ACCESS RVP
DEF safety_shutdown()
   INI

   fault_estop      = FALSE
   fault_lightcurtn = FALSE
   cycle_ok         = TRUE

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   $VEL.CP = 0.3
   $ACC.CP = 1.5

   ; Declare BEFORE first motion — per KUKA_REF_INTERRUPT_DECL
   INTERRUPT DECL 40 WHEN sig_estop == FALSE       DO estop_handler()
   INTERRUPT DECL 45 WHEN sig_light_curtn == FALSE DO lightcurtn_handler()
   INTERRUPT ON 40
   INTERRUPT ON 45

   WHILE cycle_ok DO
      run_one_cycle()

      IF fault_estop OR fault_lightcurtn THEN
         operator_ack_and_recover()
      ENDIF
   ENDWHILE

   HALT
END


;FOLD RUN ONE CYCLE
DEF run_one_cycle()
   PTP XHOME C_PTP
   LIN P_work_start
   LIN P_work_end
   PTP XHOME C_PTP
END
;ENDFOLD


;FOLD OPERATOR ACK AND RECOVER
DEF operator_ack_and_recover()
   ; Move to a safe pose, latch fault lamp, wait for reset
   sig_fault_lamp = TRUE

   ; Wait for operator: both faults cleared AND reset pressed
   WAIT FOR (sig_estop == TRUE) AND (sig_light_curtn == TRUE) AND (sig_reset == TRUE)

   ; Operator confirms clearance — zero fault flags, turn lamp off
   fault_estop       = FALSE
   fault_lightcurtn  = FALSE
   sig_fault_lamp    = FALSE

   ; Re-home before resuming the cycle
   PTP XHOME
END
;ENDFOLD


GLOBAL DEF estop_handler()
   BRAKE                       ; controlled path stop
   fault_estop = TRUE
   sig_fault_lamp = TRUE
   RESUME
END


GLOBAL DEF lightcurtn_handler()
   BRAKE                       ; controlled stop — light curtain is cat 1
   fault_lightcurtn = TRUE
   sig_fault_lamp = TRUE
   RESUME
END
```

## Design Notes

- **Two priorities, not one.** E-stop at 40 preempts light-curtain at 45; the logic is simple and the priority ordering is explicit.
- **Controlled stop (`BRAKE`) not fast stop (`BRAKE F`).** Both faults are Category 1 events. Use `BRAKE F` only where a hazard analysis demands it.
- **Flags latched, lamp latched.** A fleeting E-stop tap still requires explicit reset — no auto-recovery.
- **Operator ack requires all conditions simultaneously.** E-stop released, curtain clear, reset pressed. Prevents a reset from being held and masking a still-broken curtain.
- **Re-home before resuming.** Never resume mid-motion; bring the robot to a known reference point first.

## What Is *Not* in This Example

- **Safety-rated stop.** The `BRAKE` here is a KRL software stop; it is not a substitute for the hardware safety circuit. The real safety-rated stop happens via the KUKA safety controller (KSS 8.x safety chapter); this KRL pattern is for program-level recovery on top of hardware safety.
- **SafeOperation reduced-speed logic.** If the cell uses SafeOperation, zones/speeds are configured separately; this example is independent.
- **Diagnostic logging.** A real cell would log `$TIMER[]`, position at fault, and user id. Added in a production variant.

## Related Entries

- `KUKA_REF_INTERRUPT_DECL` — syntax reference.
- `ONE_interrupt_programming` — concepts: advance-run, priority, BRAKE variants.
- `KUKA_SAFETY_Stop_Categories` — hardware stop categories that this KRL pattern complements.
- `KUKA_SAFETY_Operating_Modes` — mode-dependent speed caps.

## Citations

- KUKA College, Robot Programming 2 Exercise Book — Chapter 14 exercise (pp. 73–78).
- KUKA College, Robot Programming 2 lecture — Chapter 14.4 (p. 220).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — Chapter 11.14 (pp. 625–633).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf`.
