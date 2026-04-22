# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: make `cautilus` adaptive mode auto-run prompt proof by default and
  reserve explicit confirmation for maintained scenario-registry mutation
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes `create-skill` and `quality` prompt-shaping
  references plus the repo validation docs, but it should preserve the
  checked-in startup routing contract while changing when adaptive proof asks
  for operator confirmation.

## Change Intent

- `prompt_affecting_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/create-skill/references/adapter-pattern.md`
- `skills/public/quality/references/prompt-asset-policy.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T071526737Z-run/`
- checked-in startup routing still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: `create-skill` guidance now treats visible
  artifacts as history-default and `latest.md` as an optional current pointer,
  which changes authoring policy without changing first-skill routing
- representative scenario 2: prompt-surface policy now treats adaptive mode as
  auto-run for regression proof plus short scenario review, rather than asking
  before every high-leverage prompt change
- maintained scenario registry review: this slice changes proof-execution
  policy, not the maintained startup routing expectations in
  `evals/cautilus/scenarios.json`, so no checked-in scenario id had to change
  yet

## Outcome

- recommendation: `accept-now`
- routing notes: maintained startup routing stayed green, and adaptive policy
  now leaves scenario review inside autonomous proof while keeping
  `scenarios.json` mutation as the explicit-confirmation seam

## Follow-ups

- migrate history-default artifact families such as `release`,
  `announcement`, `cautilus`, and `narrative` onto a shared
  `dated record + optional latest pointer` helper
- if a future slice changes maintained routing expectations rather than only
  proof-execution policy, ask before mutating `evals/cautilus/scenarios.json`
- keep `docs/public-skill-dogfood.json` aligned when `create-skill` or
  `quality` semantics move again
