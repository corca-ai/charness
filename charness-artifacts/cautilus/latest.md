# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: teach `narrative` to review and scaffold repo-local narrative
  adapters before trusting them for first-touch README rewrites
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting public skill guidance and helper
  behavior, so existing startup routing must still pass while adapter-quality
  review stays explicit in checked-in skill surfaces

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/adapter-contract.md`
- `.agents/narrative-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id narrative --json`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T001201251Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl` or `spec` for the existing instruction-surface cases
- evaluator recommendation: `accept-now`

## Scenario Review

- reviewed the `narrative` public-skill dogfood case; the expected route and
  durable artifact remain `narrative` and `charness-artifacts/narrative/latest.md`
- no maintained scenario-registry mutation was required for this
  `hitl-recommended` skill slice
- direct checks against `../cautilus`, `../ceal`, and `../crill` show the
  adapter reviewer catches missing adapters, volatile mutable sources, stale
  paths with closest-path suggestions, and path-like entrypoint drift before
  README rewriting starts

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the prompt-surface edits, and
  the changed guidance does not alter the maintained startup routing cases

## Follow-ups

- README/plugin export drift remains owned by the parallel README rewrite; do
  not use this proof slice to commit the current annotated README export
