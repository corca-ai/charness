# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-13

## Scope

Advanced `charness` toward release `5.1.0` (tag `v5.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `5.0.1`
- target version: `5.1.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.

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
- Focused preflight commands: none executed.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-12-v5-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 8.
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_claims_review.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
- Evaluated changed paths: 270.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-12-140743-packet.json`
  - `charness-artifacts/critique/2026-08-12-140743-packet.md`
  - `charness-artifacts/critique/2026-08-12-141010-packet.json`
  - `charness-artifacts/critique/2026-08-12-141010-packet.md`
  - `charness-artifacts/critique/2026-08-12-142919-packet.json`
  - `charness-artifacts/critique/2026-08-12-142919-packet.md`
  - `charness-artifacts/critique/2026-08-12-143920-packet.json`
  - `charness-artifacts/critique/2026-08-12-143920-packet.md`
  - `charness-artifacts/critique/2026-08-12-144548-packet.json`
  - `charness-artifacts/critique/2026-08-12-144548-packet.md`
  - `charness-artifacts/critique/2026-08-12-145810-packet.json`
  - `charness-artifacts/critique/2026-08-12-145810-packet.md`
  - `charness-artifacts/critique/2026-08-12-151434-packet.json`
  - `charness-artifacts/critique/2026-08-12-151434-packet.md`
  - `charness-artifacts/critique/2026-08-12-152909-packet.json`
  - `charness-artifacts/critique/2026-08-12-152909-packet.md`
  - `charness-artifacts/critique/2026-08-12-154616-packet.json`
  - `charness-artifacts/critique/2026-08-12-154616-packet.md`
  - `charness-artifacts/critique/2026-08-12-154946-packet.json`
  - ... 250 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-13-release-5-1-0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 2.027s
- `quality_command`: 124.935s
- `fresh_checkout_probes_initial`: 4.159s

## Baton Reconcile

- Baton reconcile observation: not recorded by this helper invocation.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`
- `python3 scripts/closeout_bundle.py --help >/dev/null`
- `python3 scripts/validate_retro_handoff_wiring.py --help >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
