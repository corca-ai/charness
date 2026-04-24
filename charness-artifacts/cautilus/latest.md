# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: merge remote `main` release/review-gate work into the current branch
  that added `ruff` validation setup and Python runtime inheritance guards
- claim: preserve maintained startup routing and validation-closeout routing
  while keeping both branches' quality/release behavior changes visible

## Validation Goal

- goal: preserve
- reason: the merge combines prompt-affecting `quality`, `release`,
  `premortem`, and checked-in instruction surface changes; startup routing,
  validation-closeout routing, and public-skill dogfood evidence must remain
  coherent after conflict resolution

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
- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`
- `skills/public/premortem/references/counterweight-triage.md`
- `skills/public/premortem/references/subagent-capability-check.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/adapter-gate-review.md`
- `skills/public/quality/references/entrypoint-docs-ergonomics.md`
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
- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T031752356Z-run/`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained
  instruction-surface cases

## Scenario Review

- `quality` dogfood evidence now includes both the remote delegated-review /
  adapter-gate posture and the local missing-validation-binary setup rule
- `release` keeps the remote adapter-gated CLI plus bundled-skill disclosure
  review evidence
- dogfood generation was inspected for `find-skills`, `ideation`, `init-repo`,
  `premortem`, `quality`, `release`, and `spec`; expected artifacts and review
  tiers remain coherent after the merge
- evaluator-required skills named by the planner (`find-skills`, `init-repo`,
  and `spec`) are already present in `evals/cautilus/scenarios.json`, so no
  maintained scenario-registry mutation is required for this merge
- `narrative` source mapping now keeps `docs/handoff.md` as a source document
  again, matching the repo-owned map-source gate while leaving README mutation
  boundaries unchanged

## Outcome

- recommendation: `accept-now`
- routing notes: conflict resolution preserved the maintained routing cases and
  kept validation-closeout routing through `quality`

## Follow-ups

- broad quality closeout may still expose environment-specific test failures;
  keep runtime/tooling failures separate from routing regressions when triaging
