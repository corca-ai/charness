# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: merge the narrative adapter review work and the customer-first skill
  authoring follow-up into the current README/main worktree
- claim: preserve routing while improving first-use behavior for narrative
  adapters and public-skill authoring

## Validation Goal

- goal: preserve
- reason: this merge brings in prompt-affecting public skill guidance, adapter
  review helpers, and dogfood contracts; existing startup routing must still
  pass while the new customer-first authoring rule and narrative adapter gate
  stay explicit in checked-in surfaces

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/narrative-adapter.yaml`
- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/adapter-contract.md`
- `skills/public/narrative/references/landing-rewrite-loop.md`
- `skills/public/create-skill/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `cautilus instruction-surface test --repo-root .` (rerun after one
  unrelated flaky route miss)
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id narrative --json`
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
  of expected `quality`; rerun restored `accept-now`, so this is recorded as a
  nondeterministic existing routing risk rather than a new prompt-surface
  contract change

## Scenario Review

- reviewed the `narrative` public-skill dogfood case; the expected route and
  durable artifact remain `narrative` and
  `charness-artifacts/narrative/latest.md`
- direct checks against `../cautilus`, `../ceal`, and `../crill` showed the
  adapter reviewer catches missing adapters, volatile mutable sources, stale
  paths with closest-path suggestions, and path-like entrypoint drift before
  README rewriting starts
- reviewed and updated the `create-skill` dogfood case so public-skill
  adapter/bootstrap/example changes must start from the changed skill's
  customer journey
- reviewed and updated the `premortem` dogfood case so first-use failure can
  be covered by the new `customer-of-this-capability` angle
- no maintained scenario-registry mutation was required in this merge slice;
  the existing instruction-surface routing proof remains a regression check
  rather than full semantic coverage of the new authoring rule itself

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the prompt-surface edits, and
  the changed guidance does not alter the maintained startup routing cases

## Follow-ups

- the current branch still carries README HITL draft/comment drift; markdown,
  command-doc, and plugin README export gates remain owned by the README
  rewrite slice
- consider a narrower maintained scenario later if customer-first skill
  authoring becomes a repeated regression rather than a checked dogfood rule
