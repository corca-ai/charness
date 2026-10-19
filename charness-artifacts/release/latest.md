# Release Surface Check
Date: 2026-10-20

## Scope

Advanced `charness` toward release `8.14.8` (tag `v8.14.8`) through the repo-owned release helper.

## Current Version

- previous version: `8.14.7`
- target version: `8.14.8`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 at `post-bump, pre-commit` (211.1s) and again at `post-claims-review, pre-push` (409.1s), measured by the release helper under Node `v22.23.2` first on `PATH`.
- pre-push quality receipt: `charness-artifacts/release/8.14.8-prepush-quality.json` (status `pass`, verified head `e1dee4d37`).
- An earlier first attempt of the release lane failed `release-changed-line-coverage` on `run_review_primary_promotion.py`; the helper rolled back cleanly and `tests/test_review_primary_promotion_branches.py` closed the gap before the successful runs above.
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.14.8`, checked at `post-bump, pre-commit`.
- Validated tree: commit `a81f6bbefa0ebe96f4ba2c9b6071532c99e5edd4` (tree `fad38e13179915585cd30ef428a15795a168945c`); a pushed tag or branch that does not contain this tree was not what this check validated.

## Release State

- local release mutation: complete
- branch/tag push: complete (`main` at `d52d75046`, tag `v8.14.8` at `6e8581b2b`)
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.14.8`
- public release surface verification: verified through an authenticated `gh release view` and an unauthenticated HTTPS fetch (HTTP 200, names the tag and carries the Known issue text); see `charness-artifacts/probe/2026-10-20-v8.14.8-release-observer.json`
- helper closeout: INCOMPLETE. The first resume pushed the branch and tag, then `gh release create --verify-tag` failed because an older `gh` was first on `PATH`. A later `--resume` refused ("remote branch is not the prepared record, claims evidence, or their known base") because the remote head is the helper's own artifact commit. The GitHub release was therefore created by hand with the same command the helper runs, and this record was finished by hand; the helper's distinct-channel verdict, published-notes audit, and closeout steps did not run.
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by `gh release view` (not a draft) and a credential-free HTTPS fetch of the release page.

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

- Claims review record: `charness-artifacts/release-review/2026-10-20-v8.14.8-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Review narrative: `charness-artifacts/release-review/2026-10-20-v8.14.8-claims-review.md`.
- Advisory findings carried without gating: critique scope predates the coverage-fix test; some proof figures have no saved log; the validated-tree identity names the pre-bump tree.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: `charness update` ran by hand on the maintainer machine after publication; `charness version` read `8.14.6` before and `8.14.8` after, and `charness doctor` reported checkout, Codex source, and Codex cache manifest all at `8.14.8` with no source/cache drift. Active Claude and Codex sessions must be restarted to load it.

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