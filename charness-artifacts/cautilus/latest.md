# Cautilus Dogfood
Date: 2026-05-01

## Trigger

- slice: GitHub issues #87-#89 public-skill prompt-surface closeout.
- issue: `premortem`, `debug`, and `create-cli` public skill surfaces changed,
  and the checked-in Cautilus adapter command needed to stay executable while
  refreshing proof.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while tightening delegated
  reviewer, debug scaffold, and external-capability CLI guidance.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/create-cli/SKILL.md`
- `skills/public/create-cli/references/quality-gates.md`
- `skills/public/debug/SKILL.md`
- `skills/public/debug/references/adapter-contract.md`
- `skills/public/debug/references/document-seams.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/subagent-capability-check.md`
- `skills/public/create-cli/references/external-capability-clis.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260501T020100000Z-issues-87-89`

## Regression Proof

- run artifact: `.cautilus/runs/20260501T020100000Z-issues-87-89/`
- summary:
  `.cautilus/runs/20260501T020100000Z-issues-87-89/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked
- routing: 5/5 expected routes matched; bootstrap helper remained
  `find-skills`.

## Scenario Review

- Representative scenario: public skill prompt changes should not alter the
  maintained startup routing split between `find-skills`, `impl`, `spec`, and
  `quality`.
- Expected behavior: startup discovery still routes through `find-skills`, then
  chooses the task skill required by the user prompt.
- Observed behavior: the maintained routing fixture completed successfully
  after the delegated-reviewer, debug-scaffold, and create-cli guidance changes.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  the existing routing fixture covers this preserve-goal slice.

## Outcome

- recommendation: `accept-now`
- The prompt-surface changes preserve current Cautilus routing behavior.
- The checked-in eval fixture and adapter command now use the current
  `dev/repo` Cautilus eval contract.

## Follow-ups

- Add dedicated semantic Cautilus cases only if these guidance changes start
  driving runtime behavior beyond deterministic doc/test coverage.
