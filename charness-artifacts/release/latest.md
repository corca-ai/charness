# Release Surface Check
Date: 2026-04-17

## Scope

Published `charness` release `0.3.0` through the repo-owned release helper.

## Current Version

- previous version: `0.2.0`
- target version: `0.3.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- git push and tag push completed from the release helper.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update` after pulling the published release.
- Refresh Claude or Codex plugin state if the host cache still shows the previous version.
