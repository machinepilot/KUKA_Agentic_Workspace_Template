---
name: run-eval-harness
description: Run the agent behavior eval harness (replay cases, diff outputs, summarize). Use when validating agent prompts, schema stability, or before a template release.
---

# Run Eval Harness

Replay saved agent interactions against their current definitions and compare to golden outputs.

## When to Use

- After editing any `.cursor/agents/<role>.md` — verify existing cases still pass.
- After schema changes — detect breakage.
- Before tagging a template release.
- When an agent's output quality feels off — reproduce under eval.

## Prerequisites

- `evals/runner.py` present (shipped with template).
- `evals/cases/<case>.json` files populated (you add these over time).
- `evals/golden/<case>.json` expected outputs.
- Python venv active.

## Steps

### 1. List Cases

```bash
cd evals
python runner.py --list
```

### 2. Run One Case

```bash
python runner.py --case <case_id>
```

Output: per-case verdict (`PASS` / `FAIL`), diff of actual vs. golden when fail, runtime.

### 3. Run All

```bash
python runner.py --all
```

Summary appears at end with counts per verdict.

### 4. Update Goldens (carefully)

When an intentional change produces different (better) output:

```bash
python runner.py --case <case_id> --update-golden
```

Review the diff before committing; "golden" means "reviewed by human and endorsed."

### 5. Add a New Case

Create `evals/cases/<case_id>.json`:

```json
{
  "case_id": "architect_press_brake_basic",
  "agent": "architect",
  "input": {
    "program_intake": { "...": "..." }
  },
  "expected_schema": "program_spec.schema.json",
  "expected_keys": ["modules", "variables", "motion_blocks"],
  "golden_path": "evals/golden/architect_press_brake_basic.json"
}
```

Produce a golden by:
1. Running the agent manually with the `input`.
2. Reviewing the output.
3. Saving to `evals/golden/<case_id>.json`.

### 6. Model Selection for Evals

Evals run often and don't need frontier-model reasoning. Configure `runner.py` to use a cost-effective model:

- Ollama `qwen2.5-coder:7b` or `llama3.1:8b` for cheap local replay.
- OpenAI `gpt-4o-mini` for cheap cloud replay.
- Claude Sonnet for higher-fidelity evals before releases.

## Interpreting Results

- **Schema fail** — agent output no longer matches its schema. Usually a prompt drift; fix the prompt.
- **Golden diff** — agent output changed. Decide: drift (fix prompt) or intended change (update golden).
- **Runtime spike** — agent is confusing itself; check for newly added context overwhelming the prompt.

## CI (optional)

If this workspace ever lives in CI, add a job:

```yaml
- run: python evals/runner.py --all --junit evals/results/junit.xml
```

## Close the Loop

Eval results go under `evals/results/<YYYY-MM-DD_HHMMSS>/`. Summarize pass/fail in `evals/results/INDEX.md` if desired.
