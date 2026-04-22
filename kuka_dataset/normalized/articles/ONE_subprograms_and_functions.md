---
id: ONE_subprograms_and_functions
title: "Subprograms and Functions in KRL: IN / OUT / INOUT, DEFFCT"
topic: structured_programming
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 (KSS 8.x) — Chapter 9 Subprograms"
  tier: T1
  pages: [133, 147]
  section: "Chapter 9"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [ONE_structured_programming, ONE_variables_and_datatypes]
difficulty: intermediate
tags: [subprograms, functions, parameters, deffct, global, local]
---

# Subprograms and Functions in KRL: IN / OUT / INOUT, DEFFCT

## Summary

KRL distinguishes **subprograms** (`DEF ... END`, no return value) from **functions** (`DEFFCT <type> ... ENDFCT`, return value). Both accept parameters with an explicit direction — `IN`, `OUT`, or `INOUT` — that controls whether the callee sees a copy, writes back to the caller, or both. Getting parameter direction right is the difference between a function that cleanly returns a value and a subprogram that mutates its caller's state in surprising ways.

## Subprograms (DEF)

```krl
DEF move_to_home()
   $TOOL = tool_data[1]
   $BASE = base_data[1]
   PTP XHOME
END

DEF pick_at(p : IN POS, retract_mm : IN REAL)
   LIN p
   WAIT SEC 0.2
   LIN {X 0, Y 0, Z retract_mm, A 0, B 0, C 0} :-> p      ; pseudo-offset form varies
END
```

- `IN` — parameter passed by value; callee has a local copy.
- `OUT` — callee assigns; caller receives the value on return. Initial value not visible in callee.
- `INOUT` — bidirectional; callee sees caller's value and can modify it.

Call site:

```krl
pick_at(p_pick_1, 150)
```

`OUT` and `INOUT` parameters must be writable variables at the call site (not literals).

## Functions (DEFFCT)

```krl
DEFFCT INT count_parts(ch : IN INT)
   DECL INT total
   total = part_counters[ch]
   RETURN total
ENDFCT

; Call
DECL INT n
n = count_parts(3)
```

A function must return a typed value via `RETURN`. The return type goes on the `DEFFCT` line.

## LOCAL vs. GLOBAL

- `DEF`/`DEFFCT` without qualifier — local to the `.src` module.
- `GLOBAL DEF`/`GLOBAL DEFFCT` — callable from any program.

Global subroutines should be few and obvious: common interrupt handlers, error loggers, a shared home routine. Anything cell-specific stays local.

## Parameter Types

Parameters can be any KRL type: primitives, structs (`POS`, `FRAME`, `AXIS`, etc.), enums. Arrays must be passed by reference (essentially `INOUT` semantics); pass the array name and the callee writes through.

```krl
DEF zero_array(arr : OUT INT[])
   DECL INT i
   FOR i = 1 TO 10
      arr[i] = 0
   ENDFOR
END
```

## Scope Inside Subroutines

- Declarations inside a `DEF` are local and must precede executable statements.
- The callee does not see the caller's local variables unless they are passed as parameters.
- System variables (`$TOOL`, `$BASE`, `$VEL.CP`, etc.) are shared; changes persist across the call boundary. This is why every motion-performing subroutine should restate `$TOOL`/`$BASE` if it cannot trust the caller.

## Common Pitfalls

- **Using `IN` when you meant `INOUT`.** The callee modifies its local copy; the caller sees nothing.
- **Returning large structs by value.** Expensive and often unnecessary — pass `OUT POS` instead.
- **Global subroutines mutating global state.** Invisible coupling. Prefer passing state explicitly.
- **Nested functions.** KRL does not nest function definitions; all subroutines are peers.
- **Forgetting `ENDFCT`.** Compile error; `END` applies only to `DEF`.
- **Omitting parameter type.** `pick_at(p, r)` without `: IN POS, : IN REAL` is a compile error.
- **System variable leaks.** Changing `$OV_PRO` or `$ACC.CP` inside a helper and forgetting to restore it.

## Worked Example

A module that exposes a safe "go to a taught point with check" function:

```krl
&ACCESS RVO
DEF safe_moves()
   ; empty main — just exports subroutines
END

GLOBAL DEF go_to(target : IN POS, use_blend : IN BOOL)
   IF use_blend THEN
      LIN target C_DIS
   ELSE
      LIN target
   ENDIF
END

GLOBAL DEFFCT BOOL is_at(target : IN POS, tol_mm : IN REAL)
   DECL REAL dx, dy, dz
   dx = $POS_ACT.X - target.X
   dy = $POS_ACT.Y - target.Y
   dz = $POS_ACT.Z - target.Z
   IF SQRT(dx*dx + dy*dy + dz*dz) < tol_mm THEN
      RETURN TRUE
   ENDIF
   RETURN FALSE
ENDFCT
```

## Related Entries

- `ONE_structured_programming` — when to extract a subroutine.
- `ONE_variables_and_datatypes` — declaration syntax used in parameters.

## Citations

- KUKA College, Robot Programming 2 lecture workbook (KSS 8.x) — Chapter 9 "Subprograms" (pp. 133–147).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — `DEF`/`DEFFCT` syntax (pp. 618–624).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf`.
