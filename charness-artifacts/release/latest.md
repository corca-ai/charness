# Release Surface Check
Date: 2026-07-11

## Scope

Advanced `charness` toward release `0.66.0` (tag `v0.66.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.65.0`
- target version: `0.66.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v0.66.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v0.66.0`
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
- Retro artifact: `charness-artifacts/retro/2026-07-11-v0-66-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 3.
  - `skills/public/release/SKILL.md`
  - `skills/public/release/scripts/publish_release_plan.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
- Evaluated changed paths: 76.
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.claude/agents/bounded-reviewer.md`
  - `charness-artifacts/critique/2026-07-10-053400-packet.json`
  - `charness-artifacts/critique/2026-07-10-053400-packet.md`
  - `charness-artifacts/critique/2026-07-10-070255-packet.json`
  - `charness-artifacts/critique/2026-07-10-070255-packet.md`
  - `charness-artifacts/critique/2026-07-10-233307-packet.json`
  - `charness-artifacts/critique/2026-07-10-233307-packet.md`
  - `charness-artifacts/critique/2026-07-10-428-reviewer-boundary-disposition-review.md`
  - `charness-artifacts/critique/2026-07-10-432-resolution-critique.md`
  - `charness-artifacts/critique/2026-07-10-issue-429-430-431-resolution-critique.md`
  - `charness-artifacts/critique/2026-07-11-434-release-critique.md`
  - `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release-early-close-report.md`
  - `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release-host-log-probe.json`
  - `charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`
  - `charness-artifacts/probe/2026-07-10-issue-430-bounded-reviewer-envelope-probe.json`
  - `charness-artifacts/quality/dup-ratchet-baseline.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - ... 56 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Remaining real-host checklist items, if any, still require explicit proof before full closeout.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --json --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run --json` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose --json`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --json --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose --json` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Real-Host Execution Readback

- `charness tool doctor nose --json --no-write-locks`: `doctor_status: ok`,
  `doctor_disposition: ready`, observed/current `nose 0.18.0`.
- Missing-state non-claim: `nose` was already installed, so this run could not
  observe the pre-install `advisory-install-needed` transition.
- `charness tool install nose --dry-run --json`: selected the upstream
  `nose-cli-installer.sh` route and read back latest release `v0.18.0`.
- `charness tool sync-support nose --json`: skipped materialization because
  `nose` is integration-only and has no support-skill source.
- `inventory_nose_clones.py --json`: completed with advisory refactoring
  candidates; no standing failure was inferred from the findings.
- Post-publish `charness doctor --json`: checkout, Codex source/cache, and Claude
  installed versions are `0.66.0`; tool readiness includes `nose: ok` and Codex
  source/cache drift is false.
- Installed-vs-repo spot check: the installed `achieve_adapter_policy.py` is
  byte-identical to the release repo file.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-11-434-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v0.66.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.41`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 0.65.0 -> 0.66.0
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 0.65.0 -> 0.66.0
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/skills/public/find-skills/scripts/resolve_skill_path.py --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.005s
- `cli_skill_surface_gate`: 1.832s
- `quality_command`: 72.855s
- `fresh_checkout_probes_resume`: 2.848s
- `push_create_verify_release`: 54.257s
- `distinct_channel_verification`: 0.515s
- `issue_closeout`: 0.436s
- `post_publish_install_refresh`: 8.410s

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `state-verified`.
- GitHub repo: `corca-ai/charness`
- Issue #434: `CLOSED` (https://github.com/corca-ai/charness/issues/434)
  - carrier: `direct_release_commit_body`
  - manual fallback used: `False`

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
