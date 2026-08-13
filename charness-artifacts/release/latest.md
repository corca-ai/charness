# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-13

## Scope

Advanced `charness` toward release `5.2.0` (tag `v5.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `5.1.0`
- target version: `5.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.

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
- Focused preflight commands: none executed.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-13-v5-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 14.
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/release/scripts/plan_release_prepared_stop.py`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_claims_review.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_narrative_gate.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
  - `skills/public/release/scripts/publish_release_resume_state.py`
- Evaluated changed paths: 237.
  - `.agents/retro-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/mutation-tests.yml`
  - `charness-artifacts/create-skill/2026-08-13-handoff-retro-feedback-loop-brief.md`
  - `charness-artifacts/critique/2026-08-13-115535-packet.json`
  - `charness-artifacts/critique/2026-08-13-115535-packet.md`
  - `charness-artifacts/critique/2026-08-13-120041-packet.json`
  - `charness-artifacts/critique/2026-08-13-120041-packet.md`
  - `charness-artifacts/critique/2026-08-13-120724-packet.json`
  - `charness-artifacts/critique/2026-08-13-120724-packet.md`
  - `charness-artifacts/critique/2026-08-13-121401-packet.json`
  - `charness-artifacts/critique/2026-08-13-121401-packet.md`
  - `charness-artifacts/critique/2026-08-13-four-proof-surface-repairs-two-round-critique.md`
  - `charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.json`
  - `charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.md`
  - `charness-artifacts/critique/2026-08-13-handoff-lesson-evaluation-continuity.md`
  - `charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md`
  - `charness-artifacts/critique/2026-08-13-issue-614-local-artifact-retention-resolution.md`
  - `charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md`
  - ... 217 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-13-release-5-2-0-critique.md`.

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
- `cli_skill_surface_gate`: 1.904s
- `quality_command`: 105.555s
- `fresh_checkout_probes_initial`: 4.007s

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
