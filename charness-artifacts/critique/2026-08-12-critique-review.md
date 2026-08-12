# Critique Review
Date: 2026-08-12

## Decision Under Review

Implement only the cited, append-only local lesson ledger and its gate; defer
selection, scoring, contract-register state, and graduation execution.

## Failure Angles

- State lifecycle: a materialized lesson view could diverge from transitions.
- Graduation boundary: a ledger green could be mistaken for contract-edit authority.
- Append-only integrity: committed transitions could be rewritten while retaining a coherent projection.

## Counterweight Pass

- Act Before Ship: retain the existing candidate/digest rebuild gate and add a
  separate replay/provenance ledger check.
- Bundle Anyway: use strict schema allowlists and reject duplicate IDs.
- Over-Worry: do not add UCB, scoring, registration, or cryptographic history.
- Valid but Defer: Git-history tamper resistance and a reviewed contract-diff
  receipt remain outside this local state slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/lesson_ledger_lib.py | action: fix | note: replayed projection and cited recurrence-class provenance must agree.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/lesson_ledger_lib.py | action: fix | note: reject deferred graduation/register fields and rewritten committed transitions.
- F3 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md | action: defer | note: graduation conservation belongs to the later register/proposal slice.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: host task API; no model/effort metadata was exposed to this record.
- Host exposure state: metadata-hidden
- Application state: n/a; the host returned findings but no applied-tier confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated: three pre-implementation reviewers and two proof-surface
rounds returned through the host task channel; shared-tree fingerprint checks
were clean after each returned review.

## Reviewed Input Identity

The pre-implementation packet was consumed before its findings changed the
specification; it is retained at
`charness-artifacts/critique/2026-08-12-001253-packet.md`. It is not used as a
post-repair binding claim. The repaired code received its own two fresh-eye
rounds.

## Boundary Ownership

- Producer: retro artifacts declare recurrence-class evidence.
- Consumer: the ledger validator reports local state integrity to the quality runner.
- Owning surface: repo-python and retro artifact state.
- Verdict: owned-correctly.
