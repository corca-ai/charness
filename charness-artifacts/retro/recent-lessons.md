# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run: handoff chunked routing picked chunk 1 (the 2026-07-28 triage sweep's remaining high rows), `achieve` shaped it, and `/goal` ran it to completion. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Four dup-ratchet cycles at the closeout boundary.** Each of my edits rotated a boilerplate family fingerprint (an import block, a `format_human` twin), and each rotation surfaced only when the aggregate ran. Two were genuine extractions worth doing; three were classifications of unextractable import preambles. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)
- **Not waste, though it looks like it:** the sequence "reproduce → repair → revert-check" ran five times and never once was skipped. That is the contract working, and it is what let S8 be refuted instead of "fixed". (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)

## Next-Time Checklist

- **run the pre-mortem against the pinning tests at shaping time.** For a goal whose slices change verdict logic, list the checked-in assertions that pin today's behavior *before* writing the slice plan; three of five rows had one, and one plan slice was internally contradictory because of it. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)
- teach the changed-line gate's `blocking_targets` payload to name when a blocked line's only coverage path is a subprocess test — carried forward from the 2026-07-30 retro, still unapplied, still owed its own two-round review. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)
- the two-round rule's evidence is now three-for-three — every measured slice that changed verdict logic shipped a fix carrying the class it fixed, and round 2 caught it each time. Recorded here and in the goal's slice log. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)
- **when a concept is implemented a second time inside one work unit, stop and unify it before the third.** Cheap trigger: after any fix that walks markdown structure (fences, headings, frontmatter), grep for sibling walks before moving to the next slice. This session paid two review findings and a ratchet cycle for skipping it. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-07-31-session-retro.md`
