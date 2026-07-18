# Release Close Evidence Ordering
Date: 2026-07-19
Status: implemented; focused release proof and fresh-eye code critique passed.

## Problem

The release commit is both the version carrier and the issue-close carrier.
Pushing it to the default branch can auto-close linked issues before public and
distinct-channel release evidence exists, even though later code comments and
tests treat `ensure_release_issues_closed` as the close boundary.

## Capability Contract

A maintainer can publish a release with linked issue closeout such that release
content becomes public first, a different observer records the result, and only
then one evidence-bearing default-branch commit may close the issues. A later
readback records GitHub state without being confused with behavioral proof.

## Current Slice

Split the release-content commit from the post-observer issue-close carrier and
prove the earliest external effect across normal and resumed publication paths.

## Fixed Decisions

- The initial release commit and tag never contain close keywords.
- Existing carrier validation still runs before any release mutation, but its
  validated paragraphs are reserved for the post-observer carrier commit.
- The carrier commit stages the release artifact and observer record, marks
  issue state `carrier-pending-state-verification`, and carries the validated
  close keywords. Its push atomically makes evidence durable and enables GitHub
  auto-close.
- Resume recognizes that carrier only when its exact validated message, release
  artifact, observer record, tag topology, and remote branch identity agree.
- After the carrier push, the helper reads issue state and uses the existing
  manual fallback only when auto-close did not occur; a final commit records
  `state-verified`.
- Releases without linked issues keep their current single post-publish artifact
  path.

## Probe Questions

- Whether the current resume tests expose another copy of initial-commit carrier
  construction; if so, the shared phase owner must eliminate it in this slice.
- Whether a failed carrier push leaves a sufficiently typed local commit and
  artifact for operator recovery without inventing another public command.

## Deferred Decisions

- A dedicated post-publication `--resume-closeout` command remains unnecessary:
  the existing `--resume --publish-current` classifier owns the exact carrier
  and final-artifact recovery shapes.
- GitHub webhook timing is not modeled; the post-push state readback remains the
  authority.

## Non-Goals

- Do not weaken carrier validation, behavioral verdict requirements, distinct
  observer policy, release verification, or issue state readback.
- Do not add a new blocking authoring form or another success verdict.
- Do not change non-issue release commit counts or public CLI flags.

## Deliberately Not Doing

- Do not delay the release tag itself until issue closure; publication and issue
  closure are intentionally separate boundaries.
- Do not close through an unrecorded API call merely to avoid the carrier split.
- Do not call the GitHub state readback behavioral proof.

## Constraints

- Preserve YAML-first operator planning and hidden JSON compatibility.
- Sync source to checked-in plugin exports before validation.
- A carrier-push failure must occur before issue closure or leave the evidence
  commit locally identifiable; a post-push failure must leave evidence shared.
- The release helper owns the phase order; skills and docs describe it rather
  than duplicating an executable ritual.

## Success Criteria

- No branch/tag push before public verification contains `Close #N`.
- Distinct evidence and the release observer are present in the carrier commit
  that first introduces close keywords to the default branch.
- Issue state verification happens after the carrier push.
- Normal and resume flows share the same closeout-tail ordering.
- Existing release-only tests and a new negative event-order fixture pass.

## Acceptance Checks

- unit: initial release commit construction omits carrier paragraphs when
  `close_issue` is non-empty.
- unit: carrier construction uses the preflight-validated paragraphs and stages
  both release artifact and observer when present.
- integration: fake event log orders distinct observer → carrier commit/push →
  issue state readback → state-verification commit.
- integration: injected carrier push failures before and after remote receipt
  are identity-reconciled without a duplicate carrier.
- integration: post-carrier state-readback and final-push failures resume the
  idempotent tail without rebuilding the release-content commit.
- integration: releases without issue closeout retain one final artifact commit.

## Boundary Ownership

`publish_release_execute.py` owns the initial content commit;
`publish_release_common.py` owns phase order; `release_issue_closeout.py` owns
carrier construction, push, and state record. Verdict: owned-correctly.

## Critique

- Interrupt Source: release-issue-close-evidence-ordering
- Seam Summary: git default-branch push -> GitHub issue auto-close -> release observer
- Chosen Next Step: impl
- Chosen Next Step Reason: split through the existing shared closeout tail and
  obtain a bounded fresh-eye review before locked proof.
- Impl Status: allowed
- Impl Status Reason: fixed decisions are implemented, including exact evidence
  tree validation and identity-checked recovery for ambiguous remote outcomes.
- What Disproving Observation Is Resolved: the initial default-branch push will
  no longer contain a close keyword.

## Canonical Artifact

This file is the implementation contract; the linked debug artifact remains the
causal record.

## First Implementation Slice

Add the failing event-order tests, split initial and carrier commit construction,
then update the release publication-boundary reference to the proven order.
