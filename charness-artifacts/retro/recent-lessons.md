# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run: the armed changed-line pre-push lane's known holes, taken from the handoff chunker's ranked chunk 1 and shaped through `achieve`. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Four separate changed-line BLOCKs, all the same shape.** Every slice added verdict branches exercised only through subprocess runs, which the coverage mapper cannot see, so each slice committed, got blocked, and added in-process tests. Four cycles of a lesson that was fully learned after the first. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **Not waste, and worth separating:** the six review rounds and the reproduce- first probes. Every round changed the design, and four of the six caught a defect in the repair rather than in the original. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)

## Next-Time Checklist

- **a rationale is a claim.** Writing "the adapter contract now documents this" without checking reproduced, inside the justification for a fix, the exact class the slice was closing. Verify the compensating control you cite in the same breath as citing it. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **run a reachability probe during shaping for any slice whose value claim names a consumer, host, or environment the session cannot see.** Slice 1 was ranked #1 on a claim three `ls` commands falsified. This is the Klein counterfactual, and it is cheaper than a review round. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **teach the changed-line gate to say when a blocked line's only coverage is a subprocess test.** The gate already emits `blocking_targets` with source text; the mapper already knows which tests reference the file. Reporting "reached only via `run_script`" would collapse this session's four-cycle habit into a one-line diagnosis. Filed as a Next Improvement, not applied: it changes a blocking gate's payload and owes its own two-round review. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **commit before reading a changed-line verdict, always.** The gate is a false green over uncommitted pool files and says so; the order is not optional. Recorded in the handoff `## Current State` so it is a pickup fact, not a remembered one. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-07-29-session-retro.md`
- `charness-artifacts/retro/2026-07-30-session-retro.md`
