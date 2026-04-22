---
id: KUKA_SAFETY_Monitoring_Spaces
title: "SafeOperation Monitoring Spaces (Cartesian and Axis-Specific)"
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.SafeOperation 3.6 Operating and Programming Instructions"
  tier: T1
  pages: [18, 31]
  section: "2.5 Monitoring spaces"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_SafeOp_Overview, KUKA_SAFETY_Stop_Categories, KUKA_SAFETY_Operating_Modes]
difficulty: advanced
tags: [safety, safeoperation, zones, cartesian-zone, axis-zone, safe-tool, workspace]
---

# SafeOperation Monitoring Spaces (Cartesian and Axis-Specific)

## Summary

A *monitoring space* is a zone evaluated by the SafeOperation safety CPU. The robot's current configuration (TCP position for Cartesian zones; axis positions for axis zones) is compared each safety cycle against the zone geometry. The zone type (inside/outside) and the configured response determine the safety action — Stop 0, Stop 1, or a reduced-velocity limit. Zones are the mechanism by which SafeOperation replaces or complements physical guards.

## Zone Types

### Cartesian Monitoring Spaces

- **Geometry.** Convex polygon in the X-Y plane with a height range in Z (`Z_min`, `Z_max`), expressed in `$WORLD` or a defined safety base frame. Modern SafeOperation versions support arbitrary convex polyhedra.
- **Body.** The safety-rated *safe tool* envelope — not just the TCP. The safe tool is a union of bounding spheres/capsules around the actual tool so that zone violations reflect the tool's real reach.
- **Evaluation.** Every cycle, the controller checks whether the safe tool (points along it) intersects the zone.

### Axis-Specific Monitoring Spaces

- **Geometry.** Per-axis range `[A_min, A_max]` for each monitored axis.
- **Evaluation.** Each cycle, every axis is compared to its configured range.
- **Use case.** Limit an axis's travel beyond its mechanical stop — e.g., prevent A1 from rotating into a wall when physical stops allow it.

## Zone Modes

Each zone is configured as:

- **Inclusive (TCP/envelope must stay inside).** Violation = leaving. Common for safe workspaces: the robot must not leave its designated area.
- **Exclusive (TCP/envelope must stay outside).** Violation = entering. Common for keep-out zones: operator workstation, conveyor crossing.
- **Velocity-limited.** Inside the zone, TCP velocity and/or axis velocity is capped (safety-rated). Exiting the zone returns to full speed.
- **Enable-signal-gated.** Zone is enforced only when a specific safe input is asserted — dynamic zone activation for multi-step processes.

## Configured Response

When a zone triggers:

- **Stop 0** — immediate drive power removal. For violations that indicate a hardware / position fault.
- **Stop 1** — controlled stop. For operational violations (TCP leaving workspace).
- **Safe velocity limit** — not a stop; caps speed while inside.
- **Custom signal** — raise a safe output to notify the plant PLC.

## Zone Count and Scoping

- Up to **16 Cartesian zones** and **8 axis zones** (check your SafeOperation version for exact limits).
- Each zone has a unique id.
- Zones can be **operating-mode-specific** (e.g., "Zone 5 active only in T1").
- Zones can be **tool-specific** when multiple safe tools are defined.

## Commissioning

1. **Model the cell.** Identify the reachable workspace, operator-access areas, conveyor crossings, maintenance stations.
2. **Draw zones** in WorkVisual's safety configurator. Use site coordinates (measure physical reference features).
3. **Define safe tool.** Bounding geometry around the real tool, validated in the tool-envelope editor.
4. **Assign modes and responses.** Per zone, which operating modes it's active in and what stop it triggers.
5. **Deploy + acceptance test.** Move the robot slowly across each boundary; verify the correct stop occurs.
6. **Document.** Every zone captured with its polygon coordinates, response, and mode activation.

## Common Pitfalls

- **Zone in wrong frame.** Zones can be in `$WORLD` or a safety base frame; using the wrong one offsets the zone from where it should be.
- **Safe tool too small.** Envelope must cover the real tool's extremities or zones won't catch real collisions.
- **Safe tool too large.** Overly conservative envelope causes nuisance stops in tight workspaces.
- **Forgetting height range.** A 2D polygon with no Z limits is technically supported (infinite height) but often not what the designer intended.
- **Zone for the wrong mode.** Zone configured only in AUT but operator accesses cell in T1 — no protection.
- **Reusing zone IDs across configurations.** Version control the WorkVisual project; label zones by purpose, not number.
- **Post-deploy changes without re-acceptance.** A small polygon tweak is a safety change.

## Worked Example (Descriptive)

A shared workspace with two operators (one on each side of the cell):

- **Zone 1** (exclusive, Stop 1, active in AUT EXT) — operator 1 workstation polygon. Robot cannot enter unless its cooperative-motion signal from plant PLC is active.
- **Zone 2** (exclusive, Stop 1, active in AUT EXT) — operator 2 workstation polygon. Same logic, mirrored.
- **Zone 3** (inclusive, Stop 1, active in all modes) — cell envelope. Robot must stay inside this polygon at all times.
- **Zone 4** (velocity-limited, 250 mm/s, active in all modes) — hand-off area between zones 1 and 2. Velocity cap ensures operator always has reaction time regardless of program.

## Related Entries

- `KUKA_SAFETY_SafeOp_Overview` — product overview.
- `KUKA_SAFETY_Stop_Categories` — stop categories used by zone responses.
- `KUKA_SAFETY_Operating_Modes` — zones are mode-aware.

## Citations

- KUKA.SafeOperation 3.6 Operating and Programming Instructions (T1). Chapter 2.5 "Monitoring spaces" (pp. 18–31).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_SafeOperation_36_en.pdf`.
