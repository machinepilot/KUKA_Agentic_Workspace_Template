# Safety Review: <PROGRAM_NAME>

**Task ID:** <task_id>
**Reviewer:** Safety agent
**Phase:** A (constraints) | B (draft review)
**Date:** <YYYY-MM-DD>
**Status:** In Review | Complete

---

## 0. Machine-Readable Block

```json safety_review
{
  "$schema": "../../cowork/schemas/safety_review.schema.json",
  "task_id": "",
  "phase": "A|B",
  "reviewer": "safety",
  "date": "",
  "application": "",
  "collaborative": false,
  "normative_refs": ["ISO 10218-1:2011", "ISO 10218-2:2011"],
  "constraints": {
    "max_velocity_mm_s": null,
    "max_velocity_collab_mm_s": null,
    "required_interrupts": [],
    "required_zones": [],
    "mastering_verify_required": true,
    "payload_verify_required": true,
    "tool_data_verify_required": true
  },
  "findings": [],
  "verdict": "pass|pass-with-notes|conditional-pass|fail",
  "hazard_analysis": {}
}
```

---

## 1. Application Profile

| Property | Value |
|----------|-------|
| Application | |
| Collaborative? | yes / no |
| Safety level required | SIL <n> / PL <d / c / b> |
| Human presence | full lockout / periodic / continuous (collab) |
| Tools / end effectors | |
| Payloads | |

## 2. Normative References

- [ ] ISO 10218-1:2011 — Robot construction
- [ ] ISO 10218-2:2011 — Integration
- [ ] ISO/TS 15066:2016 — Collaborative (if applicable)
- [ ] ANSI/RIA R15.06-2012 — US harmonization
- [ ] KUKA SafeOperation / SafeRangeMonitoring manuals
- [ ] Other: <list>

## 3. Safety Constraints (Phase A output)

| # | Constraint | Rationale | Source |
|---|-----------|-----------|--------|
| 1 | Max `$VEL.CP` = <v> mm/s | | |
| 2 | INTERRUPT DECL for E-stop (`$IN[E_STOP]`) | ISO 10218-2 § 5.3 | |
| 3 | INTERRUPT DECL for guard open | | |
| 4 | Reference SafeOperation zone `<name>` | | |
| 5 | Mastering verify on cold-start | | |
| 6 | Payload = <kg>; `$LOAD_DATA[1]` must be set | | |

## 4. Findings (Phase B — against draft `.src`)

| # | Severity | File | Line | Finding | Rule | Fix |
|---|----------|------|------|---------|------|-----|
| | | | | | | |

Use `safety_lint.explain_rule(<rule_id>)` for citation.

## 5. Collaborative Analysis (if applicable)

Per ISO/TS 15066:

| Body region | Limit (N or kPa) | Computed | Pass? |
|-------------|------------------|----------|-------|
| Hand — dorsal | 140 N / 220 kPa | | |
| Forearm | 160 N / 180 kPa | | |
| ... | | | |

Document assumptions (TCP geometry, max speed, stopping distance) and method.

## 6. Verdict

- **pass** — ship.
- **pass-with-notes** — only INFO-level findings; ship.
- **conditional-pass** — WARNING findings; fix before production deploy; can stage.
- **fail** — any CRITICAL; block all downstream.

Rationale: <one paragraph>

## 7. Required Actions

- [ ] <action>
- [ ] <action>

## 8. Sign-off

Safety agent verdict above. For a real deployment, this document must also be reviewed by a qualified human safety officer with authority over the installation (not a software-only sign-off).
