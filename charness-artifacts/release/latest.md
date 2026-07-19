# Release Surface Check
Date: 2026-07-19

## Scope

Advanced `charness` toward release `2.2.0` (tag `v2.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `2.1.6`
- target version: `2.2.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v2.2.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v2.2.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-ca7a1fccae0bc60c349161a70430db68696aec591b5131fadd1041d57b4a286e`.
- Linked feedback ID: `feedback-5d4bd7b176b0c5ebcb0ba8039dc877a0cc4b9d63bb76e9da6f0733baebcd8d12`.
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
- Retro artifact: `charness-artifacts/retro/2026-07-19-v2-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 3.
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/release_tag_identity.py`
- Evaluated changed paths: 96.
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-critique.md`
  - `charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.json`
  - `charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.md`
  - `charness-artifacts/critique/2026-07-19-install-update-runner-reuse-critique.md`
  - `charness-artifacts/critique/2026-07-19-install-update-runner-reuse-packet.json`
  - `charness-artifacts/critique/2026-07-19-install-update-runner-reuse-packet.md`
  - `charness-artifacts/critique/2026-07-19-portable-proof-path-and-release-identity-critique.md`
  - `charness-artifacts/critique/2026-07-19-speed-only-proof-path-critique.md`
  - `charness-artifacts/critique/2026-07-19-speed-only-slice-final-packet.json`
  - `charness-artifacts/critique/2026-07-19-speed-only-slice-final-packet.md`
  - `charness-artifacts/debug/2026-07-19-skill-contract-whitespace-coupling.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/metrics/rca-ledger.jsonl`
  - `charness-artifacts/probe/2026-07-18-v2.1.6-release-observer.json`
  - `charness-artifacts/quality/2026-07-19-quality-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-18-231235-packet.json`
  - ... 76 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-19-portable-proof-path-and-release-identity-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v2.2.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.098`
- Stdout tail: `  action: refresh
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
host_next_steps:
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

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.841s
- `quality_command`: 77.055s
- `fresh_checkout_probes_initial`: 2.852s
- `fresh_checkout_probes_after_amend`: 2.911s
- `push_create_verify_release`: 71.802s
- `distinct_channel_verification`: 0.515s
- `post_publish_install_refresh`: 8.098s
- `post_publish_installed_readback`: 1.345s
- `release_observer`: 0.000s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `2.2.0`.
- Versions claimed by the baton's routing sections: `2.2.0`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-07-19-v2.2.0-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

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
