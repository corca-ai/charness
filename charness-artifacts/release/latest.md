# Release Surface Check
Date: 2026-07-11

Timezone note: this is the UTC generation date; publication occurred on
2026-07-12 in the repo operator's Asia/Seoul timezone.

## Scope

Advanced `charness` toward release `0.66.4` (tag `v0.66.4`) through the repo-owned release helper.

## Current Version

- previous version: `0.66.3`
- target version: `0.66.4`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.66.4`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.66.4`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v0.66.3`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `real_host_required_surfaces`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_real_host.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-07-11-v0-66-4-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 43.
  - `.agents/release-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-2-disposition-review.md`
  - `charness-artifacts/critique/2026-07-12-real-host-trigger-split-code-critique.md`
  - `charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.json`
  - `charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.md`
  - `charness-artifacts/critique/2026-07-12-round3-slices-a-b-code-critique.md`
  - `charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.json`
  - `charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.md`
  - `charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-code-critique.md`
  - `charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.json`
  - `charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.md`
  - `charness-artifacts/critique/2026-07-12-v0664-release-critique.md`
  - `charness-artifacts/critique/2026-07-12-v0664-release-packet.json`
  - `charness-artifacts/critique/2026-07-12-v0664-release-packet.md`
  - `charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md`
  - `charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md`
  - `charness-artifacts/probe/2026-07-12-north-star-autonomous-two-hour-release-round-2-host-log.md`
  - `charness-artifacts/quality/2026-07-12-round3-v0664-release-readiness.md`
  - ... 23 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-12-v0664-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v0.66.4`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.08`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.66.3 -> 0.66.4
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.66.3 -> 0.66.4
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/skills/public/find-skills/scripts/resolve_skill_path.py --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.806s
- `quality_command`: 82.937s
- `fresh_checkout_probes_initial`: 2.992s
- `fresh_checkout_probes_after_amend`: 2.809s
- `push_create_verify_release`: 65.735s
- `distinct_channel_verification`: 0.515s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 8.080s

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
