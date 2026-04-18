# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `find-skills` validation discovery and `cautilus` manifest scope tightening
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: tighten prompt-change policy and closeout enforcement without intentionally changing the currently checked-in routing claims

## Prompt Surfaces

- `skills/public/find-skills/SKILL.md`
- `integrations/tools/cautilus.json`

## Commands Run

- `python3 scripts/validate-cautilus-proof.py --repo-root .`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`
- `pytest tests/test_find_skills.py tests/quality_gates/test_quality_tool_recommendations.py`
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --recommendation-role validation --next-skill-id quality`
- `cautilus instruction-surface test --repo-root .`

## A/B Compare

- baseline_ref: `HEAD~1`
- prepare-compare smoke: `cautilus workspace prepare-compare --repo-root . --baseline-ref HEAD~1 --output-dir /tmp/cautilus-compare-smoke`
- mode-evaluate smoke: `cautilus mode evaluate --repo-root . --mode held_out --intent 'Prompt-affecting repo behavior should remain legible.' --baseline-repo /tmp/cautilus-compare-smoke/baseline --candidate-repo /tmp/cautilus-compare-smoke/candidate --output-dir /tmp/cautilus-mode-smoke`
- current note: compare workspace preparation is healthy; `mode evaluate` still routes through the adapter's `baseline_ref` command path, so direct baseline/candidate workspace consumption is not yet a checked-in charness adapter behavior

## Outcome

- recommendation: `defer`
- instruction-surface summary: `3 passed / 0 failed / 1 blocked`
- routing notes: the checked-in bootstrap case still does not close cleanly because `find-skills` tries to do its normal local inventory step and the read-only instruction-surface sandbox blocks that path; compact no-bootstrap implementation still routes to `impl`, expanded no-bootstrap contract-shaping still routes to `spec`, and compact contract-shaping remains observational
- discovery notes: `find-skills` now has a direct `recommendation_role` query path, and the `cautilus` integration manifest now scopes `supports_public_skills` to the checked validation routes `impl`, `quality`, and `spec`

## Follow-ups

- teach the instruction-surface summary contract to represent bootstrap helper selection separately from the eventual work skill before treating checked-in bootstrap as a hard pass/fail route
- decide whether the checked-in bootstrap case should use a lighter route-only `find-skills` path under read-only evaluation instead of the normal inventory-writing helper flow
- widen held-out/A-B evaluator coverage when a slice claims prompt behavior improved rather than preserved
- keep compact contract-shaping observational until a lower-noise expectation is proven
