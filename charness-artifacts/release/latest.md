# Release Surface Check
Date: 2026-05-06

## Scope

Advanced `charness` toward release `0.5.17` through the repo-owned release helper.

## Current Version

- previous version: `0.5.16`
- target version: `0.5.17`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.
- `gh release view v0.5.17` verified the public GitHub release after publish.

## Premortem

- Fresh-Eye Satisfaction: parent-delegated.
- Act Before Ship: release from merged `main`, use the repo helper for patch
  `0.5.17`, verify public `v0.5.17`, and record the CodeRabbit pending status
  decision.
- Waiver: PR #107 had a non-required CodeRabbit status still pending after the
  PR was already merged. The maintainer explicitly requested merge/release, the
  branch protection did not block merge, and deterministic local/pre-push gates
  passed; release proceeded with this pending bot context treated as
  non-blocking.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: complete
- public release surface verification: complete

## Public Release Verification

- URL: https://github.com/corca-ai/charness/releases/tag/v0.5.17
- tag: `v0.5.17`
- published: 2026-05-06T12:16:32Z
- remote tag and `origin/main` both resolved to
  `1b3df173cbb4854e7cdbaedda73d505c6744ea0b`.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
