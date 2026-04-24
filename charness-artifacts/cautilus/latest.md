# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: teach `create-skill` and `premortem` to start skill/capability
  changes from the customer first-use path
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting public skill guidance, so
  existing startup routing must still pass while the customer-first authoring
  rule is explicit in checked-in skill surfaces

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/create-skill/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `cautilus instruction-surface test --repo-root .` (rerun after one
  unrelated flaky route miss)
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-skill --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id premortem --json`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T003030957Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl` or `spec` for the existing instruction-surface cases
- evaluator recommendation: `accept-now`
- note: `.cautilus/runs/20260424T002903742Z-run/` produced `3 passed / 1
  failed` on the existing validation-closeout route, selecting `hitl` instead
  of expected `quality`; rerun restored `accept-now`, so this slice records it
  as nondeterministic existing routing risk rather than a new prompt-surface
  contract change

## Scenario Review

- reviewed and updated the `create-skill` dogfood case so public-skill
  adapter/bootstrap/example changes must start from the changed skill's
  customer journey
- reviewed and updated the `premortem` dogfood case so first-use failure can
  be covered by the new `customer-of-this-capability` angle
- no maintained scenario-registry mutation was required in this slice; the
  existing instruction-surface routing proof remains a regression check rather
  than coverage of the new authoring rule itself

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the prompt-surface edits, and
  the changed guidance does not alter the maintained startup routing cases

## Follow-ups

- README/plugin export drift remains owned by the parallel README rewrite; do
  not use this proof slice to commit the current annotated README export
- consider a narrower maintained scenario later if customer-first skill
  authoring becomes a repeated regression rather than a checked dogfood rule
