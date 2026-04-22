---
id: KUKA_SAFETY_Operating_Modes
title: "Operating Modes: T1 / T2 / AUT / AUT EXT Safety Functions"
topic: safety
kuka_platform: [KR C4, KR C5]
controller: [KSS 8.5, KSS 8.6, KSS 8.7]
language: N/A
source:
  type: vendor_manual
  title: "KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators"
  tier: T1
  pages: [43, 46]
  section: "3.8–3.11 Operating mode safety functions"
  access_date: "2026-04-22"
  url: null
license: reference-only
revision_date: "2026-04-22"
related: [KUKA_SAFETY_Stop_Categories, KUKA_SAFETY_SafeOp_Overview, KUKA_REF_Velocity_Acceleration]
difficulty: intermediate
tags: [safety, operating-modes, t1, t2, aut, aut-ext, enabling-switch, override]
---

# Operating Modes: T1 / T2 / AUT / AUT EXT Safety Functions

## Summary

Every KUKA controller has four mode-keyed operating states. Each imposes different safety functions, speed caps, and allowed actions. Mode is selected via a keyswitch on the pendant (hardware) and enforced by the safety CPU. Integrators must understand which mode is appropriate for each task and what protections that mode provides — the wrong mode during commissioning is the single most common cause of crashes.

## The Four Modes

### T1 (Manual Reduced Velocity)

- **Purpose:** Teach, manual jog, program verify at reduced speed.
- **Speed cap:** TCP velocity limited to **250 mm/s** regardless of programmed `$VEL.CP`.
- **Safeguards:** Cell door may be open; operator is inside the cell envelope. Enabling switch (dead-man) must be held.
- **Override:** Operator-adjusted via pendant; max 100% of the 250 mm/s cap.
- **Typical use:** Initial teach, debugging, mastering checks.

### T2 (Manual High Velocity)

- **Purpose:** Verify program at production speed with operator present.
- **Speed cap:** None beyond programmed values.
- **Safeguards:** Cell must be closed (safeguards enforced like AUT). Enabling switch must be held.
- **Override:** Operator-adjusted.
- **Typical use:** Post-teach speed verification; not permitted by some local regulations.

### AUT (Automatic)

- **Purpose:** Production cycle, operator outside the cell.
- **Speed cap:** None beyond programmed.
- **Safeguards:** All safeguards active (doors closed, light curtains armed, safety zones enforced).
- **Override:** Usually locked at 100% by plant configuration.
- **Typical use:** Normal production.

### AUT EXT (Automatic External)

- **Purpose:** Production driven by an external source (plant PLC, line controller).
- **Differs from AUT:** Start / stop / mode commands come from PLC interface rather than pendant.
- **Safeguards:** Same as AUT.
- **Override:** Plant-controlled.
- **Typical use:** PLC-orchestrated cells; common in body shops, paint lines, machine-loading cells.

## Transitions

Mode changes happen only via the keyswitch (usually lockable). After a mode change:

- Program is halted.
- Operator must confirm the new mode.
- In T1/T2, enabling switch must be actively held before any motion.
- Some safety functions (SafeOperation zones) may be mode-dependent — zone A active in AUT, zone B active in T1, etc.

## Enabling Switch (Dead-Man)

The 3-position enabling switch on the pendant is central to T1 / T2 safety:

- **Released** — no motion allowed.
- **Middle** — motion enabled (operator holding lightly).
- **Squeezed hard** — motion blocked (reflex on startle).

Only `middle` allows motion. Releasing or crushing both produce an immediate stop.

## Speed Cap Enforcement

T1's 250 mm/s cap is enforced by the safety CPU, not the motion controller alone. Even if KRL commands `$VEL.CP = 2.0` (2 m/s), T1 will limit actual TCP velocity to 250 mm/s — programmer cannot bypass it.

Axis velocity in T1 is also reduced (typically 10–20% of max) — this is separately configurable.

## Common Pitfalls

- **Running production in T1 "to be safe".** T1 was not designed for continuous operation; heat loads on the drives and mode-dependent zones can cause unexpected behavior.
- **Leaving T2 accessible.** Some sites prohibit T2 altogether because at full speed with door open the risk is severe. Lock the keyswitch if T2 is not permitted.
- **Ignoring mode in safety-zone config.** Zones should be mode-aware: in T1 the operator is inside; zones for T1 must define where the operator stands.
- **Copy-pasting `$OV_PRO` code** assuming it scales all speeds — it does not bypass the T1 cap.
- **Starting an AUT EXT cycle during a manual teach session.** The PLC may command start the moment the key turns; always verify handshake logic.

## Related Entries

- `KUKA_SAFETY_Stop_Categories` — stop behavior that intersects with mode.
- `KUKA_SAFETY_SafeOp_Overview` — mode-dependent SafeOperation zones.
- `KUKA_REF_Velocity_Acceleration` — why `$VEL.CP` in user code doesn't guarantee actual TCP speed.

## Citations

- KUKA System Software 8.7 — Operating and Programming Instructions for System Integrators (T1). Chapter 3.8–3.11 "Operating mode safety functions" (pp. 43–46).

## Provenance

Ingested 2026-04-22 by Cowork Orchestrator from `kuka_dataset/raw_sources/vendor_manuals/KSS_87_SI_en.pdf`.
