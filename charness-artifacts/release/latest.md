# Release Surface Check
Date: 2026-06-27

## Scope

Advanced `charness` toward release `0.56.9` (tag `v0.56.9`) through the repo-owned release helper.

## Current Version

- previous version: `0.56.8`
- target version: `0.56.9`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.56.9`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 20.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-28-issue-405-405-disposition-review.md`
  - `charness-artifacts/critique/2026-06-28-v0.56.9-release-critique.md`
  - `charness-artifacts/find-skills/latest.json`
  - `charness-artifacts/find-skills/latest.md`
  - `charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md`
  - `charness-artifacts/probe/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/notes-v0.56.9.md`
  - `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/shared/references/fresh-eye-subagent-review.md`
  - `plugins/charness/skills/quality/references/quality-lenses.md`
  - `skills/public/quality/references/quality-lenses.md`
  - `skills/shared/references/fresh-eye-subagent-review.md`

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-28-v0.56.9-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.856s
- `quality_command`: 67.392s
- `fresh_checkout_probes_initial`: 2.915s

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
