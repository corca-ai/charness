# Release Surface Check
Date: 2026-05-15

## Scope

Advanced `charness` toward release `0.5.27` (tag `v0.5.27`) through the repo-owned release helper.

## Current Version

- previous version: `0.5.26`
- target version: `0.5.27`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.5.27`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- This slice still requires configured public/real-host verification before the release is fully closed.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor cautilus --json` before installing `cautilus` and confirm the missing-binary state still surfaces an install document URL instead of a guessed package-manager command.
- Follow the official Cautilus install script at `https://github.com/corca-ai/cautilus/blob/main/install.sh`, then verify `cautilus --version` and `cautilus version --verbose`.
- Re-run `charness tool doctor cautilus --json` and confirm the binary is detected on PATH.
- Run `charness tool sync-support cautilus --json`, then confirm the generated support surface exists and the doctor payload reports support as materialized.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
