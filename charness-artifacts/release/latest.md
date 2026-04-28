# Release Surface Check
Date: 2026-04-28

## Scope

Advanced `charness` package surfaces to version `0.5.14` for a branch push.
This is not a tagged public release.

## Current Version

- previous version: `0.5.13`
- target version: `0.5.14`
- git branch: `main`
- git remote: `origin`

## Verification

- `current_release.py` reported no version drift across packaging and generated
  install surfaces.
- `validate_packaging.py` passed.
- `validate_packaging_committed.py` passed.
- Full `./scripts/run-quality.sh` was intentionally not used for this slice
  because Cautilus proof enforcement is being ignored during the current
  Cautilus transition.

## Release State

- local release mutation: complete
- branch push: pending
- git tag: not created
- GitHub release record: not created

## User Update Steps

- Run `charness update` after the branch push lands.
- Restart Claude Code or Codex if the host cache still shows the previous
  version.
