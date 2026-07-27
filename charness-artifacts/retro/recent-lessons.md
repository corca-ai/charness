# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run over the handoff backlog (aarch64 excluded by the operator), plus issue #458 added mid-run. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A `git checkout -- tests/` silently reverted a conftest fixture** I had already written, and the suite still passed because this machine has a global git identity. The reviewer caught that the fix was not in the tree at all. A scoped revert with an unscoped path. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- **A named subagent spawn stranded ~8 minutes and a full review packet**, and I reported the findings unrecoverable without running `reviewer_result.py get` — the diagnostic the same contract ships for exactly that case. Running it later recovered a finding I never independently derived. The rule and the recovery path were both in a reference I had listed and not opened. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)

## Next-Time Checklist

- a lesson that ships as prose only has not shipped. Both rules that bit this session were correct, checked in, and unread. Disposition: applied: the spawn-shape rule moved to always-loaded `AGENTS.md`, propagated to the consuming-repo template, and pinned by four tests in `tests/quality_gates/test_reviewer_result_delivery.py` (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- guard the irreversible entrypoints, not the inner writes. `publish_release.py` and `issue_close.py` should refuse a foreign-copy invocation at the entrypoint, where the operator can still act, rather than failing partway through bump/sync/quality. This is the next slice, and it is `P5`-shaped: a form check at an irreversible boundary, not a new judgment gate. (source: `charness-artifacts/retro/2026-07-27-session-retro.md`)
- make backlog staleness checkable at chunk time rather than at review time — the chunker already parses `file:line` and issue refs from every entry, so it can report which cited paths/issues no longer resolve before an agent plans against them. Disposition: issue #459 (novel: no existing entry covers chunker-side staleness; the closest, D28, is about validator defaults) (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- the recurrence-class tag `guard-adjacent-to-action` is introduced by this retro across three Waste bullets, so `recent_lessons_lib` grouping has a seed for it. (source: `charness-artifacts/retro/2026-07-27-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
