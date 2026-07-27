# Release Surface Check
Date: 2026-07-27

## Scope

Advanced `charness` toward release `2.11.2` (tag `v2.11.2`) through the repo-owned release helper.

## Current Version

- previous version: `2.11.1`
- target version: `2.11.2`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v2.11.2`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-07-27-v2-11-2-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 204.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `charness`
  - `charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md`
  - `charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.json`
  - `charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.md`
  - `charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md`
  - `charness-artifacts/critique/2026-07-27-handoff-backlog-1-3-validator-cli-unification-chunker-staleness-facts-content-line-budget.md`
  - `charness-artifacts/critique/2026-07-27-issue-458-spawn-shape-rule-placement.md`
  - `charness-artifacts/critique/2026-07-27-v2-11-2-release-critique.md`
  - `charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md`
  - `charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/goals/2026-07-27-handoff-backlog-minus-aarch64.md`
  - `charness-artifacts/metrics/rca-ledger.jsonl`
  - `charness-artifacts/probe/2026-07-26-v2.11.1-release-observer.json`
  - `charness-artifacts/quality/dup-ratchet-baseline.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - ... 184 more

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

- Review proof: `charness-artifacts/critique/2026-07-27-v2-11-2-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.778s
- `quality_command`: 67.740s
- `fresh_checkout_probes_initial`: 2.990s

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
