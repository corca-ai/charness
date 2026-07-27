# Release Surface Check
Date: 2026-07-27

## Scope

Advanced `charness` toward release `2.11.3` (tag `v2.11.3`) through the repo-owned release helper.

## Current Version

- previous version: `2.11.2`
- target version: `2.11.3`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v2.11.3`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-07-27-v2-11-3-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `skills/public/release/scripts/publish_release.py`
- Evaluated changed paths: 132.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/audit/2026-07-27-derived-artifact-recompute-inventory.md`
  - `charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md`
  - `charness-artifacts/critique/2026-07-27-104618-packet.json`
  - `charness-artifacts/critique/2026-07-27-104618-packet.md`
  - `charness-artifacts/critique/2026-07-27-a3-staged-scope-packet.json`
  - `charness-artifacts/critique/2026-07-27-a3-staged-scope-packet.md`
  - `charness-artifacts/critique/2026-07-27-a3-staged-scope.md`
  - `charness-artifacts/critique/2026-07-27-empty-scope-family-packet.json`
  - `charness-artifacts/critique/2026-07-27-empty-scope-family-packet.md`
  - `charness-artifacts/critique/2026-07-27-empty-scope-family.md`
  - `charness-artifacts/critique/2026-07-27-entrypoint-guard-packet.json`
  - `charness-artifacts/critique/2026-07-27-entrypoint-guard-packet.md`
  - `charness-artifacts/critique/2026-07-27-issue-close-carrier-b1-b3.md`
  - `charness-artifacts/critique/2026-07-27-issues-460-461-463-packet.json`
  - `charness-artifacts/critique/2026-07-27-issues-460-461-463-packet.md`
  - `charness-artifacts/critique/2026-07-27-issues-460-461-463.md`
  - `charness-artifacts/critique/2026-07-27-provenance-containment-packet.json`
  - `charness-artifacts/critique/2026-07-27-provenance-containment-packet.md`
  - `charness-artifacts/critique/2026-07-27-provenance-containment.md`
  - ... 112 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-27-release-2-11-3.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.702s
- `quality_command`: 71.516s
- `fresh_checkout_probes_initial`: 3.337s

## Baton Reconcile

- Baton reconcile observation: not recorded by this helper invocation.

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
