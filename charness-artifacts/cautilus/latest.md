# Cautilus Dogfood
Date: 2026-04-28

## Trigger

- slice: quality issue #78 plus Cautilus over-trigger hardening.
- issue: quality should surface quiet-failure diagnostics and source-guard
  pressure as actionable signals, while generic review/closeout wording should
  not make Cautilus feel required.

## Validation Goal

- goal: preserve
- reason: preserve startup routing while narrowing evaluator-backed execution
  to prompt/instruction behavior, baseline compare, and explicit behavior
  evaluation tasks.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/impl/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/prompt-asset-policy.md`
- `skills/public/quality/references/public-spec-layering.md`
- `skills/public/quality/references/standing-gate-verbosity.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260428T000000000Z-cautilus-trigger-narrowing`
- `pytest -q tests/quality_gates/test_quality_standing_gate_verbosity.py tests/quality_gates/test_quality_public_spec_quality.py tests/quality_gates/test_quality_skill_docs.py tests/quality_gates/test_docs_and_misc.py::test_cautilus_guidance_does_not_use_generic_review_triggers tests/quality_gates/test_docs_and_misc.py::test_validate_integrations_rejects_generic_cautilus_triggers`

## Regression Proof

- run artifact: `.cautilus/runs/20260428T000000000Z-cautilus-trigger-narrowing/`
- summary:
  `.cautilus/runs/20260428T000000000Z-cautilus-trigger-narrowing/eval-summary.json`
- eval test result: 5 passed, 0 failed, 0 blocked; recommendation
  `accept-now`
- routing summary: `find-skills` bootstrap matched 5/5 expected routes;
  selected skills were `impl` 2, `quality` 2, and `spec` 1.

## Scenario Review

- Representative scenario: generic quality, review, or closeout wording should
  route to deterministic quality/impl/spec work first, not silently to Cautilus.
- Expected behavior: Cautilus is surfaced for evaluator-backed behavior review,
  prompt/instruction regression, baseline compare, or operator reading tests;
  ordinary closeout validates checked proof artifacts instead of executing the
  evaluator.
- Observed behavior: the maintained whole-repo routing fixture still routes
  startup discovery through `find-skills`, then to `impl`, `quality`, or `spec`
  without selecting the Cautilus support skill for generic closeout wording.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  this slice narrows trigger guidance and keeps the existing routing fixture.

## Outcome

- recommendation: `accept-now`
- #78 status: quality now inventories quiet failure detail and source-guard
  rollups so quiet gates and public spec source guards become actionable.
- Cautilus status: generic `review`, `closeout`, `검증`, and `리뷰` triggers are
  removed from the integration manifest and validator-backed against reentry.

## Follow-ups

- Build the README/operator proof ledger so deterministic, Cautilus, HITL, and
  deferred operator proof owners stay visibly separated.
