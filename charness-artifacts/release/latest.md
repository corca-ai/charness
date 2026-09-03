# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-09-03

## Scope

Advanced `charness` toward release `8.0.3` (tag `v8.0.3`) through the repo-owned release helper.

## Current Version

- previous version: `8.0.2`
- target version: `8.0.3`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 164.7s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --read-only`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.0.3`, checked at `post-bump, pre-commit`.

## Release State

- local release mutation: complete
- branch/tag push: pending independent claims review.
- GitHub release record: pending independent claims review before creation
- public release surface verification: pending independent claims review
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v8.0.2`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `sync_command`
  - `update_instructions`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_narrative_audit.py -q`
- Focused preflight execution: `passed`.
  - executed: `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - executed: `pytest tests/quality_gates/test_release_narrative_audit.py -q`

## Review Proof

- Review proof: `charness-artifacts/critique/release-8-0-3-critique.md`.

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

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.118s
- `quality_command`: 164.684s
- `fresh_checkout_probes_initial`: 4.414s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> patch, and pre-approved by name: the operator named 8.0.3 on 2026-09-03 (Interview Decisions in charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md); the derived inventories of public skills, charness subcommands, shell gates, and json-declaring scripts are identical as sets to the v8.0.2 notes' derived block and the adapter's required_release_surfaces is byte-identical to v8.0.2, so no public skill, subcommand, or install surface gained or lost a member, and the new mechanisms are repo-owned gates, task-run receipt fields, and runtime retention, which is the patch shape in version-policy.md