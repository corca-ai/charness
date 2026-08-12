# Post-publication issue closeout carriers

Date: 2026-08-12

## Decision Under Review

Whether to manually close #603, #604, #581, #594, and #593 after the published
5.0.1 release, using one validated post-publication carrier per issue rather
than retrofitting closing keywords into an already-published release commit.

## Failure Angles

- Minto: each comment must make the reporter's repaired outcome and the
  remaining non-claims actionable, not merely clear the tracker.
- Jackson: a prior release critique cannot stand in for review of the actual
  external close comments; their claims and behavior dispositions need a
  current reader.
- Counterweight: distinguish an appropriate user-directed manual fallback from
  needless re-release, retagging, or an empty direct-commit carrier.

## Counterweight Pass

- Act Before Ship: replace the prior release-critique reference in every
  carrier with this artifact, which reviewed the actual comment bodies.
- Bundle Anyway: close each issue with its independently draft-verified body,
  then use a separate GitHub `CLOSED` readback for every issue.
- Over-Worry: do not amend, retag, or create an empty commit merely to obtain
  automatic closure; the published release did not request issue closure.
- Valid but Defer: consumer CI/runtime and third-party provider execution stay
  `local-only-by-contract` dispositions, not closure claims.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: /tmp/charness-close-603.md | action: fix | note: bind every actual manual carrier to this current critique, not only the earlier release critique that deferred carrier review.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/references/closeout-discipline.md | action: document | note: publish each validated manual carrier and independently verify `CLOSED` for #603, #604, #581, #594, and #593.
- F3 | bin: over-worry | evidence: strong | ref: charness-artifacts/release/latest.md | action: defer | note: do not retag or manufacture a direct-commit close carrier because 5.0.1 published without requested issue closure.
- F4 | bin: valid-but-defer | evidence: strong | ref: /tmp/charness-close-604.md | action: defer | note: retain typed local-only dispositions; no hosted consumer or provider behavior is established by these local proofs.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=3; host model and effort controls inherited from this session.
- Host exposure state: host-defaulted
- Application state: host returned separate delegated reviewer contexts; no provider application metadata was exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — Minto, Jackson, and counterweight reviewers independently
read the packet and all five pending closeout bodies. The reviewer boundary
window `issue-post-publication-closeout-review` verified clean before this
artifact was written. A final independent Minto, Jackson, and counterweight
pass re-read the rebound input and the same bodies; window
`issue-post-publication-closeout-final-review` also verified clean.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.json
- Packet SHA256: d10935077f42d1aa4ff7a6eb1f6c345591d66bc2fa0ff009ae0da9a33a9b4102
- Identity SHA256: 0709d171854b5ab3ba13358c4c56980e299719888a72ce90b02779228d6d3bc4

## Boundary Ownership

- Producer: the issue-resolution workflow produces the classification ledger,
  behavior disposition, and manual close comment.
- Consumer: the reporter and future tracker reader need an honest resolution
  statement plus the tracker state.
- Owning surface: issue closeout carrier and GitHub issue state.
- Verdict: owned-correctly

## Next Move

Update each draft to cite this artifact, publish via `close-with-comment`, and
verify each resulting GitHub state as `CLOSED`.
