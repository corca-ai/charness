# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-17

## Scope

Advanced `charness` toward release `6.0.1` (tag `v6.0.1`) through the repo-owned release helper.

## Current Version

- previous version: `6.0.0`
- target version: `6.0.1`
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

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v6.0.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `real_host_checklist`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_real_host.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-17-v6-0-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 3.
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/scripts/bump_version.py`
  - `skills/public/release/scripts/resolve_adapter.py`
- Evaluated changed paths: 154.
  - `.agents/release-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/mutation-tests.yml`
  - `.github/workflows/quality-core.yml`
  - `charness-artifacts/critique/2026-08-17-053617-packet.json`
  - `charness-artifacts/critique/2026-08-17-053617-packet.md`
  - `charness-artifacts/critique/2026-08-17-issue-617-closeout.md`
  - `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md`
  - `charness-artifacts/issue/2026-08-16-issue-618-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-619-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-620-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-621-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-622-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-623-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-624-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-625-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-626-closeout-comment.md`
  - ... 134 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`.

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

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 2.139s
- `quality_command`: 160.832s
- `fresh_checkout_probes_initial`: 4.233s

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
