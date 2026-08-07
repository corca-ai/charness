# Goal Retro: Arm the verdict, then close the false-green cluster
Date: 2026-08-08

Goal: charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md

## Context

This retro reviews the `arm-the-verdict-and-close-the-false-green-cluster` goal,
closed EARLY at 2 of 7 slices by operator decision so its remaining claims could
be re-homed under a larger structural frame.

The interesting question is not whether the two slices worked — they did, and the
final boundary gate was 86 passed / 0 failed / 0 UNPROVEN. It is that **every
defect this goal shipped was the defect it was built to remove**, and that the
same three shapes recurred often enough to be named as mechanisms rather than
incidents.

Structural pattern: a verdict surface asserted something it had not established.
That is the goal's own subject, and it appeared inside the instrument (a stale
docstring forbidding the arming it now performs), inside the arming (a gate
claiming a 37-adapter scope while reading 18), inside the floor (two wrong
denominators in one paragraph), and inside the floor's tests (proving the helper
while the wiring went unproven).

Pattern of patterns: **the repair for a finding is the least-reviewed code in the
run.** Round 1 fixed a thing; round 2 found the fix carrying the class it fixed —
twice out of two slices. A one-round cadence would have shipped both.

## Window

Activation of the goal through slice 2's round-2 disposition and this early
close, 2026-08-07–08. Thirteen commits, all local; nothing pushed.

## Evidence Summary

- Slice 1 (`#530`): WARN tier armed for `unknown` only, across 37 adapters plus
  the flattened installed layout. Fire rate measured BEFORE arming: 0 repo-wide,
  0 across shipped examples. Mutation 14/13 killed, the survivor disclosed.
- Slice 2 (`#554` part 1): backlog-recount floor; a draft cannot activate without
  recording what it claims and does not. Mutation 6/6 killed, plus two
  hand-mutants on the repairs.
- Both slices ran round-1 AND round-2 bounded review. Round 2 found real blockers
  in both.
- Final gate: 86 passed, 0 failed, 0 UNPROVEN. Full suite 7816 passed.
- `#530` and `#554` both remain OPEN, deliberately, with reasons in the Operator
  Decision Queue.

## Waste

Measured, not estimated:

- **Two full-suite runs (~12 min each) burned on a self-inflicted false red.** I
  ran `pytest tests/` BEFORE syncing the `plugins/` mirror, so mirror-consistency
  tests failed against source I had just edited. The repo's own
  `mutate → sync → verify` phase barrier exists for exactly this; I ran verify
  before sync and then investigated the result as if it were a finding.
- **Gate-by-gate rediscovery.** dup-ratchet → skill-core-headroom →
  attention-state-visibility → skill-ergonomics each blocked in turn, one per
  re-run. `CLAUDE.md` already says to run the aggregate when a commit is
  rejected so all of them surface at once; I re-ran serially instead.
- **A `-k` filter used as if it were the suite.** `-k "achieve or goal"` was
  green while a handoff golden-render fixture was broken; the boundary quality
  gate caught it. Filtered runs answer a narrower question than they appear to.
- **Two numbers written without measuring.** "nineteen" was carried in from the
  preceding slice's unrelated count of shipped example adapters; its replacement
  "173" was `176 − 3` computed without checking that 20 of the 176 were not goal
  artifacts. Both looked authoritative in a verdict surface's own rationale.
- **A finding repaired at one call site out of two.** Round 1 named a wrong
  predicate; I fixed the floor it pointed at and left the sibling gate, which
  converted a shared bypass into a live single-gate bypass.
- **Ordering slips with no bad outcome but real risk:** a reviewer-boundary
  window verified after repairs instead of before, and a commit allowed past a
  blocked closeout because it was not chained to the gate's exit status.

## Critical Decisions

- **Tier scope decided by measurement, not judgement.** Reading all 23
  `reader-elsewhere` instances found 3 false positives, one inside a SHIPPED
  example. That single fact refuted arming the state and is the reason the tier
  is `unknown`-only. Cost: minutes. Value: it prevented shipping a wolf-crier to
  every consumer who copies that example.
- **Premise check kept as a phase.** 5 for 5 across this goal family. Its largest
  save was slice 2: the plan's named remedy would have wired `achieve` to
  `handoff`'s duplicate tracker backend, inheriting a foreign adapter's kill
  switch and pointing the coupling backwards.
- **Refusing to claim `#530` closed.** The gate warns on the issue's exact
  reproduction, but the resolver still emits the literal string in the issue
  title. Closing on the gate alone would have been the false green this goal
  exists to remove.
- **Deleting rather than suppressing.** Two unreachable branches and one
  duplicate `main()` shim were removed; only genuinely irreducible duplication
  was classified `intentional` with a written reason.

## Trends vs Last Retro

The predecessor's lesson — "round 1's fix carried the class it fixed, both
times" — held again, 2 for 2. This is now measured across two consecutive goals
and four slices. It should stop being a lesson and become a mechanism.

New this run: the same failure has a THIRD face nobody had named — tests that
prove the module computing a verdict while the wiring acting on it goes unproven.
It appeared three times in one goal.

## North Star Alignment

Aligned: teeth were kept only where a wrong answer escapes (WARN not refuse,
presence-only not judgement-grading), and irreversible boundaries were respected
(nothing pushed, no issue closed, no release).

Tension: the harness caught every one of these defects — but only via bounded
review and the broad gate, i.e. the expensive channels. Three of the recurring
shapes are mechanical enough to be checked cheaply.

## Expert Counterfactuals

- A **release engineer** would have run the aggregate gate once after the first
  rejection instead of four serial re-runs, and would have synced before
  verifying without being told.
- A **measurement specialist** would have refused to write any denominator into a
  rationale without a command producing it — which would have caught both wrong
  numbers at authoring time, not at review.

## Sibling Search

The wiring-vs-helper gap and the sibling-predicate drift are not local to
`achieve`. The open tracker already carries the same shapes elsewhere: `#548`
(two scaffolds emit one key name meaning opposite things), `#552` (a checker
requires a token the renderer never emits, so two policy checks can never fire),
`#555` (two tracker backends), `#537` (a correct refusal surfacing as five broken
tests — hit live this run and worked around without linking it).

This is transferable waste, and it is the successor goal's subject.

## Portable Candidate

Not yet. The three mechanisms are named but only one is guarded (by tests I wrote
for specific instances). A portable gate needs the successor goal's evidence
across several unrelated surfaces before it can be generalized without becoming
another wolf-crier.

## Next Improvements

1. A cheap check for a verdict predicate implemented twice — the sibling-drift
   mechanism. Evidence: fixed twice by hand this run, and `#548`/`#552`/`#555`
   are the same shape.
2. A cheap check that a floor's REFUSAL is asserted through the composed verdict,
   not only its computing module — the wiring-vs-helper mechanism, three
   instances this run.
3. `#537`'s repair, so a correct refusal reports itself instead of appearing as
   unrelated broken tests. Hit live this run.

## Persisted

Persisted: yes: charness-artifacts/retro/recent-lessons.md

Carried into the successor goal's Boundaries, and appended to
`charness-artifacts/retro/recent-lessons.md`.

(The first draft of this section asserted the `recent-lessons.md` half in the past
tense before it had run — a `Persisted` claim about a persistence step that had
not executed, caught by the delegated disposition review. That is the goal's own
subject appearing in its retro, which is why the correction is left visible.)
