# Release Surface Check
Date: 2026-05-08

## Scope

Advanced `charness` toward release `0.5.19` through the repo-owned release helper.

## Current Version

- previous version: `0.5.18`
- target version: `0.5.19`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.
- `gh release view v0.5.19` verified the public GitHub release after publish.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: complete
- public release surface verification: complete

## Public Release Verification

- URL: https://github.com/corca-ai/charness/releases/tag/v0.5.19
- tag: `v0.5.19`
- published: 2026-05-08T11:44:48Z
- release: public, non-draft, non-prerelease
- target commitish: `main`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
