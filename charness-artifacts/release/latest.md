# Release Surface Check
Date: 2026-08-12

## Scope

Advanced `charness` toward release `5.0.1` (tag `v5.0.1`) through the repo-owned release helper.

## Current Version

- previous version: `5.0.0`
- target version: `5.0.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v5.0.1`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
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
- Retro artifact: `charness-artifacts/retro/2026-08-12-v5-0-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 87.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-12-104057-packet.json`
  - `charness-artifacts/critique/2026-08-12-104057-packet.md`
  - `charness-artifacts/critique/2026-08-12-105645-packet.json`
  - `charness-artifacts/critique/2026-08-12-105645-packet.md`
  - `charness-artifacts/critique/2026-08-12-110534-packet.json`
  - `charness-artifacts/critique/2026-08-12-110534-packet.md`
  - `charness-artifacts/critique/2026-08-12-111219-packet.json`
  - `charness-artifacts/critique/2026-08-12-111219-packet.md`
  - `charness-artifacts/critique/2026-08-12-111657-packet.json`
  - `charness-artifacts/critique/2026-08-12-111657-packet.md`
  - `charness-artifacts/critique/2026-08-12-final-goal-disposition-final3-packet.json`
  - `charness-artifacts/critique/2026-08-12-final-goal-disposition-final3-packet.md`
  - `charness-artifacts/critique/2026-08-12-issue-581-adapter-example-resolution.md`
  - `charness-artifacts/critique/2026-08-12-issue-593-hotl-target-binding-critique.md`
  - `charness-artifacts/critique/2026-08-12-issue-594-closeout-draft-scope-critique.md`
  - `charness-artifacts/critique/2026-08-12-issue-603-quality-packet-critique.md`
  - `charness-artifacts/critique/2026-08-12-issue-604-canonical-gate-critique.md`
  - `charness-artifacts/critique/2026-08-12-issues-585-596-598-closeout-review.md`
  - `charness-artifacts/critique/2026-08-12-release-5-0-1-packet.json`
  - ... 67 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-12-release-5-0-1-publish.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.904s
- `quality_command`: 114.155s
- `fresh_checkout_probes_initial`: 4.076s

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
