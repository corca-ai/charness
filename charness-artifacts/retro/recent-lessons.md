# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- The `close-the-copies-this-run-measured` goal: three slices against three filed issues. (source: `charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md`)

## Repeat Traps

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A finding repaired at one call site out of two.** Round 1 named a wrong predicate; I fixed the floor it pointed at and left the sibling gate, which converted a shared bypass into a live single-gate bypass. (source: `charness-artifacts/retro/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-retro.md`)

## Next-Time Checklist

- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- a repo-owned mutate-and-restore helper that refuses to report a kill unless the unmutated baseline first reported a passing test count. This is the Engelbart T-half; three hand-rolled harnesses in one run is the trigger. (source: `charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md`)
- add one line to the goal template's `## Agent Verification Plan` — **a mutation sweep states its baseline test COUNT before its first mutant**, and **at least one mutant per repair deletes the CALL SITE rather than the body**. Both are this run's measured misses and neither is currently written anywhere. (source: `charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md`)

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
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-retro.md`
- `charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md`
- `charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md`
- `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`
