# Recent Retro Lessons

## Current Focus

- A discussion session that became a work session: close `#572`, verify the `#582`-`#585` umbrella premise, amend the north star, dispose of four umbrella classes under an operator-directed deletion bias. (source: `charness-artifacts/retro/2026-08-11-session-retro.md`)
- The second work unit of 2026-08-11, distinct from the umbrella-disposition session that owns `2026-08-11-session-retro.md`. (source: `charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md`)

## Repeat Traps

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **A docstring asserting intent, sourced from nothing** — "dead by decision rather than by oversight", while the repo's own audit calls those lines an open defect — plus a misquote of `AGENTS.md:26` inside quotation marks that dropped the clause carrying the rule's reason. The exact class I had spent the day repairing in other people's code, shipped in the one slice I wrote. (source: `charness-artifacts/retro/2026-08-11-session-retro.md`)
- **A self-suspicion section that admitted five things and missed the real one.** The accommodation was effort, not deletion: on `#524` a deletion was available and I chose IGNORE because deleting a shared reference means touching consumers. A reviewer named it. I was simulating a critic rather than tracing what I did. (source: `charness-artifacts/retro/2026-08-11-session-retro.md`)

## Next-Time Checklist

- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- `>= 35` is a ratchet floor implemented in this repo's worst available form — an inline magic number plus a prose instruction to bump it. Every other ratchet here has a baseline file and an accept command. Either give it that form or drop it. (source: `charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md`)
- a `consumers <symbol|path|key>` command printing every reference outside the target's own tests and mirrors. Structural pattern: a method requiring the agent to remember to search has no tool, so it degrades to memory — the sentence the digest already carries about backlog re-verification. Triggering instance(s): seven wrong removal/keep proposals in one session, each refuted by one grep. Destination: new issue. (source: `charness-artifacts/retro/2026-08-11-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md`
- `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`
- `charness-artifacts/retro/2026-08-11-session-retro.md`
- `charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md`
