---
id: KUKA_WorkVisual_Project_Deployment
title: Transferring and Activating a WorkVisual Project
topic: workvisual
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.2, KSS 8.3, KSS 8.5, KSS 8.6, KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA.WorkVisual 6.0 Operating Instructions"
  tier: T1
  pages: [231, 246]
  section: "Chapter 14 Project transfer and activation"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_WorkVisual_Fieldbus_Setup, KUKA_WorkVisual_IO_Mapping, KUKA_Fieldbus_KRC5_Interfaces]
difficulty: intermediate
tags: [workvisual, deployment, project-transfer, activation, kss]
---

# Transferring and Activating a WorkVisual Project

## Summary

A WorkVisual project is offline configuration until it is transferred to the controller and activated. Transfer pushes the project files; activation compiles and loads them, replacing the running configuration. The process has explicit safety gates (T1 mode, operator confirm, controller restart for certain changes) and is sensitive to version compatibility between the WV project and the controller's KSS version. Getting deployment right is a repeatable procedure, not an improvisation.

## Pre-Deployment Checklist

- [ ] Controller is reachable (KLI ping).
- [ ] Controller KSS version matches the WV project's target KSS version.
- [ ] Project builds cleanly in WorkVisual (no errors / unresolved device mappings).
- [ ] Controller is in T1 mode (or OFF for some changes).
- [ ] Cell is safe for a restart (no tooling in a position that would conflict with power loss).
- [ ] Current controller project backed up (`Project → Save current state`).

## Transfer Steps

1. **In WorkVisual:** `Project → Transfer`.
2. Select target controller from discovered list (or enter IP address).
3. WorkVisual compares the controller's current project hash with the project to be transferred; differences shown.
4. Confirm transfer; files copied to controller's `PROJECTS/` area.
5. Transfer completes; the project is present but *not yet active*.

## Activation Steps

1. On the controller (pendant or WorkVisual remote activate):
   - `Main Menu → Activate project → <project name>`.
2. Controller prompts: "Activate as production project?" Confirm.
3. Depending on what changed, the controller will either:
   - **Hot-swap** (I/O mapping, KRL modules) — activation completes in seconds.
   - **Require restart** (safety config, field-bus topology changes) — controller reboots; cell must be safe.
4. On successful activation, the project becomes the running config.

## Post-Deployment Verification

Always verify — every deployment is a change event that could break the cell:

- [ ] `$config.dat` loaded correctly; SIGNAL aliases visible.
- [ ] Fieldbus diagnostics green for every device.
- [ ] I/O mapping sanity-check: toggle a known input, verify `$IN[]` changes.
- [ ] Run a short T1 test cycle; confirm program motion, signals, safety signals all behave as expected.
- [ ] Check safety configuration unchanged if it wasn't supposed to change (or confirm the new safety configuration against the safety acceptance checklist).

## Version Compatibility

WorkVisual supports KSS 8.2 through 8.7 (and VW variants). Deploying a project built for a different KSS version can succeed partially, silently skipping unsupported features. Always match:

- WV project target KSS version = controller KSS version.
- Option packages (mxAutomation, RSI, EKI, SafeOperation) must be installed on both sides if used in the project.

## Rollback

If activation fails verification:

1. Revert via `Activate project → <previous project name>`.
2. Fix the WV project (identify what changed, diff against the last known-good project hash).
3. Re-transfer and re-activate.

Never "fix on the controller" — any changes made directly on the pendant will be overwritten by the next WV deployment.

## Common Pitfalls

- **KSS version mismatch** — silent feature loss, subtle bugs that surface weeks later.
- **Activating during production.** The hot-swap path is fast but not instantaneous; production windows matter.
- **Forgetting safety acceptance.** Changes to safety configuration require a formal safety acceptance per local regulation (EN ISO 10218).
- **Parallel edits.** Two integrators editing the same WV project in different workspaces → merge nightmare. Treat the WV project as a single-writer artifact or use proper VCS.
- **No backup.** `Save current state` before transfer is not optional.
- **Skipping verification.** "It built, ship it" — incorrect; always verify on the controller.

## Related Entries

- `KUKA_WorkVisual_Fieldbus_Setup` — upstream: configuring buses before deployment.
- `KUKA_WorkVisual_IO_Mapping` — the mapping that gets deployed.
- `KUKA_Fieldbus_KRC5_Interfaces` — the physical targets of the deployed configuration.

## Citations

- KUKA.WorkVisual 6.0 Operating Instructions (T1). Chapter 14 "Project transfer and activation" (pp. 231–246).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KST_WorkVisual_60_en.pdf`.
