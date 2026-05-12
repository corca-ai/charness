# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: Charness runtime-budget and eval-adjacent closeout changed the
  prompt-affecting quality adapter after the grouped issue fix and release
  repair work.
- source: `validate-cautilus-proof` required refreshing
  `charness-artifacts/cautilus/latest.md` because
  `.agents/quality-adapter.yaml` changed.

## Validation Goal

- goal: preserve
- reason: confirm the existing whole-repo routing surface still routes through
  the intended startup `find-skills` bootstrap and durable work skills after
  quality adapter budget updates.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `scenario_review_change`
- changed surfaces:
  - `.agents/quality-adapter.yaml`

## Prompt Surfaces

- `.agents/quality-adapter.yaml` increases the local
  `local-linux-x86_64-36cpu` `check-coverage` runtime budget from 35000ms to
  45000ms, matching observed expanded coverage-gate runtime without changing
  skill routing semantics.
- The Cautilus adapter and whole-repo routing fixture remain unchanged in this
  slice; this proof checks that the quality-adapter change did not disturb the
  maintained instruction-surface routing contract.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `cautilus eval evaluate --input .cautilus/runs/20260512T082131710Z-run/eval-observed.json`

## Regression Proof

- live eval run: `.cautilus/runs/20260512T082131710Z-run/`
- eval test result: runner command passed in 96423ms; recommendation
  `accept-now`.
- eval evaluate result: 5 passed / 0 failed / 0 blocked.
- proof class: `declared-eval-runner`, runtime `codex`, target surface
  `dev/repo`, `productProofReady: true`.
- routing summary: bootstrap helper `find-skills` matched in 5/5 cases;
  durable work skills matched `impl` 2/2, `quality` 2/2, and `spec` 1/1.

## Scenario Review

- The active planner requested scenario review because the quality adapter is a
  prompt-affecting adapter contract. No maintained scenario registry change is
  needed: the changed field is a runtime budget, not a route discriminator.
- The evaluator-required `gather` script change is a doctor/release-probe
  reliability repair and does not alter gather selection, provider routing, or
  prompt text consumed by the whole-repo routing fixture.
- The whole-repo fixture remains the representative proof because the expected
  behavior is preservation of existing route choices, not a new Cautilus
  scenario.

## Outcome

- recommendation: accept.
- Charness can release the grouped issue fixes with the added pytest-temp
  amplification guard and release-gate reliability repair once deterministic
  quality gates pass.

## Follow-ups

- Consider a separate disk-usage preflight for heavy release/pre-push flows if
  large temp incidents recur; it is not required for this slice because the
  copy-boundary bug is now guarded directly.
