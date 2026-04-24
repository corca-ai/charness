# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: merge remote `main` source-guard work into the current validation
  stabilization branch
- claim: preserve maintained startup routing and validation-closeout routing
  while keeping both branches' quality, init-repo, release, and runtime-gate
  behavior changes visible

## Validation Goal

- goal: preserve
- reason: this merge combines prompt-affecting `quality`, `init-repo`,
  `release`, `premortem`, and checked-in instruction surface changes; startup
  routing, validation-closeout routing, public-skill dogfood evidence, and
  bounded source-guard defaults must remain coherent after conflict resolution

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `.agents/init-repo-adapter.yaml`
- `.agents/narrative-adapter.yaml`
- `.agents/quality-adapter.yaml`
- `.agents/release-adapter.yaml`
- `skills/public/find-skills/SKILL.md`
- `skills/public/ideation/SKILL.md`
- `skills/public/ideation/references/decision-question-response.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/references/normalization-flow.md`
- `skills/public/init-repo/scripts/init_repo_adapter.py`
- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`
- `skills/public/premortem/references/counterweight-triage.md`
- `skills/public/premortem/references/subagent-capability-check.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/adapter-gate-review.md`
- `skills/public/quality/references/entrypoint-docs-ergonomics.md`
- `skills/public/quality/scripts/inventory_brittle_source_guards.py`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/adapter-contract.md`
- `skills/public/spec/SKILL.md`
- `skills/public/spec/references/taxonomy-axis-checkpoint.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id find-skills --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id ideation --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id premortem --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id spec --json`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T031752356Z-run/`
- latest upstream summary:
  `.cautilus/runs/20260424T033032495Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained
  instruction-surface cases

## Scenario Review

- `quality` dogfood evidence keeps delegated-review / adapter-gate posture,
  missing-validation-binary setup rules, bounded scan defaults, and explicit
  override behavior visible
- `init-repo` dogfood rows record bounded source-guard scanning defaults and
  adapter/CLI override behavior
- `release` keeps adapter-gated CLI plus bundled-skill disclosure review
  evidence
- evaluator-required skills named by the planner (`find-skills`, `init-repo`,
  and `spec`) are already present in `evals/cautilus/scenarios.json`, so no
  maintained scenario-registry mutation is required for this merge
- repo-owned tests cover bounded scan roots, adapter/CLI overrides, hidden
  workflow directories, and unreadable markdown warnings

## Outcome

- recommendation: `accept-now`
- routing notes: conflict resolution preserved the maintained routing cases and
  kept validation-closeout routing through `quality`

## Follow-ups

- broad quality closeout may still expose environment-specific test failures;
  keep runtime/tooling failures separate from routing regressions when triaging
