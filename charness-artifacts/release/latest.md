# Release Surface Check
Date: 2026-07-18

## Scope

Advanced `charness` toward release `2.1.6` (tag `v2.1.6`) through the repo-owned release helper.

## Current Version

- previous version: `2.1.5`
- target version: `2.1.6`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v2.1.6`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v2.1.6`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-a33a9ba0f2d587e5e5951636865c129862d8010a3472fdcdcd10e678a5be7dda`.
- Linked feedback ID: `feedback-9939428bbc4ca63dc6789b86b64c1d7a2d055001a36f5369c9f6315bfb7b7880`.
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
- Retro artifact: `charness-artifacts/retro/2026-07-18-v2-1-6-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 18.
  - `skills/public/release/references/publication-boundary.md`
  - `skills/public/release/references/real-host-proof.md`
  - `skills/public/release/scripts/check_fresh_checkout_probes.py`
  - `skills/public/release/scripts/check_real_host_proof.py`
  - `skills/public/release/scripts/check_requested_review_gate.py`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_runtime.py`
  - `skills/public/release/scripts/release_delta.py`
  - `skills/public/release/scripts/release_issue_closeout.py`
  - `skills/public/release/scripts/release_issue_closeout_artifact.py`
  - `skills/public/release/scripts/release_issue_closeout_message.py`
- Evaluated changed paths: 82.
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-07-18-185648-packet.json`
  - `charness-artifacts/critique/2026-07-18-185648-packet.md`
  - `charness-artifacts/critique/2026-07-19-critique-review.md`
  - `charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md`
  - `charness-artifacts/critique/v2-1-6-release-candidate-packet.json`
  - `charness-artifacts/critique/v2-1-6-release-candidate-packet.md`
  - `charness-artifacts/debug/2026-07-19-release-issue-close-evidence-ordering.md`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/goals/2026-07-19-gajae-pattern-adoption.md`
  - `charness-artifacts/metrics/rca-ledger.jsonl`
  - `charness-artifacts/probe/2026-07-18-v2.1.5-release-observer.json`
  - `charness-artifacts/quality/2026-07-19-quality-review.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/latest.md`
  - `charness-artifacts/release/2026-07-19-v2.1.6-notes.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-19-session-retro.md`
  - ... 62 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v2.1.6`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.189`
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
- `cli_skill_surface_gate`: 1.840s
- `quality_command`: 93.387s
- `fresh_checkout_probes_initial`: 2.918s
- `fresh_checkout_probes_after_amend`: 2.919s
- `push_create_verify_release`: 98.584s
- `distinct_channel_verification`: 0.482s
- `post_publish_install_refresh`: 8.189s
- `post_publish_installed_readback`: 1.419s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `2.1.6`.
- Versions claimed by the baton's routing sections: `2.1.5`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `2.1.6`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-07-18-v2.1.6-release-observer.json`.
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
