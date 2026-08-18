# session retro

Date: 2026-08-18

## Context

The goal-drafting session of 2026-08-18 — the one that wrote
`charness-artifacts/goals/2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md`
and folded its pre-implementation critique (`b65514355`, `1b49a1ae0`). It declared a
lesson session at 20:16 and ended without a retro, leaving its emission unclaimed.

This retro exists to dispose of that emission honestly and to do nothing else. It is
written by the SUCCEEDING session, which did not do the work under review.

## Window

`c29f5de95..1b49a1ae0` — the goal draft and the critique fold.

## Evidence Summary

- Receipt `charness-artifacts/retro/lesson-session-receipts/2026-08-18-b5ad3bee-f554-4036-b685-737d3fe5e5da.md`,
  written 20:16 and committed in `1b49a1ae0`.
- The ledger's `session_events` entry for the same id, with zero score events.
- The commits above, read from `git log`.

That is the whole evidence set, and it is why this retro claims almost nothing: a
receipt proves bytes were ISSUED, not that they were read, and nothing else survives
from that session for a later one to inspect.

## Waste

Not assessable from here. The succeeding session has no observation of how that
session spent its time, and inventing one from its commit list would be exactly the
"a verdict may not claim more than its probe measured" failure the goal those commits
created exists to prevent.

The one structural fact worth recording: a session that declares a lesson session and
ends without a retro leaves a permanent `unclaimed-emission` that blocks pre-push for
whoever comes next. That is what happened here, and it is what this file resolves.

## Critical Decisions

- Disposing of the emission as `not-evaluated / presentation-unproven` rather than
  scoring it. The lessons may well have changed that session's actions; the succeeding
  session cannot know, and a score appended without an observed action is precisely the
  unanchored claim the ledger's own anchor rule forbids.
- Not writing a substantive retro for work this session did not do.

## North Star Alignment

P5's rule — a claim is bounded by what was actually observed — applied to a retro about
another session. The honest output is a disposition and a stated non-claim, not a
reconstruction.

## Expert Counterfactuals

**Direct lens: the durable-record boundary.** The counterfactual is not about the
drafting work; it is about the session boundary. Had that session run its retro before
ending, this file would be unnecessary and its lesson scores would exist while the
evidence for them was still in view. The changed action is a sequencing one and it
belongs to the session that declares: **declare the lesson session only if the session
will end in a retro, and treat the retro as part of the declaration's cost.**

## Sibling Search

n/a — trivial fix; no plausible siblings. This is a single unclaimed emission resolved
by the instrument the evaluator already provides.

## Lesson Evaluation

The list was emitted and the session was declared, so emission is proven. Presentation
is not: nothing available to this session shows the list was read before the affected
work, and this session cannot supply that proof for another. No score is appended.

Lesson evaluation: {"reason":"presentation-unproven","score_event_count":0,"session_id":"2026-08-18-b5ad3bee-f554-4036-b685-737d3fe5e5da","status":"not-evaluated"}

## Next Improvements

- **workflow — a declared lesson session owes a retro before the session ends.** The
  declaration is cheap and the retro is not, and the cost lands on the NEXT session as a
  pre-push block. Recorded here rather than as a new gate: the continuity reconciler
  already detects it, and it detected this one.

## Retro Dispositions

- `applied: the unclaimed emission is dispositioned` — this file, carrying the
  `not-evaluated / presentation-unproven` status the evaluator defines for exactly this
  case.
- Retro dispositions: none beyond the above — this retro reviews no work of its own.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-18-goal-drafting-session-emission-disposition.md
