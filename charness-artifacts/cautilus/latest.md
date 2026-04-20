# Cautilus Dogfood
Date: 2026-04-20

## Trigger

- slice: tighten `release` closure semantics after issue `#45`, separating
  local/tag completion from workflow publication and public release surface
  verification
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes release-skill wording and release adapter guidance,
  but it should not change the maintained public instruction routing contract

## Prompt Surfaces

- `.agents/release-adapter.yaml`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/adapter-contract.md`
- `skills/public/release/references/install-surface.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `pytest -q tests/quality_gates/test_release_publish.py tests/quality_gates/test_release_real_host.py`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in surface still preserves the maintained
  `find-skills -> impl` path, compact direct implementation still routes to
  `impl`, and direct contract-shaping still routes to `spec`

## Follow-ups

- keep `tag pushed`, workflow publication, and `public release surface
  verified` as separate release states instead of collapsing them back into one
  publish-complete phrase
- if the repo later adds async public-release verification helpers, wire them
  into the release adapter/helper contract rather than leaving the boundary as
  prose-only closeout guidance
