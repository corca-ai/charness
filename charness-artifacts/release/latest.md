# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-31

## Scope

Advanced `charness` toward release `8.0.0` (tag `v8.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `7.0.0`
- target version: `8.0.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --non-claim=release-changed-line-coverage` exited 0 in 131.8s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --non-claim=release-changed-line-coverage`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.0.0`, checked at `post-bump, pre-commit`.

## Release State

- local release mutation: complete
- branch/tag push: pending independent claims review.
- GitHub release record: pending independent claims review before creation
- public release surface verification: pending independent claims review
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v7.0.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `checked_in_plugin_root`
  - `materialized_plugin_root`
  - `quality_command`
  - `real_host_checklist`
  - `real_host_required_path_globs`
  - `real_host_required_surfaces`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
- Focused preflight execution: `passed`.
  - executed: `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-31-v8.0.0-release-repair-critique.md`.

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

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 0.127s
- `quality_command`: 131.767s
- `fresh_checkout_probes_initial`: 4.082s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> Publish the already-prepared 8.0.0 major release: it removes incompatible task and handoff surfaces, renames the materialized plugin export contract, and changes existing automation expectations.