# Cautilus Dogfood
Date: 2026-04-20

## Trigger

- slice: tighten `handoff` reference discipline so always-loaded host
  instruction surfaces are non-default and the current baton pass drops
  redundant `AGENTS.md`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes `handoff` wording around reference selection and
  host-injected instruction surfaces, but it should not change the maintained
  public instruction routing contract

## Prompt Surfaces

- `skills/public/handoff/SKILL.md`
- `skills/public/handoff/references/document-seams.md`
- `skills/public/handoff/references/state-selection.md`

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
  `impl`, and direct contract-shaping still routes to `spec` after the
  tighter handoff reference wording

## Follow-ups

- keep always-loaded host instruction surfaces out of handoff `References`
  unless omitting them would change the first move
- keep `docs/handoff.md` pointer-heavy and continue pushing durable detail back
  to its owning artifacts before the baton pass re-inflates
