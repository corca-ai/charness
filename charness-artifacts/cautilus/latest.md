# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: tighten startup `find-skills` routing, strengthen repo-reality
  bootstrap in `ideation` and `spec`, and restructure the README entry surface
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes repo-owned instruction surfaces and truth docs, but
  it should preserve the first-skill routing contract while making startup
  `find-skills` bootstrap more explicit and reducing checked-in routing noise.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `README.md`
- `skills/public/ideation/SKILL.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/spec/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- checked-in `AGENTS.md` still preserves
  `bootstrapHelper=find-skills` plus `workSkill=impl`
- the new compact startup-bootstrap cases both passed:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: a task-oriented session now sees a short
  checked-in routing block that explicitly forces a startup `find-skills`
  pass before broader exploration instead of copying a long skill catalog
- representative scenario 2: `ideation` and `spec` now inspect current repo
  files, code, tests, and operator docs before opening clarification branches,
  reducing fake ambiguity from chat-only discovery
- representative scenario 3: the README now leads with hook plus quick start,
  then moves the concept inventory below as numbered sections instead of a
  top-of-file table

## Outcome

- recommendation: `accept-now`
- routing notes: the shorter `AGENTS.md` routing block still reliably triggers
  startup `find-skills` bootstrap, and the compact synthetic `impl` and `spec`
  routes both matched the new evaluator expectation

## Follow-ups

- if more public skills need stronger repo-reality bootstrap, reuse the same
  "inspect current surfaces before asking" pattern instead of inventing a new
  clarify stage
- if startup `find-skills` proves too sticky for obviously direct requests in
  future dogfood, rerun as `goal: improve` with a compare-backed routing study
