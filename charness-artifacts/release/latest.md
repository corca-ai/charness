# Release Surface Check
Date: 2026-05-12

## Scope

Advanced `charness` to public release `0.5.24` through the repo-owned release
helper, follow-up release-gate repair, tag push, and GitHub release creation.

## Current Version

- previous version: `0.5.23`
- target version: `0.5.24`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --read-only` passed in the pre-push hook before
  publish: 55 passed / 0 failed.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- `cautilus eval test` produced accept-now proof in
  `.cautilus/runs/20260512T082131710Z-run/`; `cautilus eval evaluate` reported
  5 passed / 0 failed / 0 blocked.
- one git push carried the release branch update and tag `v0.5.24`.
- `gh release view v0.5.24 --json tagName,url,isDraft,isPrerelease,publishedAt,targetCommitish`
  verified the public GitHub release record.
- GitHub auto-closed issues #146-#154 after the release train reached `main`.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: created
- public release surface verification: checked
- tag commit: `be81b0e2b2e46ebcbd37aad1b9d0ae427b1bd2df`
- release URL: `https://github.com/corca-ai/charness/releases/tag/v0.5.24`

## Public Release Verification

- `gh release view v0.5.24` reports `isDraft: false`,
  `isPrerelease: false`, `publishedAt: 2026-05-12T08:28:44Z`, and
  `targetCommitish: main`.
- `git rev-list -n1 v0.5.24` resolves to
  `be81b0e2b2e46ebcbd37aad1b9d0ae427b1bd2df`, matching `HEAD` at publish time.
- `gh issue list --state open --limit 100` returned no open issues after
  GitHub processed the auto-close references.

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
