# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal, three slices, three commits, three issues repaired (#494, #493, #492). (source: `charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A doc correction shipped FALSE.** Slice B's repair of a wrong claim about `mutation_testing` asserted a new wrong claim (that every blank sub-key errors; a blank nested BLOCK header does not). Caught by round 2. The repair was to pin it with a test, not to word it more carefully. (source: `charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md`)
- **A false-positive control varied the wrong axis.** Slice B's control used DEFAULT values, so `merged == default` masked the mis-naming bug; the broad suite found it. A control is only a control against the inputs it varies, and mine varied presence without varying value. (ONE measured instance — an earlier draft said "every" and "twice" and could name only this one.) (source: `charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md`)

## Next-Time Checklist

- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- a gate refusing a change whose owning reference still describes the old behaviour — issue #491. (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`)
- a standalone-import check for every module in a package, generalizing the one-pair guard already committed — issue #492. (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`)
- none surfaced by this review beyond the four already filed. (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-disposition-review.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
- `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-disposition-review.md`
- `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`
- `charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md`
