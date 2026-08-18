# Release Surface Check
Date: 2026-08-18

## Scope

Advanced `charness` toward release `6.1.0` (tag `v6.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.0.1`
- target version: `6.1.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.1.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.1.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.1.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-aa6eddadb9a2d69d2d9aac0a5f57fe42d353f1cf9b9a8185584059f34c7fda20`.
- Linked feedback ID: `feedback-51a9846670c968305e834d878dc36aea5fffab137b8c79bf505ce2476b6ba4a1`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-18-v6-1-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 13.
  - `skills/public/release/references/version-policy.md`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_adapter_preflight.py`
  - `skills/public/release/scripts/publish_release_arg_guards.py`
  - `skills/public/release/scripts/publish_release_args.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_plan.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_premutation_sections.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
- Evaluated changed paths: 96.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-17-release-v6-0-1.md`
  - `charness-artifacts/critique/2026-08-17-session-release-record-retro-prefix.md`
  - `charness-artifacts/critique/2026-08-18-issue-633-verify-and-close.md`
  - `charness-artifacts/critique/2026-08-18-issue-636-resolution.md`
  - `charness-artifacts/critique/2026-08-18-issues-632-631-630-verify-and-close.md`
  - `charness-artifacts/critique/2026-08-18-v6.1.0-release-critique.md`
  - `charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json`
  - `charness-artifacts/probe/2026-08-17-v6.0.1-release-observer.json`
  - `charness-artifacts/quality/2026-08-18-quality-review.md`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/latest.md`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-17-204807-packet.json`
  - `charness-artifacts/retro/2026-08-17-204807-packet.md`
  - ... 76 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-18-v6.1.0-release-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Spawned as a bounded-reviewer subagent whose envelope exposed only Read, Grep and Glob; it reported Bash/Edit/Write/Agent absent, verified refs by reading .git files directly, and returned CLAIMS-CLEAN with five minors the preparer had not written down, including a date inconsistency inside the preparer's own helper run.
- Review narrative: `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.1.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.044`
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
- `cli_skill_surface_gate`: 1.920s
- `quality_command`: 142.239s
- `fresh_checkout_probes_resume`: 4.126s
- `push_create_verify_release`: 125.899s
- `distinct_channel_verification`: 0.494s
- `published_notes_audit`: 0.420s
- `post_publish_install_refresh`: 9.044s
- `post_publish_installed_readback`: 1.515s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `no_version_claim` for `docs/handoff.md`.
- Just-published version: `6.1.0`.
- The baton's routing sections claim no release version.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.1.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-18-v6.1.0-release-observer.json`.
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

> Minor, not patch: this range ships one genuinely new operator-facing surface — the --bump-rationale flag and the release record's Bump Rationale section, absent at the 6.0.1 base (git-proven) — on top of acceptance-equivalent repairs (#636 one-pass debug-validator reporting, critique blocked-vocabulary fix, void-disposition pin). Nothing renames, removes, or changes invocation expectations, so major is not in question; patch would understate the additive surface.