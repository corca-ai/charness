# Release Surface Check
Date: 2026-06-25

## Scope

Advanced `charness` toward release `0.55.0` (tag `v0.55.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.54.2`
- target version: `0.55.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` is queued for this publish attempt.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.55.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v0.54.2`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `update_instructions`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_narrative_audit.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-06-25-v0-55-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 17.
  - `skills/public/release/adapter.example.yaml`
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/release/references/install-refresh.md`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/support/web-fetch/references/routing-table.md`
  - `skills/support/web-fetch/scripts/acquire_public_url.py`
  - `skills/support/web-fetch/scripts/browser_fallback_stages.py`
  - `skills/support/web-fetch/scripts/reddit_source.py`
  - `skills/support/web-fetch/scripts/route_public_fetch.py`
  - `skills/support/web-fetch/scripts/source_identity_lib.py`
  - `skills/support/web-fetch/scripts/text_attempts.py`
  - `skills/support/web-fetch/scripts/twitter_exact_source.py`
  - `skills/support/web-fetch/scripts/url_reader.py`
  - `skills/support/web-fetch/scripts/youtube_source.py`
- Evaluated changed paths: 175.
  - `.agents/critique-adapter.yaml`
  - `.agents/release-adapter.yaml`
  - `.agents/retro-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/mutation-tests.yml`
  - `charness-artifacts/critique/2026-06-23-204121-packet.json`
  - `charness-artifacts/critique/2026-06-23-204121-packet.md`
  - `charness-artifacts/critique/2026-06-24-debug-planner-closeout.md`
  - `charness-artifacts/critique/2026-06-24-gather-exact-terminal-records.md`
  - `charness-artifacts/critique/2026-06-24-issue-387-closeout.md`
  - `charness-artifacts/critique/2026-06-24-issue-396-handoff-planner-closeout.md`
  - `charness-artifacts/critique/2026-06-25-004012-packet.json`
  - `charness-artifacts/critique/2026-06-25-004012-packet.md`
  - `charness-artifacts/critique/2026-06-25-issue-400-js-mutation-resolution.md`
  - `charness-artifacts/critique/2026-06-25-release-adapter-update-instructions-decoupling.md`
  - `charness-artifacts/critique/2026-06-25-v0.55.0-release-critique.md`
  - `charness-artifacts/critique/release-0-55-0-full-packet.json`
  - `charness-artifacts/critique/release-0-55-0-full-packet.md`
  - `charness-artifacts/debug/2026-06-25-issue-400-js-mutation-weight-gap.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - ... 155 more

## Real-Host Verification

- This slice still requires configured real-host verification before the release is fully closed.

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

- Review proof: `charness-artifacts/critique/2026-06-25-v0.55.0-release-critique.md`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

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
