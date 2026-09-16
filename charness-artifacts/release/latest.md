# Release Surface Check
Date: 2026-09-17

## Scope

Advanced `charness` toward release `8.9.0` (tag `v8.9.0`) through the repo-owned release helper.

## Current Version

- previous version: `8.8.0`
- target version: `8.9.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 258.9s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/3523980-1789583226119763012/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.9.0-prepush-quality.json` (sha256: `b8b04d65377f654fd92fb15a1cdfe76530d5b110e1ee5cd6690ecb134c867fea`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.9.0`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.9.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.9.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.9.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/v890-release-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-09-17-v8.9.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: ephemeral codex exec session 01a0ab6c-5fa4-7c80-97a1-3daec70f9db5, --sandbox read-only --ephemeral, fresh context, no repo mutation; full audit persisted in charness-artifacts/release-review/v8.9.0-claims-review.md
- Review narrative: `charness-artifacts/release-review/v8.9.0-claims-review.md`.
- Verdict scope: 61 blocking path(s) gated this tag; 1 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 2 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - Quality exit-0 line is honest but single-sourced; no 8.9.0 quality receipt in the prepared commit and the record hedges quality-unestablished pending final resume.
  - Fresh-checkout probe passage is record-asserted only; no independently durable probe receipt in the prepared commit.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.9.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `7.895`
- Stdout tail: `de to load or
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
  source: codex_host_guidance
session_staleness:
  message: Updated plugin caches were rotated. Active Codex/Claude sessions may have
    stale absolute skill paths injected into their system prompt. Restart those sessions,
    or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/adapters/capability_catalog.py
    resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale>
    [--marketplace <m> --plugin <p>]`.
  affected_count: 1`
- Stderr tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.263s
- `quality_command`: 258.898s
- `fresh_checkout_probes_resume`: 5.789s
- `push_create_verify_release`: 258.785s
- `distinct_channel_verification`: 0.525s
- `published_notes_audit`: 0.458s
- `post_publish_install_refresh`: 7.895s
- `post_publish_installed_readback`: 1.137s
- `release_observer`: 0.001s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-09-16-v8.9.0-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `carrier-pending-state-verification`.

## User Update Steps

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> minor, not patch: #820 adds a new additive declarative plan capability (expected_failing_test for Node/TAP mutation) that existing users adopt without migration; no invocation break, so not major.