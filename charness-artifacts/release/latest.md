# Release Surface Check
Date: 2026-07-29

## Scope

Advanced `charness` toward release `2.12.0` (tag `v2.12.0`) through the repo-owned release helper.

## Current Version

- previous version: `2.11.3`
- target version: `2.12.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v2.12.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v2.12.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v2.12.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (8683 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-4f052775ba0ef620fe8cbfc6b4a870f8488b3d0252ae378d9db37b05e80e4dd5`.
- Linked feedback ID: `feedback-fd523faf68febe36a1d740d18bb89b61a49bcac2a19a43193078d6dff51c87b7`.
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
- Retro artifact: `charness-artifacts/retro/2026-07-29-v2-12-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 13.
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/scripts/audit_public_release_narrative.py`
  - `skills/public/release/scripts/check_real_host_proof.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/publish_release_narrative_gate.py`
  - `skills/public/release/scripts/publish_release_post_create.py`
  - `skills/public/release/scripts/publish_release_same_proxy_guard.py`
  - `skills/public/release/scripts/publish_release_verification_sections.py`
  - `skills/public/release/scripts/release_observer.py`
- Evaluated changed paths: 203.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-push`
  - `AGENTS.md`
  - `charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md`
  - `charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md`
  - `charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md`
  - `charness-artifacts/critique/2026-07-27-publish-gate-d1-d2-d3-d5.md`
  - `charness-artifacts/critique/2026-07-28-102134-packet.json`
  - `charness-artifacts/critique/2026-07-28-102134-packet.md`
  - `charness-artifacts/critique/2026-07-28-112813-packet.json`
  - `charness-artifacts/critique/2026-07-28-112813-packet.md`
  - `charness-artifacts/critique/2026-07-28-a-second-bounded-review-round-for-verdict-logic-slices.md`
  - `charness-artifacts/critique/2026-07-28-critique-evidence-floor-as-one-subsystem.md`
  - `charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md`
  - `charness-artifacts/critique/2026-07-28-empty-scope-remainder-d7-d9-d10-e5.md`
  - `charness-artifacts/critique/2026-07-28-four-unestablished-scope-readers-in-the-quality-dup-nose-subsystem.md`
  - `charness-artifacts/critique/2026-07-28-i464-round2-packet.json`
  - `charness-artifacts/critique/2026-07-28-i464-round2-packet.md`
  - `charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md`
  - ... 183 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-29-v2.12.0-release.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v2.12.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.815`
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
- `cli_skill_surface_gate`: 1.726s
- `quality_command`: 77.265s
- `fresh_checkout_probes_initial`: 3.460s
- `fresh_checkout_probes_after_amend`: 3.335s
- `push_create_verify_release`: 47.182s
- `distinct_channel_verification`: 0.550s
- `published_notes_audit`: 0.465s
- `post_publish_install_refresh`: 8.815s
- `post_publish_installed_readback`: 1.237s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `no_version_claim` for `docs/handoff.md`.
- Just-published version: `2.12.0`.
- The baton's routing sections claim no release version.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `2.12.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-07-29-v2.12.0-release-observer.json`.
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
