# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: tighten init-repo and quality review-scope drift detection after
  inspecting `../crill/AGENTS.md`
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes `init-repo` and `quality` prompt surfaces plus the
  maintained `init-repo` eval helper, so startup routing, validation-closeout
  routing, and consumer-side AGENTS normalization behavior must remain stable

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/references/normalization-flow.md`
- `skills/public/quality/references/entrypoint-docs-ergonomics.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T012738698Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- `init-repo` remains `evaluator-required`; the existing
  `init-repo-inspect-states` evaluator was widened to include a premortem-only
  AGENTS rule that now must produce `fresh_eye_task_review_scope_drift`
- no scenario-registry mutation is needed: the registered scenario already owns
  inspect-state behavior, and the maintained helper now covers this regression
- `quality` remains `hitl-recommended`; reviewed dogfood now records
  `host_instruction_runbook_pressure` for AGENTS files that embed multi-step
  runbooks instead of only reporting generic long-doc pressure

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; the new `init-repo` inspection
  detects the `crill`-shaped missing `init-repo` / `quality` review scope, and
  `quality` now makes AGENTS runbook overfit pressure visible as an advisory
  inventory signal

## Follow-ups

- when `crill` updates to the next Charness build, rerun `init-repo` there and
  move the long Missing Operator Session procedure out of AGENTS if the
  maintainer agrees it belongs in a deeper recovery doc or command surface
