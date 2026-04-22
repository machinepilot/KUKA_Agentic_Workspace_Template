---
id: KUKA_WorkVisual_IO_Mapping
title: Mapping Bus I/Os to $IN / $OUT / SIGNAL
topic: fieldbus
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.2, KSS 8.3, KSS 8.5, KSS 8.6, KSS 8.7]
language: KRL
source:
  type: vendor_manual
  title: "KUKA.WorkVisual 6.0 Operating Instructions"
  tier: T1
  pages: [161, 170]
  section: "9.4 Mapping process data to KRL signals"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_WorkVisual_Fieldbus_Setup, KUKA_Fieldbus_KRC5_Interfaces, KUKA_WorkVisual_Project_Deployment]
difficulty: intermediate
tags: [fieldbus, workvisual, io-mapping, signal, $in, $out, process-data]
---

# Mapping Bus I/Os to $IN / $OUT / SIGNAL

## Summary

Once a fieldbus device is configured (`KUKA_WorkVisual_Fieldbus_Setup`), its process-data objects (PDOs) need to be wired to KRL-accessible I/O. KRL sees inputs and outputs as flat arrays `$IN[1..N]` / `$OUT[1..M]` with optional named `SIGNAL` aliases. WorkVisual's I/O mapping editor connects each PDO bit or word to a specific array index; the result is compiled into the controller's I/O image and visible to every program.

## The Three Layers

1. **Field device → Bus master.** PDO structure defined by the device's GSDML / EDS / ESI.
2. **Bus master → KRL I/O image.** Mapping edited in WorkVisual; result burned into `$machine.dat` and related system files.
3. **KRL I/O image → Named signals.** `SIGNAL` declarations in `$config.dat` alias flat `$IN[]` / `$OUT[]` addresses to meaningful names.

Each layer is maintained separately; changing one does not silently update the others.

## The Mapping Editor

In WorkVisual: `Project Tree → Controller → I/O Mapping`. The editor shows two columns:

- **Device PDO tree** (left) — expand each device to see its bits/bytes/words.
- **KRL I/O image** (right) — `$IN[1..]`, `$OUT[1..]`, and structured I/O addresses.

Drag a PDO onto a KRL address to create a mapping. Bit-level granularity is supported; you can map a single bit of a device's status word to `$IN[23]`.

Save the mapping when done; the `_machine.dat` and related config files are regenerated.

## SIGNAL Aliases

After the KRL image exists, give bits names in `$config.dat`:

```krl
SIGNAL sig_feed_ready     $IN[10]
SIGNAL sig_part_present   $IN[11]
SIGNAL sig_estop_ok       $IN[1]

SIGNAL sig_gripper_close  $OUT[5]
SIGNAL sig_cycle_done     $OUT[8]

; Multi-bit signals for integer / binary values
SIGNAL station_select     $IN[100] TO $IN[103]   ; 4-bit selector
```

Use the named alias in program code:

```krl
IF sig_part_present THEN
   sig_gripper_close = TRUE
ENDIF
```

Never reference `$IN[11]` or `$OUT[5]` directly from program code — it breaks when the mapping changes.

## Address Range Discipline

A recurring integration headache is address-range collisions. Establish (and document) ranges before mapping:

| Range | Purpose |
|-------|---------|
| `$IN[1..9]` | Safety & infrastructure (E-stop, reset, mode confirm) |
| `$IN[10..99]` | Process signals (sensors, part-present, feeder ready) |
| `$IN[100..199]` | Recipe / station selectors (integer-packed) |
| `$OUT[1..9]` | End-effector & process actuators (gripper, torch) |
| `$OUT[10..99]` | Status lamps, PLC handshakes |
| `$OUT[100..199]` | Integer returns (cycle count, part id) |

These ranges are workspace convention; customer-specific plants may differ. Document in the cell's runbook.

## Safety I/O

PROFIsafe / CIP Safety / FSoE bits map into a *separate* safety I/O image, accessed from KRL via dedicated safety variables, not ordinary `$IN` / `$OUT`. SafeOperation zones, safe stop signals, and reduced-speed inputs use the safety image.

**Do not try to map safety PDOs onto standard `$IN`** — the mapping editor enforces this but confusion happens.

## Common Pitfalls

- **Drifting mappings.** Edit WorkVisual → forget to deploy → code references addresses that moved. Always deploy after mapping changes; version-control the WV project.
- **Hard-coded addresses in KRL.** Use `SIGNAL` aliases for every bit used in business logic.
- **Overlapping ranges.** Two SIGNALs pointing at the same `$IN` bit — legal but confusing. Make signals one-to-one.
- **Forgetting active-low NC safety inputs.** E-stop reads `FALSE` when pressed; logic must check `sig_estop == FALSE`.
- **Mapping bits without re-reading device spec.** A PDO bit may mean "ready" in the device but "busy" in the mapping.
- **Renaming PDOs.** If the device description changes, WorkVisual may lose its mapping and silently drop it. Validate after every catalog update.

## Worked Example

Minimal end-to-end: a pick/place cell with an E-stop, two part sensors, and a gripper output.

1. **Mapping (in WorkVisual):**
   - Safety PDO `EStop_OK` → `$IN[1]`.
   - IO-block PDO bit 0 → `$IN[10]` (`sig_feed_ready`).
   - IO-block PDO bit 1 → `$IN[11]` (`sig_part_present`).
   - IO-block PDO bit 4 → `$OUT[5]` (`sig_gripper_close`).

2. **Aliases (`$config.dat`):**
   ```krl
   SIGNAL sig_estop_ok       $IN[1]
   SIGNAL sig_feed_ready     $IN[10]
   SIGNAL sig_part_present   $IN[11]
   SIGNAL sig_gripper_close  $OUT[5]
   ```

3. **KRL (any program):**
   ```krl
   WAIT FOR sig_feed_ready AND sig_part_present
   sig_gripper_close = TRUE
   ```

## Related Entries

- `KUKA_WorkVisual_Fieldbus_Setup` — upstream: creating the bus and adding devices.
- `KUKA_Fieldbus_KRC5_Interfaces` — the physical ports this data flows through.
- `KUKA_WorkVisual_Project_Deployment` — activating the mapping on the controller.

## Citations

- KUKA.WorkVisual 6.0 Operating Instructions (T1). Chapter 9.4 "I/O mapping" (pp. 161–170).
- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators — `$IN`, `$OUT`, `SIGNAL` discussion.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_WorkVisual_60_en.pdf`.
