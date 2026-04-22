---
id: KUKA_REF_INTERRUPT_DECL
title: INTERRUPT DECL Syntax (Priority, Condition, Handler)
topic: interrupts
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [625, 633]
  section: "11.14 Interrupt programming"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [ONE_interrupt_programming, EG_Interrupt_Safety_Shutdown]
difficulty: advanced
tags: [interrupts, interrupt-decl, brake, resume, handler]
---

# INTERRUPT DECL Syntax

## Summary

`INTERRUPT DECL` declares a handler subroutine that fires asynchronously when a boolean condition becomes true. An interrupt has a priority (1 highest, 128 lowest), a condition expression, and a target handler. After declaration it must be armed (`INTERRUPT ON`) to take effect. Interrupts are the primary KRL mechanism for reacting to safety inputs, end-of-process signals, E-stops, and other events that cannot be handled by polling.

## Syntax / Specification

```krl
INTERRUPT DECL <priority> WHEN <condition> DO <handler_name>()
INTERRUPT ON  [<priority>]       ; arm (specific priority, or all declared)
INTERRUPT OFF [<priority>]       ; disarm
INTERRUPT DISABLE [<priority>]   ; queue but do not fire
INTERRUPT ENABLE  [<priority>]   ; release queued interrupts
```

Inside a handler, KRL motion-control primitives are available:

```krl
BRAKE           ; decelerate along the planned path, keep axes coordinated
BRAKE F         ; apply brakes immediately (category 0-style, maximum deceleration)
RESUME          ; abort the handler; return control to the main-run backward one point
```

Priority ranges:

| Range | Usage |
|-------|-------|
| 1–39 | Reserved for KUKA system (do not use in user code) |
| 40–128 | Available to application code; 40–80 typical for safety, 81–128 for diagnostic/process |

## Semantics / Behavior

- **Declaration is static.** `INTERRUPT DECL` must appear textually in the program flow before the first motion that should be protected. Common practice: immediately after `INI` in the main program.
- **Condition is edge-triggered.** The handler fires on the FALSE→TRUE transition of the condition. If the condition is already TRUE when `INTERRUPT ON` executes, the interrupt fires immediately.
- **Priority governs preemption.** A higher-priority interrupt preempts a lower-priority handler.
- **Handler is a normal subroutine.** It can call `BRAKE`, `RESUME`, motion instructions, assignments, logging — but the body runs in interrupt context and should be short. Long handlers block other interrupts and risk cycle-time errors.
- **`BRAKE` semantics.**
  - `BRAKE` — controlled path stop: the robot decelerates along the programmed trajectory, preserving TCP path. Preferred for E-stop-equivalent safety because it is predictable and minimizes mechanical shock.
  - `BRAKE F` — hold brakes immediately (Cat 0-style). Stops fastest but the TCP leaves the programmed path and stress on gearboxes is higher. Use only where the risk justifies it.
- **`RESUME`** — terminates the handler and returns program control to one step before the interrupted motion; the interrupted motion is aborted. Typical use: after `BRAKE`, the handler sets alarms, then `RESUME` kicks program flow back to a known idle state.
- **INTERRUPT DECL inside a subroutine** — the interrupt is active while that subroutine is in the call stack; on return, it is auto-deactivated.

## Common Pitfalls

- **Declaring after the first motion.** Safety interrupt is then not armed during the initial move.
- **Using priority < 40.** Clashes with KUKA system interrupts; behavior undefined.
- **Forgetting `INTERRUPT ON`.** Declaration alone does not arm the interrupt.
- **Long handlers.** Complex logic, multi-point motions, and network I/O do not belong in an interrupt handler. Set a flag; handle details in the main program after `RESUME`.
- **Expecting `RESUME` to re-enter the handler.** It does not; it aborts and rewinds.
- **Using `BRAKE F` as a default.** Mechanical stress accumulates; use only where the hazard analysis demands it.
- **Re-declaring the same priority.** The later declaration replaces the earlier silently — easy to miss when two modules both think they own priority 5.

## Worked Example

Minimal E-stop interrupt with controlled stop and fault latch:

```krl
DEF main_prog()
   BOOL fault

   INI
   fault = FALSE

   ; Safety input on $IN[1] — goes FALSE when E-stop pressed
   INTERRUPT DECL 40 WHEN $IN[1] == FALSE DO estop_handler()
   INTERRUPT ON 40

   PTP XHOME
   LIN P1
   LIN P2

   IF fault THEN
      ; clean exit; user must clear fault before next start
      HALT
   ENDIF
END

GLOBAL DEF estop_handler()
   BRAKE           ; controlled path stop
   fault = TRUE    ; latch — handled by main after RESUME
   RESUME
END
```

See `EG_Interrupt_Safety_Shutdown` for a more complete pattern (multi-priority, light curtain + E-stop, recovery path).

## Related Entries

- `ONE_interrupt_programming` — conceptual article on interrupts, BRAKE/RESUME, advance-run interaction.
- `EG_Interrupt_Safety_Shutdown` — end-to-end worked example.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 11.14 "Interrupt programming" (pp. 625–633).
- KUKA College, Robot Programming 2 lecture — Chapter 14 "Interrupts" (T1 training).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
