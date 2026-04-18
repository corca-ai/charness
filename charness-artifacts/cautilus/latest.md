# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `find-skills` canonical inventory artifact contract
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: keep the checked-in `find-skills` routing and artifact contract stable
  while stopping recommendation-query flags from rewriting the canonical
  `latest.*` inventory artifact

## Prompt Surfaces

- `skills/public/find-skills/SKILL.md`

## Commands Run

- `pytest -q tests/test_find_skills.py`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in bootstrap case still routes as
  `bootstrapHelper=find-skills` plus `workSkill=impl`; compact no-bootstrap
  implementation still routes to `impl`; contract-shaping cases still route to
  `spec`
- artifact notes: recommendation-query flags now stay in stdout payloads while
  `charness-artifacts/find-skills/latest.*` remains the canonical local-first
  inventory artifact

## Follow-ups

- if `find-skills` later needs durable query-specific evidence, add a separate
  artifact family instead of overloading `latest.*`
- keep treating incidental invocation-shape churn as auto-revert cleanup, not
  as a user-facing judgment call
