# Release Surface Check
Date: 2026-08-03

## Scope

Advanced `charness` toward release `3.1.0` (tag `v3.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.0.1`
- target version: `3.1.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v3.1.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v3.0.1`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `required_release_surfaces`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_real_host.py tests/quality_gates/test_release_backend.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-03-v3-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 14.
  - `skills/public/release/adapter.example.yaml`
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/release/references/real-host-proof.md`
  - `skills/public/release/scripts/current_release.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_retro.py`
  - `skills/public/release/scripts/release_issue_closeout_message.py`
  - `skills/public/release/scripts/resolve_adapter.py`
  - `skills/support/README.md`
  - `skills/support/web-fetch/references/routing-table.md`
- Evaluated changed paths: 550.
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/quality-core.yml`
  - `.gitignore`
  - `AGENTS.md`
  - `charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md`
  - `charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md`
  - `charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md`
  - `charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md`
  - `charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md`
  - `charness-artifacts/audit/2026-08-06-make-a-verdict-state-the-scope-it-measured-host-log-probe.md`
  - `charness-artifacts/critique/2026-08-01-467-mutation-regression-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-01-close-the-sweeps-remaining-high-rows-by-class-disposition-review.md`
  - `charness-artifacts/critique/2026-08-01-decline-d44-blocking-targets-subprocess-coverage.md`
  - `charness-artifacts/critique/2026-08-01-disposition-the-stragglers-a3-c6-d4-d28-s3-stub-disposition-review.md`
  - `charness-artifacts/critique/2026-08-01-goal-midpoint-claims-review.md`
  - `charness-artifacts/critique/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows-closeout-claims-review.md`
  - `charness-artifacts/critique/2026-08-01-slice-1-a3-residual-1.md`
  - `charness-artifacts/critique/2026-08-01-slice-1-absent-input-batch.md`
  - `charness-artifacts/critique/2026-08-01-slice-2-3-declaration-corroboration.md`
  - ... 530 more

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

- Review proof: `charness-artifacts/critique/2026-08-07-release-3.1.0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.006s
- `cli_skill_surface_gate`: 1.706s
- `quality_command`: 255.342s
- `fresh_checkout_probes_resume`: 3.305s

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
