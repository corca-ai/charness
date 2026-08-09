# Release Surface Check
Date: 2026-08-09

## Scope

Advanced `charness` toward release `4.1.0` (tag `v4.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `4.0.0`
- target version: `4.1.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v4.1.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-08-09-v4-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `scripts/capability_catalog_sources.py`
- Evaluated changed paths: 250.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-commit`
  - `.githooks/pre-push`
  - `AGENTS.md`
  - `charness-artifacts/audit/2026-08-09-no-observed-effect-census.md`
  - `charness-artifacts/audit/closeout-floors.md`
  - `charness-artifacts/critique/2026-08-09-080414-packet.json`
  - `charness-artifacts/critique/2026-08-09-080414-packet.md`
  - `charness-artifacts/critique/2026-08-09-082846-packet.json`
  - `charness-artifacts/critique/2026-08-09-082846-packet.md`
  - `charness-artifacts/critique/2026-08-09-083309-packet.json`
  - `charness-artifacts/critique/2026-08-09-083309-packet.md`
  - `charness-artifacts/critique/2026-08-09-issue-523-root-routing-split-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-530-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-549-hook-failure-visibility-reader-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-560-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-563-title-slug-checker-deletion-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-564-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-565-resolution-critique.md`
  - ... 230 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-09-release-4-1-0-safety-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 0.079s
- `quality_command`: 101.040s
- `fresh_checkout_probes_initial`: 3.795s

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
