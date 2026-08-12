# Goal Progress Frame and Ledger Critique
Date: 2026-08-12

## Decision Under Review

Synchronize the active goal and fixed-cohort execution ledger with local proof,
open tracker state, and explicit non-closure ownership after the first runtime,
fixture, and SessionStart slices.

## Failure Angles

- A local commit could be represented as GitHub closure.
- A partial umbrella repair could use an invalid disposition or lose the
  unimplemented successor's owner.
- Calling Slice 2 current while Slice 1 is incomplete could launder unresolved
  premises into a completed plan.

## Counterweight Pass

- #584 is `split`, remains GitHub OPEN, and names the unimplemented planner
  successor plus its revisit trigger; #595 and #597 stay OPEN with separate
  tracker carriers and final-carrier/readback boundaries.
- Preserve #546's `unproven-defer`: its measured membership repair does not
  decide conditional labels or consumer runner inventories.
- Describe Slice 1 and Slice 2 as concurrent and name the unfinished families.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md | action: document | note: local proof and GitHub OPEN state now have separate tracker carriers and revisit conditions.
- F2 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md | action: document | note: the active frame makes concurrent Slice-1/Slice-2 work and remaining residuals explicit.
- F3 | bin: over-worry | evidence: strong | ref: https://github.com/corca-ai/charness/issues/546#issuecomment-5268428686 | action: defer | note: #546 remains correctly deferred rather than downgraded because the conditional and consumer cases are outside the measured membership proof.
- F4 | bin: valid-but-defer | evidence: strong | ref: https://github.com/corca-ai/charness/issues/584#issuecomment-5268493705 | action: defer | note: the planner read-cost successor is specified but not implemented, so #584 cannot close.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: task_name `goal_progress_repair_review`; read-only scope; critique packet path; no model override.
- Host exposure state: metadata-hidden
- Application state: n/a — host exposes completion findings but no typed reviewer-tier confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-145810-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-145810-packet.json
- Packet SHA256: 0709f23d085e99482fdc22126fd1ff45e682aafd248bcb48d1881db55337dbea
- Identity SHA256: 699a69587e3def08eab81c748cc78430569f6f495fb10323fbc6d6ab8a74a282

## Boundary Ownership

- Producer: local debug, critique, test, and commit records establish local behavior.
- Consumer: the execution ledger and the GitHub issue carriers establish each claim's scope and revisit boundary.
- Owning surface: active-goal and issue-closeout coordination.
- Verdict: owned-correctly
