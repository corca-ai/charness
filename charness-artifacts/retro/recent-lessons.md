# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- This retro covers the shaped goal's five slices: selecting the evidence-carrying control for #499/#491, building the semantic reviewer question, assigning the #502 receipt owner, repairing the #500/#501/#497 producer/export boundaries, and staging the final closeout carrier. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- The broad verification, fresh-eye rounds, and carrier checks were necessary safety work at proof and issue boundaries, not waste. No host metric evidence supports a per-goal runtime or token comparison. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)
- **Wrong retro binding at the completion boundary** — the goal cited `2026-08-04-session-retro.md`, whose `Goal:` names a different objective. The goal status was already `complete`, but the authoritative closeout validator rejected the evidence binding. The avoidable waste was not the validator run; it was allowing a claimed completion to carry a merely existing artifact instead of a goal-bound one. Decision: fix now by creating this bound retro, updating the goal's citation, and rerunning the evidence gate. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

## Next-Time Checklist

- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- carry the semantic reviewer question and the worked #499/#491 application in the critique packet and its source/plugin mirrors. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)
- freeze quality artifacts and host probes before broad verification so the proof record and the implementation surface share one identity. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)
- keep rolling telemetry separate from a per-run receipt until a named consumer, retention, and stale-state contract exists. (source: `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`)

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
- `charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md`
