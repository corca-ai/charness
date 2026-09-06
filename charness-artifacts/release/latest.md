# Release Surface Check
Date: 2026-09-06

## Scope

Advanced `charness` toward release `8.4.4` (tag `v8.4.4`) through the repo-owned release helper.

## Current Version

- previous version: `8.4.3`
- target version: `8.4.4`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 383.4s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.4.4`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.4.4`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.4.4`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.4.4`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (3644 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-09-06-goal798-release-8-4-4.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-09-06-v8.4.4-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Parent delegated exact prepared commit00400d1cf4e3 to /root/preview_design in a separate agent context; the reviewer independently delivered the new claims narrative and four advisory evidence limits.
- Review narrative: `charness-artifacts/release-review/2026-09-06-v8.4.4-claims-review.md`.
- Verdict scope: 191 blocking path(s) gated this tag; 5 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 4 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - The release quality result is corroborated by local receipt `e83944f5c683da3eb28792df482a07a46dbd27c1ddd1d6f756467dc63ddb4c65`, but that receipt is uncommitted and its index-tree binding is the pre-bump parent source tree rather than the prepared release commit.
  - Fresh-checkout passed is corroborated by parent-held initial and post-amend helper output, but the prepared commit contains no raw per-probe receipt.
  - Consumer acceptance outputs are committed, while strict duplicate counts and some token/runtime provenance depend on normalized judgment records plus ephemeral or parent-held producer traces rather than a complete committed set of raw task receipts.
  - The notes' phrase `Installed-package` refers to canonical exported plugin packages used outside the consumer repos, not a post-publish installed-host roundtrip; install refresh remains pending.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.4.4`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.375`
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
STEP: source checkout code differs from the running CLI; re-executing the checkout's CLI so the run matches its scripts
STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.007s
- `cli_skill_surface_gate`: 2.287s
- `quality_command`: 383.362s
- `fresh_checkout_probes_resume`: 4.407s
- `push_create_verify_release`: 4.696s
- `distinct_channel_verification`: 0.593s
- `published_notes_audit`: 0.409s
- `post_publish_install_refresh`: 9.375s
- `post_publish_installed_readback`: 1.203s
- `release_observer`: 0.002s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-09-06-v8.4.4-release-observer.json`.
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

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

> Patch: repair existing verification guidance, advisory rendering, review preview continuation, and staged-owner selection without adding or breaking a public command, skill, or schema.