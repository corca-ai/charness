# Issue 542 Closeout Target Disagreement Resolution Critique
Date: 2026-08-13

## Decision Under Review

Make a protected `close-with-comment` refusal identify a disagreement between
its manual target declaration and separately supplied CLI target, without
changing the aggregate interpretation of other carrier sources.

## Failure Angles

- A source-specific branch could accidentally relax aggregate target protection
  or alter the commit-hook interpretation.
- A refusal could reach the irreversible backend close boundary before it is
  rendered to the operator.
- A new error code could omit either conflicting identity or shadow the matching
  singleton path.

## Counterweight Pass

- R1 found two evidence gaps: exact conflicting targets were not asserted and
  matching singleton `close-with-comment` behavior was not shown to reach its
  existing next floor. Both regressions were added.
- R2 confirmed the repaired proof: mismatch stays source-scoped and names both
  `repo#number` values; matching singletons reach `matrix_incomplete`; commit
  and multi-target carriers remain `not_singleton`; ingress remains zero-call.
- Extending this semantic distinction to unprotected targets or a broad source
  taxonomy refactor is over-worry for this protected closeout boundary.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_evidence_boundary_crosswalk.py | action: fix | note: assert both declaration and CLI target identities in the distinct refusal.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_evidence_boundary_crosswalk.py | action: fix | note: prove matching singleton close-with-comment reaches the existing matrix floor.
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/issue/scripts/issue_close.py | action: defer | note: hosted valid-close behavior is outside this local refusal repair and was not attempted.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot task with inherited model and effort.
- Host exposure state: metadata-hidden
- Application state: R1 semantic, ingress, and counterweight reviewers found two proof gaps; the parent repaired them. R2 semantic, ingress, and counterweight reviewers accepted the repaired surface. All six reviewer boundary fingerprints were clean.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; two rounds completed. R1 changed the proof surface; R2 found
no remaining Act Before Ship concern.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-164956-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-164956-packet.json
- Packet SHA256: df0407ea7a2cfc90d80769e0a8e7467a5a4352b2ea56b84f3f3af32ec1d68806
- Identity SHA256: 698fe6cdd586237853a79710111460a58e9039cf0b884ec4d35c2b3f34dfdde2

## Boundary Ownership

- Producer: `issue_close` supplies the manual declaration and CLI target to crosswalk authorization.
- Consumer: the close ingress renders refusal before any backend close operation.
- Owning surface: source-aware protected closeout authorization.
- Verdict: owned-correctly
