---
id: EG_Palletizing_Skeleton
title: Palletizing Program Skeleton (Structured KRL)
topic: palletizing
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: training
  title: "KUKA College — Robot Programming 2 Exercises Ch 8: Structured Palletizing"
  tier: T1
  pages: [31, 44]
  section: "Exercise 8"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [ONE_structured_programming, ONE_variables_and_datatypes, ONE_subprograms_and_functions, KUKA_REF_PTP_Motion, KUKA_REF_LIN_Motion, EG_PTP_Hello]
difficulty: intermediate
tags: [example, palletizing, structured_programming, pattern, pick-and-place]
---

# Palletizing Program Skeleton (Structured KRL)

## Summary

A reusable structured-KRL skeleton for a rectangular-pattern palletizing job: pick from a fixed feed location, place into an M-row × N-column pattern, index position, detect full pallet, return home. This skeleton shows how to combine module-local data, a global index function, and a main loop that delegates to single-purpose subroutines. Use as a starting point when scaffolding a new palletizing cell.

## Files

Two files per the workspace convention:

- `palletize.src` — executable program and module-local subroutines.
- `palletize.dat` — module data: pattern dimensions, teach points, state flags.

## `palletize.dat`

```krl
DEFDAT palletize PUBLIC
   ; --- Pattern geometry (module-local data) ---
   DECL GLOBAL CONST INT PALLET_ROWS = 5
   DECL GLOBAL CONST INT PALLET_COLS = 6
   DECL GLOBAL CONST REAL ROW_PITCH_MM = 120.0
   DECL GLOBAL CONST REAL COL_PITCH_MM = 100.0
   DECL GLOBAL CONST REAL LAYER_HEIGHT_MM = 40.0

   ; --- Teach points ---
   DECL GLOBAL POS p_home           = {X 1000, Y   0, Z 1500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS p_feed_approach  = {X  400, Y   0, Z  500, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS p_feed_pick      = {X  400, Y   0, Z  300, A 0, B 90, C 0, S 2, T 2}
   DECL GLOBAL POS p_pallet_origin  = {X 1200, Y 800, Z  400, A 0, B 90, C 0, S 2, T 2}  ; row 1, col 1 approach

   ; --- State ---
   DECL GLOBAL INT  current_index = 0         ; 0..ROWS*COLS-1
   DECL GLOBAL BOOL pallet_full   = FALSE
   DECL GLOBAL BOOL fault         = FALSE
ENDDAT
```

## `palletize.src`

```krl
&ACCESS RVP
DEF palletize()
   INI

   setup_frames_and_speeds()
   setup_interrupts()

   ; Recover state if a previous run left a partial pallet
   IF current_index >= PALLET_ROWS * PALLET_COLS THEN
      pallet_full = TRUE
   ENDIF

   WHILE NOT pallet_full AND NOT fault DO
      wait_for_feed_part()
      pick_from_feed()
      place_at_pallet(current_index)
      current_index = current_index + 1
      IF current_index >= PALLET_ROWS * PALLET_COLS THEN
         pallet_full = TRUE
      ENDIF
   ENDWHILE

   park()

   IF fault THEN
      HALT
   ENDIF
END


;FOLD SETUP FRAMES AND SPEEDS
DEF setup_frames_and_speeds()
   $TOOL = tool_data[1]          ; gripper
   $LOAD = load_data[1]
   $BASE = base_data[2]          ; pallet base
   $IPO_MODE = #BASE

   $VEL_AXIS[1] = 60
   $VEL_AXIS[2] = 60
   $VEL_AXIS[3] = 60
   $VEL_AXIS[4] = 60
   $VEL_AXIS[5] = 60
   $VEL_AXIS[6] = 60
   $ACC_AXIS[1] = 75

   $VEL.CP    = 0.4
   $ACC.CP    = 2.0
   $APO.CDIS  = 50
   $APO.CPTP  = 75
END
;ENDFOLD


;FOLD SETUP INTERRUPTS
DEF setup_interrupts()
   INTERRUPT DECL 40 WHEN $IN[1] == FALSE DO estop_handler()
   INTERRUPT ON 40
END
;ENDFOLD


;FOLD WAIT FOR FEED PART
DEF wait_for_feed_part()
   WAIT FOR $IN[10] == TRUE      ; feed sensor; alias via SIGNAL in $config.dat
END
;ENDFOLD


;FOLD PICK FROM FEED
DEF pick_from_feed()
   PTP p_feed_approach C_PTP
   LIN p_feed_pick
   $OUT[1] = TRUE                ; gripper close
   WAIT SEC 0.15
   LIN p_feed_approach C_DIS
END
;ENDFOLD


;FOLD PLACE AT PALLET
DEF place_at_pallet(index : IN INT)
   DECL INT row, col
   DECL POS p_place_approach, p_place

   row = index / PALLET_COLS     ; 0..ROWS-1
   col = index - row * PALLET_COLS

   p_place_approach = pallet_offset(row, col, LAYER_HEIGHT_MM + 200.0)
   p_place          = pallet_offset(row, col, LAYER_HEIGHT_MM)

   PTP p_place_approach C_PTP
   LIN p_place
   $OUT[1] = FALSE               ; gripper open
   WAIT SEC 0.15
   LIN p_place_approach C_DIS
END
;ENDFOLD


;FOLD PALLET OFFSET (function)
DEFFCT POS pallet_offset(row : IN INT, col : IN INT, z_mm : IN REAL)
   DECL POS p
   p     = p_pallet_origin
   p.X   = p_pallet_origin.X + row * ROW_PITCH_MM
   p.Y   = p_pallet_origin.Y + col * COL_PITCH_MM
   p.Z   = p_pallet_origin.Z + z_mm
   RETURN p
ENDFCT
;ENDFOLD


;FOLD PARK
DEF park()
   PTP p_home
END
;ENDFOLD


GLOBAL DEF estop_handler()
   BRAKE
   fault = TRUE
   RESUME
END
```

## Design Notes

- **Pattern math is a function.** `pallet_offset` returns a fully-formed `POS`; the caller does not manipulate coordinates directly.
- **One subroutine per action.** `pick_from_feed`, `place_at_pallet`, `park` — readable and individually testable.
- **State is persistent.** `current_index` lives in `.dat`; a restart after a fault resumes where the pallet was.
- **Gripper signals are hardware-aliased.** Production code should replace `$OUT[1]` with a `SIGNAL` alias declared in `$config.dat`.
- **Fault latched, not quietly swallowed.** Main loop checks `fault` and halts.

## Common Pitfalls

- **Teach points in `.src`.** Keep them in `.dat` as shown; make the program portable across shifts.
- **Rebuilding the POS from scratch in `pallet_offset`.** The example copies from `p_pallet_origin` to preserve S/T and A/B/C.
- **Forgetting `C_PTP` on `p_place_approach`.** Un-blended PTP transitions add cycle time.
- **Using `$OV_PRO`** to slow the program globally. Use `$VEL.CP` or adjust `$VEL_AXIS[]`.

## Related Entries

- `ONE_structured_programming`, `ONE_subprograms_and_functions`, `ONE_variables_and_datatypes`.
- `KUKA_REF_PTP_Motion`, `KUKA_REF_LIN_Motion`, `ONE_motion_termination`.

## Citations

- KUKA College, Robot Programming 2 Exercise Book (KSS 8.x) — Exercise 8 "Palletizing program" (pp. 31–44).
- KUKA College, Robot Programming 2 lecture — Chapter 11.8 palletizing example (p. 194).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/WorkBook_PROG_P2_KSS_8_EB_R1_V1_en.pdf`.
