# Release Surface Check
Date: 2026-08-06

## Scope

Advanced `charness` toward release `3.4.0` (tag `v3.4.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.3.0`
- target version: `3.4.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v3.4.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v3.3.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `fresh_checkout_probes`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes tests/quality_gates/test_release_backend.py::test_release_adapter_rejects_invalid_fresh_checkout_probes -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-06-v3-4-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 62.
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-evidence-identity-and-release-disposition.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-final-claims-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-final-claims-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff.md`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh.md`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.json`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.md`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique.md`
  - `charness-artifacts/critique/2026-08-06-runtime-evidence-and-final-boundary-disposition-review.md`
  - `charness-artifacts/critique/runtime-evidence-final-boundary-packet.json`
  - `charness-artifacts/critique/runtime-evidence-final-boundary-packet.md`
  - ... 42 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-06-release-3-4-0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.969s
- `quality_command`: 88.186s
- `fresh_checkout_probes_initial`: 3.853s

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
