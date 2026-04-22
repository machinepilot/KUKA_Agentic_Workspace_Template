---
id: KUKA_REF_KL5000_Linear_Unit
title: KUKA KL 5000 RV3 Linear Unit (External Axis)
topic: external_axis
kuka_platform: [KR C4, KR C5]
language: N/A
source:
  type: vendor_manual
  title: "KUKA Linear Unit KL 5000 RV3 — Product Datasheet (0012401208_EN)"
  tier: T1
  pages: [1, 1]
  section: "full sheet"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_REF_Tool_Base_Frames]
difficulty: beginner
tags: [external_axis, linear_unit, kl5000, floor-mounted, travel-rail]
---

# KUKA KL 5000 RV3 Linear Unit

## Summary

The KL 5000 RV3 is a floor-mounted linear axis for KUKA robots. It extends the working envelope by translating the entire robot along a rail. It couples to a KR C4 or KR C5 controller as an external axis (commonly E1) and is programmed in KRL like any additional axis — `E6POS` / `E6AXIS` targets include `E1..E6` components.

## Syntax / Specification

Rail/cart mechanical:

- Nominal payload class: RV3 (high-stiffness cart sized for KUKA KR-series robots — specific payload depends on robot family).
- Drive: servo-driven via robot controller; feedback via absolute resolver/encoder mastered to the cart.
- Travel range: segmented rail — length is configurable per order; typical installations run 3–30 m.

KRL integration example:

```krl
; Cart position embedded in an E6POS target
PTP {X 1000, Y 0, Z 1200, A 0, B 90, C 0, S 2, T 2, E1 2500.0}

; Cart position embedded in an E6AXIS target
PTP {A1 0, A2 -90, A3 90, A4 0, A5 0, A6 0, E1 2500.0}
```

Commissioning:

- External axis declaration in the controller's machine data (`$EX_AX_IGNORE`, `$EX_AX_SWITCH_OFF`, etc.).
- Mastering: `$MASTER_COR` and cart-specific reference gauge; follow mastering procedure in the KL manual and confirm in WorkVisual.
- Zero position and travel limits set via `$SOFTP_END`, `$SOFTN_END` or equivalent.

## Semantics / Behavior

- **Additional axis in the same kinematic chain.** The controller can coordinate cart motion with robot motion (synchronized CP motion) or decouple them (cart moves to position, then robot moves).
- **`$IPO_MODE` and cart motion.** For coordinated work the cart contributes to the `$BASE`-to-`$WORLD` transform; programming is typically identical to a stationary robot once calibrated.
- **Safe zones.** Safety configuration must include cart travel range; cart end-stops are hardware-protected, but SafeOperation monitoring should reflect the cart axis, too.
- **Mastering and referencing.** The cart has its own mastering position; re-master after collision, belt change, or any encoder event. Use the `Brake test` procedure for the drive and the `Mastering test` for the cart encoder chain — see safety/ entries.

## Common Pitfalls

- **Missing cart component in point records.** Saving `POS` instead of `E6POS` drops the `E1..E6` fields; the cart then defaults to its last position on playback, leading to collisions.
- **Assuming PTP coordination.** Pure PTP may not coordinate cart and arm timing tightly; for process work, use spline with cart components to guarantee synchronization.
- **Mastering drift ignored.** A cart out of master by a few mm can still "run" but the coordinated CP path will deviate; always check mastering status after service.

## Worked Example

Simple "park at cart station A, pick, translate to station B, place":

```krl
DEF rail_demo()
   INI

   $TOOL = tool_data[1]
   $BASE = base_data[1]

   ; Move cart to station A, robot at home
   PTP {A1 0, A2 -90, A3 90, A4 0, A5 0, A6 0, E1 0.0}

   ; Pick at station A
   LIN {X 400, Y 0, Z 500, A 0, B 90, C 0, E1 0.0}
   LIN {X 400, Y 0, Z 300, A 0, B 90, C 0, E1 0.0}

   ; Translate cart to station B (robot follows)
   LIN {X 400, Y 0, Z 500, A 0, B 90, C 0, E1 2500.0}

   ; Place at station B
   LIN {X 400, Y 0, Z 300, A 0, B 90, C 0, E1 2500.0}
END
```

## Related Entries

- `KUKA_REF_Tool_Base_Frames` — rail installations often require a second `base_data[i]` per station.

## Citations

- KUKA Linear Unit KL 5000 RV3 — Product Datasheet (T1). `kuka_dataset/raw_sources/vendor_manuals/0012401208_EN.pdf`.
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — for `E6POS` / `E6AXIS` structure.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator. Datasheet is a single page; most mechanical and electrical specifics belong in a dedicated installation/commissioning entry when the KL assembly manual is acquired.
