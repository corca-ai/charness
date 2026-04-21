# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: connect managed install/doctor to repo onboarding and tighten
  `create-skill` plus `init-repo` so skill-bearing repos freeze current intent
  and proof decisions before broad public-skill edits
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes repo-owned `create-skill` and `init-repo`
  instruction surfaces, but it should preserve the checked-in first-skill
  routing contract while making repo onboarding and skill-proof planning more
  explicit.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`
- `truth_surface_change`

## Prompt Surfaces

- `skills/public/create-skill/SKILL.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/default-surfaces.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- checked-in `AGENTS.md` still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`

## Scenario Review

- representative scenario 1: after `charness init` and host restart, running
  `charness doctor` from a consumer repo that only has a thin `README.md`
  should now surface repo onboarding as the next repo-level move instead of
  implying that host install success means the repo is ready for broad work
- representative scenario 2: a skill-bearing repo normalized through
  `init-repo` should keep `AGENTS.md` short but still tell later sessions that
  semantic skill edits must freeze current intent through reviewed dogfood,
  maintained evaluator scenarios, or checked-in scenario review proof
- representative scenario 3: when improving an existing public skill with
  `create-skill`, the operator should decide `preserve` vs `improve` and the
  proof carrier before broad trigger rewrites instead of discovering that
  obligation only during closeout
- maintained scenario registry review: `create-skill` already maps to
  `representative-skill-contracts`, and `init-repo` already maps to
  `init-repo-adapter-bootstrap`, `init-repo-inspect-states`, and
  `init-repo-compact-skill-routing-discoverability`, so this slice did not yet
  need a new checked-in scenario id

## Outcome

- recommendation: `accept-now`
- routing notes: repo onboarding guidance and public-skill proof planning are
  more explicit now, while the maintained startup routing surface still matched
  the evaluator expectation

## Follow-ups

- if repo onboarding proves too noisy for harmless read-only repos, tune the
  repo-detection heuristic rather than dropping the onboarding check entirely
- if future `create-skill` or `init-repo` edits change behavior beyond the
  current representative scenario coverage, add the missing maintained scenario
  in `evals/cautilus/scenarios.json` instead of relying on prose-only review
