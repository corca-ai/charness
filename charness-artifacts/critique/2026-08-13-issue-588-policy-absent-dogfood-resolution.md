# Issue 588 Policy-Absent Dogfood Resolution Critique
Date: 2026-08-13

## Decision Under Review

Render a policy-absent consumer repository as typed not-applicable output rather
than an uncaught traceback, without treating present but invalid policy state as
applicable or clean.

## Failure Angles

- A malformed or directory policy could be silently misclassified as absence.
- Root, shipped skill, and plugin entrypoints could disagree.
- A policy-present unknown skill could lose its existing error behavior.

## Counterweight Pass

- R1 found the initial `is_file()` absence check falsely accepted a directory.
  The repair recognizes only a nonexistent path as absence; the directory
  fixture preserves the original validation error.
- R2 approved root human, quality summary/detail, and plugin behavior, plus
  policy-present unknown-ID behavior. No broader malformed-policy renderer is
  claimed in this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: R1 fresh-eye review | action: fix | note: distinguish nonexistent from existing non-file policy paths.
- F2 | bin: bundle-anyway | evidence: moderate | ref: R1 fresh-eye review | action: document | note: cover root human and quality summary in addition to detail output.
- F3 | bin: valid-but-defer | evidence: strong | ref: R2 review | action: defer | note: malformed-policy friendly rendering remains outside the absence-only repair.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot task with inherited model and effort.
- Host exposure state: metadata-hidden
- Application state: R1 repair was read by R2; R2 found no blocker.
- Delivery state: findings-received; R1 and R2 findings were delivered.

## Fresh-Eye Satisfaction

parent-delegated; R1 and R2 completed, with R1 repair reviewed in R2.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-173947-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-173947-packet.json
- Packet SHA256: 610b456096f3c0f818ceeeb52b8a22b65616f08bfdd7d0991c3f7ddf4a91a116
- Identity SHA256: 3fc13c694ebb70ef7ad5d7e0a550496cc1a5b733eca5d421ec7f017dffa10906

## Boundary Ownership

- Producer: public-skill dogfood policy preflight and matrix builder.
- Consumer: repository operator invoking root or shipped dogfood helpers.
- Owning surface: typed public-helper applicability contract.
- Verdict: owned-correctly
