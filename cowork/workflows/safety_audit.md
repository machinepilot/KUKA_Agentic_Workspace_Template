# Workflow: Safety Audit

Audit a program or a full customer cell against ISO 10218 / ISO/TS 15066 and KUKA SafeOperation best practices.

**Who runs this:** Orchestrator + Safety + QA.
**Duration:** minutes for a single program; hours for a full cell.

## When to Use

- Before first deployment of any motion-bearing program.
- After any change to safety-rated I/O, SafeOperation configuration, or payload.
- Periodic (quarterly or after maintenance) audit of customer cells.
- When investigating a near-miss or incident.

## Inputs

- Customer id + system, or explicit file list.
- Application profile (collaborative? safety category? risk assessment on file?).

## Outputs

- `SAFETY_AUDIT_<customer>_<system>_<YYYY-MM-DD>.md`
- Optional: `HANDOFF_*.md` for Cursor to apply recommended fixes.

## Steps

### Step 1 — Scope & Context

Orchestrator collects:
- The program file(s) in scope.
- The WorkVisual project reference (for SafeOperation zone config).
- Payload / tool data current values.
- Risk assessment (if any) — if missing, note it as a finding.

### Step 2 — Safety Phase A Baseline

Safety agent produces `safety_constraints` for the application profile:
- Max velocity (normal / reduced / collaborative).
- Required interrupts.
- Zone references.
- Payload / tool requirements.
- Mastering requirements.
- Collaborative body-region limits (if collab).

This becomes the baseline the programs are audited against.

### Step 3 — Static Audit

For each `.src` file:
1. `safety_lint.lint_src(<path>)` → findings.
2. Manual check against the 10 KRL conventions.
3. Verify each Phase-A constraint is satisfied in code.
4. Verify interrupt priorities and handlers' correctness.
5. Verify no programmatic `$OV_PRO` override.
6. Verify no inline SafeOperation zone redefinition.

### Step 4 — Configuration Audit

Review (or cross-reference with the user):
- WorkVisual project's I/O mapping — safety-rated signals use safety-rated channels.
- SafeOperation zone definitions — match the intended cell layout.
- `$MACHINE.DAT` mastering status — current, valid.
- `$LOAD_DATA[]` — matches actual payload.

### Step 5 — Collaborative Body-Force (if applicable)

For collaborative applications, Safety computes TCP forces under worst-case kinematics and compares to ISO/TS 15066 Annex A limits per body region.

### Step 6 — Produce the Audit Document

Use `cowork/templates/SAFETY_REVIEW_TEMPLATE.md` (adapted title `SAFETY_AUDIT_*`). Include:
- Scope and normative references.
- Phase-A baseline constraints.
- Static audit findings.
- Configuration audit findings.
- Collab body-force analysis (if applicable).
- Final verdict.
- Required actions and responsible party.

### Step 7 — Handoff Fixes (if needed)

If actions require code or config changes, Orchestrator spawns Documentation to author a `HANDOFF_*.md` with the specific fixes. Cursor (or the user) executes.

### Step 8 — Sign-off Escalation

Software sign-off is necessary but NOT sufficient. Safety verdict + audit document go to a qualified human safety officer for final sign-off before production. Record the sign-off in the customer README safety log.

## Exit Criteria

- Audit document written and schema-valid.
- Verdict captured.
- Required actions logged.
- Customer `README.md` safety log updated.
- If verdict was `fail`, production deployment is explicitly blocked until follow-up audit passes.
