# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: add adapter-driven cautilus proof planning, make closeout a proof
  gatekeeper instead of an evaluator runner, and strengthen narrative /
  validation guidance around scenario review plus `why` / `what` / `how`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes proof policy and high-leverage prompt guidance, but
  it should not silently rewrite first-skill routing expectations or collapse
  repo truth-shaping into fallback inference.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`
- `cross_repo_communication_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`
- `skills/public/impl/SKILL.md`
- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/landing-rewrite-loop.md`
- `skills/public/narrative/references/cross-repo-issue-shaping.md`
- `skills/public/quality/references/prompt-asset-policy.md`
- `skills/public/spec/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 1 failed / 0 blocked`
- failing case: `checked-in-bootstrap-before-impl`
- regression note: compact direct `impl` routing and both `spec` routing cases
  still passed, but the checked-in surface still did not register
  `find-skills` as the explicit bootstrap helper in the evaluator's routing
  output

## Scenario Review

- representative scenario 1: high-leverage prompt changes now route through an
  adapter-visible proof plan instead of assuming cautilus auto-runs during
  closeout
- representative scenario 2: `narrative` guidance now stops to shape adapter,
  reader, and truth-surface contracts before rewriting README-like landing
  surfaces in earnest
- representative scenario 3: cross-repo issue shaping now keeps `why` and
  `what` ahead of `how`, which matches the new intended coordination contract

## Outcome

- recommendation: `reject`
- routing notes: the new proof-planning and narrative-shaping policy landed,
  but the checked-in bootstrap-helper expectation still disagrees with the
  current evaluator observation for the workspace default surface

## Follow-ups

- isolate whether the `checked-in-bootstrap-before-impl` failure is a real
  prompt-surface regression or an evaluator expectation drift around the
  mandatory session-start `find-skills` rule
- if the repo decides this policy slice should claim behavioral improvement
  rather than preservation, rerun as `goal: improve` with an A/B compare block
