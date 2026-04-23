# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: teach HITL and impl to handle review-state, nested-fence,
  browser/runtime verification, and hidden validation-tool routing misses from
  GitHub issues #59, #60, and #61, with a maintained closeout-routing scenario
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting public skill routing and review
  guidance, so existing startup routing must still work while the new guidance
  stays explicit in checked-in skill surfaces

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/find-skills/SKILL.md`
- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/chunk-contract.md`
- `skills/public/hitl/references/state-model.md`
- `skills/public/impl/SKILL.md`
- `skills/public/impl/references/verification-ladder.md`
- `skills/public/quality/SKILL.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id find-skills --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id hitl --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id impl --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T135213638Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl` or `spec` for the existing instruction-surface cases
- new `validation-closeout-routes-before-hitl` case routes validation-shaped
  closeout to `quality` before HITL/manual review; `quality` now says to run
  validation tool recommendations for evaluator-backed closeout work
- evaluator recommendation: `accept-now`

## Scenario Review

- added and reviewed a maintained case in
  `evals/cautilus/instruction-surface-cases.json` for #60's
  validation-shaped issue closeout / operator reading test wording
- reviewed dogfood suggestions for `find-skills`, `hitl`, and `impl`; the
  current contracts still match their required skill and artifact surfaces
- kept the route as public `quality` plus validation recommendation discovery
  instead of exposing Cautilus as a public top-level workflow skill

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the prompt-surface edits, and
  #60 now has maintained instruction-surface coverage for the HITL/manual-review
  misroute

## Follow-ups

- if later dogfood expects Cautilus to be selected directly instead of via
  `quality` recommendation discovery, split that into a product-boundary issue
