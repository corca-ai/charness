# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- Release publish triggered a configured automatic session retro for `v3.0.0`. (source: `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`; sources: 125)
- NOT MEASURED HERE: this session's own rework. A release-delta detector cannot see it; only a session retro can. (source: `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`; sources: 5)

## Next-Time Checklist

- the release trigger closeout is persisted, but it covers the release delta only. Decide whether this session also owes a session retro; if it did substantive work, run `retro` before closing. (source: `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`; sources: 5)
- **a rationale is a claim.** Writing "the adapter contract now documents this" without checking reproduced, inside the justification for a fix, the exact class the slice was closing. Verify the compensating control you cite in the same breath as citing it. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **run a reachability probe during shaping for any slice whose value claim names a consumer, host, or environment the session cannot see.** Slice 1 was ranked #1 on a claim three `ls` commands falsified. This is the Klein counterfactual, and it is cheaper than a review round. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)
- **teach the changed-line gate to say when a blocked line's only coverage is a subprocess test.** The gate already emits `blocking_targets` with source text; the mapper already knows which tests reference the file. Reporting "reached only via `run_script`" would collapse this session's four-cycle habit into a one-line diagnosis. Filed as a Next Improvement, not applied: it changes a blocking gate's payload and owes its own two-round review. (source: `charness-artifacts/retro/2026-07-30-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-42-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-43-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-44-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-45-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-47-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-48-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-49-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-15-v0-50-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-50-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-52-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-56-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-7-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-8-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-02-v0-58-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-03-v0-59-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-03-v0-60-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-04-v0-61-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-04-v0-62-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-09-v0-63-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-09-v0-63-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-64-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-65-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-66-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-7-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-8-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-10-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-11-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-9-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-16-v1-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-2-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-3-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v2-0-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-19-v2-2-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-19-v2-2-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-3-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-3-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-4-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-4-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-21-v2-4-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-22-v2-4-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-25-v2-5-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-25-v2-6-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-25-v2-7-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-25-v2-8-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-25-v2-9-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-v2-10-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-v2-11-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-v2-11-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-07-27-v2-11-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-27-v2-11-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-29-v2-12-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-30-session-retro.md`
- `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`
