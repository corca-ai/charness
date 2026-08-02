# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- Goal `2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round`. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A background test run reported "exit code 0" while its output showed 10 failures — and it happened TWICE, on two separate runs (10 failures, then 4).** I only caught both by reading the output file. Anything read from a completion summary rather than the artifact is a proxy. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)
- **Dup-ratchet fingerprints rotated twice mid-slice** — once on a refactor, once on removing a single unused import — costing three classify-and-recheck cycles before the ratchet went clean. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)

## Next-Time Checklist

- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- a slice that deletes or renames a module-level name should run the broad suite at its own boundary, not defer to closeout — `--skip-broad-pytest` is correct for additive slices and blind to this one. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)
- do not run a generated-surface sync while a background suite is reading the tree — four phantom failures came from exactly that, and they look identical to real ones until you rerun them in isolation. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)
- read the OUTPUT of a background command, never its completion summary. Two summaries this run said "exit code 0" over runs with 10 and 4 failures respectively. (source: `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`)

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
- `charness-artifacts/retro/2026-08-03-close-the-unreachable-file-class-and-widen-the-claims-round.md`
