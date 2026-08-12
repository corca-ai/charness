# Issue 602 Create Verification Grammar Resolution Critique
Date: 2026-08-13

## Decision Under Review

Replace create's deferred raw-backend readback affordance with a typed
`verify-create` operation, while retaining automatic readback and keeping
body-fidelity claims conditional on the original body file.

## Failure Angles

- A custom backend view template or response could be for another target while
  the tool reported a verified readback.
- A missing or non-string returned body could be mistaken for an empty body.
- A public transport argv or help literal could lead an operator to retry a
  mutation or prime a refused placeholder title.
- The new command could overclaim provider behavior, selection policy, or body
  byte fidelity without its original body input.

## Counterweight Pass

- R1 found the missing template target requirements, response target checks,
  empty-body false positive, raw create argv, unparseable verification
  affordance, and absent help regression. The repair requires `{repo}`,
  `{number}`, and `{json_fields}` before backend invocation; validates returned
  number/repository/body shape; exposes no raw argv; and adds the focused tests.
- R2 found that repository silence could still pass an identity readback and
  that boolean, zero, and negative numbers could pass an integer-shaped path.
  The parent now requires explicit matching repository evidence and positive
  real integers in the helper, parser, and create affordance. These R2 repairs
  are accepted-unreviewed under the two-round cap.
- The pre-commit length gate then required extracting the already-reviewed
  verifier into cohesive `issue_create_verify.py`; focused behavior, lint, and
  length checks re-proved that mechanical boundary change without a third
  review round.
- Provider roundtrips, agent choice, issue-state checks, global custom-backend
  URL policy, and a broader placeholder-title policy remain outside this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: R1 fresh-eye review | action: fix | note: bind custom view templates and returned response identity before reporting verification.
- F2 | bin: act-before-ship | evidence: strong | ref: R1 fresh-eye review | action: fix | note: require a string returned body for byte verification and never expose transport argv as workflow guidance.
- F3 | bin: act-before-ship | evidence: strong | ref: R2 fresh-eye review | action: fix | note: require returned repository evidence and positive non-boolean issue numbers; R2 repair accepted-unreviewed.
- F4 | bin: valid-but-defer | evidence: strong | ref: issue 602 causal boundary | action: defer | note: no provider, agent-choice, state-verification, or title-policy claim is made.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot task with inherited model and effort.
- Host exposure state: metadata-hidden
- Application state: R1 repairs received R2 review; R2 repairs are accepted-unreviewed under the two-round cap.
- Delivery state: findings-received; R1 contract, CLI, and counterweight findings received; R2 contract, CLI, and counterweight findings received.
- Boundary state: R1 review fingerprints were parent-attributed. R2 CLI and contract fingerprints were parent-attributed. R2 counterweight fingerprint was quarantined because the parent documentation repair was not declared in that verifier invocation; its repair finding was acted on but no R2 approval is claimed.

## Fresh-Eye Satisfaction

parent-delegated; R1 and R2 findings received. R2 repairs are
accepted-unreviewed under the required two-round cap.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-172306-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-172306-packet.json
- Packet SHA256: 922bdde9649b8eada95115881d0cc12d08cd948810635082fe9b5dc740b939e2
- Identity SHA256: f9c23cbd9990a21c4f4f9da5f9f6b48910fcc749d931143c5c5820d10481f5c2

## Boundary Ownership

- Producer: issue create lifecycle and selected issue-backend view operation.
- Consumer: operator or agent completing deferred create readback through issue_tool.
- Owning surface: typed issue workflow grammar and create verification payload.
- Verdict: owned-correctly
