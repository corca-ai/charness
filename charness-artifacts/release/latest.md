# Release Surface Check
Date: 2026-04-23

## Scope

Advanced `charness` toward release `0.5.7` through the repo-owned release helper.

## Current Version

- previous version: `0.5.6`
- target version: `0.5.7`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: created (https://github.com/corca-ai/charness/releases/tag/v0.5.7)
- public release surface verification: complete via `gh release view v0.5.7 --repo corca-ai/charness`

## Public Release Verification

- `gh release view v0.5.7 --repo corca-ai/charness` reports a non-draft, non-prerelease GitHub release published at `2026-04-23T13:11:29Z`.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
