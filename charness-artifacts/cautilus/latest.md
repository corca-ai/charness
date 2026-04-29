# Cautilus Dogfood
Date: 2026-04-29

## Trigger

- slice: quality adapter budget and command-contract hardening.
- issue: `.agents/quality-adapter.yaml` is prompt-affecting adapter policy, so
  budget and gate-command changes need routing regression proof in the same
  slice.

## Validation Goal

- goal: preserve
- reason: preserve startup routing and skill selection while tightening local
  quality enforcement.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260429T232900000Z-quality-budget-command-gates`

## Regression Proof

- run artifact: `.cautilus/runs/20260429T232900000Z-quality-budget-command-gates/`
- summary:
  `.cautilus/runs/20260429T232900000Z-quality-budget-command-gates/eval-summary.json`
- eval test result: passed; recommendation `accept-now`

## Scenario Review

- Representative scenario: changing quality adapter runtime budgets and command
  contracts should not change public skill routing.
- Expected behavior: startup discovery still routes through `find-skills`, then
  selects the task skill such as `quality`, `impl`, or `spec` from the request.
- Observed behavior: the maintained whole-repo routing fixture completed
  successfully after the adapter change.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  this is adapter-policy proof only.

## Outcome

- recommendation: `accept-now`
- Quality adapter budget changes and exact command-contract validation preserve
  the existing whole-repo routing fixture.

## Follow-ups

- Build the README/operator proof ledger so deterministic, Cautilus, HITL, and
  deferred operator proof owners stay visibly separated.
