# Recent Retro Lessons

## Current Focus

- One session under the standing operator direction (bug fixes, friction/rework, test/code speed) that closed the handoff's blocker 1 — two holes in the runtime-profile affinity switch — and published `v2.11.0`. (source: `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`; sources: 2)
- Two lanes against one defect class: a verdict that reads clean because nothing distinct ever checked it. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)

## Repeat Traps

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the INSTALLED `publish_release.py` against the source tree.** The installed copy's `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own `validate-retro-lesson-index` then rejected it and the helper rolled back. The first attempt I misdiagnosed entirely — I re-ran the standalone quality suite (83/0, clean), concluded the failure was release-state-specific, and only found the real cause by reading the guard's own docstring, which names this exact lineage ("four release publishes died to one shape"). (source: `charness-artifacts/retro/2026-07-27-session-retro.md`; sources: 3)
- **Three planned items were premises, not debt, and one was work that already shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit; #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when the one-pass machinery already existed and only three validators were unwired. Cost: a slice plan written against a tree nobody had checked, caught by a reviewer rather than by planning. (source: `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`; sources: 2)
- **A dup-ratchet hard-block at closeout on my own code** (two clone families in `_refusal_reason`'s repeated message blocks). The low-cost check says to run the ratchet at the FIRST edit to a gated file, not at the closeout aggregate; I ran it at the aggregate. Cost was small only because the fix was a genuine refactor rather than an accept. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- **Round 1's repair of Lane B introduced two new blockers, and folding those introduced a third.** Matching delegated tokens by containment (to stop over-blocking ten honest artifacts) made the `blocked` valve bypassable in 24 characters — cheaper than the bare word the previous repair had just closed. Narrowing that with value-wide negation markers then demoted eleven honest artifacts on the words "no blockers". Each fix was locally correct and globally wrong, and only re-measuring the corpus caught the third. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)

## Next-Time Checklist

- a slice packet's non-claims are claims and need the same premise check as a plan's remedies; the one blocker in Lane A's review was a packet assertion I had not checked. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- verify the reviewer boundary fingerprint IMMEDIATELY on the reviewer's return, before any parent write — two of three windows this run were verified late and resolved only by parent testimony. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- when a slice changes what a floor REFUSES, measure the refusal against the real checked-in corpus and pin the number with its denominator in a test, before the fold and after — this run's only structural defence, and it caught the one over-block inspection missed. (source: `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`)
- **a goal's own claims are a verdict surface and got one review round, at the end, which found two blockers.** The slice-level discipline has no goal-level analogue. (source: `charness-artifacts/retro/2026-08-01-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-26-session-retro.md`
- `charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md`
- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-01-session-retro.md`
- `charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`
