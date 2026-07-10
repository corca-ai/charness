# Release Surface Check
Date: 2026-07-10

## Scope

Advanced `charness` toward release `0.64.0` (tag `v0.64.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.63.1`
- target version: `0.64.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.64.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.64.0`
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
- Retro artifact: `charness-artifacts/retro/2026-07-10-v0-64-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 78.
  - `.agents/surfaces.json`
  - `.agents/usage-episodes-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness`
  - `charness-artifacts/critique/2026-07-09-211611-packet.json`
  - `charness-artifacts/critique/2026-07-09-211611-packet.md`
  - `charness-artifacts/critique/2026-07-09-212954-packet.json`
  - `charness-artifacts/critique/2026-07-09-212954-packet.md`
  - `charness-artifacts/critique/2026-07-10-outcome-driven-autonomous-improvement-disposition-review.md`
  - `charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md`
  - `charness-artifacts/critique/2026-07-10-plain-version-readonly-critique.md`
  - `charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.json`
  - `charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.md`
  - `charness-artifacts/critique/2026-07-10-release-0-64-0-packet.json`
  - `charness-artifacts/critique/2026-07-10-release-0-64-0-packet.md`
  - `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-critique.md`
  - `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.json`
  - `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.md`
  - `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-critique.md`
  - `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.json`
  - ... 58 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Completed real-host checklist on the maintainer/dev machine. `charness update`
  refreshed the installed source/cache/Claude surfaces to 0.64.0; installed
  `charness version --verbose` reports 0.64.0, GIT_HEAD `ad673083`, and
  `managed-local-cli`. Installed doctor readback reports source/cache/Claude
  all 0.64.0 and ready. It also surfaces the pre-existing
  `commit_discipline_drift` setup recommendation; that recommendation was not
  changed or claimed fixed.
- `charness tool doctor nose --json --no-write-locks`: ready, 0.18.0 (>= 0.17).
- `charness tool install nose --dry-run --json`: upstream latest installer,
  release v0.18.0.
- `nose --version`: 0.18.0.
- `charness tool sync-support nose --json`: skipped; this integration declares
  no `support_skill_source`.
- `inventory_nose_clones.py --repo-root . --json`: one 55-line `_portable_path`
  family, explicitly advisory rather than a standing quality failure.
- Missing-nose behavior was not tested because `nose` was already installed;
  no missing-nose claim is made.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-10-v0-64-0-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v0.64.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `10.006`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.63.1 -> 0.64.0
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.63.1 -> 0.64.0
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/skills/public/find-skills/scripts/resolve_skill_path.py --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.841s
- `quality_command`: 76.959s
- `fresh_checkout_probes_initial`: 2.771s
- `fresh_checkout_probes_after_amend`: 2.798s
- `push_create_verify_release`: 50.938s
- `distinct_channel_verification`: 0.499s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 10.006s

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
