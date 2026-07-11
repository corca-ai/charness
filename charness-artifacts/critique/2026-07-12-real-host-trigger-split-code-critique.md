# Real-Host Trigger Surface Split Code Critique
Date: 2026-07-12

## Decision Under Review

Subscribe release real-host proof to an exact host-sensitive external-tool
surface instead of the broad integrations surface whose plugin wildcard made
unrelated scripts trigger the nose checklist.

## Failure Angles

- Ownership completeness: the initial split omitted control-plane library,
  lifecycle, and renderer dependencies that directly feed doctor/install paths.
- Behavior: narrowing must keep true positives and fail-loud unresolved ids
  while proving an unrelated derived `run-quality.sh` remains off.

## Counterweight Pass

- Act Before Ship: fixed — added exact root and plugin paths for
  `control_plane_lib.py`, `control_plane_lifecycle_lib.py`, and
  `control_plane_render.py` after a fresh-eye HOLD.
- Bundle Anyway: the new surface and release subscription ship together; the
  existing broad surface stays intact for validation and retro consumers.
- Over-Worry: no generic file-dependency graph or all-plugin host proof is
  justified by the observed false positive.
- Valid but Defer: future host-sensitive files outside the explicit surface
  need a normal surface update when introduced.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json | action: fix | note: include direct control-plane dependencies and mirrors
- F2 | bin: bundle-anyway | evidence: strong | ref: .agents/release-adapter.yaml | action: fix | note: subscribe release only to external-tool-control-plane
- F3 | bin: over-worry | evidence: weak | ref: n/a | action: defer | note: do not make every checked-in plugin script a real-host trigger

## Fresh-Eye Satisfaction

parent-delegated — ownership and behavior reviewers plus a separate
counterweight completed read-only. The initial HOLD was fixed; stable-diff
reruns approved and reviewer-boundary verification reported zero drift.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`,
  `service_tier=priority` for the ownership reviewer; other reviewers used a
  lower-power host mapping appropriate to the bounded checks.
- Host exposure state: requested_fields_sent
- Application state: requested fields were accepted where supplied; provider
  application metadata was not exposed.

## Boundary Ownership

- Producer: `.agents/surfaces.json` declares named path ownership.
- Consumer: the release real-host detector subscribes through the adapter.
- Owning surface: `external-tool-control-plane`; the broad integrations surface
  remains a separate validation/retro concern.
- Verdict: moved-to-owner

## Verification

- Six focused real-host routing tests passed.
- Surface and integration validators plus dry-run support/update checks passed.
- The current release delta now reports `real_host.required=false`; actual
  clean-host proof remains a separate publication-boundary claim.
