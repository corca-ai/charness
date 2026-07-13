# Release Surface Check
Date: 2026-07-13

## Scope

Advanced `charness` toward release `1.0.0` (tag `v1.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.66.4`
- target version: `1.0.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed: 82 checks passed, 0 failed, in 73.7 seconds.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- The changed-line mutation gate warned that eight uncommitted Python files were excluded; commit-based mutation proof remains required before publication.

## Release State

- local release mutation: complete
- branch/tag push: not started; the first execute attempt stopped at the release-quality gate
- GitHub release record: not created; target URL is `https://github.com/corca-ai/charness/releases/tag/v1.0.0`
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: not started; no local or remote `v1.0.0` tag exists yet.

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
- Retro artifact: `charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 5.
  - `README.md`
  - `scripts/capability_catalog.py`
  - `scripts/capability_catalog_artifact.py`
  - `scripts/capability_catalog_resolver.py`
  - `scripts/capability_catalog_sources.py`
- Evaluated changed paths: 238.
  - `.agents/inference-interpretation-surfaces.json`
  - `.agents/narrative-adapter.yaml`
  - `.agents/retro-adapter.yaml`
  - `.agents/surfaces.json`
  - `.agents/usage-episodes-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `README.md`
  - `charness`
  - `charness-artifacts/capability-catalog/latest.json`
  - `charness-artifacts/capability-catalog/latest.md`
  - `charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-3-disposition-review.md`
  - `charness-artifacts/critique/2026-07-13-005302-packet.json`
  - `charness-artifacts/critique/2026-07-13-005302-packet.md`
  - `charness-artifacts/critique/2026-07-13-011911-packet.json`
  - `charness-artifacts/critique/2026-07-13-011911-packet.md`
  - `charness-artifacts/critique/2026-07-13-031004-packet.json`
  - `charness-artifacts/critique/2026-07-13-031004-packet.md`
  - `charness-artifacts/critique/2026-07-13-033046-packet.json`
  - `charness-artifacts/critique/2026-07-13-033046-packet.md`
  - ... 218 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Real-host checklist items remain open until their executed proof is recorded.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --json --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run --json` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose --json`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --json --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose --json` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-13-find-skills-legacy-removal-v1-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: not recorded by this helper invocation.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- Release helper runtime: not recorded by this helper invocation.

## Fresh Checkout Probes

- Fresh-checkout probe status: configured.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
