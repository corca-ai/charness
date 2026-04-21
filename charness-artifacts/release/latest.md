# Release Surface Check
Date: 2026-04-21

## Scope

Advanced `charness` toward release `0.5.1` through the repo-owned release helper.

## Current Version

- previous version: `0.5.1`
- target version: `0.5.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: not created by this helper run
- public release surface verification: not checked by this helper

## Public Release Verification

- No configured public/real-host verification trigger matched this slice, but async publication repos should still keep workflow/public checks explicit.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
