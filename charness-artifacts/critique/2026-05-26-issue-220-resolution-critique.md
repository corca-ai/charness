# Issue 220 Resolution Critique

Date: 2026-05-26
Target: code critique for GitHub issue #220 resolution
Fresh-Eye Satisfaction: nested-delegated
Packet Consumed: charness-artifacts/critique/2026-05-26-115838-packet.md

## Change

Make `find-skills --recommend-for-task` surface verbatim-named public skills.
Adds `skills/public/find-skills/scripts/public_skill_recommendations.py`
(`public_skill_recommendations_for_task` + Unicode-word-boundary matcher),
wires `public_skill_recommendations` / `public_recommendation_query` into the
payload, suppresses the misleading support "empty result" note when a public
skill matched, keeps the durable inventory artifact query-free, and syncs the
plugin export. Closes the public-skill blind spot the reporter hit twice.

## Angles

Three bounded angle subagents (matching semantics, contract/cross-surface
consistency, JTBD/recurrence) plus one separate counterweight pass.

## Counterweight Triage

### Act Before Ship

- ASCII-only lookarounds treated an adjacent CJK letter as a boundary, so
  `hitl스킬` false-matched `hitl`. Korean is a first-class trigger language.
  Switched to a Unicode word boundary (`\b`); added two CJK-adjacency tests.

### Bundle Anyway

- Regenerated the durable `charness-artifacts/find-skills/latest.{json,md}` so
  the capability map carries the new keys; this also dropped stale
  `installed-plugin-support` entries that had leaked absolute host paths.

### Over-Worry

- None. Every surfaced concern was grounded or a legitimately-deferred gap.

### Valid but Defer

- Path-embedded token match (`spec` inside `index.spec.md`) and ranking
  prominence over co-present tool/support signals (reporter direction #3):
  needs matcher-semantics + ranking work, not a one-liner.
- Korean-noun / transliteration matching (`이슈` → `issue`, reporter repro #2):
  needs a fuzzy/transliteration layer.
- Trusted-skill layer is the same "whole layer invisible to the recommend
  path" blind spot (`trusted_entries` never feed any `*_recommendations_for_task`).

## Next Move

Ship the narrow high-precision slice (reporter direction #1 + partial #2).
Record the three deferred gaps in the #220 close comment so it is not closed
silently on the two still-open footguns; recommend one combined follow-up issue.
