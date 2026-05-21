# Release Surface Check
Date: 2026-05-21

## Scope

Advanced `charness` toward release `0.7.9` (tag `v0.7.9`) through the repo-owned release helper.

## Current Version

- previous version: `0.7.8`
- target version: `0.7.9`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` was attempted and failed only because
  [quality latest](../quality/latest.md) exceeded the 140-line current-pointer
  limit; the artifact was compressed before resuming publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- branch/tag push has not started yet for `v0.7.9`; resume with the release
  helper's `--publish-current` path after this prepared surface is committed.

## Release State

- local release mutation: complete
- branch/tag push: pending
- GitHub release record: target URL `https://github.com/corca-ai/charness/releases/tag/v0.7.9`; creation runs after the branch/tag push
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

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

- Review proof: `charness-artifacts/critique/2026-05-21-v0.7.9-release-risk-check.md`.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
