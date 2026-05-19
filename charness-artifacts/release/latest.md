# Release Surface Check
Date: 2026-05-19

## Scope

Advanced `charness` toward release `0.7.4` (tag `v0.7.4`) through the repo-owned release helper.

## Current Version

- previous version: `0.7.3`
- target version: `0.7.4`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.7.4`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by `gh release view v0.7.4 --repo corca-ai/charness --json tagName,url,name,publishedAt,isDraft,isPrerelease,targetCommitish`.

## Critique

- Critique proof: `charness-artifacts/critique/2026-05-19-v0.7.4-hotfix-critique.md`.

## Post-Publish Proof

- Public release check: `gh release view v0.7.4 --repo corca-ai/charness --json tagName,url,name,publishedAt,isDraft,isPrerelease,targetCommitish`.
- Post-publish artifact commit: `aefb1745ff5b2a2ff5f85e5b6ca3d674fef98c5b`.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Fresh Checkout Probes

- No repo-declared fresh checkout probes were configured for this release.

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.
