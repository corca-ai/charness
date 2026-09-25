# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-09-26

## Scope

Advanced `charness` toward release `8.14.0` (tag `v8.14.0`) through the repo-owned release helper.

## Current Version

- previous version: `8.12.0`
- target version: `8.14.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 155.8s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --read-only --release-prepare`); quality unestablished: pytest-release pending final resume.
- pre-push quality receipt: NOT recorded by this helper invocation, so the quality sentence above cites no durable receipt.
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.14.0`, checked at `post-bump, pre-commit`.
- Validated tree: commit `c42aa392e5006aa38cb0a4d9beb3ab462bb0d026` (tree `6c2a5685afd2eef882081fcb155e5d9cc7d18a77`); a pushed tag or branch that does not contain this tree was not what this check validated.

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

- Review proof: `charness-artifacts/critique/v8140-critique.md`.

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

- `requested_review_gate`: 0.003s
- `cli_skill_surface_gate`: 5.584s
- `quality_command`: 155.756s
- `fresh_checkout_probes_initial`: 8.088s

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

- Bump: `8.12.0` -> `8.14.0` (`set-version`).
> minor, not patch: 870 (train metrics), 871 (goal re-inject hook), and 872 (status report template) add operator-facing capabilities; not major: no invocation breaks or renames. 8.14.0, not 8.13.0: that tag already exists on origin for the #866-869 batch.