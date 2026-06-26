# Release Surface Check
Date: 2026-06-26

## Scope

Advanced `charness` toward release `0.56.3` (tag `v0.56.3`) through the repo-owned release helper.

## Current Version

- previous version: `0.56.2`
- target version: `0.56.3`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.56.3`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.56.3`
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
- Retro artifact: `charness-artifacts/retro/2026-06-26-v0-56-3-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 3.
  - `skills/support/web-fetch/scripts/acquire_public_url.py`
  - `skills/support/web-fetch/scripts/acquire_public_url_io.py`
  - `skills/support/web-fetch/scripts/acquire_public_url_payloads.py`
- Evaluated changed paths: 110.
  - `.claude-plugin/marketplace.json`
  - `charness`
  - `charness-artifacts/critique/2026-06-26-054254-packet.json`
  - `charness-artifacts/critique/2026-06-26-054254-packet.md`
  - `charness-artifacts/critique/2026-06-26-sustained-quality-speed-token-release-disposition-review.md`
  - `charness-artifacts/critique/2026-06-26-sustained-quality-speed-token-release-round-2-disposition-review.md`
  - `charness-artifacts/critique/2026-06-26-v0-56-3-release-critique.md`
  - `charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release-round-2.md`
  - `charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release.md`
  - `charness-artifacts/probe/2026-06-26-sustained-quality-speed-token-release-host-log.json`
  - `charness-artifacts/probe/2026-06-26-sustained-quality-speed-token-release-round-2-host-log.json`
  - `charness-artifacts/quality/dup-ratchet-baseline.json`
  - `charness-artifacts/quality/nose-baseline.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/v0.56.3-notes.md`
  - `charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-goal-retro.md`
  - `charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-round-2-goal-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `packaging/charness.json`
  - ... 90 more

## Real-Host Verification

- Configured real-host verification: satisfied after publish on this
  maintainer/dev machine.

## Real-Host Proof

- `charness update` ran after publish with return code `0`; stdout reported
  `VERSION: 0.56.2 -> 0.56.3`, refreshed the managed checkout, Codex cache,
  Claude marketplace/plugin entries, and upstream support skills.
- `charness doctor --json` ran after update with return code `0`; it reported
  checkout version `0.56.3`, Codex cache manifest version `0.56.3`, Claude
  installed plugin version `0.56.3`, and no plugin-preamble warnings.
- `charness tool doctor nose --json --no-write-locks` ran with return code `0`;
  it detected `nose 0.15.0`, version status `matched`, latest upstream
  `v0.15.0`, and `doctor_disposition: ready`.
- `charness tool install nose --dry-run --json` ran with return code `0`; it
  pointed at the manifest-supported upstream release installer
  `nose-cli-installer.sh` and latest release metadata `v0.15.0`.
- `nose --version` ran with return code `0` and printed `nose 0.15.0`.
- `charness tool sync-support nose --json` ran with return code `0`; it reported
  `status: skipped`, `reason: integration has no support_skill_source`, and
  doctor readiness remained `ready`.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`
  ran with return code `0`; it reported `status: clean`, `family_count: 0`,
  `total_dup_lines: 0`, and `tool_version: 0.15.0`.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-06-26-v0-56-3-release-critique.md`.

## Post-Publish Proof

- Public release check: `gh release view v0.56.3`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.56.2 -> 0.56.3
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.56.2 -> 0.56.3
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
