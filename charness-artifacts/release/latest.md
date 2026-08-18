# Release Surface Check
Date: 2026-08-18

## Scope

Advanced `charness` toward release `6.2.0` (tag `v6.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.1.0`
- target version: `6.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- Version drift check: NOT recorded by this helper invocation, so this record makes no no-drift claim about packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.2.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.2.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.2.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (4937 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-cafad13b7afe858ea19704cd6b333c42a2fbe34064f6e1e71243e00d4f9d967d`.
- Linked feedback ID: `feedback-3b00e03630c242b4e7e0f6ff2024d385a6a2cbe3b7adeddc2992e09d75019aa6`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-18-v6-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 94.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-18-issue-640-resolution.md`
  - `charness-artifacts/critique/2026-08-18-release-6-2-0.md`
  - `charness-artifacts/issue/2026-08-18-issue-640-brief.md`
  - `charness-artifacts/probe/2026-08-18-v6.1.0-release-observer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.md`
  - `charness-artifacts/release-review/2026-08-18-v6.2.0-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-18-v6.2.0-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-18-v6-1-0-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-18-v6-2-0-release-auto-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - ... 74 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-18-release-6-2-0.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-18-v6.2.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Spawned as a bounded-reviewer subagent whose envelope exposed only Read, Grep and Glob; it reported Bash/Edit/Write/Agent absent, named four evidence items it could not fetch rather than asserting them, and returned blockers-found with three record defects the preparer had not written down - the relevel inside the delta, the Review Proof artifact contradicting the tree, and the missing --no-verify non-claim. All three were repaired before publication and the prepared commit amended.
- Review narrative: `charness-artifacts/release-review/2026-08-18-v6.2.0-prepared-claims-review.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.2.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.876`
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

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.041s
- `quality_command`: 219.917s
- `fresh_checkout_probes_resume`: 4.175s
- `push_create_verify_release`: 206.969s
- `distinct_channel_verification`: 0.660s
- `published_notes_audit`: 0.420s
- `post_publish_install_refresh`: 9.876s
- `post_publish_installed_readback`: 1.390s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `no_version_claim` for `docs/handoff.md`.
- Just-published version: `6.2.0`.
- The baton's routing sections claim no release version.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.2.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-18-v6.2.0-release-observer.json`.
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


## Bump Rationale

> minor: additive operator surface. Three new optional adapter fields (max_artifact_lines on debug and quality, max_content_lines on handoff), a new optional_int primitive in the shared adapter vocabulary, and two additive payload keys (size_budget.source, content_line_budget). Not patch, because a consuming repo gains a capability it can adopt without migration. Not major, because the shipped defaults are byte-identical to c34155a48 -- verified with git show, not assumed -- so a consumer who sets nothing sees no change; the only removed name is NEAR_LIMIT_LINES, a module constant of a CLI-invoked skill script with no in-tree importer.