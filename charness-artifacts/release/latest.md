# Release Surface Check
Date: 2026-07-15

## Scope

Advanced `charness` toward release `1.0.9` (tag `v1.0.9`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.8`
- target version: `1.0.9`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v1.0.9`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v1.0.9`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-c861de0cfa20fa890875e27259dab2fcc8cf17ecd65e0dbcb51c9a6caf9e7e36`.
- Linked feedback ID: `feedback-f3279d4021663737298eec968d2a3a71d455ac58e549dadb7d7dbb31b163ca9c`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v1.0.8`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `real_host_checklist`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_real_host.py -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-07-15-v1-0-9-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 114.
  - `.agents/cli-side-effect-probes.json`
  - `.agents/command-docs.yaml`
  - `.agents/command-registry.json`
  - `.agents/quality-adapter.yaml`
  - `.agents/release-adapter.yaml`
  - `.charness/specdown/report.json`
  - `.charness/specdown/report/index.html`
  - `.charness/specdown/report/on-demand-validation.html`
  - `.charness/specdown/report/readme-proof.html`
  - `.charness/specdown/report/tool-doctor.html`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `charness`
  - `charness-artifacts/critique/2026-07-15-022604-packet.json`
  - `charness-artifacts/critique/2026-07-15-022604-packet.md`
  - `charness-artifacts/critique/2026-07-15-cli-yaml-stdout-contract.md`
  - `charness-artifacts/critique/2026-07-15-critique-review.md`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-critique.md`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-packet.json`
  - `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-packet.md`
  - ... 94 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Checklist disposition: completed on the maintainer machine after publication.
- `charness doctor --repo-root /home/hwidong/.agents/src/charness` reported installed checkout, Codex cache, and host-facing manifests at `1.0.9`, with `codex_source_cache_drift: false`.
- `charness tool doctor nose --no-write-locks` reported `doctor_disposition: ready`; installed `nose 0.18.0` satisfies the `>=0.17.0` constraint, so no new installation was needed.
- `charness tool install nose --dry-run` retained the manifest-supported upstream installer route and discovered latest release `v0.19.0`.
- `charness tool sync-support nose` confirmed the intentional integration-only disposition (`support status: skipped`, no support skill source).
- `inventory_nose_clones.py --json` completed with `status: clean` and no displayed extractable clone family.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-15-v1-0-9-root-cli-yaml-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v1.0.9`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.618`
- Stdout tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete
PACKAGE: charness
VERSION: 1.0.8 -> 1.0.9
CHECKOUT: pulled /home/hwidong/.agents/src/charness
SCOPE: self
COMPLETED: codex_source_prepared, codex_marketplace_registered, upstream_support_skills_synced, claude_marketplace_updated, claude_plugin_updated, codex_cache_refreshed
SESSION_STALENESS: cache paths rotated for active sessions
  - local/charness 1.0.8 -> 1.0.9
  -> Updated plugin caches were rotated. Active Codex/Claude sessions may have stale absolute skill paths injected into their system prompt. Restart those sessions, or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/capability_catalog.py resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale> [--marketplace <m> --plugin <p>]`.
NEXT_ACTION:
  - codex: Codex host install markers are present. Start a new Codex session to load charness.
  - claude: Claude host install markers are present. Restart Claude Code to load or refresh charness.`

## Release Runtime

- `requested_review_gate`: 0.005s
- `cli_skill_surface_gate`: 1.894s
- `quality_command`: 81.846s
- `fresh_checkout_probes_resume`: 2.988s
- `push_create_verify_release`: 61.034s
- `distinct_channel_verification`: 0.548s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 8.618s

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
