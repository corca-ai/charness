# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: repair current quality-review drift by replacing stale Cautilus
  `install.md` links with the live upstream `install.sh` URL, and tighten
  checked-in routing so evaluator-backed closeout reaches `quality` before
  `hitl`
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting checked-in routing guidance and
  the release adapter checklist, so existing startup routing must still work
  while validation-shaped closeout continues to route through `quality`

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `checked_in_instruction_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `.agents/release-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- first instruction-surface run found the closeout routing regression:
  `.cautilus/runs/20260423T221410173Z-run/`, recommendation `reject`
- instruction-surface summary after AGENTS routing repair:
  `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T221549607Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl` or `spec` for the existing instruction-surface cases
- `validation-closeout-routes-before-hitl` again routes validation-shaped
  closeout to `quality` before HITL/manual review after the checked-in AGENTS
  routing repair
- evaluator recommendation: `accept-now`

## Scenario Review

- reviewed the maintained `validation-closeout-routes-before-hitl` case after
  the first run selected `hitl`; the repair keeps the route as public
  `quality` plus validation recommendation discovery instead of exposing
  Cautilus as a public top-level workflow skill

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the checked-in routing repair,
  and the current quality closeout no longer depends on same-agent manual
  interpretation for evaluator-backed closeout routing

## Follow-ups

- if later dogfood expects Cautilus to be selected directly instead of via
  `quality` recommendation discovery, split that into a product-boundary issue
