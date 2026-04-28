# Cautilus Dogfood
Date: 2026-04-28

## Trigger

- slice: quality skill hardening plus Charness issue #76.
- issue: current Charness proof guidance still pointed at the removed
  `instruction-surface` command instead of the `cautilus eval` surface.

## Validation Goal

- goal: preserve
- reason: preserve startup and validation routing while migrating the maintained
  whole-repo proof command and fixture shape.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`
- `truth_surface_change`

## Prompt Surfaces

- `skills/public/impl/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/prompt-asset-policy.md`
- `.agents/cautilus-adapter.yaml`
- `.agents/quality-adapter.yaml`
- `evals/cautilus/whole-repo-routing.fixture.json`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260428T000000000Z-eval-migration`
- `pytest -q tests/test_cautilus_scenarios.py tests/test_cautilus_proof_artifact.py`

## Regression Proof

- run artifact: `.cautilus/runs/20260428T000000000Z-eval-migration/`
- summary:
  `.cautilus/runs/20260428T000000000Z-eval-migration/eval-summary.json`
- eval test result: 5 passed, 0 failed, 0 blocked; recommendation
  `accept-now`
- routing summary: `find-skills` bootstrap matched 5/5 expected routes;
  selected skills were `impl` 2, `quality` 2, and `spec` 1.

## Scenario Review

- Representative scenario: an agent receives prompt-surface or validation
  closeout work after the Cautilus eval migration and should still route
  through startup discovery before selecting `impl`, `quality`, or `spec`.
- Expected behavior: proof guidance names `cautilus eval test/evaluate`, the
  adapter declares `evaluation_input_default` and `eval_test_command_templates`,
  and removed `instruction-surface` command text is rejected by validators.
- Observed behavior: the migrated fixture ran through upstream
  `../cautilus/bin/cautilus eval test`, generated `eval-observed.json`, and
  produced an accept-now `eval-summary.json`.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  this slice migrates the existing whole-repo routing proof only.

## Outcome

- recommendation: `accept-now`
- #76 status: current Charness guidance and proof validators now target
  `cautilus eval test` / `cautilus eval evaluate` and reject the removed
  `cautilus instruction-surface test` command in current proof artifacts.
- quality status: the skill now requires user-visible weak/missing/advisory
  disclosure and separates missing prompt asset roots from inline bulk
  inventory.

## Follow-ups

- Build the README/operator proof ledger now that the maintained routing proof
  is on `cautilus.evaluation_input.v1` and `cautilus eval test`.
