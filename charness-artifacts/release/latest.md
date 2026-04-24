# Release Surface Check
Date: 2026-04-24

## Scope

Advanced `charness` toward release `0.5.12` through the repo-owned release helper.

## Current Version

- previous version: `0.5.11`
- target version: `0.5.12`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the `v0.5.12` tag.
- GitHub release view verified the public release record.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: created (https://github.com/corca-ai/charness/releases/tag/v0.5.12)
- public release surface verification: GitHub release page exists

## Public Release Verification

- Verified GitHub release surface:
  https://github.com/corca-ai/charness/releases/tag/v0.5.12

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
