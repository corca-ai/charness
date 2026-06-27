# Release Surface Check
Date: 2026-06-27

## Scope

Advanced `charness` toward release `0.56.9` (tag `v0.56.9`) through the repo-owned release helper.

## Current Version

- previous version: `0.56.8`
- target version: `0.56.9`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.56.9`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.56.9`
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
- Retro artifact: `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 20.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-06-28-issue-405-405-disposition-review.md`
  - `charness-artifacts/critique/2026-06-28-v0.56.9-release-critique.md`
  - `charness-artifacts/find-skills/latest.json`
  - `charness-artifacts/find-skills/latest.md`
  - `charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md`
  - `charness-artifacts/probe/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/notes-v0.56.9.md`
  - `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/shared/references/fresh-eye-subagent-review.md`
  - `plugins/charness/skills/quality/references/quality-lenses.md`
  - `skills/public/quality/references/quality-lenses.md`
  - `skills/shared/references/fresh-eye-subagent-review.md`

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-28-v0.56.9-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v0.56.9`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.255`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.56.8 -> 0.56.9
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.56.8 -> 0.56.9
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/skills/public/find-skills/scripts/resolve_skill_path.py --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION: codex: Codex host install markers are present. Start a new Codex session to load charness.
CODEX_NEXT_STEP: Codex host install markers are present. Start a new Codex session to load charness.
CLAUDE_NEXT_STEP: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.856s
- `quality_command`: 67.392s
- `fresh_checkout_probes_initial`: 2.915s
- `fresh_checkout_probes_after_amend`: 2.754s
- `push_create_verify_release`: 45.891s
- `distinct_channel_verification`: 0.506s
- `issue_closeout`: 0.436s
- `post_publish_install_refresh`: 8.255s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `verified`.
- GitHub repo: `corca-ai/charness`
- Issue #405: `CLOSED` (https://github.com/corca-ai/charness/issues/405)
  - carrier: `direct_release_commit_body`
  - manual fallback used: `False`

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
