# Release Surface Check
Date: 2026-06-26

## Scope

Advanced `charness` toward release `0.56.2` (tag `v0.56.2`) through the repo-owned release helper.

## Current Version

- previous version: `0.56.1`
- target version: `0.56.2`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.56.2`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.56.2`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none executed.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-06-26-v0-56-2-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 138.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-26-artifact-path-payload-runtime.md`
  - `charness-artifacts/critique/2026-06-26-behavior-recommendation-runtime.md`
  - `charness-artifacts/critique/2026-06-26-bootstrap-visibility-runtime.md`
  - `charness-artifacts/critique/2026-06-26-boundary-inventory-cache.md`
  - `charness-artifacts/critique/2026-06-26-cli-skill-surface-runtime.md`
  - `charness-artifacts/critique/2026-06-26-command-docs-parallel.md`
  - `charness-artifacts/critique/2026-06-26-create-skill-adapter-runtime.md`
  - `charness-artifacts/critique/2026-06-26-current-pointer-scanner-runtime.md`
  - `charness-artifacts/critique/2026-06-26-debug-scaffold-runtime.md`
  - `charness-artifacts/critique/2026-06-26-debug-seam-index-runtime.md`
  - `charness-artifacts/critique/2026-06-26-dependencies-seed-runtime.md`
  - `charness-artifacts/critique/2026-06-26-doc-links-runtime.md`
  - `charness-artifacts/critique/2026-06-26-goal-head-freshness-runtime.md`
  - `charness-artifacts/critique/2026-06-26-goal-pursue-ready-runtime.md`
  - `charness-artifacts/critique/2026-06-26-issue-57-renderer-runtime.md`
  - `charness-artifacts/critique/2026-06-26-markdown-preview-backend-check-runtime.md`
  - `charness-artifacts/critique/2026-06-26-markdown-preview-bootstrap-runtime.md`
  - `charness-artifacts/critique/2026-06-26-markdown-preview-support-runtime.md`
  - `charness-artifacts/critique/2026-06-26-narrative-scenario-runtime.md`
  - ... 118 more

## Real-Host Verification

- Configured release real-host verification is satisfied for this release by
  the post-publish install refresh and fresh-checkout probes recorded below.

## Real-Host Proof

- Release-time real-host proof was required for this slice and is recorded in
  `## Install Refresh` and `## Fresh Checkout Probes`.
- `charness update` refreshed the maintainer/dev machine from `0.56.1` to
  `0.56.2` after publication.
- Fresh checkout probes passed for the command surfaces listed below.
- Nose real-host proof is not a release blocker for this slice; the release
  delta did not change the nose integration contract.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-26-release-v0-56-2-critique.md`.

## Post-Publish Proof

- Public release check: `gh release view v0.56.2`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.56.1 -> 0.56.2
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.56.1 -> 0.56.2
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/skills/public/find-skills/scripts/resolve_skill_path.py --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION: codex: Codex host install markers are present. Start a new Codex session to load charness.
CODEX_NEXT_STEP: Codex host install markers are present. Start a new Codex session to load charness.
CLAUDE_NEXT_STEP: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
