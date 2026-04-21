# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: add deterministic public-skill fallback policy tiers and tighten
  high-leverage missing-adapter behavior for `narrative`, `hitl`, and
  `release`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes prompt-facing fallback guidance and policy
  classification, but it should preserve the existing first-skill routing
  contract while making missing-adapter behavior more explicit.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/announcement/SKILL.md`
- `skills/public/create-skill/references/portable-authoring.md`
- `skills/public/hitl/SKILL.md`
- `skills/public/narrative/SKILL.md`
- `skills/public/release/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- checked-in bootstrap routing now preserves
  `bootstrapHelper=find-skills` plus `workSkill=impl`
- compact direct `impl` routing and both `spec` routing cases still passed

## Scenario Review

- representative scenario 1: `narrative` now treats missing adapter on a
  high-leverage truth surface as a stop-and-shape seam instead of an implicit
  fallback
- representative scenario 2: `hitl` now refuses to start a resumable review
  loop in earnest until adapter-owned state, rules, and queue ownership are
  explicit
- representative scenario 3: `release` now stops at adapter scaffolding when
  the release boundary is missing, while `announcement` stays draftable under
  visible inferred-default fallback

## Outcome

- recommendation: `accept-now`
- routing notes: fallback tier wording did not regress the checked-in
  instruction-surface cases, and the mandatory startup `find-skills` bootstrap
  case now matches the evaluator expectation again

## Follow-ups

- if a current `visible` skill starts repeatedly rewriting repo-truth or
  review-policy surfaces, consider promoting it from `visible` to `block`
- if the repo later claims fallback-policy behavior improved beyond preserved
  routing clarity, rerun as `goal: improve` with an A/B compare block
