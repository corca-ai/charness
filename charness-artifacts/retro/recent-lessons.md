# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- Goal `2026-08-03-repair-the-commands-the-skills-tell-agents-to-run`. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A dup-ratchet hard-block at closeout on my own code** (two clone families in `_refusal_reason`'s repeated message blocks). The low-cost check says to run the ratchet at the FIRST edit to a gated file, not at the closeout aggregate; I ran it at the aggregate. Cost was small only because the fix was a genuine refactor rather than an accept. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- **A test asserted a proxy instead of the real thing, and failed on its own docstring.** `assert "--strict" not in source` matched the module docstring *explaining* that `--strict` is deliberately absent. Replaced with a read of the real `argparse` parser's option strings. Same family as the standing "build test inputs from the source constant" trap, one level up: not a retyped fixture, but a grep standing in for the structure it describes. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`)

## Next-Time Checklist

- a proof-surface repair owes its second round, and the round that reads the REPAIRS is where the class reappears — twice in this run, neither visible to round 1. (source: `charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md`)
- a slice packet's non-claims are claims and need the same premise check as a plan's remedies; the one blocker in Lane A's review was a packet assertion I had not checked. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- build test inputs from the source constant, never by retyping the string the code is supposed to accept. Applied in this run (`_decline_status_line` reads `_DECLINE_ACTION` and splits it) after the hand-typed version passed against a form nothing prescribes. (source: `charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md`)
- **capability** — A check whose subject is a shipped surface must resolve against the shipped layout, not the authoring one. Applied here; the general form is the Portable Candidate below. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md`
- `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
