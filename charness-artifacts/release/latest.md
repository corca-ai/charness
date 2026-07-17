# Release Surface Check
Date: 2026-07-17

## Scope

Advanced `charness` toward release `1.3.0` (tag `v1.3.0`) through the repo-owned release helper.

## Current Version

- previous version: `1.2.0`
- target version: `1.3.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v1.3.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v1.3.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-34567de27d972b569b92f335767c74474924f8d9e6a0a1e563b6ae68a39fc1b6`.
- Linked feedback ID: `feedback-c1e68b61aa48c325429d4556cdbecb7c9a68218fb2c7a210172c128bc56e49dd`.
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
- Retro artifact: `charness-artifacts/retro/2026-07-17-v1-3-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 30.
  - `.agents/critique-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `AGENTS.md`
  - `charness-artifacts/critique/2026-07-17-prove-dogfood-via-444-polish-disposition-review.md`
  - `charness-artifacts/critique/2026-07-17-v1-3-0-release-critique.md`
  - `charness-artifacts/goals/2026-07-16-scout-driven-improvement.md`
  - `charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish-host-log-probe.json`
  - `charness-artifacts/goals/2026-07-17-prove-dogfood-via-444-polish.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-07-17-prove-dogfood-via-444-polish-goal-session-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/handoff.md`
  - `docs/public-skill-dogfood.json`
  - `docs/public-skill-dogfood.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/scripts/check_issue_closeout_commit_msg.py`
  - ... 10 more

## Real-Host Verification

- No configured release-time real-host verification trigger matched this slice.

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-07-17-v1-3-0-release-critique.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v1.3.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.705`
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

- `requested_review_gate`: 0.001s
- `cli_skill_surface_gate`: 1.853s
- `quality_command`: 82.923s
- `fresh_checkout_probes_initial`: 3.057s
- `fresh_checkout_probes_after_amend`: 3.078s
- `push_create_verify_release`: 60.445s
- `distinct_channel_verification`: 0.537s
- `issue_closeout`: 0.000s
- `post_publish_install_refresh`: 8.705s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `1.3.0`.
- Versions claimed by the baton's routing sections: `1.2.0`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `1.3.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

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
