# Release Surface Check
Date: 2026-08-17

## Scope

Advanced `charness` toward release `6.0.1` (tag `v6.0.1`) through the repo-owned release helper.

## Current Version

- previous version: `6.0.0`
- target version: `6.0.1`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.0.1`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.0.1`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.0.1`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-9c06edf7fb09c2a50d7dca7bfaba9ce8fbccb7fced718ba408484eea7187dd3d`.
- Linked feedback ID: `feedback-d7a768bbaa10c6fbc65514d168c3a4701a5ebd386cba63e95366983416e2abae`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v6.0.0`
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
- Retro artifact: `charness-artifacts/retro/2026-08-17-v6-0-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 3.
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/scripts/bump_version.py`
  - `skills/public/release/scripts/resolve_adapter.py`
- Evaluated changed paths: 157.
  - `.agents/release-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/mutation-tests.yml`
  - `.github/workflows/quality-core.yml`
  - `charness-artifacts/critique/2026-08-17-053617-packet.json`
  - `charness-artifacts/critique/2026-08-17-053617-packet.md`
  - `charness-artifacts/critique/2026-08-17-issue-617-closeout.md`
  - `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/issue/2026-08-16-6-0-0-closeout-ledger.md`
  - `charness-artifacts/issue/2026-08-16-issue-618-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-619-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-620-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-621-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-622-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-623-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-624-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-625-closeout.md`
  - `charness-artifacts/issue/2026-08-16-issue-626-closeout-comment.md`
  - ... 137 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Spawned as a bounded-reviewer subagent whose envelope exposed only Read, Grep and Glob; it reported Bash/Edit/Write/Agent absent and returned findings the preparer had not written. It returned fail on its first pass, and its blocker was a FALSE CLAIM in the preparer's own critique artifact -- that the bump rationale was recorded in the release record, which it was not. A same-agent reread would have re-read the sentence it wrote.
- Review narrative: `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.0.1`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `11.155`
- Stdout tail: `essage: Codex host install markers are present. Start a new Codex session to load
    charness.
claude_host_guidance:
  status: installed
  manual_action_required: false
  message: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
grok_host_guidance:
  status: unavailable
  manual_action_required: false
  message: Grok CLI not detected on this machine.
host_next_steps:
  codex: Codex host install markers are present. Start a new Codex session to load
    charness.
  claude: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
  grok: Grok CLI not detected on this machine.
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

- `requested_review_gate`: 0.006s
- `cli_skill_surface_gate`: 2.007s
- `quality_command`: 152.375s
- `fresh_checkout_probes_resume`: 4.055s
- `push_create_verify_release`: 141.789s
- `distinct_channel_verification`: 0.522s
- `published_notes_audit`: 0.499s
- `post_publish_install_refresh`: 11.155s
- `post_publish_installed_readback`: 1.396s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `no_version_claim` for `docs/handoff.md`.
- Just-published version: `6.0.1`.
- The baton's routing sections claim no release version.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.0.1`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-17-v6.0.1-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`
- `python3 scripts/closeout_bundle.py --help >/dev/null`
- `python3 scripts/validate_retro_handoff_wiring.py --help >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
