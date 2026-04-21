# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: add sparse named-expert anchors to public skill cores plus the
  `quality` lens reference and README examples
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice adds retrieval anchors without changing the intended
  routing contract or swapping skill boundaries. Existing first-skill behavior
  must stay stable while the wording becomes more distinctive.

## Prompt Surfaces

- `skills/public/create-cli/SKILL.md`
- `skills/public/debug/SKILL.md`
- `skills/public/find-skills/SKILL.md`
- `skills/public/hitl/SKILL.md`
- `skills/public/ideation/SKILL.md`
- `skills/public/narrative/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/quality-lenses.md`
- `skills/public/release/SKILL.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: checked-in bootstrap still selects `find-skills` before
  `impl`, and direct contract-shaping requests still route to `spec`

## Follow-ups

- if a future anchor rewrite changes routing language, trigger phrasing, or
  skill-boundary wording rather than adding sparse recall cues, refresh this
  artifact as `goal: improve` with an A/B compare block
- keep additive expert anchors sparse; if adjacent skills start accumulating
  overlapping names, move the overlap back into references before it becomes
  decoration
