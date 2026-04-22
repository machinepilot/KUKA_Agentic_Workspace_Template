---
id: KUKA_SAFETY_SafeOp_Overview
title: KUKA.SafeOperation 3.6 — Overview and Safety Interfaces
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.SafeOperation 3.6 Operating and Programming Instructions"
  tier: T1
  pages: [13, 15]
  section: "2.1–2.3 Overview and interfaces"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_Stop_Categories, KUKA_SAFETY_Operating_Modes, KUKA_SAFETY_Monitoring_Spaces, KUKA_SAFETY_Mastering_Test, KUKA_SAFETY_Brake_Test]
difficulty: advanced
tags: [safety, safeoperation, srm, safety-zones, pl-d, cat-3]
---

# KUKA.SafeOperation 3.6 — Overview and Safety Interfaces

## Summary

SafeOperation is KUKA's safety-rated motion-monitoring option. On top of the base controller's stop-category safety, SafeOperation adds monitored workspace zones (Cartesian and axis-specific), safe velocity monitoring, safe reference monitoring (SRM), and safe I/O via PROFIsafe / CIP Safety / FSoE. Together these enable cells where the robot can continue running while an operator works in a defined zone — a collaborative or co-existent workflow that the base controller alone cannot certify.

## What SafeOperation Provides

- **Monitored spaces.** Cartesian and axis-specific zones where the TCP (or axis position) must stay inside (or outside) a polygon/range. Violation triggers a safety-rated stop.
- **Safe velocity monitoring.** TCP and axis velocities capped independently of KRL programming. Max speed per zone.
- **Safe tool.** Safety-rated definition of the tool envelope; zones apply to the envelope, not just the TCP.
- **Safe reference monitoring (SRM).** Periodic verification that encoder values still agree with an external reference switch.
- **Safe inputs/outputs.** PROFIsafe / CIP Safety / FSoE signals wired into the safety CPU.
- **Mastering and brake tests.** Procedural tests (covered in `KUKA_SAFETY_Mastering_Test` and `KUKA_SAFETY_Brake_Test`) that keep the certification valid.

## Safety Architecture

SafeOperation runs on the controller's safety CPU — a physically separate, redundant-compare processor from the motion controller. The safety CPU:

- Reads safe I/O frames from PROFIsafe / CIP Safety / FSoE.
- Monitors drive encoders via safety-rated feedback channels.
- Evaluates zones, velocities, and references every cycle (typically 4 ms).
- Issues safety-rated stop signals to the drives when violated.

Certification level: PL d / Cat 3 per EN ISO 13849-1; SIL 2 per IEC 62061. Actual achieved level depends on overall cell design including external safety devices.

## Interfaces

SafeOperation is commissioned through a combination of:

- **WorkVisual safety configuration** — zones, velocities, tool, reference switches, I/O mapping. Offline editing; deploy + acceptance test.
- **Pendant safety menu** — runtime view of zone/velocity/SRM status; mastering test, brake test.
- **Safe I/O** via PROFIsafe / CIP Safety / FSoE — wired to plant safety PLC.
- **KRL-visible flags** (non-safety): read-only indicators of zone state for logic purposes (do not use for safety).

## Relationship to the Base Safety System

SafeOperation layers on top of the base KSS safety:

- Base KSS provides stop categories, operating modes, E-stop chain, enabling switch.
- SafeOperation adds zones, velocities, SRM, and their associated safe I/O.

A cell without SafeOperation still has Stop 0 / Stop 1 / Stop 2 and operating-mode protections — but no monitored zones beyond workspace limits.

## When SafeOperation Is Required

- **Collaborative or co-existent workspace.** Operator and robot sharing a cell with interaction.
- **Safety-rated reduced speed.** Required by the application's risk assessment.
- **Safety-rated workspace limits beyond workspace envelope.** E.g., a fenceless cell where a zone replaces a physical barrier.
- **Any cell where SIL 2 / PL d / Cat 3 is required for a function beyond the base controller's guarantees.**

## Commissioning Overview

Full commissioning is multi-day for a nontrivial cell. The acceptance flow:

1. Author safety configuration in WorkVisual (zones, velocities, tool, SRM).
2. Deploy to controller + activate.
3. **Mastering test** — verify axis mastering is valid (see `KUKA_SAFETY_Mastering_Test`).
4. **Brake test** — verify mechanical brakes hold within spec (see `KUKA_SAFETY_Brake_Test`).
5. **Functional acceptance** — traverse each zone boundary, provoke each velocity limit, verify stops occur.
6. **Document acceptance.** Every safety-relevant setting captured; counter-signed per local regulation.
7. **Periodic re-validation.** Many regions require annual or semi-annual brake/mastering tests plus re-acceptance after any safety-config change.

## Common Pitfalls

- **Editing SafeOperation config without re-acceptance.** Any change to zones/velocities/SRM requires re-running the acceptance procedure.
- **Using zone-state KRL flags for safety logic.** They're not safety-rated; use safe I/O.
- **Assuming "safe zone" means "operator-safe."** Zones enforce robot-side monitoring; plant-side barriers (physical guards, light curtains, interlocks) still required per hazard analysis.
- **Skipping periodic brake / mastering tests.** Certification lapses.
- **Mixing up standard I/O and safe I/O.** Standard signals are not safety-rated; safety-rated logic must use the safety PDOs.

## Related Entries

- `KUKA_SAFETY_Monitoring_Spaces` — zone configuration detail.
- `KUKA_SAFETY_Mastering_Test` — periodic test.
- `KUKA_SAFETY_Brake_Test` — periodic test.
- `KUKA_SAFETY_Stop_Categories` — underlying stop categories used by SafeOperation.
- `KUKA_SAFETY_Operating_Modes` — zones are mode-dependent.

## Citations

- KUKA.SafeOperation 3.6 Operating and Programming Instructions (T1). Chapter 2.1–2.3 "Overview and interfaces" (pp. 13–15).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_SafeOperation_36_en.pdf`.
