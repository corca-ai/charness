# Round 5 Closeout Disposition Review

Date: 2026-07-13
Goal: north-star-autonomous-two-hour-release-round-5
Fresh-eye satisfaction: parent-delegated — bounded release and post-release
quality observers checked public/install evidence and caught stale durable
memory before this artifact accepted closeout.
Decision: accept v1.0.4 and the round-five goal only after release, quality,
goal, retro, and handoff records agree with the independent evidence.

## Failure Angles

### Public presence without substantive release content

- Risk: a tag or helper success could escape while the public release omits the
  operator-visible fixes.
- Evidence: the bounded observer queried the unauthenticated GitHub REST release
  resource, received HTTP 200, and found both the catalog invalid-root and
  custom-home Claude changes in the body.
- Disposition: resolved by
  `charness-artifacts/probe/2026-07-13-v1.0.4-independent-release-observer.json`.

### Published bits without installed-state agreement

- Risk: the public release could be correct while local source, caches, or host
  plugin state remained at 1.0.3.
- Evidence: the release helper refreshed the install, then a separate observer
  read CLI, checkout, provenance, Codex source/cache, and Claude state as 1.0.4
  with no Codex source/cache drift.
- Disposition: resolved by the independent observer artifact and
  `charness-artifacts/release/latest.md`.

### Passing release with stale durable quality memory

- Risk: final proof could exist while the goal and quality artifacts still say
  it is missing, leaving the next session with a false state model.
- Evidence: the post-release quality reviewer placed closeout on HOLD for this
  exact contradiction.
- Disposition: applied before goal completion by reconciling quality, goal,
  retro, and handoff records from the release evidence.

### Unlocked or mutable-bundle proof

- Risk: focused tests or an earlier HEAD could be mistaken for final-bundle
  confidence.
- Evidence: the verification-lock standing broad pytest passed in 94.92s for
  the frozen bundle, followed by the 72.297s release gate and fresh-checkout
  probes. The release tag is `ef4016b8`; the expected post-publish evidence
  commit makes remote main `84354696` rather than pretending tag and branch are
  identical.
- Disposition: resolved; the distinct SHA roles are explicit.

## Counterweight

- A real Claude custom-home session was not exercised. The fake-CLI public
  process tests prove environment propagation and both mutation directions,
  but the real-host claim remains intentionally open.
- Cautilus, remote CI, issue closure, and a test-speed improvement were not part
  of the accepted evidence. The run reports their absence rather than treating
  them as implied by a release.
- The managed-install release-only tests are expensive, but no safe same-command
  improvement was demonstrated; keeping them is preferable to optimizing the
  proof boundary by assertion.

## Structured Findings

- public-install-closeout | bin: act-before-ship | evidence: strong | ref: charness-artifacts/probe/2026-07-13-v1.0.4-independent-release-observer.json | action: document | note: durable public and installed observer evidence plus post-release memory reconciliation were completed before goal closeout.
- release-bundle | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/latest.md | action: document | note: v1.0.4 contains two reproduced operator-boundary fixes with focused and locked-bundle proof.
- extra-proof-floors | bin: over-worry | evidence: moderate | ref: docs/handoff.md | action: document | note: no extra broad floor, destructive real-host mutation, remote CI, or issue lifecycle action was manufactured for this patch.
- root-host-proof-trigger | bin: valid-but-defer | evidence: moderate | ref: docs/handoff.md#next-session | action: defer | note: evaluate a narrow real-host release trigger for root charness host-plugin mutations only with a safe scoped proof design.

## Reviewer Tier Evidence

- Requested tier: gpt-5.5 medium
- Requested spawn fields: model=gpt-5.5; reasoning_effort=medium; role=bounded read-only reviewer
- Host exposure state: applied
- Application state: host-confirmed: bounded release/post-release reviewers returned read-only findings through separate agent contexts.

Fresh-eye bounded release and post-release quality observers used read-only
remote/API/install channels distinct from the release helper.

## Boundary Ownership

- Verdict: owned-correctly

The release helper owned mutation and initial verification. The bounded
observer owned public and installed readback. This artifact owns only the human
disposition of those claims and records the remaining nonclaims.
