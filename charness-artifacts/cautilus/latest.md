# Cautilus Dogfood
Date: 2026-04-30

## Trigger

- slice: source-bound records closeout and Cautilus command-contract repair.
- issue: `.agents/cautilus-adapter.yaml` is prompt-affecting adapter policy, so
  fixing the recommended eval command requires routing regression proof in the
  same slice.

## Validation Goal

- goal: preserve
- reason: preserve startup routing and skill selection while making the
  recommended Cautilus eval command executable with its fixture.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260430T055300000Z-source-bound-records`

## Regression Proof

- run artifact: `.cautilus/runs/20260430T055300000Z-source-bound-records/`
- summary:
  `.cautilus/runs/20260430T055300000Z-source-bound-records/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked

## Scenario Review

- Representative scenario: adding fixture context to the Cautilus adapter's
  recommended eval command should not change public skill routing.
- Expected behavior: startup discovery still routes through `find-skills`, then
  selects the task skill such as `quality`, `impl`, or `spec` from the request.
- Observed behavior: the maintained whole-repo routing fixture completed
  successfully after the adapter command repair.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  this is adapter command-contract proof only.

## Outcome

- recommendation: `accept-now`
- Adding the fixture to the recommended Cautilus eval command preserves the
  existing whole-repo routing fixture.

## Follow-ups

- The checked-in source-bound records guidance still has deterministic public
  skill tests; add a maintained semantic Cautilus case only if this pattern
  graduates into runtime behavior.
