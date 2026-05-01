# Cautilus Dogfood
Date: 2026-05-01

## Trigger

- slice: GitHub issue #90 debug artifact contract alignment.
- issue: `debug` public skill, scaffold helper, validator, and exported plugin
  layout changed after recent issue analysis showed repeated source-of-truth
  drift between docs, generated artifacts, validators, and consumer layouts.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while tightening the `debug`
  artifact contract and exported-layout validator path.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/debug/SKILL.md`
- `skills/public/debug/references/adapter-contract.md`
- `skills/public/debug/references/document-seams.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260501T040000000Z-debug-contract`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id debug --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- run artifact: `.cautilus/runs/20260501T040000000Z-debug-contract/`
- summary:
  `.cautilus/runs/20260501T040000000Z-debug-contract/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked
- routing: 5/5 expected routes matched; bootstrap helper remained
  `find-skills`.

## Scenario Review

- Representative scenario: tightening `debug` artifact current-pointer,
  validator, and exported-layout guidance should not change maintained startup
  routing for implementation, spec, or validation-shaped tasks.
- Expected behavior: startup discovery still routes through `find-skills`, then
  chooses the task skill required by the user prompt.
- Observed behavior: the maintained routing fixture completed successfully
  after the debug contract guidance changes.
- Debug dogfood decision: update `docs/public-skill-dogfood.json` for `debug`
  to freeze that exported-layout scaffold validation is now part of the
  consumer contract.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  the deterministic exported-layout tests prove the #90 behavior directly, and
  the existing routing fixture covers the preserve-goal prompt surface slice.

## Outcome

- recommendation: `accept-now`
- The prompt-surface changes preserve current Cautilus routing behavior.
- The debug contract is now backed by deterministic source and exported plugin
  tests rather than requiring a new maintained Cautilus scenario.

## Follow-ups

- Add dedicated semantic Cautilus cases only if future `debug` changes alter
  routing or diagnosis-before-repair behavior beyond deterministic
  scaffold/validator coverage.
