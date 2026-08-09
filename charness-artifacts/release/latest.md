# Release Surface Check
Date: 2026-08-09

## Scope

Advanced `charness` toward release `4.1.0` (tag `v4.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `4.0.0`
- target version: `4.1.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v4.1.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v4.1.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v4.1.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (5244 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-7c04b890f3bbe0bb2f320ef7d83c1f3e842e08d1771d4c3fe68897a85fed3803`.
- Linked feedback ID: `feedback-4fb4049bfe575c7156761a2bf4444731b90b075aa9706b91226c91eaf66cdd25`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-09-v4-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `scripts/capability_catalog_sources.py`
- Evaluated changed paths: 250.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-commit`
  - `.githooks/pre-push`
  - `AGENTS.md`
  - `charness-artifacts/audit/2026-08-09-no-observed-effect-census.md`
  - `charness-artifacts/audit/closeout-floors.md`
  - `charness-artifacts/critique/2026-08-09-080414-packet.json`
  - `charness-artifacts/critique/2026-08-09-080414-packet.md`
  - `charness-artifacts/critique/2026-08-09-082846-packet.json`
  - `charness-artifacts/critique/2026-08-09-082846-packet.md`
  - `charness-artifacts/critique/2026-08-09-083309-packet.json`
  - `charness-artifacts/critique/2026-08-09-083309-packet.md`
  - `charness-artifacts/critique/2026-08-09-issue-523-root-routing-split-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-530-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-549-hook-failure-visibility-reader-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-560-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-563-title-slug-checker-deletion-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-564-resolution-critique.md`
  - `charness-artifacts/critique/2026-08-09-issue-565-resolution-critique.md`
  - ... 230 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-09-release-4-1-0-safety-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v4.1.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.201`
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
- `cli_skill_surface_gate`: 0.079s
- `quality_command`: 101.040s
- `fresh_checkout_probes_initial`: 3.795s
- `fresh_checkout_probes_after_amend`: 3.817s
- `push_create_verify_release`: 70.186s
- `distinct_channel_verification`: 0.535s
- `published_notes_audit`: 0.426s
- `post_publish_install_refresh`: 8.201s
- `post_publish_installed_readback`: 1.314s
- `release_observer`: 0.001s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `4.1.0`.
- Versions claimed by the baton's routing sections: `4.1.0`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-09-v4.1.0-release-observer.json`.
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

- Issue closeout verification: `carrier-pending-state-verification`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
