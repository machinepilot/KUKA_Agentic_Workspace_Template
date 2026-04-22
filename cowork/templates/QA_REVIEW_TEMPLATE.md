# QA Review: <CUSTOMER_ID> — <SYSTEM>

**Task ID:** <task_id>
**Reviewer:** QA agent
**Date:** <YYYY-MM-DD>
**Status:** In Review | Findings Complete | Fixes Handed Off | Closed

---

## 0. Machine-Readable Block

```json review
{
  "$schema": "../../cowork/schemas/review.schema.json",
  "task_id": "",
  "reviewer": "qa",
  "date": "",
  "files_reviewed": [],
  "convention_compliance": {},
  "findings": [],
  "pattern_comparison": [],
  "verdict": "pass|conditional|fail",
  "dataset_refs": []
}
```

---

## 1. Files Reviewed

| File | Role | Lines | Last Modified |
|------|------|-------|---------------|
| | | | |

## 2. Convention Compliance

| # | Convention | Status | Notes |
|---|-----------|--------|-------|
| 1 | `INI` block at top of main `DEF` | | |
| 2 | `INTERRUPT DECL` before first motion | | |
| 3 | `$TOOL`/`$BASE`/`$IPO_MODE` set before motion | | |
| 4 | `$VEL.CP`/`$VEL_AXIS`/`$ACC` set explicitly | | |
| 5 | SPLINE wrapped with `BAS(#INITMOV, 0)` | | |
| 6 | No hardcoded numeric literals where constants apply | | |
| 7 | Subprograms in own `.src`; shared data in `.dat` | | |
| 8 | Error/recovery logic in dedicated subprograms | | |
| 9 | Descriptive comments on every `DECL` | | |
| 10 | I/O via aliases; no raw `$IN[n]`/`$OUT[n]` | | |

**Status key:** PASS · FAIL · PARTIAL · N/A

## 3. Findings

| # | Severity | Rule | File | Line | Description | Dataset Ref | Suggested Fix |
|---|----------|------|------|------|-------------|-------------|---------------|
| 1 | | | | | | | |
| 2 | | | | | | | |

**Severity:**
- **CRITICAL** — Safety risk, logic error, spec violation. Must fix before ship.
- **WARNING** — Convention violation affecting maintainability/reliability. Should fix.
- **INFO** — Style, comment quality. Fix when convenient.

## 4. Pattern Comparison

For each major program section, the closest normalized example and deviations:

| Section | Closest Dataset Example | Deviations |
|---------|------------------------|------------|
| Main loop | | |
| Pick subprogram | | |
| Place subprogram | | |
| Error recovery | | |

Paths are relative to `kuka_dataset/normalized/`.

## 5. Spec Conformance

- [ ] All modules in spec exist as files.
- [ ] All variables in spec declared.
- [ ] All motion blocks implemented.
- [ ] All aliases in integration contract used in code.
- [ ] All required interrupts declared.
- [ ] All fault handlers present.

## 6. Verdict

**`pass`** | **`conditional`** | **`fail`**

Rationale: <one paragraph>

## 7. Implementation Order (for fixes)

### Phase 1: Critical
- [ ] Finding #<n>

### Phase 2: Warning
- [ ] Finding #<n>

### Phase 3: Info (optional polish)
- [ ] Finding #<n>

## 8. Handoff (if fixes required)

Produce a `HANDOFF_<slug>_<date>.md` using `HANDOFF_TEMPLATE.md` with the fix list and cite this review.
