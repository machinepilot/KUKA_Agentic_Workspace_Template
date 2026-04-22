# Handoff: <TASK_NAME>

**From:** <producing agent — Cowork Orchestrator | QA | Motion Synthesis | Documentation>
**To:** <consuming agent / Cursor>
**Task ID:** <task_id>
**Date:** <YYYY-MM-DD>
**Priority:** Critical | High | Medium | Low
**Source:** <which PROGRAM_SPEC, REVIEW, or SAFETY_REVIEW triggered this handoff>

---

## 0. Machine-Readable Block

```json handoff
{
  "$schema": "../../cowork/schemas/handoff.schema.json",
  "task_id": "",
  "from_agent": "",
  "to_agent": "",
  "priority": "",
  "source_documents": [],
  "target_files": [],
  "applicable_rules": [],
  "dataset_refs": [],
  "instructions": [],
  "acceptance_criteria": [],
  "notes": ""
}
```

---

## 1. Target Files

| File | Action | Description |
|------|--------|-------------|
| | Create / Edit / Refactor / Review | |

## 2. Context

One-paragraph description of what is to happen and why. Reference the source spec / review.

## 3. Applicable Cursor Rules

These glob-scoped rules should auto-apply when the target files are opened:

| Rule | Triggers On | Why |
|------|-------------|-----|
| `kuka-krl-conventions.mdc` | `**/*.src,**/*.dat` | Structure + conventions |
| `kuka-safety.mdc` | `**/*.src` | Safety patterns |
| `kuka-dataset-reference.mdc` | `**/*.src,**/*.dat,**/HANDOFF_*.md` | Citation practice |

## 4. Dataset References

| Entry | Use For |
|-------|---------|
| `kuka_dataset/normalized/<path>` | <what pattern / syntax to apply> |

## 5. Edit Instructions (numbered)

1. **<file>** — <specific instruction>
   - Pattern to follow: <dataset entry>
   - Before: <state / snippet>
   - After: <state / snippet>

2. **<file>** — <instruction>

## 6. Acceptance Criteria

- [ ] <verifiable criterion>
- [ ] <verifiable criterion>
- [ ] `safety_lint.lint_src` returns no CRITICAL findings on modified files.
- [ ] QA review verdict `pass` or `conditional-pass`.

## 7. Notes

Anything Cursor should NOT touch, timing constraints, dependencies on other tasks, special considerations.
