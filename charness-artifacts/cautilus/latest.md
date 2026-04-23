# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: implement issue #64 delegated-review posture for `init-repo` and
  `quality`, including AGENTS spawn authorization, adapter recommendation
  fields, quality advisory/delegated-review reporting, and plugin export sync
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting AGENTS, adapter, public skill,
  and quality-reference surfaces, so maintained startup and closeout routing
  must stay stable while the new review posture becomes visible

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/init-repo-adapter.yaml`
- `.agents/quality-adapter.yaml`
- `AGENTS.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/normalization-flow.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/adapter-gate-review.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- first instruction-surface run for this slice:
  `.cautilus/runs/20260423T225726810Z-run/`, recommendation `reject`
- rejected because `validation-closeout-routes-before-hitl` selected
  `quality` but failed to record `find-skills` as the required bootstrap helper
- AGENTS was tightened to say the validation routing rule does not skip
  startup `find-skills`
- instruction-surface summary after repair:
  `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T225842725Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- reviewed the maintained validation-closeout case after the first run: the
  intended behavior remains `find-skills` bootstrap plus public `quality`
  before HITL/manual review, not direct Cautilus selection
- reviewed issue #64 prompt-surface changes against current dogfood: `init-repo`
  now exposes reviewable recommendations, while `quality` now exposes advisory
  and delegated-review status
- scenario-registry decision: no maintained scenario mutation in this slice;
  instruction-surface routing remains covered, and recommendation-queue
  behavior is locked by repo tests plus refreshed dogfood evidence

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the AGENTS bootstrap wording
  repair, and task-completing `init-repo`/`quality` review work now has an
  explicit spawn-authorized posture

## Follow-ups

- decide separately whether maintained Cautilus scenarios should gain a
  dedicated issue #64 recommendation-queue case; this slice did not mutate the
  scenario registry
