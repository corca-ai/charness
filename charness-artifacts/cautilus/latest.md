# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: add `ruff` as a quality validation integration, repair the merged
  narrative adapter helper that `ruff` flagged, and make missing validation
  binaries explicit setup work in the `quality` skill
- claim: preserve startup routing while improving quality closeout behavior for
  missing local validation tools

## Validation Goal

- goal: preserve
- reason: this slice changes one public skill prompt surface and the README
  integration map; existing startup routing should remain stable while the new
  missing-binary rule stays visible through `quality`

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/quality/SKILL.md`
- `README.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260424T011541756Z-run/`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the existing instruction-surface
  cases
- evaluator recommendation: `accept-now`

## Scenario Review

- reviewed the generated `quality` public-skill dogfood case; the route remains
  `quality` and the durable artifact remains
  `charness-artifacts/quality/latest.md`
- the new `quality` rule specifically covers the observed miss: an existing
  gate blocked by a missing validation binary must become setup work with an
  install/verify path or an explicit user question, not a silent skip
- no maintained scenario-registry mutation was required; this is a preserve
  proof plus checked dogfood review for the changed public skill surface

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed after the prompt-surface edit, and the
  changed guidance does not alter the maintained startup routing cases

## Follow-ups

- if missing local validation binaries recur across repos, consider adding a
  direct scenario for quality closeout on a missing manifest-backed tool
