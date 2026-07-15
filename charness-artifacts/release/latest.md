# Release Surface Check
Date: 2026-07-15

## Scope

Advanced `charness` toward release `1.0.9` (tag `v1.0.9`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.8`
- target version: `1.0.9`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` is queued for this publish attempt.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v1.0.9`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v1.0.8`
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
- Retro artifact: `charness-artifacts/retro/2026-07-15-v1-0-9-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 111.
  - `.agents/cli-side-effect-probes.json`
  - `.agents/command-docs.yaml`
  - `.agents/command-registry.json`
  - `.agents/release-adapter.yaml`
  - `.charness/specdown/report.json`
  - `.charness/specdown/report/index.html`
  - `.charness/specdown/report/on-demand-validation.html`
  - `.charness/specdown/report/readme-proof.html`
  - `.charness/specdown/report/tool-doctor.html`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `charness`
  - `charness-artifacts/critique/2026-07-15-022604-packet.json`
  - `charness-artifacts/critique/2026-07-15-022604-packet.md`
  - `charness-artifacts/critique/2026-07-15-cli-yaml-stdout-contract.md`
  - `charness-artifacts/critique/2026-07-15-critique-review.md`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-critique.md`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-packet.json`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-packet.md`
  - `charness-artifacts/critique/cli-yaml-stdout-contract-packet.json`
  - ... 91 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Real-host checklist items remain open until their executed proof is recorded.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-critique.md`.

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
