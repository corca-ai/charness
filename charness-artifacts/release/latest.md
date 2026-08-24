# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-25

## Scope

Advanced `charness` toward release `6.4.1` (tag `v6.4.1`) through the repo-owned release helper.

## Current Version

- previous version: `6.4.0`
- target version: `6.4.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 211.0s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release`).
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.4.1`, checked at `post-bump, pre-commit`.

## Release State

- local release mutation: complete
- branch/tag push: pending independent claims review.
- GitHub release record: pending independent claims review before creation
- public release surface verification: pending independent claims review
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: `not_run`.
- This is a recorded absence, not a passing preflight: no focused adapter check is claimed to have completed successfully for this release.
  - Reason: focused preflight status is `not_required`; no commands were required

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-24-v6-4-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 216.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-file-backed-work.md`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.md`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-round2-resolution.md`
  - `charness-artifacts/critique/2026-08-24-issue-689-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.json`
  - ... 196 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-25-release-6-4-1.md`.

## Claims Review

- Claims review: not yet performed -- THIS record is the subject of the pending independent review, and publication is stopped until that review is committed.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.004s
- `cli_skill_surface_gate`: 1.931s
- `quality_command`: 211.042s
- `fresh_checkout_probes_initial`: 4.315s

## Baton Reconcile

- Baton reconcile observation: not recorded by this helper invocation.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`
- `python3 scripts/closeout_bundle.py --help >/dev/null`
- `python3 scripts/validate_retro_handoff_wiring.py --help >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> patch, not minor: this release fixes validation, identity, diagnostic, and packaging/consumer-friction paths without adding or changing a public command or install surface.