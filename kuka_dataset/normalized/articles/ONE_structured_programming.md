---
id: ONE_structured_programming
title: Structured Programming in KRL (FOLDs, Naming, Modular Organization)
topic: structured_programming
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 (KSS 8.x) — Chapter 5 Structured Programming"
  tier: T1
  pages: [47, 56]
  section: "Chapter 5"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [ONE_variables_and_datatypes, ONE_subprograms_and_functions, EG_Palletizing_Skeleton]
difficulty: intermediate
tags: [structured_programming, folds, naming, program-organization]
---

# Structured Programming in KRL

## Summary

KRL programs written for maintainability follow the same discipline that applies to any industrial control software: small, single-purpose subroutines; explicit data declarations kept in `.dat` files; expressive names; and documentation in comments *and* `FOLD` markers that the teach pendant collapses into human-readable labels. The KUKA College "Robot Programming 2" course treats structured programming as a precondition for every pattern that follows in the curriculum (palletizing, interrupts, SPLINE). This article captures the conventions the workspace uses.

## File Layout

Every program module is a pair of files:

- `<module>.src` — executable code: `DEF <module>() ... END`, subroutines, `DECL` declarations local to the module.
- `<module>.dat` — data file: `DEFDAT <module> ... ENDDAT`, global or module-scoped variables, teach points, arrays.

Global programs (system-wide macros, tool data, base data) live in `$config.dat` and `$robcor.dat`. Customer-specific globals go in a named data module, not in `$config.dat`.

Name modules after the thing they do: `palletize.src`, `weld_cycle.src`, `estop_handler.src`. Avoid generic names like `main.src` or `prog1.src` outside of trivial test programs.

## Subroutines

Break work into subroutines as soon as a section repeats or a block of code has a clear single purpose:

```krl
DEF palletize_cycle()
   INI
   setup_frames()
   setup_speeds()
   home()
   WHILE cycle_count < pallet_size DO
      pick_next()
      place_at_index(cycle_count)
      cycle_count = cycle_count + 1
   ENDWHILE
   park()
END
```

Subroutines can be `LOCAL` (module-scope) or `GLOBAL` (callable from any program). Use `GLOBAL DEF` sparingly — only for primitives used from multiple programs (e.g., a common E-stop handler).

## FOLDs

`;FOLD ... ;ENDFOLD` markers collapse a block of code in the teach-pendant editor into a single readable line. Teach-pendant-generated programs are full of folds already:

```krl
;FOLD PTP HOME  Vel= 100 %  DEFAULT
   $BWDSTART = FALSE
   PDAT_ACT = PDEFAULT
   BAS(#PTP_PARAMS, 100 )
   FDAT_ACT = FHOME
   PTP XHOME
;ENDFOLD
```

Custom folds make hand-written programs pendant-friendly:

```krl
;FOLD SETUP FRAMES AND SPEEDS
   $TOOL = tool_data[1]
   $BASE = base_data[2]
   $VEL.CP = 0.4
   $ACC.CP = 2.0
;ENDFOLD
```

Keep fold labels short and descriptive. The line after `;FOLD` is what the operator sees.

## Naming

- **Variables:** `snake_case` descriptive nouns. `cycle_count`, `pallet_row`, `weld_speed`.
- **Points:** `P_` or `X` prefix, descriptive suffix. `P_pick_approach`, `XHOME`.
- **Subroutines:** `snake_case` verbs. `pick_next()`, `retract_z()`, `wait_part_present()`.
- **Flags:** `is_`, `has_`, `fault_`. `is_homed`, `has_part`, `fault_estop`.
- **Constants:** `UPPER_SNAKE_CASE` declared `CONST`. `PALLET_SIZE`.
- **Reserved prefixes:** `$` is always a system variable — never name your own that way.

## Data Discipline

- **No magic numbers.** Speeds, indices, part counts declared in the `.dat` with a name.
- **Teach points live in `.dat`.** Never in the middle of a `.src` motion instruction.
- **Reset state at program start.** `INI` + explicit frame/speed/flag setup.
- **Fail closed.** Initialize flags to the safe value (`fault = FALSE`, `is_homed = FALSE`).

## Common Pitfalls

- **Copy-pasted subroutine bodies** that drift out of sync. If two subroutines do "almost the same thing," unify them.
- **Deep FOLD nesting.** If you have three levels of fold, you have three functions that should be extracted.
- **Teach points inline.** Makes programs non-portable and hard to diff.
- **Overusing `GLOBAL DEF`.** Creates cross-module coupling; use module-local `DEF` unless the routine must be shared.
- **Relying on inherited module state.** Every `DEF` should assume nothing about `$TOOL`, `$BASE`, flags; set them.

## Related Entries

- `ONE_variables_and_datatypes` — KRL data types, declaration syntax.
- `ONE_subprograms_and_functions` — parameter passing, `IN`/`OUT`/`INOUT` modes.
- `EG_Palletizing_Skeleton` — a worked structured example.

## Citations

- KUKA College, Robot Programming 2 lecture workbook (KSS 8.x) — Chapter 5 "Structured programming" (pp. 47–56).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — file-structure conventions.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf`.
