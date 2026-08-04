# Release Surface Check
Date: 2026-08-04

## Scope

Advanced `charness` toward release `3.2.0` (tag `v3.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.1.1`
- target version: `3.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v3.2.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-08-04-v3-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `skills/support/markdown-preview/scripts/markdown_preview_render.py`
- Evaluated changed paths: 126.
  - `.agents/critique-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-03-211703-packet.json`
  - `charness-artifacts/critique/2026-08-03-211703-packet.md`
  - `charness-artifacts/critique/2026-08-03-221939-packet.json`
  - `charness-artifacts/critique/2026-08-03-221939-packet.md`
  - `charness-artifacts/critique/2026-08-03-222903-packet.json`
  - `charness-artifacts/critique/2026-08-03-222903-packet.md`
  - `charness-artifacts/critique/2026-08-03-223438-packet.json`
  - `charness-artifacts/critique/2026-08-03-223438-packet.md`
  - `charness-artifacts/critique/2026-08-03-225320-packet.json`
  - `charness-artifacts/critique/2026-08-03-225320-packet.md`
  - `charness-artifacts/critique/2026-08-04-critique-review.md`
  - `charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.json`
  - `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.md`
  - `charness-artifacts/critique/2026-08-04-make-recurring-closeout-cost-actionable-critique.md`
  - `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.json`
  - `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface-packet.md`
  - ... 106 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-04-release-3-2-0-additive-operator-surface.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.819s
- `quality_command`: 168.190s
- `fresh_checkout_probes_initial`: 3.457s

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
