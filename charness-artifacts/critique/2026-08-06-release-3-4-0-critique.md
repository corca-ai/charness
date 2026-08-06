# Critique Review
Date: 2026-08-06

## Release Scope

- Version: `3.4.0` from `3.3.0`; minor bump justified by additive maintained
  repository-operator capability without changing existing invocation
  expectations.
- Tag: `v3.4.0`.
- Consumer outcome: operators gain an opt-in repo-local closeout bundle plan/
  execute flow with a repository-relative receipt and a companion
  retro-to-handoff wiring validator; this is not a new top-level `charness`
  command or ordinary installed-user workflow.

## Surface-Lock Inventory

- Versioned packaging manifest and Claude/Codex plugin manifests/marketplace
  source path.
- Root and checked-in plugin copies of `closeout_bundle.py`,
  `closeout_bundle_lib.py`, and `validate_retro_handoff_wiring.py`.
- `docs/development.md`, closeout execution contract, goal/handoff guidance,
  and the scoped `v3.4.0` release notes.
- Release adapter fresh-checkout probe declarations and the direct help
  surfaces.

## Decision Under Review

Whether the additive 3.4.0 release surface is sufficiently synchronized,
discoverable, and honestly documented to enter version-bump and publication
preflight.

## Failure Angles

- Operational: a manifest or plugin mirror could drift, or release probes could
  omit a newly maintained direct-script surface.
- Communication: generated release notes could omit scope, update/rollback
  guidance, or promote local proof into public verification.
- Humane interface: operators could mistake the opt-in direct script for a new
  top-level command, or fail to find its plan-first workflow and receipt path.

## Counterweight Pass

The initial angle round found real pre-ship gaps in release notes, direct help
probe declarations, stable workflow guidance, and receipt-path wording. Those
repairs were applied in `d9a6baa4`: scoped notes were added, both direct help
probes were declared, `docs/development.md` became the stable first-reader
path, and help/docs now say “repository-relative receipt intended for check-in.”
The separate counterweight rejected a new root command and rejected promoting
configured-but-not-run fresh-checkout probes to execution proof. The final
resolution reviewer read the repaired fixed-target packet and returned SHIP.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/v3.4.0-notes.md:1 | action: document | note: Scoped notes name both additive capabilities, the direct-script boundary, update/rollback path, and local-only proof limits.
- F2 | bin: bundle-anyway | evidence: strong | ref: .agents/release-adapter.yaml:76 | action: document | note: Direct help probes for both new scripts are declared; actual fresh-checkout execution remains a separate receipt.
- F3 | bin: over-worry | evidence: strong | ref: docs/development.md:55 | action: defer | note: A new top-level `charness closeout` command is unnecessary for this explicitly opt-in repo-local workflow.
- F4 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/probe/2026-08-06-closeout-local-proof.json:29 | action: document | note: Provider, installed-consumer, remote-CI, host-window, Cautilus, push, tag, publication, and release-readback proof remain separate post-boundary claims.

## Operator Action Required

- Before publication, pass the tracked critique artifact to the publish helper
  with `--critique-artifact` and supply the tracked notes with `--notes-file`.
- Keep the version bump at minor `3.4.0`; do not add a root CLI command as part
  of this release.
- After publication, follow the adapter's update/doctor readback and distinct
  public release verification channels.

## Upgrade Path

Existing callers need no migration or default-behavior change. Operators may
remain on 3.3.0 if they do not need the new repo-local workflow. Otherwise run
`charness update`, then `charness version` and `charness doctor`. Roll back the
plugin/workflow surface with a source checkout at `v3.3.0` and the documented
`--skip-cli-install` path; a full managed-CLI rollback remains outside this
release's local proof.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: spawn accepted; provider-applied model metadata was not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; three release-angle reviewers, a separate counterweight, and
the final resolution reviewer ran read-only. The final reviewer
(`019fd76c-6230-7d03-be50-35a8c21cf677`) returned SHIP for fixed target
`d9a6baa4`; rail-1 boundary verification was clean for the angle and resolution
windows.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.json
- Packet path: charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.json
- Packet SHA256: 56c750768c37bcbd420202a8db7e99e254a359d5c7e0e1b378e73d9f0bdf7097
- Identity SHA256: 6b5a41fd1e0d82f3f105808dbdf375260556f9dc5ed89f24fbb140a0f7a2d9db

## Boundary Ownership

- Producer: packaging/version sync, checked-in plugin mirrors, release notes,
  direct help/probe declarations, and the repo-owned release helper.
- Consumer: maintainers publishing 3.4.0 and operators reading notes or using
  the repo-local workflow; public/install/CI consumers require distinct reads.
- Owning surface: synchronized release surfaces plus the tracked release notes
  and critique artifact, not session prose or local green alone.
- Verdict: owned-correctly
