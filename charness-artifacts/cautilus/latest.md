# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: prompt-sensitive validation policy, gate, and repo-skill closeout for `cautilus`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: tighten prompt-change policy and closeout enforcement without intentionally changing the currently checked-in routing claims

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/impl/SKILL.md`
- `skills/public/spec/SKILL.md`
- `skills/public/quality/references/prompt-asset-policy.md`

## Commands Run

- `python3 scripts/validate-cautilus-proof.py --repo-root .`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`
- `pytest tests/test_cautilus_scenarios.py`
- `cautilus instruction-surface test --repo-root .`

## A/B Compare

- baseline_ref: `HEAD~1`
- prepare-compare smoke: `cautilus workspace prepare-compare --repo-root . --baseline-ref HEAD~1 --output-dir /tmp/cautilus-compare-smoke`
- mode-evaluate smoke: `cautilus mode evaluate --repo-root . --mode held_out --intent 'Prompt-affecting repo behavior should remain legible.' --baseline-repo /tmp/cautilus-compare-smoke/baseline --candidate-repo /tmp/cautilus-compare-smoke/candidate --output-dir /tmp/cautilus-mode-smoke`
- current note: compare workspace preparation is healthy; `mode evaluate` still routes through the adapter's `baseline_ref` command path, so direct baseline/candidate workspace consumption is not yet a checked-in charness adapter behavior

## Outcome

- recommendation: `reject`
- instruction-surface summary: `3 passed / 1 failed / 0 blocked`
- routing notes: compact no-bootstrap implementation still routes to `impl`, expanded no-bootstrap contract-shaping still routes to `spec`, and compact contract-shaping remains observational; the remaining gap is the checked-in bootstrap case, where the model loads `find-skills` first but still reports `impl` as the selected work skill, so the current summary schema does not cleanly separate bootstrap helper choice from durable work-skill choice

## Follow-ups

- teach the instruction-surface summary contract to represent bootstrap helper selection separately from the eventual work skill before treating checked-in bootstrap as a hard pass/fail route
- widen held-out/A-B evaluator coverage when a slice claims prompt behavior improved rather than preserved
- keep compact contract-shaping observational until a lower-noise expectation is proven
