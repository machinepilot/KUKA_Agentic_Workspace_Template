---
name: kuka-program-lint
description: Run the safety_lint MCP server against KRL .src files, explain findings, and produce a REVIEW artifact. Use when QA is auditing a draft program or when a customer program is being refactored.
---

# KUKA Program Lint

Run deterministic static checks on KRL `.src` files via the `safety_lint` MCP server and translate findings into a structured review.

## When to Use

- Before declaring a draft program done (QA agent invocation).
- When auditing a customer program prior to refactor.
- After a convention change — re-lint everything affected.

## Prerequisites

- `safety_lint` MCP server registered and running.
- `cowork/schemas/review.schema.json` in context.
- `cowork/templates/QA_REVIEW_TEMPLATE.md` in context.

## Steps

### 1. Enumerate Files

List every `.src` in scope:
- For a single program: spec.modules.
- For a customer audit: `program_repository.search(".*", scope=<customer_id>)`.

### 2. Lint Each File

For each path, call `safety_lint.lint_src(<path>)`. You receive a list of findings:

```json
[
  {
    "rule_id": "KRL-SAFETY-001",
    "severity": "CRITICAL",
    "file": "path/to/pick.src",
    "line": 23,
    "column": 1,
    "message": "Missing INTERRUPT DECL for E-stop before first motion",
    "fix_hint": "Add INTERRUPT DECL for the E-stop signal before line 42."
  }
]
```

### 3. Explain Rules

For each unique `rule_id` in findings, call `safety_lint.explain_rule(<rule_id>)` once and cache the returned rationale + normative citation.

### 4. Convention Audit (manual companion to lint)

Even when lint passes, check the 10 conventions from `.cursor/rules/kuka-krl-conventions.mdc`:

1. INI block at top
2. INTERRUPT DECL before first motion
3. $TOOL/$BASE/$IPO_MODE set
4. $VEL/$ACC explicit
5. SPLINE + BAS init
6. No magic numbers
7. Subprograms in own files
8. Error handling modular
9. DECL comments
10. I/O aliases only

### 5. Emit REVIEW

Use `cowork/templates/QA_REVIEW_TEMPLATE.md`. Include:

- Files audited (table)
- Convention compliance (checkbox table)
- Findings (from lint + manual inspection, with severity)
- Dataset references for each finding (what pattern to follow)
- Verdict: `pass` / `conditional` / `fail`
- JSON block per `review.schema.json`

### 6. Close Loop

Append to `task_state.json.qa.artifacts[]`. Hand back to Orchestrator.

## Rule Catalog (seed — extend as you learn)

| rule_id | severity | description |
|---------|----------|-------------|
| KRL-SAFETY-001 | CRITICAL | Missing INTERRUPT DECL for E-stop before first motion |
| KRL-SAFETY-002 | CRITICAL | Programmatic override increase ($OV_PRO) detected |
| KRL-SAFETY-003 | CRITICAL | Unbounded WAIT FOR without timeout interrupt |
| KRL-MOTION-001 | WARNING | `$TOOL` not set before first motion |
| KRL-MOTION-002 | WARNING | `$BASE` not set before first motion |
| KRL-MOTION-003 | WARNING | `$VEL.CP` not set before LIN/CIRC block |
| KRL-MOTION-004 | WARNING | SPLINE without BAS(#INITMOV,0) init |
| KRL-IO-001 | WARNING | Raw `$IN[n]` / `$OUT[n]` in program body (use SIGNAL alias) |
| KRL-STYLE-001 | INFO | `DECL` without descriptive comment |
| KRL-STYLE-002 | INFO | Magic numeric literal (use named constant) |

New rules land in the `safety_lint` MCP server implementation, not in this skill.
