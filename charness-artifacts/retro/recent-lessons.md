# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run end to end — handoff chunked routing, two operator decisions, then `achieve` shaped and `/goal` ran the "un-dispositioned stragglers" chunk through five slices and seven commits. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Four dup-ratchet cycles at the closeout boundary.** Each of my edits rotated a boilerplate family fingerprint (an import block, a `format_human` twin), and each rotation surfaced only when the aggregate ran. Two were genuine extractions worth doing; three were classifications of unextractable import preambles. (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)
- **Not waste, though it looks like it:** the sequence "reproduce → repair → revert-check" ran five times and never once was skipped. That is the contract working, and it is what let S8 be refuted instead of "fixed". (source: `charness-artifacts/retro/2026-07-31-session-retro.md`)

## Next-Time Checklist

- **a goal's own claims are a verdict surface and got one review round, at the end, which found two blockers.** The slice-level discipline has no goal-level analogue. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- **a lesson learned on one file is not learned until the second file of its class passes without review.** The second measurement script repeated all three of the first one's defects, in the same session, with the first still in context. (source: `charness-artifacts/retro/2026-08-01-sweep-high-rows-goal-retro.md`)
- **a refusal-category renderer detector**, per the Portable Candidate, once a second instance appears. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- a self-authored constraint in a goal artifact is not a check. This session violated its own stop condition within two hours of writing it, and a reviewer, not the author, caught it. Either the constraint becomes machine-read or the slice's first move is to read its own goal's Boundaries against the planned diff. (source: `charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md`)

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
- `charness-artifacts/retro/2026-08-01-session-retro.md`
- `charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md`
- `charness-artifacts/retro/2026-08-01-sweep-high-rows-goal-retro.md`
