# Release 6.2.2 Preparation Retro
Date: 2026-08-22

## Context

This session prepared patch release `6.2.2` to carry the `#681` cadence-owner
repair to consumers. It covers everything up to the publish attempt: scope
freeze, evidence, the release critique, and the three repairs that critique
required before the cut. Publication itself is not in this window — the first
`--execute` was refused and rolled back, which is what this retro was written to
clear.

## Window

From the `2026-08-22-b-release` lesson-session declaration through the refused
publish attempt at candidate `ef57979c7`.

## Evidence Summary

- Release planner: `6.2.1`, no surface drift, no blockers, adapter valid.
- Real-host proof re-evaluated over the FROZEN range `46169b7ad..5bd80a7b6`:
  28 changed paths, no trigger matched, `required: false`. The planner's own
  verdict had been scoped to three dirty worktree files and was not used.
- Fresh-checkout probes: 5/5 executed and passed.
- Changed-line coverage over the frozen diff: `ok: true`, `blocking_targets: {}`.
  Re-run after the critique repairs moved the candidate to `ef57979c7`: same
  verdict, new `resolved_head_sha`.
- Release critique returned `ship-with-changes` / `approve-with-notes`; all three
  ship conditions were applied before any bump.
- Publish `--execute` refused on `run-quality.sh --release` (97 passed, 1 failed)
  and rolled back cleanly: HEAD unchanged, eight bumped files restored, the
  auto-retro quarantined under `.git/charness-release-rollbacks/`.

## Waste

- **The release attempt was spent discovering an ordering I could have read
  for.** The refusal is the lesson-continuity gate demanding that the session I
  opened be claimed. Nothing about it is surprising in hindsight: I opened
  `2026-08-22-b-release` at the start, did substantive work, and tried to publish
  without writing its retro. The previous release's auto-retro says in its own
  body that it does not cover the session — so the answer was readable before the
  attempt, and instead it cost a full `--release` lane (166s) plus a rollback.
- **A blind-class paragraph was written without verifying the instance it
  named.** The comment claimed the achieve scaffold's seeded cadence line as a
  live over-fire instance. It is not — the seeded line defers in its first
  clause, so refusing it is a true positive. The release reviewer caught it. Had
  it shipped, the next maintainer taking the over-fire issue could have widened
  the matcher to stop refusing the template and disarmed the floor on its own
  scaffold.
- **The same unverified claim reached the consumer-facing payload.** The
  disclosure's escape clause was reachable from the true-positive side, so a
  correctly-refused consumer could have read "known over-fire" and dismissed it.

## Critical Decisions

- **Re-scoping the real-host check to the frozen release range.** The planner
  reported `required: false` from three dirty worktree files. Same answer, but
  the first was not evidence about the release.
- **Re-running changed-line after the critique repairs.** The reviewer warned
  against carrying the `5bd80a7b6` receipts onto a candidate they no longer
  covered. The repairs moved the candidate; the receipts were re-earned.
- **Refusing the reviewer's ask to name the tracker id in the payload.** The
  repo's anchor guard forbids issue anchors in a portable skill package, and a
  consumer reading an installed copy cannot search one anyway. Two concrete
  remedies went in instead, and the conflict is recorded rather than silently
  resolved.
- **Shipping the over-fire with a disclosure rather than a matcher patch.**
  Reading a cadence line's polarity is the paraphrase matching the module refuses
  by design; patching it would have carried the class the release repairs.

## North Star Alignment

The irreversible boundary is publication, and it has not been crossed. Every
verdict recorded so far names its observer and channel, and the one read the
reviewer could not perform is recorded as not performed rather than inferred.

## Expert Counterfactuals

A release manager would have asked "what does the previous release's retro
artifact actually claim?" before the first `--execute`. One read of
`2026-08-21-v6-2-1-release-auto-retro.md` answers it — the artifact says plainly
that it does not cover the session — and the refused attempt does not happen.

## Sibling Search

The refused publish and this session's earlier broad-quality failure are the same
gate firing twice on the same cause: a declared lesson session with no
disposition. The first was cleared by writing a retro; this one is the same
remedy at a more expensive boundary. That the gate fires at BOTH boundaries is
the improvement the issue behind it asked for.

## Next Improvements

- Before a publish attempt, run the release lane's own quality command once
  rather than discovering its refusals through a rollback. The rollback is clean,
  but 166 seconds and a quarantine is a costly way to read a gate.
- When writing a blind-class note, verify every instance it names against the
  constant or template it claims — a blind class stated with a false example
  actively misleads the person who acts on it.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":5,"session_id":"2026-08-22-b-release","status":"effect-recorded"}

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-22-release-6-2-2-preparation-retro.md

Bound to lesson session `2026-08-22-b-release`, frozen bundle
`charness-artifacts/retro/lesson-session-receipts/2026-08-22-b-release.md`.
