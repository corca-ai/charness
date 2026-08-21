# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-21

## Scope

Advanced `charness` toward release `6.2.1` (tag `v6.2.1`) through the repo-owned release helper.

## Current Version

- previous version: `6.2.0`
- target version: `6.2.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.2.1`, checked at `post-bump, pre-commit`.

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

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: `not_run`.
- This is a recorded absence, not a passing preflight: no focused adapter check is claimed to have completed successfully for this release.
  - Reason: focused preflight status is `not_required`; no commands were required

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-21-v6-2-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 15.
  - `README.md`
  - `scripts/capability_catalog.py`
  - `skills/public/release/scripts/check_fresh_checkout_probes.py`
  - `skills/public/release/scripts/check_real_host_proof.py`
  - `skills/public/release/scripts/check_requested_review_gate.py`
  - `skills/public/release/scripts/current_release.py`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/release/scripts/publish_release_args.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/release_closeout_authorization.py`
  - `skills/public/release/scripts/release_closeout_floors.py`
  - `skills/public/release/scripts/release_issue_closeout.py`
  - `skills/public/release/scripts/resolve_adapter.py`
  - `skills/support/web-fetch/scripts/route_public_fetch_routes.py`
- Evaluated changed paths: 858.
  - `.agents/closeout-floor-matrix.json`
  - `.agents/consumer-validator-adoption.yaml`
  - `.agents/critique-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.gitignore`
  - `README.md`
  - `charness`
  - `charness-artifacts/critique/2026-08-06-041231-packet.md`
  - `charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md`
  - `charness-artifacts/critique/2026-08-18-111738-packet.json`
  - `charness-artifacts/critique/2026-08-18-111738-packet.md`
  - `charness-artifacts/critique/2026-08-18-closing-four-verified-resolved-issues.md`
  - `charness-artifacts/critique/2026-08-18-probe-provenance-goal-before-activation.md`
  - `charness-artifacts/critique/2026-08-19-issue-673-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-19-issue-674-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-19-issue-675-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-20-142117-packet.json`
  - `charness-artifacts/critique/2026-08-20-142117-packet.md`
  - `charness-artifacts/critique/2026-08-20-221521-packet.json`
  - ... 838 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Real-host checklist items remain open until their executed proof is recorded.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class. Use `charness doctor` here and NOT `python3 scripts/doctor.py --repo-root .`, which is the external-tool doctor and reports nothing about managed-checkout or plugin-root skew; discharging this item with it would record a verification that measured none of what the item is about.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: blocking-install-needed` with an actionable install `next_step`, and that the command itself exits 1. Blocking is CORRECT here: nose.json `degradation.when_missing` records that a missing nose makes the quality `doc-duplicates` phase fail closed with no fallback, and `integrations/tools/README.md` permits `doctor_policy: advisory` only where the consuming workflow has a degraded path. Do NOT read this verdict from `charness doctor`, which is the managed-install doctor and returns 0 regardless of external-tool state; the external-tool verdict comes from `charness tool doctor` or `python3 scripts/doctor.py --repo-root .`. Quoted because the unquoted form parses as a mapping under standard YAML.
- Run `charness tool install nose --dry-run --detail` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata. `--detail` is REQUIRED, not optional polish; the summary response level prints neither the installer command nor the release metadata this item asks you to confirm, so the plain `--dry-run` form cannot discharge it.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --detail` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-21-r3-current-candidate-release-critique.md`.

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

- `requested_review_gate`: 0.003s
- `cli_skill_surface_gate`: 1.924s
- `quality_command`: 324.534s
- `fresh_checkout_probes_initial`: 3.920s

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


## Bump Rationale

- Bump rationale: patch release for fail-closed host-delivery status, same-version content readback, typed update-all recovery, and source/plugin parity fixes; no intentional breaking interface or feature-surface change.
