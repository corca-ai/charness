# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- A week-audit of the last 161 commits (a 5-lens dynamic workflow, each lens adversarially challenged) reported that the repo's biggest regression was operator-facing: five of the last twelve releases published a one-line body, and one of them was the release whose notes amended an earlier release's wrong migration instruction. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **Four serial validator rejections on the critique artifact** (`bin`, `evidence`, `action` enum values, then a stale binding) because I hand-authored instead of starting from `scaffold_critique_artifact.py` — which the validator's own hint names. Same for the handoff: three trim cycles against the length cap and one rejected version literal, all of which `check_doc_authoring_preflight.py` reports up front. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)
- **I ran the changed-line gate before committing, where its verdict is a false green, and it told me so in its own warning.** The recent-lessons digest already carries "read the `reason`, not the exit code" from the prior session. Running it in the wrong order cost one full gate cycle and nearly shipped two dead guards. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)

## Next-Time Checklist

- **commit before reading a changed-line verdict, always.** The gate is a false green over uncommitted pool files and says so; the order is not optional. Recorded in the handoff `## Current State` so it is a pickup fact, not a remembered one. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)
- **make the pre-commit changed-line invocation refuse rather than warn**, per the Engelbart counterfactual. The gate already computes the uncommitted-pool condition and emits it; converting that to a refusal in the pre-commit path removes the false-green window instead of labelling it. Not filed as an issue this session — it belongs with D40's owner decisions. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)
- **start critique and handoff artifacts from their scaffolds.** Four serial enum rejections and three length-trim cycles were all pre-announced by `scaffold_critique_artifact.py` and `check_doc_authoring_preflight.py`. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)
- **verify the reviewer boundary at review return, before making any repair.** A verify run after parent writes cannot attribute drift, which downgrades an otherwise-clean round to a structural claim. (source: `charness-artifacts/retro/2026-07-29-session-retro.md`)

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
