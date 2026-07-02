# Release Surface Check
Date: 2026-07-02

## Scope

Advanced `charness` toward release `0.58.0` (tag `v0.58.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.57.0`
- target version: `0.58.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.58.0`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

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
- Retro artifact: `charness-artifacts/retro/2026-07-02-v0-58-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 10.
  - `skills/public/find-skills/scripts/resolve_adapter.py`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/resolve_adapter.py`
  - `skills/support/gather-notion/SKILL.md`
  - `skills/support/gather-notion/references/provenance.md`
  - `skills/support/gather-slack/SKILL.md`
  - `skills/support/gather-slack/references/provenance.md`
  - `skills/support/web-fetch/SKILL.md`
  - `skills/support/web-fetch/references/provenance.md`
- Evaluated changed paths: 478.
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/cautilus/achieve-claim-fidelity-slice7-2026-07-01/finding.md`
  - `charness-artifacts/cautilus/achieve-claim-fidelity-slice7-2026-07-01/justification.md`
  - `charness-artifacts/cautilus/achieve-claim-fidelity-slice7-2026-07-01/observed.v1.json`
  - `charness-artifacts/cautilus/achieve-claim-fidelity-slice7-2026-07-01/transcript.txt`
  - `charness-artifacts/cautilus/create-cli-claim-fidelity-slice7-2026-07-01/finding.md`
  - `charness-artifacts/cautilus/create-cli-claim-fidelity-slice7-2026-07-01/justification.md`
  - `charness-artifacts/cautilus/create-cli-claim-fidelity-slice7-2026-07-01/observed.v1.json`
  - `charness-artifacts/cautilus/create-cli-claim-fidelity-slice7-2026-07-01/transcript.txt`
  - `charness-artifacts/cautilus/critique-decision-claim-fidelity-slice7-2026-07-01/finding.md`
  - `charness-artifacts/cautilus/critique-decision-claim-fidelity-slice7-2026-07-01/justification.md`
  - `charness-artifacts/cautilus/critique-decision-claim-fidelity-slice7-2026-07-01/observed.decision.v1.json`
  - `charness-artifacts/cautilus/critique-decision-claim-fidelity-slice7-2026-07-01/observed.v1.json`
  - `charness-artifacts/cautilus/critique-decision-claim-fidelity-slice7-2026-07-01/transcript.decision.txt`
  - `charness-artifacts/cautilus/critique-default-claim-fidelity-slice7-2026-07-01/finding.md`
  - `charness-artifacts/cautilus/critique-default-claim-fidelity-slice7-2026-07-01/justification.md`
  - `charness-artifacts/cautilus/critique-default-claim-fidelity-slice7-2026-07-01/observed.default.v1.json`
  - `charness-artifacts/cautilus/critique-default-claim-fidelity-slice7-2026-07-01/observed.v1.json`
  - `charness-artifacts/cautilus/critique-default-claim-fidelity-slice7-2026-07-01/transcript.default.txt`
  - ... 458 more

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

- Review proof: `charness-artifacts/critique/2026-07-02-release-0.58.0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.773s
- `quality_command`: 67.154s
- `fresh_checkout_probes_initial`: 3.120s

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
