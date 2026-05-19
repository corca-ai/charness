# Release Surface Check
Date: 2026-05-19

## Scope

Advanced `charness` toward release `0.7.1` (tag `v0.7.1`) through the repo-owned release helper.

## Current Version

- previous version: `0.7.0`
- target version: `0.7.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.7.1`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- No configured public/real-host verification trigger matched this slice, but async publication repos should still keep workflow/public checks explicit.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
