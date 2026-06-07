# Release Surface Check
Date: 2026-06-07

## Scope

Staged `charness` toward release `0.26.0` (tag `v0.26.0`) for issue #324
(preserve external-source context in issue workflows). STAGE-ONLY: the agent
staged the release surface and proved it locally; it did NOT push, tag, or
publish a GitHub release. The maintainer publishes (repo policy: No push/tag CI).

## Current Version

- previous version: `0.25.0`
- target version: `0.26.0`
- git branch: `main`
- git remote: `origin`

The `--release` gate's components were each proven; the broad suite was run
once under the mutation-coverage producer (no redundant full re-run, per the
`producer-rerun-waste` retro):

- broad pytest suite green (`-m "not release_only"`, 2399 passed / 4 skipped)
  via the changed-line mutation-coverage producer run; `release_only`
  install/update lifecycle regression tests green separately (26 passed).
- deterministic closeout gates green (ruff, length, validate_skills,
  validate_skill_ergonomics, markdown, doc-links, packaging, mirror-drift,
  dogfood) at the commit boundary via the repo pre-commit hook.
- `current_release.py` reported no version drift across packaging and generated
  install surfaces (all `0.26.0`).
- changed-line mutation coverage **active and green** base→worktree: base
  `b60d5c7c` (origin/main) → the #324 source-preservation Python committed in
  `7dcfb43d`. Run against the committed head, so it is NOT the `--head-sha HEAD`
  false-green dry-run — the changed Python is committed history, and the only
  uncommitted worktree changes (this release surface plus the test updates)
  carry no mutation-pool Python.
- the #324 invariant itself is proven by
  `tests/quality_gates/test_issue_source_preservation.py` (12 tests) plus the
  existing issue closeout suite.

## Release State

- local release mutation: complete (staged commit on local `main`)
- branch/tag push: NOT done (staged for maintainer)
- GitHub release record: NOT created (staged for maintainer)
- public release surface verification: NOT done (staged for maintainer)

## Public Release Verification

- not performed by the agent. The maintainer pushes `main`, tags `v0.26.0`, and
  publishes the GitHub release; that push auto-closes #324 via the staged close
  keyword.

## Issue Closeout

- #324 close keyword (`Close #324.`) is staged in the release commit body with
  the feature closeout ledger plus a `Critique:` binding to
  `charness-artifacts/critique/2026-06-07-324-source-preservation.md`.
  `gh issue view 324` remains OPEN until the maintainer's push auto-closes it.

## Non-Claims (the agent did NOT do these)

- no `git push`, no tag, no GitHub release publication
- no real-host smoke (handoff item 1 — human, async)
- no provider / live proof

## User Update Steps (after the maintainer publishes)

- Run `charness update` to pull `0.26.0`.
- Restart Claude Code or Codex if the host cache still shows `0.25.0`.
