# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: clarify nested fresh-eye review requirements for issue #67
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes `premortem` prompt surfaces and shared subagent
  review guidance, so maintained startup routing and validation-closeout routing
  must remain stable while parent-level delegation is clarified

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`
- `skills/public/premortem/references/counterweight-triage.md`
- `skills/public/premortem/references/subagent-capability-check.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id premortem --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T011737356Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- `premortem` dogfood still expects non-trivial pending decisions to route to
  `premortem` and produce a maintainer-reviewable output
- the new behavior clarifies execution context inside that skill: parent-level
  spawned reviewers report `parent-delegated`, recursive delegation is opt-in,
  and blocked states still require a concrete host signal
- no maintained Cautilus scenario registry mutation is needed in this slice:
  the change is a public-skill contract clarification, while existing maintained
  scenarios guard startup and route selection

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; the new `premortem` guidance preserves
  the mandatory subagent requirement while preventing accidental recursive
  spawning inside already delegated reviewers

## Follow-ups

- consider a dedicated evaluator scenario if nested delegation confusion repeats
  after this contract clarification lands in a release
