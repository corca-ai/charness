# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: teach `init-repo` and repo AGENTS policy that meaningful
  `charness-artifacts/` changes are repo state and commit targets, while
  current-pointer helpers should no-op without canonical content changes
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting AGENTS and `init-repo` skill
  surfaces, so maintained startup routing and validation-closeout routing must
  remain stable while the artifact policy becomes visible

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/references/normalization-flow.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T000750987Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- reviewed the maintained `init-repo` dogfood row with
  `suggest_public_skill_dogfood`; it still expects normalization of a partially
  initialized mature repo, durable state at
  `charness-artifacts/init-repo/latest.md`, and `init-repo` selection rather
  than an adjacent skill
- no maintained Cautilus scenario mutation is needed for this slice because the
  changed behavior is locked by repo tests for AGENTS policy wording,
  `inspect_repo.py` recommendation output, surface obligations, and the
  existing `init-repo` dogfood contract

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed, and `init-repo` now carries the
  artifact commit/no-op policy without changing the expected work-skill route

## Follow-ups

- consider a shared current-pointer persistence helper so other `latest.*`
  writers can inherit the `find-skills` canonical no-op behavior
