# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-10-20

## Scope

Advanced `charness` toward release `8.14.8` (tag `v8.14.8`) through the repo-owned release helper.

## Current Version

- previous version: `8.14.7`
- target version: `8.14.8`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 211.1s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release --read-only --release-prepare`); quality unestablished: pytest-release pending final resume.
- pre-push quality receipt: NOT recorded by this helper invocation, so the quality sentence above cites no durable receipt.
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.14.8`, checked at `post-bump, pre-commit`.
- Validated tree: commit `a81f6bbefa0ebe96f4ba2c9b6071532c99e5edd4` (tree `fad38e13179915585cd30ef428a15795a168945c`); a pushed tag or branch that does not contain this tree was not what this check validated.

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

- Review proof: `charness-artifacts/critique/2026-10-20-v8.14.8-release-critique.md`.

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

- `requested_review_gate`: 0.004s
- `cli_skill_surface_gate`: 2.376s
- `quality_command`: 211.145s
- `fresh_checkout_probes_initial`: 6.978s

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

- Bump: `8.14.7` -> `8.14.8` (`patch`).
> patch, not minor: four behavior repairs (steer resume model and effort, review carrier promotion, debug prior-record routing, implementation-lane stop rule); no public skill, command, or install surface is added, renamed, or removed.