# Release Surface Check
Date: 2026-10-21

## Scope

Advanced `charness` toward release `8.15.0` (tag `v8.15.0`) through the repo-owned release helper.

## Current Version

- previous version: `8.14.9`
- target version: `8.15.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 671.0s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/3690622-1792519675779221150/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.15.0-prepush-quality.json` (sha256: `ab281dc97a611ce77c96e930dad0d68e252d031e8ec1a172108ad9375dbbc444`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.15.0`, checked at `post-claims-review, pre-push`.
- Validated tree: commit `1b1584609372877f2f2646e9af8498396d3bb5f6` (tree `9ccae5a09f22527cf3611873b2d47443bf07d3fe`); a pushed tag or branch that does not contain this tree was not what this check validated.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.15.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.15.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.15.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (9627 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-10-20-release-critique-charness-v8-15-0-2.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-10-21-v8.15.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: native Claude Code charness:bounded-reviewer subagent with only Read, Grep and Glob, spawned by the release parent
- Review narrative: `charness-artifacts/release-review/2026-10-21-v8.15.0-claims-review.md`.
- Verdict scope: 1848 blocking path(s) gated this tag; 3 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 7 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - A1: a deferred checkpoint request preempts the 3rd-run debug request when nothing else runs; tested but not in notes or spec
  - A2: loop counts key on command text and tree fingerprint over the lane life, so an edit-then-revert counts as a repeat
  - A3: notes call a reader-probe start unnamed but not also uncounted; spec says both (critique F12)
  - A4: docs/agent-task-runs.md phrase 'delays either a check' is garbled (critique F12)
  - A5: latest.md names the pre-bump tree as the validated tree; helper-generated wording
  - A6: window 0 with no timeout is not wholly unbounded for require-change lanes; first-edit budget still applies
  - A7: progress_guard.stop_enabled reflects only the first-edit budget; progress_rule.stop_enabled can differ

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.15.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.344`
- Stdout tail: `odex host install markers are present. Start a new Codex session to load
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
    or re-resolve a stale charness skill path with `python3 /home/hwidong/.agents/src/charness/scripts/adapters/capability_catalog.py
    resolve-skill-path --repo-root <repo> --skill-id <id> --reported-path <stale>
    [--marketplace <m> --plugin <p>]`.
  affected_count: 1`
- Stderr tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.003s
- `cli_skill_surface_gate`: 2.248s
- `quality_command`: 671.008s
- `fresh_checkout_probes_resume`: 8.320s
- `push_create_verify_release`: 636.522s
- `distinct_channel_verification`: 0.729s
- `published_notes_audit`: 0.506s
- `post_publish_install_refresh`: 8.344s
- `post_publish_installed_readback`: 1.107s
- `release_observer`: 0.005s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-10-20-v8.15.0-release-observer.json`.
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

- Bump: `8.14.9` -> `8.15.0` (`publish-current`).
- Bump rationale: NOT recorded by this helper invocation. `version-policy.md` requires a stated rationale whenever the bump level is debatable; this record carries none, so the level above is an unexplained judgment call.