# Release Surface Check
Date: 2026-05-06

## Scope

Advanced `charness` toward release `0.5.18` through the repo-owned release helper.

## Current Version

- previous version: `0.5.17`
- target version: `0.5.18`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.
- `gh release view v0.5.18` verified the public GitHub release after publish.

## Premortem

- Fresh-Eye Satisfaction: parent-delegated.
- Act Before Ship: fix `publish_release` proof scoping so the release artifact
  carries `origin/main..HEAD` real-host triggers, use patch `0.5.18`, and
  verify public `v0.5.18` after creation.
- Result: helper proof scoping was fixed before release; `v0.5.18` was created
  and publicly verified. Real-host proof remains an explicit post-publish
  checklist before claiming the release fully closed.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: complete
- public release surface verification: complete

## Public Release Verification

- URL: https://github.com/corca-ai/charness/releases/tag/v0.5.18
- tag: `v0.5.18`
- published: 2026-05-06T21:29:39Z
- remote tag and `origin/main` both resolved to
  `2172403dc4651c84dfd0c4e32066b7b96dffef8e`.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Not executed in this local publish pass; keep the release open at the
  real-host boundary until the checklist below is run on a clean host.
- On a second machine or a clean temp-home, refresh `charness` through the published operator path before claiming the release surface is ready.
- Run `charness tool doctor cautilus --json` before installing `cautilus` and confirm the missing-binary state still surfaces an install document URL instead of a guessed package-manager command.
- Follow the official Cautilus install script at `https://github.com/corca-ai/cautilus/blob/main/install.sh`, then verify `cautilus --version` and `cautilus version --verbose`.
- Re-run `charness tool doctor cautilus --json` and confirm the binary is detected on PATH.
- Run `charness tool sync-support cautilus --json`, then confirm the generated support surface exists and the doctor payload reports support as materialized.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
