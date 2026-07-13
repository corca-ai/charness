# Release Surface Check
Date: 2026-07-13

## Scope

Advanced `charness` toward release `1.0.3` (tag `v1.0.3`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.2`
- target version: `1.0.3`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v1.0.3`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

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
- Retro artifact: `charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 19.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-critique.md`
  - `charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.json`
  - `charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.md`
  - `charness-artifacts/debug/2026-07-13-quality-scaffold-reproduction-source-omission.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md`
  - `charness-artifacts/release/2026-07-13-v1.0.3-notes.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-13-071142-packet.json`
  - `charness-artifacts/retro/2026-07-13-071142-packet.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py`
  - `skills/public/quality/scripts/scaffold_quality_artifact.py`
  - `tests/test_quality_scaffold.py`

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.790s
- `quality_command`: 72.016s
- `fresh_checkout_probes_initial`: 2.938s

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
