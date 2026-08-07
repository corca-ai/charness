# Issue 540 resolution critique
Date: 2026-08-07

## Decision Under Review

Closing #540 — the unreachable `target_disagreement` branch was deleted, the docstring
promise it could not keep was withdrawn, and the hedged test assertion was replaced by two
exact pins.

## Failure Angles

- Deleting a refusal on an authorization surface.
- Closing a defect report while the design question it exposes has no home.
- Claiming the removal tightened the gate.

## Counterweight Pass

- Verified by the delegated reviewer: no authorize-vs-refuse verdict changed. The branch
  sat after the singleton check with `len(distinct) == 1` and both operand sets non-empty
  subsets of it, so it could not be true; every input that used to refuse still refuses
  under the identical name.
- "Deleted and explained" is the honest resolution rather than a punt: leaving unreachable
  code while a follow-up matured would keep claiming a protection that does not exist,
  which is what the issue reported.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/evidence_boundary_crosswalk.py:176 | action: file-issue | note: three in-code sites said the design question was "tracked on its own issue" with no such issue; closing #540 would have pointed them at a closed issue — the promise-outlives-its-keeper shape #540 is about. Filed and all three now name the number | follow-up: https://github.com/corca-ai/charness/issues/542
- F2 | bin: over-worry | evidence: strong | ref: scripts/evidence_boundary_crosswalk.py:249 | action: document | note: deleting a refusal reads as weakening; here it changed no verdict at all, which is the evidence the branch was dead

## Boundary Ownership

- Producer: `authorize_closeout`, which owns the refusal vocabulary.
- Consumer: the operator reading the refusal and choosing a remedy.
- Owning surface: the closeout authorization crosswalk.
- Verdict: single-surface

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (`.claude/agents/bounded-reviewer.md`).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, session-model inheritance per the per-host split for Claude Code hosts.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported Read/Grep/Glob only and returned findings inline.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One delegated read-only reviewer examined BOTH fixes before either
close, and returned a separate verdict per issue. Recorded deviation: the
causal-review-before-design round was not run separately for these two, because both were
already fixed in `2ecd7c79` as a consequence of the changed-line mutation lane naming them
as dead code — the diagnosis was produced by an executed gate, not by reading. The
delegated critique is what caught the residual in each.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer read the worktree directly.
The binding floor is therefore not turned on for this artifact. -->

## Non-Claims

- No target-disagreement refusal now works, and none is "deferred but safe" — there is
  none. #542 holds the design.
- Aggregation is right for the commit-hook path, where both sets are halves of one carrier
  GitHub closes together. It is NOT proven right for close-with-comment.
- Removing the branch did not tighten the gate.
