# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- One goal run over the handoff backlog (aarch64 excluded by the operator), plus issue #458 added mid-run. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)

## Repeat Traps

- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A `git checkout -- tests/` silently reverted a conftest fixture** I had already written, and the suite still passed because this machine has a global git identity. The reviewer caught that the fix was not in the tree at all. A scoped revert with an unscoped path. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- **A named subagent spawn stranded ~8 minutes and a full review packet**, and I reported the findings unrecoverable without running `reviewer_result.py get` — the diagnostic the same contract ships for exactly that case. Running it later recovered a finding I never independently derived. The rule and the recovery path were both in a reference I had listed and not opened. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- **Iterated one line at a time against a counted limit** when trimming a debug artifact to its 180-line ceiling — four rounds — which is the exact counted-limit-as-retry-loop trap the repo already records. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)

## Next-Time Checklist

- a lesson that ships as prose only has not shipped. Both rules that bit this session were correct, checked in, and unread. Disposition: applied: the spawn-shape rule moved to always-loaded `AGENTS.md`, propagated to the consuming-repo template, and pinned by four tests in `tests/quality_gates/test_reviewer_result_delivery.py` (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- make backlog staleness checkable at chunk time rather than at review time — the chunker already parses `file:line` and issue refs from every entry, so it can report which cited paths/issues no longer resolve before an agent plans against them. Disposition: issue #459 (novel: no existing entry covers chunker-side staleness; the closest, D28, is about validator defaults) (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- the recurrence-class tag shipped this session has no data until retros carry it. This retro is the first to carry tags, which starts the corpus. Disposition: applied: recurrence-class tags on the Waste bullets above, grouped by `scripts/recent_lessons_lib.py` (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`)
- the release trigger closeout is persisted, but it covers the release delta only. Decide whether this session also owes a session retro; if it did substantive work, run `retro` before closing. (source: `charness-artifacts/retro/2026-07-27-v2-11-2-release-auto-retro.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-v2-11-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-v2-11-2-release-auto-retro.md`
