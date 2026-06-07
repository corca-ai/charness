# Release Surface Check
Date: 2026-06-07

## Scope

Released `charness` `0.26.0` (tag `v0.26.0`) for issue #324 (preserve
external-source context in issue workflows). The release surface was staged and
proven locally, then pushed/tagged/published at the maintainer's explicit
direction.

## Current Version

- previous version: `0.25.0`
- target version: `0.26.0`
- git branch: `main`
- git remote: `origin`

Verification (the `--release` gate components were each proven; the broad suite
ran once under the mutation-coverage producer, no redundant full re-run per the
`producer-rerun-waste` retro):

- broad pytest suite green (`-m "not release_only"`, 2399 passed / 4 skipped)
  via the changed-line mutation-coverage producer run; `release_only`
  install/update lifecycle regression tests green separately (26 passed).
- the pre-push `run-quality.sh --read-only` gate passed on both the `main` push
  and the tag push (72 passed, 0 failed each).
- deterministic closeout gates green (ruff, length, validate_skills,
  validate_skill_ergonomics, markdown, doc-links, packaging, mirror-drift,
  dogfood) at every commit boundary via the repo pre-commit hook.
- `current_release.py` reported no version drift across packaging and generated
  install surfaces (all `0.26.0`).
- changed-line mutation coverage **active and green** base→worktree: base
  `b60d5c7c` (origin/main) → the #324 source-preservation Python committed in
  `7dcfb43d`. Run against the committed head, so it is NOT the `--head-sha HEAD`
  false-green dry-run.
- the #324 invariant itself is proven by
  `tests/quality_gates/test_issue_source_preservation.py` (12 tests) plus the
  existing issue closeout suite.

## Release State

- local release mutation: complete
- branch/tag push: complete (`main` → `97a11160`; tag `v0.26.0`)
- GitHub release record: published — `https://github.com/corca-ai/charness/releases/tag/v0.26.0`
- public release surface verification: verified (release `isDraft: false`;
  fresh-checkout probes pass)

## Public Release Verification

- GitHub release `v0.26.0` published and verified via `gh release view`
  (`isDraft: false`).
- Fresh-checkout probes pass: `./charness --help`, `./charness goal check --help`,
  `python3 scripts/doctor.py --repo-root . --json --skip-release-probe`.

## Issue Closeout

- #324 (`Close #324.` close keyword carried in release commit `e0043ac9`):
  auto-closed on push to `main`. `gh issue view 324` → `state: CLOSED`. Resolution
  critique bound at `charness-artifacts/critique/2026-06-07-324-source-preservation.md`.

## Non-Claims (the agent did NOT do these)

- no real-host smoke on a second machine / clean temp-home (handoff item 1 —
  human, async); the local fresh-checkout probes are not a substitute.
- no provider / live proof beyond the local fresh-checkout probes and the
  GitHub release/issue verification.

## User Update Steps

- Run `charness update` to pull `0.26.0`.
- Restart Claude Code or Codex if the host cache still shows `0.25.0`.
- No migration is required.
