# safety_lint MCP Server

Deterministic static checks on KRL `.src` files. Seeds the rule catalog referenced in `.cursor/skills/kuka-program-lint/SKILL.md` and `.cursor/rules/kuka-krl-conventions.mdc`.

The implementation is intentionally small and rule-based. Extend by adding entries to `safety_lint/rules.py`.

## Install

```bash
pip install uv
uv pip install -e .
```

## Tools

### `lint_src(path: str) -> list[Finding]`

Run all enabled rules on a file. Returns:

```json
[
  {
    "rule_id": "KRL-SAFETY-001",
    "severity": "CRITICAL",
    "file": "pick.src",
    "line": 23,
    "column": 1,
    "message": "Missing INTERRUPT DECL for E-stop before first motion",
    "fix_hint": "Add INTERRUPT DECL before the first motion instruction."
  }
]
```

### `list_rules() -> list[Rule]`

Return the full rule catalog (id, severity, description, category).

### `explain_rule(rule_id: str) -> dict`

Rationale + normative citation for a single rule.

## Seed Rule Catalog

| rule_id | severity | description |
|---------|----------|-------------|
| KRL-SAFETY-001 | CRITICAL | Missing INTERRUPT DECL for E-stop before first motion |
| KRL-SAFETY-002 | CRITICAL | Programmatic override ($OV_PRO) modification detected |
| KRL-SAFETY-003 | CRITICAL | Unbounded WAIT FOR (no timeout interrupt or WAIT SEC fallback) |
| KRL-MOTION-001 | WARNING | `$TOOL` not set before first motion |
| KRL-MOTION-002 | WARNING | `$BASE` not set before first motion |
| KRL-MOTION-003 | WARNING | `$VEL` not set before first Cartesian motion |
| KRL-MOTION-004 | WARNING | SPLINE block without `BAS(#INITMOV, 0)` initialization |
| KRL-IO-001 | WARNING | Raw `$IN[n]` or `$OUT[n]` in program body (use SIGNAL alias) |
| KRL-STYLE-001 | INFO | `DECL` without descriptive comment |
| KRL-STYLE-002 | INFO | Magic numeric literal |

The regex patterns are simple and fallible; they are calibrated to catch obvious issues and flag for human review. A full KRL parser is out of scope for this stub.
