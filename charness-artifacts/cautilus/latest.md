# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: adjust the repo-local `quality` adapter runtime budget after the
  standing pytest gate repeatedly exceeded the previous 45s budget on the
  current test suite
- claim: preserve maintained startup routing and validation-closeout routing
  while making the runtime budget reflect the actual standing gate rather than
  encouraging agents to bypass or ignore slow validation

## Validation Goal

- goal: preserve
- reason: this slice changes `.agents/quality-adapter.yaml`, a prompt-affecting
  adapter surface. The change should not alter skill routing; it should only
  keep `quality`'s deterministic runtime gate honest for the current repo size.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T034545011Z-run/`
- summary artifact:
  `.cautilus/runs/20260424T034545011Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained
  instruction-surface cases

## Scenario Review

- Representative scenario: a maintainer asks `quality` to review current repo
  posture and run available gates before proposing new ones.
- Expected behavior: the agent should run or name existing repo-owned gates and
  persist review state in `charness-artifacts/quality/latest.md` when useful.
- Budget-specific review: the standing pytest target currently passes but takes
  roughly 60-67s on this machine with `python3 -m pytest -n auto`; keeping a
  45s budget would fail the closeout after successful validation and train
  agents to route around the gate. A 70s budget keeps the gate blocking real
  drift while matching the current suite size.
- Public-skill dogfood posture remains `hitl-recommended` for `quality`; no
  maintained scenario-registry mutation is needed for this budget-only adapter
  adjustment.

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof preserved the maintained routing cases; the
  adapter change affects runtime-budget evaluation only

## Follow-ups

- If standing pytest remains above 70s after the suite stabilizes, split the
  standing target or add a separate performance improvement slice rather than
  repeatedly widening the budget.
