# Release Surface Check
Date: 2026-07-15

## Scope

Advanced `charness` toward release `1.0.11` (tag `v1.0.11`) through the repo-owned release helper.

## Current Version

- previous version: `1.0.10`
- target version: `1.0.11`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v1.0.11`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v1.0.11`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-23aad15ec305f80023342d88aeea90ba7bd9aa38f41b220c6f83989b4dd11694`.
- Linked feedback ID: `feedback-11f09a3178804dabac0a6126479328e4b5534369728835f8440e64aa1f337abc`.
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
- Retro artifact: `charness-artifacts/retro/2026-07-15-v1-0-11-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 37.
  - `.claude-plugin/marketplace.json`
  - `charness`
  - `charness-artifacts/critique/2026-07-15-083904-packet.json`
  - `charness-artifacts/critique/2026-07-15-083904-packet.md`
  - `charness-artifacts/critique/2026-07-15-update-all-aggregate-provenance-release-critique.md`
  - `charness-artifacts/debug/2026-07-15-debug-review.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/gather/2026-07-15-raw-githubusercontent-com-gitleaks-gitleaks-master-go-mod-e21d9f59.md`
  - `charness-artifacts/gather/2026-07-15-specdown-install-readme.md`
  - `charness-artifacts/gather/latest.md`
  - `charness-artifacts/quality/2026-07-15-quality-review.md`
  - `charness-artifacts/quality/latest.md`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-15-v1-0-10-release-auto-retro.md`
  - `charness-artifacts/retro/2026-07-15-v1-0-11-release-auto-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/control-plane.md`
  - ... 17 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Remaining real-host checklist items, if any, still require explicit proof before full closeout.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-15-update-all-aggregate-provenance-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v1.0.11`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.607`
- Stdout tail: `shed
  action: refresh
  method: codex-app-server-plugin-install
  reason: plugin-install-succeeded
codex_host_guidance:
  status: installed
  manual_action_required: false
  message: Codex host install markers are present. Start a new Codex session to load
    charness.
claude_host_guidance:
  status: installed
  manual_action_required: false
  message: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
next_steps:
  codex: Codex host install markers are present. Start a new Codex session to load
    charness.
  claude: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
repo_onboarding:
  status: skipped
  manual_action_required: false
  message: null
  reason: skipped during update unless --target-repo-root is provided
next_action:
  kind: restart
  host: codex
  status: installed
  manual_action_required: false
  message: Codex host install markers are present. Start a new Codex session to load
    charness.
  source: codex_host_guidance
session_staleness:
  message: Updated plugin caches were rotated. Active Codex/Claude sessions may have
    stale absolute skill paths injected into their system prompt. Restart those sessions,
    or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/capability_catalog.py
    resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale>
    [--marketplace <m> --plugin <p>]`.
  affected_count: 1`
- Stderr tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.005s
- `cli_skill_surface_gate`: 1.880s
- `quality_command`: 88.788s
- `fresh_checkout_probes_resume`: 3.024s
- `push_create_verify_release`: 65.842s
- `distinct_channel_verification`: 0.534s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 8.607s

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
