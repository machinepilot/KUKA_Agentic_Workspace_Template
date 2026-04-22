---
id: ONE_variables_and_datatypes
title: KRL Variables and Data Types
topic: structured_programming
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 (KSS 8.x) — Chapter 8 Variables"
  tier: T1
  pages: [95, 115]
  section: "Chapter 8.1–8.4"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [ONE_structured_programming, ONE_subprograms_and_functions, KUKA_REF_Tool_Base_Frames]
difficulty: intermediate
tags: [variables, data-types, pos, e6pos, frame, axis, int, real, bool, char, struct]
---

# KRL Variables and Data Types

## Summary

KRL is a statically typed language with a small set of primitive types and a rich set of built-in structures for kinematic data. All variables are declared explicitly before use. Declarations may be local to a `DEF` body, module-scoped in a `.dat` file, or global. This article covers primitives, the standard kinematic structures, arrays, enumerations, and the rules for scope and initialization.

## Primitives

| Type | Range / size | Notes |
|------|--------------|-------|
| `INT` | 32-bit signed integer | Default for counters, indices. |
| `REAL` | 32-bit IEEE float | All Cartesian/axis coordinates use REAL. |
| `BOOL` | TRUE / FALSE | Use explicitly; KRL does not coerce 0/1 to BOOL. |
| `CHAR` | Single ASCII character | String handling is rare; usually used for flags. |
| `STRING` | Fixed-length character buffer | Declared with `DECL CHAR name[N]`. |

Example:

```krl
DECL INT  cycle_count = 0
DECL REAL weld_speed_mps = 0.15
DECL BOOL is_homed = FALSE
DECL CHAR program_name[20]
```

## Kinematic Structures

Built-in structs that appear everywhere in motion code:

```krl
; POS — Cartesian pose with Status/Turn
STRUC POS REAL X, Y, Z, A, B, C, INT S, T

; E6POS — Cartesian pose + 6 external axes
STRUC E6POS REAL X, Y, Z, A, B, C, INT S, T, REAL E1, E2, E3, E4, E5, E6

; FRAME — Cartesian pose without Status/Turn
STRUC FRAME REAL X, Y, Z, A, B, C

; AXIS — 6 joint angles (degrees)
STRUC AXIS REAL A1, A2, A3, A4, A5, A6

; E6AXIS — 6 joints + 6 external axes
STRUC E6AXIS REAL A1, A2, A3, A4, A5, A6, REAL E1, E2, E3, E4, E5, E6
```

Initialization and member access:

```krl
DECL POS p1 = {X 1000, Y 0, Z 500, A 0, B 90, C 0, S 2, T 2}

; Access / modify a single field
p1.Z = p1.Z + 50

; Conversion between types is explicit — not all fields carry
DECL FRAME f1
f1.X = p1.X ; ... one field at a time
```

Aggregate assignment between `POS` and `FRAME` is not direct; assign field by field (KRL is strict about struct identity).

## Arrays

One- or two-dimensional arrays of any type, declared with fixed bounds:

```krl
DECL INT counters[10]
DECL POS pallet_points[5, 6]        ; 2D array: 5 rows × 6 columns

counters[1] = 0                     ; 1-indexed
pallet_points[3, 4] = {X 100, Y 200, Z 0, A 0, B 90, C 0, S 2, T 2}
```

Arrays are **1-indexed** (not 0). The first element is `counters[1]`. This is a frequent source of off-by-one bugs for programmers coming from C or Python.

## Enums

```krl
ENUM state_t
   IDLE,
   PICKING,
   PLACING,
   FAULTED
ENDENUM

DECL state_t state = IDLE
```

Compare and assign with the `#` prefix or via the declared identifier; conventions vary — match the customer codebase style.

## Scope

Four scope tiers:

1. **Local to `DEF`** — `DECL` inside a subroutine body.
2. **Module-local (`LOCAL`)** — in the `.dat` without `GLOBAL`; accessible throughout the same module only.
3. **Global (`GLOBAL`)** — declared `GLOBAL` in a `.dat`; accessible from any module.
4. **System** — prefixed with `$`, defined by the controller. Never declare your own.

```krl
DEFDAT palletize PUBLIC
   DECL GLOBAL INT pallet_size = 60         ; global
   DECL INT current_row = 0                  ; module-local
ENDDAT
```

## Constants

Mark intent-immutable values with `CONST`:

```krl
DECL CONST INT PALLET_ROWS = 10
DECL CONST INT PALLET_COLS = 6
```

## Common Pitfalls

- **1-indexed arrays.** `for i = 0 to n-1` works but looks wrong; use `for i = 1 to n`.
- **Partial struct initialization.** `{X 100}` on a `POS` leaves other fields undefined and may cause motion errors. Always initialize every field.
- **Missing `DECL`.** Forgetting `DECL` on a local variable results in a compile error.
- **Declaring inside a loop.** All `DECL`s must precede executable statements in a `DEF` body.
- **Unit mismatches.** Linear in mm, angular in degrees, CP velocity in m/s. Look before you set.
- **Using `BOOL` as 1/0.** Writing `is_homed = 1` is invalid; use `TRUE`/`FALSE`.

## Worked Example

```krl
DEFDAT weld_cell PUBLIC
   DECL GLOBAL CONST INT MAX_RETRIES = 3
   DECL GLOBAL INT retry_count = 0

   DECL GLOBAL POS p_weld_start = {X 500, Y 0, Z 300, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS p_weld_end   = {X 700, Y 0, Z 300, A 0, B 90, C 0, S 2, T 2}

   DECL GLOBAL BOOL part_present = FALSE
ENDDAT
```

## Related Entries

- `ONE_structured_programming` — where to put these declarations.
- `ONE_subprograms_and_functions` — passing variables into subroutines.
- `KUKA_REF_Tool_Base_Frames` — `$TOOL`, `$BASE` are `FRAME` typed system variables.

## Citations

- KUKA College, Robot Programming 2 lecture workbook (KSS 8.x) — Chapter 8 "Variables and data types" (pp. 95–115).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — primitives and kinematic structs (around p. 551).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8 R3_V1_en.pdf`.
