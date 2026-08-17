# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-18

## Scope

Advanced `charness` toward release `6.1.0` (tag `v6.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.0.1`
- target version: `6.1.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.1.0`, checked at `post-bump, pre-commit`.

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
- Retro artifact: `charness-artifacts/retro/2026-08-17-v6-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 13.
  - `skills/public/release/references/version-policy.md`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_adapter_preflight.py`
  - `skills/public/release/scripts/publish_release_arg_guards.py`
  - `skills/public/release/scripts/publish_release_args.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_plan.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_premutation_sections.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
- Evaluated changed paths: 93.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`
  - `charness-artifacts/critique/2026-08-17-session-release-record-retro-prefix.md`
  - `charness-artifacts/critique/2026-08-18-issue-633-verify-and-close.md`
  - `charness-artifacts/critique/2026-08-18-issue-636-resolution.md`
  - `charness-artifacts/critique/2026-08-18-issues-632-631-630-verify-and-close.md`
  - `charness-artifacts/critique/2026-08-18-v6.1.0-release-critique.md`
  - `charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json`
  - `charness-artifacts/probe/2026-08-17-v6.0.1-release-observer.json`
  - `charness-artifacts/quality/2026-08-18-quality-review.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/latest.md`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-17-204807-packet.json`
  - `charness-artifacts/retro/2026-08-17-204807-packet.md`
  - `charness-artifacts/retro/2026-08-17-v6-0-1-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-18-3bbe7879-unclaimed-session-disposition.md`
  - ... 73 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-18-v6.1.0-release-critique.md`.

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

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 2.140s
- `quality_command`: 144.095s
- `fresh_checkout_probes_initial`: 4.124s

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

> Minor, not patch: this range ships one genuinely new operator-facing surface — the --bump-rationale flag and the release record's Bump Rationale section, absent at the 6.0.1 base (git-proven) — on top of acceptance-equivalent repairs (#636 one-pass debug-validator reporting, critique blocked-vocabulary fix, void-disposition pin). Nothing renames, removes, or changes invocation expectations, so major is not in question; patch would understate the additive surface.