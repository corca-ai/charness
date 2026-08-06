# Release Surface Check
Date: 2026-08-06

## Scope

Advanced `charness` toward release `3.4.0` (tag `v3.4.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.3.0`
- target version: `3.4.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v3.4.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v3.4.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v3.4.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (2832 body bytes).

## Remote CI Readback

- Durable observer record: `charness-artifacts/probe/2026-08-06-v3.4.0-remote-ci.json`.
- Workflow: `Quality Core` run `31111004866` for `main` commit `76e96fe9`.
- Core deterministic gates: `success`.
- Changed-line mutation coverage (push/PR mirror): `success`.
- Observer/channel: GitHub Actions service via the GitHub Actions API, distinct from the `git push origin main` exit status.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-bcbd01da4a3f115f5ecf2aecf43a2b276f194b6d22f23b4f8ed254cd08fee9e1`.
- Linked feedback ID: `feedback-aa7daa3583c1aef63302c0065b6b85a66d4adef892c8b09e0afa29e459a58cba`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v3.3.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `fresh_checkout_probes`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes tests/quality_gates/test_release_backend.py::test_release_adapter_rejects_invalid_fresh_checkout_probes -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-06-v3-4-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 62.
  - `.agents/release-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-evidence-identity-and-release-disposition.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-final-claims-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-final-claims-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice1-critique.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-bundle-slice3-retro-handoff.md`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh-packet.json`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh-packet.md`
  - `charness-artifacts/critique/2026-08-06-closeout-handoff-refresh.md`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.json`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique-packet.md`
  - `charness-artifacts/critique/2026-08-06-release-3-4-0-critique.md`
  - `charness-artifacts/critique/2026-08-06-runtime-evidence-and-final-boundary-disposition-review.md`
  - `charness-artifacts/critique/runtime-evidence-final-boundary-packet.json`
  - `charness-artifacts/critique/runtime-evidence-final-boundary-packet.md`
  - ... 42 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-06-release-3-4-0-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v3.4.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.803`
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

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.969s
- `quality_command`: 88.186s
- `fresh_checkout_probes_initial`: 3.853s
- `fresh_checkout_probes_after_amend`: 3.817s
- `push_create_verify_release`: 64.384s
- `distinct_channel_verification`: 0.474s
- `published_notes_audit`: 0.398s
- `post_publish_install_refresh`: 8.803s
- `post_publish_installed_readback`: 1.398s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `3.4.0`.
- Versions claimed by the baton's routing sections: `3.4.0`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-06-v3.4.0-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`
- `python3 scripts/closeout_bundle.py --help >/dev/null`
- `python3 scripts/validate_retro_handoff_wiring.py --help >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
