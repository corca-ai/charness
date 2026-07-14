# Release Surface Check
Date: 2026-07-14

## Scope

Advanced `charness` toward release `1.0.8` (tag `v1.0.8`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.7`
- target version: `1.0.8`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v1.0.8`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v1.0.8`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-92b3ff7261a8427c26db2682b5fcd011177ddff752d0ae1a4ff26d801faba046`.
- Linked feedback ID: `feedback-89b8f63ab9c3bd618f2046540beb075bc59be8f45ecd78cf906fa32aa7f2319d`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

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
- Retro artifact: `charness-artifacts/retro/2026-07-14-v1-0-8-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 49.
  - `.agents/critique-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `charness-artifacts/critique/2026-07-14-103252-packet.json`
  - `charness-artifacts/critique/2026-07-14-103252-packet.md`
  - `charness-artifacts/critique/2026-07-14-103608-packet.json`
  - `charness-artifacts/critique/2026-07-14-103608-packet.md`
  - `charness-artifacts/critique/2026-07-14-103913-packet.json`
  - `charness-artifacts/critique/2026-07-14-103913-packet.md`
  - `charness-artifacts/critique/2026-07-14-104105-packet.json`
  - `charness-artifacts/critique/2026-07-14-104105-packet.md`
  - `charness-artifacts/critique/2026-07-14-113227-packet.json`
  - `charness-artifacts/critique/2026-07-14-113227-packet.md`
  - `charness-artifacts/critique/2026-07-14-codex-v2-terra-medium-defaults-code-critique.md`
  - `charness-artifacts/critique/2026-07-14-v1-0-8-codex-v2-defaults-release-critique.md`
  - `charness-artifacts/probe/2026-07-14-v1.0.7-installed-reviewer-boundary-consumer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release/2026-07-14-v1.0.8-notes.md`
  - `charness-artifacts/release/latest.md`
  - ... 29 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-14-v1-0-8-codex-v2-defaults-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v1.0.8`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `10.116`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 1.0.7 -> 1.0.8
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_replaced, claude_marketplace_added, claude_marketplace_updated, claude_marketplace_updated, claude_plugin_installed, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 1.0.7 -> 1.0.8
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/capability_catalog.py resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 0.095s
- `quality_command`: 80.392s
- `fresh_checkout_probes_initial`: 2.997s
- `fresh_checkout_probes_after_amend`: 2.917s
- `push_create_verify_release`: 61.940s
- `distinct_channel_verification`: 0.506s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 10.116s

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
