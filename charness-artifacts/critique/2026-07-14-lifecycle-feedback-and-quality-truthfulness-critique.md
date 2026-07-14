# Critique Review
Date: 2026-07-14

## Decision Under Review

Add deterministic, linked lifecycle capture to verified issue-close and release-
publish producers, reconcile the current quality record, and keep objective
follow-through separate from human satisfaction.

## Failure Angles

- Problem framing and boundary ownership: whether the producer owns an exact
  lifecycle fact, whether replay/conflict handling can inflate evidence, and
  whether downstream reporting changes the fact into a stronger claim.
- Operational and communication safety: whether capture happens after the
  irreversible proof, failures stay non-fatal but visible, installed-plugin
  layout works, and durable artifacts state the correct non-claims.

## Counterweight Pass

- Real blockers: downstream satisfaction overclaim, missing durable release
  capture status, untested partial/conflicting identities, and an unproven plugin
  mirror.
- Cheap bundle: narrow the concurrency wording to one locked append-mode write.
- Over-worry: a new standing gate, broad concurrency framework, validator
  refactors, and retroactive installed behavior proof for v1.0.5.
- Valid but deferred: rotated mixed-stream reconciliation and richer human
  feedback capture.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/usage_episode_feedback.py | action: fix | note: classify closed_issue and released as objective lifecycle follow-through, not human satisfaction
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_artifact_sections.py | action: fix | note: render structured lifecycle capture status and its non-claim in the durable release artifact
- F3 | bin: act-before-ship | evidence: strong | ref: tests/test_lifecycle_usage_capture.py | action: fix | note: exercise partial/conflicting identities and installed-plugin capture without a skip
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/lifecycle_usage_capture.py | action: document | note: describe the actual locked append guarantee without claiming cross-producer atomicity
- F5 | bin: over-worry | evidence: weak | ref: charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md | action: defer | note: do not add gates, a concurrency framework, validator cleanup, or retroactive release behavior proof
- F6 | bin: valid-but-defer | evidence: moderate | ref: docs/product-success-metrics.md | action: defer | note: retain explicit human feedback and rotated-stream reconciliation as later product-evidence work

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the spawn surface accepted the requested fields but did not return provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated

Two distinct angle reviewers and one separate counterweight ran against
`charness-artifacts/critique/2026-07-14-003710-packet.md`. Parent-side reviewer
fingerprint verification passed with no worktree or index drift after each
review result.

## Boundary Ownership

- Producer: verified issue-close and release-publish workflows.
- Consumer: usage episode reporting and release artifact readers.
- Owning surface: lifecycle producers own the compact fact; the shared capture helper owns linkage/persistence; reporting owns interpretation.
- Verdict: owned-correctly
