# Release Surface Check
Date: 2026-08-09

## Scope

Advanced `charness` toward release `4.2.0` (tag `v4.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `4.1.0`
- target version: `4.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v4.2.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-08-09-v4-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 2.
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/release_issue_closeout_message.py`
- Evaluated changed paths: 88.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-push`
  - `charness-artifacts/critique/2026-08-09-post-4-1-0-bug-closeout-critique.md`
  - `charness-artifacts/critique/2026-08-09-post-4-1-0-surface-closeout-critique.md`
  - `charness-artifacts/critique/2026-08-10-release-4-2-0-critique.md`
  - `charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned-disposition-review.md`
  - `charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`
  - `charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md`
  - `charness-artifacts/probe/2026-08-09-v4.1.0-release-observer.json`
  - `charness-artifacts/probe/2026-08-10-refuse-the-verdict-host-log-probe.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/release/2026-08-10-v4.2.0-notes.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/handoff.md`
  - `docs/prompt-mutation-policy.md`
  - `docs/public-skill-dogfood.json`
  - ... 68 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-10-release-4-2-0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.894s
- `quality_command`: 117.890s
- `fresh_checkout_probes_initial`: 3.837s

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
