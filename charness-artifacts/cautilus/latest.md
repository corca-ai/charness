# Cautilus Dogfood
Date: 2026-04-20

## Trigger

- slice: clarify lifecycle ownership for materialized install surfaces after
  `premortem` subagent enforcement and compress `handoff` into a more
  pointer-heavy baton pass
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes `premortem`, `handoff`, `quality`, and `spec`
  wording around fresh-eye subagent requirements and baton-pass compression,
  but it should not change the maintained public instruction routing contract

## Prompt Surfaces

- `skills/public/handoff/SKILL.md`
- `skills/public/handoff/references/premortem-loop.md`
- `skills/public/handoff/references/spill-targets.md`
- `skills/public/handoff/references/state-selection.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/premortem/references/angle-selection.md`
- `skills/public/premortem/references/subagent-capability-check.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/fresh-eye-premortem.md`
- `skills/public/spec/SKILL.md`
- `skills/public/spec/references/premortem-loop.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate-skills.py`
- `python3 scripts/check-skill-contracts.py --repo-root .`
- `python3 scripts/validate-handoff-artifact.py --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in surface still preserves the maintained
  `find-skills -> impl` path, compact direct implementation still routes to
  `impl`, and direct contract-shaping still routes to `spec` even after the
  stronger subagent and handoff wording

## Follow-ups

- if host runtimes still make subagent availability feel optional, lift that
  capability into a more explicit machine-readable contract instead of relying
  on prose alone
- keep `docs/handoff.md` pointer-heavy and push fresh metrics, counts, and
  historical proof back to their owning artifacts before they re-inflate the
  baton pass
