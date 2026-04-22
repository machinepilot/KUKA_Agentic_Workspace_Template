---
id: KUKA_WorkVisual_Fieldbus_Setup
title: Fieldbus Setup in WorkVisual
topic: fieldbus
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.2, KSS 8.3, KSS 8.5, KSS 8.6, KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.WorkVisual 6.0 Operating Instructions"
  tier: T1
  pages: [153, 156]
  section: "9.1–9.2 Fieldbus overview and controller configuration"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_WorkVisual_IO_Mapping, KUKA_Fieldbus_KRC5_Interfaces, KUKA_WorkVisual_Project_Deployment]
difficulty: intermediate
tags: [fieldbus, workvisual, profinet, ethernet-ip, ethercat, configuration]
---

# Fieldbus Setup in WorkVisual

## Summary

WorkVisual is the engineering tool used to configure a KUKA controller's fieldbus interfaces — Profinet (with or without PROFIsafe), EtherNet/IP (with or without CIP Safety), and EtherCAT (with or without FSoE). Fieldbus setup happens at the project level: you add a bus master or slave, configure its addressing, import device descriptions (GSDML, EDS, ESI), then map the bus data onto KRL signals. This article covers the master/slave configuration phase; the mapping phase lives in `KUKA_WorkVisual_IO_Mapping`.

## Overview of the Workflow

1. **Create / open a WorkVisual project** and add the target controller.
2. **Install the field-bus catalog** (GSDML for Profinet, EDS for EtherNet/IP, ESI for EtherCAT) into WorkVisual's device catalog.
3. **Configure the controller's bus role.** Controller can act as master, slave, or both simultaneously on different buses.
4. **Add devices** (IO blocks, drives, safety devices) from the catalog. Assign station names / IP addresses.
5. **Configure cycle times** appropriate for the bus and device mix.
6. **Map process-data objects** (PDOs) onto KRL I/O addresses — the mapping step.
7. **Deploy** project to the controller (`KUKA_WorkVisual_Project_Deployment`).
8. **Activate** on the controller; re-boot if required.

## Supported Buses on KR C5

The KR C5 ships with integrated interfaces for:

- **Profinet / PROFIsafe** — KUKA acts as controller or device; PROFIsafe CPU for safety traffic.
- **EtherNet/IP / CIP Safety** — scanner or adapter role.
- **EtherCAT / FSoE** — master (typical for KUKA + external axes / servo drives) or slave.

Each bus is configured independently in WorkVisual; a controller may run multiple buses concurrently.

## Device Catalog

Before configuring devices you need their description files:

- **GSDML (Profinet).** XML; vendor-supplied. Import via `Catalog → Import`.
- **EDS (EtherNet/IP).** Text file; vendor-supplied. Same import path.
- **ESI (EtherCAT).** XML; vendor-supplied.

Keep catalog files per project in version control — device FW revisions matter; a newer GSDML may change PDO structure.

## Configuration Checklist

Per bus, confirm:

- [ ] Bus master is the correct node (controller vs. external PLC).
- [ ] IP addressing / station name scheme matches plant standard.
- [ ] Cycle time set (typical: 4 ms for Profinet IO, 1–2 ms for EtherCAT drives).
- [ ] Safety CPU instantiated if any PROFIsafe / CIP Safety / FSoE devices exist.
- [ ] Topology matches physical wiring (line, ring, tree).

## Common Pitfalls

- **Mismatched GSDML version** vs. installed device firmware — yields process-data-mapping errors that surface only at runtime.
- **Duplicate station names / IP addresses** — bus master will refuse to start.
- **Cycle time too aggressive** for the devices on the wire — intermittent timeouts.
- **Forgetting to deploy after adding a device** — WorkVisual shows the device but the controller still doesn't know about it.
- **Configuring safety traffic on the wrong CPU** — PROFIsafe / CIP Safety / FSoE must run on the safety CPU, not the standard CPU.
- **Changing bus topology live** — always deploy offline, reboot controller, verify.

## Related Entries

- `KUKA_WorkVisual_IO_Mapping` — mapping PDOs onto `$IN` / `$OUT` / `SIGNAL`.
- `KUKA_Fieldbus_KRC5_Interfaces` — KR C5 integrated bus-interface hardware.
- `KUKA_WorkVisual_Project_Deployment` — transferring and activating the project.

## Citations

- KUKA.WorkVisual 6.0 Operating Instructions (T1). Chapter 9.1–9.2 "Fieldbus — overview and controller configuration" (pp. 153–156).
- KUKA KR C5 datasheet — integrated bus-interface listing.

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_WorkVisual_60_en.pdf`.
