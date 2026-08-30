# Release Surface Check
Date: 2026-08-31

## Scope

Advanced `charness` toward release `8.0.1` (tag `v8.0.1`) through the repo-owned release helper.

## Current Version

- previous version: `8.0.0`
- target version: `8.0.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only --non-claim=release-changed-line-coverage` exited 0 in 127.4s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --non-claim=release-changed-line-coverage`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.0.1`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.0.1`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.0.1`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.0.1`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (5077 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v8.0.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `quality_command`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-31-v8-0-1-release.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-31-v8.0.1-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Separate agent /root/luna_v801_claims_review read-only audited prepared commit b4753f3b29b7e976be2b5f05e6e366eef4fb80dd in the isolated release checkout against v8.0.0.
- Review narrative: `charness-artifacts/release-review/2026-08-31-v8.0.1-claims-review.md`.
- Verdict scope: 19 blocking path(s) gated this tag; 2 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: none recorded by this review.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.0.1`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.102`
- Stdout tail: `Claude Code to load or
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
- `cli_skill_surface_gate`: 2.066s
- `quality_command`: 127.422s
- `fresh_checkout_probes_resume`: 4.052s
- `push_create_verify_release`: 4.344s
- `distinct_channel_verification`: 0.622s
- `published_notes_audit`: 0.464s
- `post_publish_install_refresh`: 8.102s
- `post_publish_installed_readback`: 1.160s
- `release_observer`: 0.000s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-30-v8.0.1-release-observer.json`.
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

> Patch, not minor: this repairs duplicate release-push verification and preserves the public skill and CLI capability shape.