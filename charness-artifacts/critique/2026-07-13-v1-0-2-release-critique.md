# v1.0.2 Release Critique
Date: 2026-07-13

## Decision Under Review

Publish `v1.0.2` as a patch release over `009d56aa..HEAD`, bundling the
issue-plan local-target ordering repair, runtime aggregate test-economics
repair, Codex cache proof-economics repair, and their quality/goal evidence.

Packet Consumed:
`charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.md`.

## Counterweight Verdict

Verdict: APPROVE for patch release after the exact release bytes pass the clean
verification lock and the repo-owned release helper completes publication plus
distinct-channel readback.

The accepted counterweight is the replacement read-only pass run after a prior
counterweight attempt mutated/staged the shared tree. That prior attempt was
quarantined by a failed reviewer-boundary fingerprint and supplies no verdict;
the replacement pass verified zero drift and independently reclassified the
two angle findings.

## Act Before Ship

- Persist this critique and the release packet before release mutation.
- Run the exact clean verification lock after critique persistence.
- Use the release helper for the patch bump and surface sync.
- Run configured fresh-checkout probes and scan the release carrier for issue
  close keywords before publication.
- After publish, require public unauthenticated content/readback and installed
  doctor/readiness evidence; helper green or tag existence is not terminal proof.

## Bundle Anyway

- Public notes should say invalid `issue resolve --target` is rejected locally
  before provider readiness checks.
- Describe test-speed changes as maintainer/local quality-test economics, not
  user-facing runtime speed.
- Preserve non-claims: no Cautilus run, no #433/#436 closure, no full-suite speed
  claim.

## Over-Worry

- No minor or major bump is needed; valid public invocation shape is unchanged.
- No Cautilus evaluation is required for this patch because deterministic
  no-call proof covers the observed issue ordering defect and Cautilus remains
  ask-before-run.
- No additional real-host proof trigger matched this slice.

## Valid But Defer

- Managed-install serial test economics remain a measured follow-up.
- Broader local-error ordering audit for the issue CLI is not a release blocker.
- Full-suite speed benchmarking should wait for repeated same-condition runs.

## Boundary Ownership

- Producer: release helper and release adapter produce version bump, manifest
  sync, tag/release publication, fresh-checkout probes, and install refresh.
- Consumer: operators and installed Charness users consume the published plugin
  package, release notes, update instructions, and public tag/release surface.
- Owning surface: release skill workflow plus repo release adapter.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Operational release lens: parent-delegated fresh-eye review, read-only,
  APPROVE after exact lock/publication proof.
- User/compatibility release lens: parent-delegated fresh-eye review, read-only,
  APPROVE as patch with value-facing notes.
- Counterweight: replacement parent-delegated read-only pass, APPROVE after
  separating the exact-byte/publication blockers from Cautilus, semver, and
  real-host over-worry; reviewer-boundary fingerprint verified zero drift.
- Requested tier: high-leverage for release-boundary critique.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium,
  service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: provider application not exposed; no application claim.

Fresh-Eye Satisfaction: parent-delegated.
