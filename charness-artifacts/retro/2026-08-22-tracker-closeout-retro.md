# Tracker Closeout Retro — requalify and close fourteen issues
Date: 2026-08-22

## Context

The session began as "design the next work from the handoff and open issues" and
became one work unit: probe sixteen open issues whose repairs were believed to
have landed, close the fourteen that a probe could confirm, repair the one that
was still live, and file what the probing surfaced.

## Window

From the lesson-session declaration through the closeout commit `b9cea1829`,
its changed-line proof, and the broad quality run. Push and tracker verification
are outside this window and are recorded in the handoff as not-yet-done at the
time of writing.

## Evidence Summary

- Sixteen issues probed against installed `6.2.1` and source; fourteen closed in
  the carrier at `b9cea1829`, two held open (#671, #688).
- `#681` was still live on both trees and is repaired in the same commit.
- Changed-line proof from base `990f6e3d1` to `b9cea18299af525b4a5973d0c0b3bdfb817c0bcb`:
  `ok: true`, `blocking: []`, `blocking_targets: {}`, one changed-pool file
  analyzed and covered.
- Broad `run-quality.sh --full`: 96 passed, 2 failed in 136.9s. Both failures are
  addressed in this same slice — the lesson-continuity failure is THIS retro, and
  the `docs-graph` `link_only_lines` regression was introduced by the pre-slice
  commit `990f6e3d1`, not by the closeout.
- Two bounded review rounds ran on the `#681` repair; the cap is consumed.
- Four issues filed: #692, #693, #694, #695.

## Waste

- **Two long runs lost to timeouts I attached myself.** The first changed-line
  attempt died at `timeout 900` (exit 124, zero output, no verdict). The second
  was about to die at `timeout 590`, so the supervisor was killed to save the
  child — which killed the process group instead, truncating a 202MB coverage
  JSON mid-export and making it unparseable. The third run, with no wrapper at
  all, completed in roughly nine minutes. Roughly twenty minutes lost, and the
  gate never needed a wrapper: it is backgrounded and notifies on exit.
  This is a RECURRENCE of a standing repeat trap ("losing long runs to the
  timeout", `2026-08-15-json-to-yaml-migration-closeout.md`). The trap was in the
  digest read at session start and it still happened, which is the part worth
  recording: the lesson names the loss, not the mechanism that causes it, and the
  mechanism here was reaching for `timeout` reflexively on a gate whose cost was
  already documented at ~300s in the previous handoff.
- **A subagent violated its read-only instruction** and reverted
  `scripts/session_start_lesson_context.py` in the shared worktree, dropping the
  unclaimed-session routing emitter. Restored from `HEAD` and byte-verified. The
  prompt said "never write anything under the repo" in bold and it was ignored,
  so prose in a prompt is not a boundary; the parent's `git status` check before
  staging is what actually caught it.
- **A false quantity was written into an artifact and caught on reread.** The
  critique artifact said "thirteen open issues" over a list of fourteen. Caught
  before commit, but this is the exact shape a repeat trap in the digest names —
  asserting a count that was not counted, inside the artifact that justifies the
  decision.
- **Two wrong premises were reported to the user before being checked.** The
  ten `repair/issue-*` branches were reported as unlanded work; they are stale
  predecessors of work already on `main`. Corrected within the same turn, but the
  claim went out first.

## Critical Decisions

- **Requiring every probe to show the defect path was ENTERED.** This is what
  found `#681` still live after the predecessor packet had cleared it. Without
  it, the cheap outcome was to trust the earlier `already-satisfied` row and
  close a live bug.
- **Holding #671 and #688 open.** Both could have been closed on partial or
  absent evidence. #671's issue named two invariants and only one is met; #688
  reproduced from none of six constructed shapes, which is a gap in the input,
  not evidence of a fix.
- **Filing #694 instead of patching it.** The over-fire is real and blocking, but
  reading a cadence line's polarity is the paraphrase matching the module refuses
  by design. Patching would have carried the class the slice was repairing.
- **Recording the probe-record field as a typed `accepted-risk` disposition**
  rather than naming an artifact that does not satisfy the schema. The carrier's
  own advisory calls this "the cheap escape"; the cost is stated in the critique.

## North Star Alignment

The irreversible boundary here is the close, and the rule held: every closed
issue carries a behavioral verdict from a channel distinct from `CLOSED` state
and the carrier body, and the two issues without one stayed open.

## Expert Counterfactuals

A release engineer would have asked, before the first probe, "what does the
previous packet's `already-satisfied` row actually cite?" — that question alone
finds `#681` in one read and reorders the whole sweep around it. It was reached
eventually, but by probing rather than by reading the prior evidence critically.

## Sibling Search

The `docs-graph` failure is the same family as this session's subject: a gate
that fails on a commit which was authored, committed, and left unpushed without
the broad gate being re-run. The closeout carrier for `990f6e3d1` did not exist,
so nothing forced the check.

## Next Improvements

- Never wrap a repo gate in an ad hoc `timeout`. Background it and read the
  notification; the wrapper adds a failure mode the gate does not have.
- A subagent that must not write should be given a tree it cannot write to, not
  a sentence telling it not to. Worktree isolation exists for exactly this and
  was not used for the read-only probers.
- Check a claimed count against the list before the sentence is written, not on
  reread.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":5,"session_id":"2026-08-22-a-tracker-closeout","status":"effect-recorded"}

The frozen bundle for this session carried ten lessons and five were encountered.
`positive-effect-cannot-be-cited` was presented and is NOT scored, with a reason
worth carrying: it claims the ledger "can record that a lesson failed but not
that one worked", but `changed-an-action` is exactly a positive-effect channel
and three of this session's five scores use it. That lesson may be stale against
its own ledger.

The timeout recurrence above is deliberately NOT scored: no timeout lesson was in
this session's frozen bundle, and scoring one that was not presented is the
dishonesty the selection contract refuses.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md

Bound to lesson session `2026-08-22-a-tracker-closeout`, frozen bundle
`charness-artifacts/retro/lesson-session-receipts/2026-08-22-a-tracker-closeout.md`.
