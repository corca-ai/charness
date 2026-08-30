# Release Surface Check
Date: 2026-08-31

## Scope

Advanced `charness` toward release `8.0.0` (tag `v8.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `7.0.0`
- target version: `8.0.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --non-claim=release-changed-line-coverage` exited 0 in 130.8s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --non-claim=release-changed-line-coverage`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.0.0`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.0.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.0.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.0.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (10933 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v7.0.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `checked_in_plugin_root`
  - `materialized_plugin_root`
  - `quality_command`
  - `real_host_checklist`
  - `real_host_required_path_globs`
  - `real_host_required_surfaces`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-31-v8.0.0-release-repair-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-31-v8.0.0-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: This Luna typed subagent independently audited prepared commit f680aae434fbf2cca5d4dafb3471e5c0f7083918 after preparation as a separate claims observer.
- Review narrative: `charness-artifacts/release-review/2026-08-31-v8.0.0-claims-review.md`.
- Verdict scope: 2561 blocking path(s) gated this tag; 185 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 3 defect(s) recorded in the advisory scope and SHIPPED KNOWN-INACCURATE rather than repaired before this tag:
  - Mutation execution and mutation score remain unestablished under explicit release non-claim policy.
  - The 10,597-launch census is structural evidence; no consumer-repository speedup or elapsed-time claim is established.
  - Public GitHub/tag visibility and maintainer install-refresh readback remain unverified at the prepared stop.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.0.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `10.87`
- Stdout tail: `078cf6d9792a141b33f46de12f38558e720e1b522a
  post_refresh_cache_manifest_version: 8.0.0
  post_refresh_drift: false
  post_refresh_host_status: installed
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
grok_host_guidance:
  status: installed
  manual_action_required: false
  message: Grok plugin tree is present at `~/.grok/plugins/charness`. List `charness`
    in `[plugins].enabled` (do not add a marketplace), then restart Grok Build.
host_next_steps:
  codex: Codex host install markers are present. Start a new Codex session to load
    charness.
  claude: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
  grok: Grok plugin tree is present at `~/.grok/plugins/charness`. List `charness`
    in `[plugins].enabled` (do not add a marketplace), then restart Grok Build.
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
  source: codex_host_guidance`
- Stderr tail: `STEP: refreshing source checkout
STEP: source checkout code differs from the running CLI; re-executing the checkout's CLI so the run matches its scripts
STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.006s
- `cli_skill_surface_gate`: 2.176s
- `quality_command`: 130.800s
- `fresh_checkout_probes_resume`: 4.335s
- `push_create_verify_release`: 100.824s
- `distinct_channel_verification`: 0.628s
- `published_notes_audit`: 0.480s
- `post_publish_install_refresh`: 10.870s
- `post_publish_installed_readback`: 1.119s
- `release_observer`: 0.009s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-30-v8.0.0-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> Publish the already-prepared 8.0.0 major release: it removes incompatible task and handoff surfaces, renames the materialized plugin export contract, and changes existing automation expectations.