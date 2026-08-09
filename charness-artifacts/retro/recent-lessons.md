# Recent Retro Lessons

## Current Focus

- Closeout retro for the `refuse-the-verdict-a-surface-never-earned` goal, picked up mid-flight from a Codex session that had stalled waiting on hosted CI behind a GitHub rate limit. (source: `charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md`)
- One session that started from "design the next work" and ended having shipped it. (source: `charness-artifacts/retro/2026-08-09-session-retro.md`)

## Repeat Traps

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- A crude regex proxy produced "14 checks cannot fail" including `pytest` and `dup-ratchet`. Discarded before use, but it was run and reported before being sanity-checked. All three are the same shape: **I spoke before measuring, on questions a command could answer in seconds.** The repo already names this ("Settle by measuring, not by debating, when a command can answer") and it still fired three times. **Not waste, recorded so it is not mistaken for it:** the census's 744K subagent tokens bought a decision on an open `question`-labelled issue that had been unanswerable for days, and its adversarial pass prevented four wrong deletions. The gate-runtime telemetry (peak 475s) is the standing suite doing its job; this session ran targeted modules instead and paid it only at commit boundaries. (source: `charness-artifacts/retro/2026-08-09-session-retro.md`)

## Next-Time Checklist

- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- before closing an issue as already-fixed, read the slice log of the goal that shipped the fix, not only the issue's premise. One grep for the issue number across `charness-artifacts/goals/` would have caught `#554` before a reviewer round was spent. Structural pattern: a closeout is judged against the claim under review rather than against the record that already dispositioned it. Triggering instance(s): `#554`'s draft close, refused by a delegated reviewer citing a slice log neither the packet nor I had read. Destination: issue #571 — verified against its body rather than its title: its instance 2 is `#567`, "already fully repaired… the session's first disposition was re-scope — based on the issue body rather than on the commit that fixed it", which is the same shape as the `#554` draft close. → tracked issue #571 (source: `charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md`)
- make backlog re-verification executable, specified as an extension of the existing tracker-recount seam rather than a second backlog reader — the shape `#554`'s part 2 named and the Engelbart lens independently reached. Structural pattern: a method that requires re-reading a record has no tool, so it degrades to memory. Triggering instance(s): three re-read failures in one session. Destination: the successor goal's slice 2, already specified. → applied: `charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md` slice 2, committed at `b7d93729` with its floor and non-goals written (source: `charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md`)

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
- `charness-artifacts/retro/2026-08-09-session-retro.md`
- `charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md`
