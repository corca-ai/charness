# Release Surface Check
Date: 2026-07-31

## Scope

Advanced `charness` toward release `3.0.0` (tag `v3.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `2.12.0`
- target version: `3.0.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v3.0.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-07-31-v3-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 7.
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/scripts/audit_public_release_narrative.py`
  - `skills/public/release/scripts/drafted_release_notes.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_narrative_gate.py`
  - `skills/public/release/scripts/publish_release_plan.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
- Evaluated changed paths: 186.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md`
  - `charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md`
  - `charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md`
  - `charness-artifacts/critique/2026-07-30-issue-465-resolution.md`
  - `charness-artifacts/critique/2026-07-30-issue-466-mutation-lane-baseline-repair.md`
  - `charness-artifacts/critique/2026-07-31-release-3-0-0.md`
  - `charness-artifacts/critique/2026-07-31-sweep-s11-delegated-review-substantiation.md`
  - `charness-artifacts/critique/2026-07-31-sweep-s3-s4-closeout-evidence-binding.md`
  - `charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md`
  - `charness-artifacts/probe/2026-07-29-v2.12.0-release-observer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release/2026-07-31-v3.0.0-notes.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-30-session-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/conventions/authoring-preflight.md`
  - ... 166 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-31-release-3-0-0.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.762s
- `quality_command`: 88.779s
- `fresh_checkout_probes_initial`: 3.231s

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
