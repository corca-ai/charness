# Release Surface Check
Date: 2026-08-09

## Scope

Prepared the complete untagged `charness` `4.1.0` release candidate (planned
tag `v4.1.0`). This rolling pointer records candidate state only; it does not
claim a pushed branch, tag, GitHub release, or public installation.

## Current Version

- previous version: `4.0.0`
- target version: `4.1.0`
- git branch: `main`
- git remote: `origin`

## Verification

- Packaging validation and the focused release-boundary regressions passed on
  the version-synchronized worktree.
- Source, checked-in plugin, Claude marketplace, and Codex plugin surfaces all
  report `4.1.0` with no version drift.
- The final verification lock, exact-candidate real-host trigger evaluation,
  hosted Quality Core, and public readbacks are still pending.

## Release State

- local release mutation: complete
- branch/tag push: pending; neither the candidate branch nor tag has been pushed
- GitHub release record: absent; publication has not run
- public release surface verification: not run
- audit narrative: provisional candidate record at `charness-artifacts/release/latest.md`; final publication evidence must replace it

## Public Release Verification

Not performed. The authorized sequence is candidate branch push, distinct
hosted Quality Core readback, then tag/publication push and public/install/
doctor/baton readback. A successful local gate or push exit cannot satisfy any
later phase.

## Review Proof

- Release safety critique:
  `charness-artifacts/critique/2026-08-09-release-4-1-0-safety-critique.md`.
- Release-record claims review:
  `charness-artifacts/critique/2026-08-09-release-4-1-0-claims-review.md`.

## Non-Claims

- Cautilus was not run.
- Hosted CI, the tag, the GitHub release, public visibility, installed 4.1.0,
  doctor state, baton reconciliation, and linked issue closure are unverified.

## User Update Steps

After publication, run `charness update`, `charness version`, and
`charness doctor`. Before publication these commands do not establish 4.1.0.
