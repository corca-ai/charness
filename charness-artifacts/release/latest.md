# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-09-08

## Scope

Advanced `charness` toward release `8.6.1` (tag `v8.6.1`) through the repo-owned release helper.

This patch release carries compatible boundary repairs: retained task
worktrees survive generic cleanup; review lifecycle results preserve
structured metadata while complete worker input remains available;
implementation guidance tolerates repositories without `docs/index.md`; the
implementation fixture preserves literal relative reference paths; resolved
debug risks route through their existing handoff; and task completion persists
useful candidates before later proof gates run.

## Current Version

- previous version: `8.6.0`
- target version: `8.6.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 328.4s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --read-only --release-prepare`); quality unestablished: pytest-release pending final resume.
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.6.1`, checked at `post-bump, pre-commit`.

## Release State

- local release mutation: complete
- branch/tag push: pending independent claims review.
- GitHub release record: pending independent claims review before creation
- public release surface verification: pending independent claims review
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: `not_run`.
- This is a recorded absence, not a passing preflight: no focused adapter check is claimed to have completed successfully for this release.
  - Reason: focused preflight status is `not_required`; no commands were required

## Review Proof

- Review proof: `charness-artifacts/critique/2026-09-08-release-8-6-1.md`.

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
- `cli_skill_surface_gate`: 3.192s
- `quality_command`: 328.441s
- `fresh_checkout_probes_initial`: 5.389s

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

> Patch release: repairs task-worktree retention, review lifecycle transport,
> optional implementation documentation-index handling, literal reference
> resolution, resolved-risk routing, and task proof ordering while preserving
> existing invocation and metadata contracts.
