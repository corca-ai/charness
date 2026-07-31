# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run, end to end: handoff chunked routing over the live backlog, the operator's two queued decisions answered, then `achieve` shaped and `/goal` ran the "un-dispositioned stragglers" chunk to completion. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Not waste, though it looks like it:** ten review rounds on five slices. Nine of them changed the code. The one that did not (the disposition review) is the one the contract requires anyway. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- **The slice-log helper mangled a slice report.** Backticks in shell arguments were command-substituted, and the recorded report lost every code span before I noticed and rewrote it by hand. Pure transport waste. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)

## Next-Time Checklist

- **a `blocking_targets` payload that names subprocess-only coverage paths** — carried forward unapplied from two retros now, and this session's nine uncovered lines included exactly that shape. Still owed its own two-round review. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- **a threshold defended by prose gets withdrawn; a threshold defended by a checked-in script survives.** The S3 floor is the worked example — script, recorded run, and a test that re-runs the recorded run. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- **run the existing suite against a repair before designing the next one.** Both reverted repairs this session were designed on top of an untested predecessor; the fixture regression in slice 4 was caught by a test that already existed and would have been free to run. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)
- **the two-round rule is four-for-four, and the class arrives in the direction the author was not looking.** Written into the goal's slice log and the recent-lessons digest, not just here. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-01-session-retro.md`
