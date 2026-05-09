# Release Surface Check
Date: 2026-05-09

## Scope

Advanced `charness` toward release `0.5.20` through the repo-owned release helper.

This release closes [#135](https://github.com/corca-ai/charness/issues/135) — the 6-leg T-first self-evolving unit umbrella — by publishing the cumulative substrate from PRs 1–5 plus the close-of-issue cleanup slice.

## Current Version

- previous version: `0.5.19`
- target version: `0.5.20`
- git branch: `main`
- git remote: `origin`

## Critique

- short — version drift, generated surfaces, publish boundary, operator risk:
  - patch bump justified: 5-PR umbrella was substrate-shape preserving (rename + reference widening). Hard renames (`premortem` → `critique`, `init-repo` → `setup`) are absorbed by `charness update` host-cache invalidation; legacy snippet detection ships as advisory drift to give consumer migration time. Per-PR critiques (Leg 5 / Leg 6) already covered the rename surface itself; this release-level critique focuses on publication risk.
  - publish boundary: `publish_release.py --execute` closed local mutation + branch/tag push + GitHub release create + verify-tag in one helper invocation; public release surface verified via `gh release view v0.5.20` (non-draft, non-prerelease).
  - operator risk: cautilus refresh batch (two-run `concern-but-ship`, see [`charness-artifacts/cautilus/latest.md`](../cautilus/latest.md)) flagged compact-AGENTS.md routing nondeterminism on the `impl` vs `create-cli` boundary; workspace_checked_in (real consumer surface) routes 3/3 in both runs. Compact-surface discriminator follow-up logged in [`docs/handoff.md`](../../docs/handoff.md).

## Verification

- `./scripts/run-quality.sh` passed before publish (51 passed / 0 failed).
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- one git push carried both the release branch update and the tag from the release helper.
- `gh release view v0.5.20` verified the public GitHub release after publish.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: complete
- public release surface verification: complete

## Public Release Verification

- URL: https://github.com/corca-ai/charness/releases/tag/v0.5.20
- tag: `v0.5.20`
- published: 2026-05-09T12:54:17Z
- release: public, non-draft, non-prerelease
- target commitish: `main`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## User Update Steps

- Run `charness update`.
- Restart Claude Code or Codex if the host cache still shows the previous version.

## Open Risks

- Compact-surface discriminator nondeterminism in cautilus eval (compact_with_startup_bootstrap variant): 1/5 different failing case across two runs while workspace_checked_in stays 3/3. Tracked as a follow-up to tighten compact-AGENTS.md `impl` vs `create-cli` phrasing in a future slice; not a release blocker.
