---
id: ONE_interrupt_programming
title: "Interrupt Programming: BRAKE, RESUME, Priorities, Advance-Run Interaction"
topic: interrupts
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 (KSS 8.x) — Chapter 14 Interrupts"
  tier: T1
  pages: [209, 220]
  section: "Chapter 14"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_INTERRUPT_DECL, EG_Interrupt_Safety_Shutdown]
difficulty: advanced
tags: [interrupts, brake, resume, priority, advance-run, e-stop]
---

# Interrupt Programming: BRAKE, RESUME, Priorities, Advance-Run Interaction

## Summary

Interrupts in KRL are the primary mechanism for reacting to asynchronous events: E-stops, light curtains, part-present switches, end-of-weld signals. This article goes beyond the bare syntax (`KUKA_REF_INTERRUPT_DECL`) to cover *how to use interrupts correctly*: priority scheme, `BRAKE` vs. `BRAKE F`, `RESUME` semantics, and the interaction with the advance-run pointer that makes some interrupt patterns trickier than they look.

## Priority Scheme

KRL supports interrupt priorities 1..128. The integer specifies the priority and also the handler-slot identity — redeclaring priority 40 replaces the previous declaration.

- **1–39** — reserved for KUKA system. Do not use.
- **40–80** — application safety (E-stop, light curtain, collision detect, machine-guard).
- **81–128** — application process / diagnostic (part-present, quality sensor, log triggers).

Lower number = higher priority. A higher-priority interrupt preempts a running lower-priority handler.

## `BRAKE` Variants

- **`BRAKE`** — the controller decelerates the robot along its planned path. The TCP follows the programmed trajectory and comes to rest. Category-1-equivalent stop: predictable, minimizes mechanical shock, preserves programmed geometry.
- **`BRAKE F`** — "brake fast." Applies mechanical brakes immediately; the TCP leaves the programmed path. Category-0-equivalent stop. Use when the risk justifies the mechanical stress.
- **No `BRAKE`** — the handler runs in parallel with the motion; the robot keeps going. Useful for logging/diagnostic handlers that must not stop the process.

After `BRAKE`, motion is stopped but program state is preserved; a subsequent `RESUME` aborts the interrupted motion.

## `RESUME` Semantics

`RESUME` terminates the handler and aborts the interrupted motion, returning control to the main program at the point before the motion that was executing when the interrupt fired. In practice:

1. Controller runs handler up to `RESUME`.
2. Interrupted motion is aborted (if not already stopped by `BRAKE`).
3. Main program resumes at the statement *preceding* the interrupted motion.
4. Program continues normally.

`RESUME` cannot be used outside a handler. A handler without `RESUME` simply returns; the main program continues the interrupted motion.

## Advance-Run Interaction

KRL has an advance-run pointer that reads ahead of the current motion for planning (typical lookahead: 3). This affects interrupts:

- **Handler runs in main-run context**, not advance-run. The handler sees the program state as it was when the motion began, not when the interrupt fired.
- **Variables modified in a handler** may already be read past in advance-run. Use `WAIT FOR TRUE` or `WAIT SEC 0` before the instruction that depends on the flag — this forces advance-run to resynchronize.

```krl
INTERRUPT DECL 60 WHEN $IN[3] == TRUE DO mark_part_ok()
INTERRUPT ON 60

; Later in the main program
WAIT FOR TRUE               ; resynchronize advance-run
IF part_ok THEN
   ; safe to read here
ENDIF
```

## Decision Guide: Which Stop?

| Situation | Action |
|-----------|--------|
| E-stop button pressed by operator | `BRAKE` (controlled stop, latch fault) |
| Light curtain broken | `BRAKE` (controlled), then slow recovery |
| Collision sensor tripped (hard impact) | `BRAKE F` (fast mechanical) |
| Tool torque limit exceeded | `BRAKE` then fault analysis |
| Part-present signal arrived | No `BRAKE` — set flag, let program sync |
| End-of-weld ack | No `BRAKE` — signal next step |

## Common Pitfalls

- **Declaring an interrupt after the first motion.** There is a window where the interrupt is not armed.
- **`BRAKE F` for non-emergency stops.** Accelerates gearbox wear unnecessarily.
- **Long handlers.** Put logic in the main program; handlers set flags.
- **Forgetting `RESUME`** after `BRAKE`. Program hangs in the handler; from the operator's perspective, the robot "stopped" but the program counter is stuck.
- **Advance-run blindness.** Flag set in handler, read in main program before advance-run catches up, read returns stale value.
- **Nested interrupt logic that self-disarms.** Don't `INTERRUPT OFF` a higher-priority interrupt from a lower-priority handler.

## Worked Example

Full pattern: E-stop handler (high priority) + part-present flag handler (lower priority) with proper advance-run resync:

```krl
DEF weld_cycle()
   BOOL part_present
   BOOL fault
   INI

   part_present = FALSE
   fault        = FALSE

   INTERRUPT DECL 40 WHEN $IN[1] == FALSE DO estop_handler()
   INTERRUPT DECL 90 WHEN $IN[5] == TRUE  DO part_present_handler()
   INTERRUPT ON 40
   INTERRUPT ON 90

   PTP XHOME
   LIN P_approach
   WAIT FOR TRUE           ; resync advance-run before checking flag
   IF part_present THEN
      weld_one()
   ENDIF
   IF fault THEN
      HALT
   ENDIF
END

GLOBAL DEF estop_handler()
   BRAKE
   fault = TRUE
   RESUME
END

GLOBAL DEF part_present_handler()
   part_present = TRUE       ; no BRAKE — we don't want to stop
END
```

See `EG_Interrupt_Safety_Shutdown` for a complete production pattern with recovery path.

## Related Entries

- `KUKA_REF_INTERRUPT_DECL` — syntax reference for `INTERRUPT DECL`.
- `EG_Interrupt_Safety_Shutdown` — end-to-end example.

## Citations

- KUKA College, Robot Programming 2 lecture workbook (KSS 8.x) — Chapter 14 "Interrupts" (pp. 209–220).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — Chapter 11.14 "Interrupt programming" (pp. 625–633).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf` + `KSS_87_SI_en.pdf`.
