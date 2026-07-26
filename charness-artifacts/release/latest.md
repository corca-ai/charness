# Release Surface Check
Date: 2026-07-26

## Scope

Advanced `charness` toward release `2.11.0` (tag `v2.11.0`) through the repo-owned release helper.

## Current Version

- previous version: `2.10.0`
- target version: `2.11.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v2.11.0`; creation runs after the branch/tag push
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
- Retro artifact: `charness-artifacts/retro/2026-07-26-v2-11-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 22.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md`
  - `charness-artifacts/critique/2026-07-26-v2-11-0-release-critique.md`
  - `charness-artifacts/probe/2026-07-26-v2.10.0-release-observer.json`
  - `charness-artifacts/release/2026-07-26-v2.11.0-notes.md`
  - `charness-artifacts/release/latest.md`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/skills/quality/references/adapter-contract.md`
  - `plugins/charness/skills/quality/scripts/check_runtime_budget.py`
  - `plugins/charness/skills/quality/scripts/runtime_budget_lib.py`
  - `plugins/charness/skills/quality/scripts/runtime_budget_sizing_lib.py`
  - `plugins/charness/skills/quality/scripts/runtime_profile_lib.py`
  - `skills/public/quality/references/adapter-contract.md`
  - `skills/public/quality/scripts/check_runtime_budget.py`
  - `skills/public/quality/scripts/runtime_budget_lib.py`
  - `skills/public/quality/scripts/runtime_budget_sizing_lib.py`
  - ... 2 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-26-v2-11-0-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.764s
- `quality_command`: 58.109s
- `fresh_checkout_probes_initial`: 3.261s

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
