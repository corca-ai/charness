# Release Surface Check
Date: 2026-08-08

## Scope

Advanced `charness` toward release `4.0.0` (tag `v4.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.5.0`
- target version: `4.0.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v4.0.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-08-08-v4-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 4.
  - `README.md`
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/release_issue_closeout_message.py`
- Evaluated changed paths: 275.
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `README.md`
  - `charness-artifacts/audit/2026-08-08-open-issue-opinion.md`
  - `charness-artifacts/capability-catalog/latest.json`
  - `charness-artifacts/capability-catalog/latest.md`
  - `charness-artifacts/critique/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-disposition-review.md`
  - `charness-artifacts/critique/2026-08-08-issue-536-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-537-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-548-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-552-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-555-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-556-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-557-559-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-issue-558-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent-disposition-review.md`
  - `charness-artifacts/critique/2026-08-09-issue-562-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-release-4-0-0-proof-surfaces.md`
  - `charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`
  - `charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`
  - ... 255 more

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

- Review proof: `charness-artifacts/critique/2026-08-09-release-4-0-0-proof-surfaces.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 2.049s
- `quality_command`: 173.973s
- `fresh_checkout_probes_initial`: 3.968s

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
