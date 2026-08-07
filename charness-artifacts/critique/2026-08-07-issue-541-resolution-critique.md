# Issue 541 resolution critique
Date: 2026-08-07

## Decision Under Review

Closing #541 — the unreachable `missing_issue` cross-check and the uncalled
`snapshot_payload_text` were deleted in `2ecd7c79`.

## Failure Angles

- Deleting a guard that turns out to be live.
- Leaving the second serializer's divergence unaddressed while removing only the symbol.
- Explaining the removal with a claim that is itself false — the exact defect class.

## Counterweight Pass

- Both deletions verified real, not bypassed: no `missing = set(numbers) - returned`
  remains and `snapshot_payload_text` has zero occurrences repo-wide. `canonical_json`
  survives only at its owner and one legitimate re-export, so no dual snapshot
  serialization path remains.
- The deleted cross-check genuinely could not fire, so nothing was lost with it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:298 | action: fix | note: the comment left at the removal site claimed `capture_issue` "compares the BACKEND's answer to the requested number" — it did not; it only null-checked. A false protection asserted in the explanation of the fix for a false protection. Comment corrected.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/issue_source_capture_lib.py:186 | action: fix | note: the gap the false comment revealed is real. The GraphQL query selects `number` but the return stamps the REQUESTED number, so a backend answering #999 to a request for #514 yields a snapshot labelled #514 carrying #999's content, and the freeze receipt binds its digest. Added a `wrong_issue` refusal and a test.
- F3 | bin: over-worry | evidence: strong | ref: scripts/issue_source_capture_lib.py:264 | action: document | note: removing the cross-check looked like reducing defence in depth; it removed a branch that could not execute

## Boundary Ownership

- Producer: `capture_issue`, which owns both real refusals.
- Consumer: the freeze receipt and the closeout authorization that reads its digest.
- Owning surface: the issue-source capture library.
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

- The new `wrong_issue` refusal fires only when the backend RETURNS a number. A backend
  that omits `number` entirely is still stamped with the requested one.
- Snapshot serialization is single-path because there is one caller, not because a test
  pins it.
