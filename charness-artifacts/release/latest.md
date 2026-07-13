# Release Surface Check
Date: 2026-07-13

## Scope

Advanced `charness` toward release `1.0.2` (tag `v1.0.2`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.1`
- target version: `1.0.2`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v1.0.2`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v1.0.2`
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
- Retro artifact: `charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 27.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-13-issue-resolve-preflight-ordering-code-critique.md`
  - `charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.json`
  - `charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.md`
  - `charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.json`
  - `charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.md`
  - `charness-artifacts/critique/2026-07-13-v1-0-2-release-critique.md`
  - `charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.json`
  - `charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.md`
  - `charness-artifacts/debug/2026-07-13-debug-review-followup-2.md`
  - `charness-artifacts/debug/2026-07-13-debug-review-followup.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md`
  - `charness-artifacts/quality/2026-07-13-round4-v1-0-2-release-readiness.md`
  - `charness-artifacts/quality/latest.md`
  - `charness-artifacts/release/2026-07-13-v1.0.2-notes.md`
  - `charness-artifacts/release/latest.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - ... 7 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-13-v1-0-2-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v1.0.2`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.963`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 1.0.1 -> 1.0.2
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 1.0.1 -> 1.0.2
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/capability_catalog.py resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.868s
- `quality_command`: 75.250s
- `fresh_checkout_probes_initial`: 2.924s
- `fresh_checkout_probes_after_amend`: 2.964s
- `push_create_verify_release`: 61.781s
- `distinct_channel_verification`: 0.662s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 8.963s

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
