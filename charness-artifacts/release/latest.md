# Release Surface Check
Date: 2026-07-14

## Scope

Advanced `charness` toward release `1.0.6` (tag `v1.0.6`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.5`
- target version: `1.0.6`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v1.0.6`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-07-14-v1-0-6-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 4.
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
- Evaluated changed paths: 73.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-13-231102-packet.json`
  - `charness-artifacts/critique/2026-07-13-231102-packet.md`
  - `charness-artifacts/critique/2026-07-14-003710-packet.json`
  - `charness-artifacts/critique/2026-07-14-003710-packet.md`
  - `charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md`
  - `charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-critique.md`
  - `charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.json`
  - `charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-5-handoff-refresh-critique.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-dup-ratchet-packet.json`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-dup-ratchet-packet.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-dup-ratchet-resolution-critique.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-critique.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.json`
  - `charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.md`
  - `charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md`
  - `charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - ... 53 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 0.081s
- `quality_command`: 77.393s
- `fresh_checkout_probes_initial`: 3.002s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
