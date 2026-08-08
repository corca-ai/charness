# Recent Retro Lessons

## Current Focus

- One session that started from "design the next work" and ended having shipped it. (source: `charness-artifacts/retro/2026-08-09-session-retro.md`)
- The `make-proof-surfaces-report-what-they-observed` goal, all eight slices, ending in the `v4.0.0` release and push. (source: `charness-artifacts/retro/2026-08-09-make-proof-surfaces-report-what-they-observed.md`)

## Repeat Traps

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- A crude regex proxy produced "14 checks cannot fail" including `pytest` and `dup-ratchet`. Discarded before use, but it was run and reported before being sanity-checked. All three are the same shape: **I spoke before measuring, on questions a command could answer in seconds.** The repo already names this ("Settle by measuring, not by debating, when a command can answer") and it still fired three times. **Not waste, recorded so it is not mistaken for it:** the census's 744K subagent tokens bought a decision on an open `question`-labelled issue that had been unanswerable for days, and its adversarial pass prevented four wrong deletions. The gate-runtime telemetry (peak 475s) is the standing suite doing its job; this session ran targeted modules instead and paid it only at commit boundaries. (source: `charness-artifacts/retro/2026-08-09-session-retro.md`)

## Next-Time Checklist

- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- a check that flags a test asserting an external tool's output shape from a hand-written string when no captured fixture for that tool exists. (source: `charness-artifacts/retro/2026-08-09-make-proof-surfaces-report-what-they-observed.md`)
- **capability**: `achieve`'s Before phase should ask, for each remedy a durable record proposes, whether that remedy's premise still holds — the same shape as `## Backlog Recount` but pointed at prior goals, audits, and issue comments rather than the tracker. `#564` is the measured instance: two records had already declined its filed remedy. Destination: issue. (source: `charness-artifacts/retro/2026-08-09-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md`
- `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`
- `charness-artifacts/retro/2026-08-09-make-proof-surfaces-report-what-they-observed.md`
- `charness-artifacts/retro/2026-08-09-session-retro.md`
