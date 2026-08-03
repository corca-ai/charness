# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal, five slices, seven commits, four issues repaired (#487, #488, #489, and #490 which the goal's own activation produced). (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Four dup-ratchet hard blocks, none of them new duplication** — every one a span shift bringing a pre-existing boilerplate parallel over the threshold. (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`)
- **The unplanned artifact repair came first.** ~1 slice of budget reconstructing a goal artifact rather than pursuing the goal. Cost created by the previous session's write, not avoidable in-session. (source: `charness-artifacts/retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md`)

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
