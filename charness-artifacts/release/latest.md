# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-09-01

## Scope

Advanced `charness` toward release `8.0.2` (tag `v8.0.2`) through the repo-owned release helper.

## Current Version

- previous version: `8.0.1`
- target version: `8.0.2`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 247.9s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --read-only`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.0.2`, checked at `post-bump, pre-commit`.

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
- Previous release ref: `refs/tags/v8.0.1`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `quality_command`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
- Focused preflight execution: `passed`.
  - executed: `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`

## Review Proof

- Review proof: `charness-artifacts/critique/release-8-0-2-critique.md`.

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
- `cli_skill_surface_gate`: 2.234s
- `quality_command`: 247.861s
- `fresh_checkout_probes_initial`: 4.141s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> patch: no feat: commit and no BREAKING marker in origin/main..HEAD, and no public skill, command, or install surface gained or lost a member (skills/public + packaging + .agents show 22 modifications, 0 additions, 0 deletions). The range is correctness repairs to repo-owned gates and their tests. Two consumer-observable changes are disclosed in the notes rather than denied: the repo-local release adapter's quality_command no longer disclaims changed-line proof, and a shipped commit-time gate that previously died at import now evaluates. Both are bug fixes within a patch, not added or removed surface.