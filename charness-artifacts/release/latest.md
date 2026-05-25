# Release Surface Check
Date: 2026-05-25

## Scope

Advanced `charness` toward release `0.7.13` (tag `v0.7.13`) through the repo-owned release helper.

## Current Version

- previous version: `0.7.12`
- target version: `0.7.13`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- release branch and tag were pushed to GitHub.
- public release check verified `gh release view v0.7.13`.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.7.13`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by `gh release view v0.7.13`.

## Real-Host Verification

- This slice still requires configured real-host verification before the release is fully closed.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor cautilus --json` before installing `cautilus` and confirm the missing-binary state still surfaces an install document URL instead of a guessed package-manager command.
- Follow the official Cautilus install script at `https://github.com/corca-ai/cautilus/blob/main/install.sh`, then verify `cautilus --version` and `cautilus version --verbose`.
- Re-run `charness tool doctor cautilus --json` and confirm the binary is detected on PATH.
- Run `charness tool sync-support cautilus --json`, then confirm the generated support surface exists and the doctor payload reports support as materialized.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-05-25-v0.7.13-release-risk-check.md`.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
