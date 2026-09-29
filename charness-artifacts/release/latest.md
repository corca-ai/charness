# Release Surface Check
Date: 2026-09-29

## Scope

Advanced `charness` toward release `8.14.3` (tag `v8.14.3`) through the repo-owned release helper.

## Current Version

- previous version: `8.14.2`
- target version: `8.14.3`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 503.8s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/686908-1790684181630530682/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.14.3-prepush-quality.json` (sha256: `807e97a23c06ebdb3d3de64168b3b76d16dc1ae1067208169abc35d2178b77e9`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.14.3`, checked at `post-claims-review, pre-push`.
- Validated tree: commit `dadb0a5d1446c6b4b8312bac3f16671d00fbbc46` (tree `ef4520932d3ff6ec18d47f333ec24de1b5014d66`); a pushed tag or branch that does not contain this tree was not what this check validated.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.14.3`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.14.3`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.14.3`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (83 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/v8143-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-09-29-v8.14.3-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: subagent claims-review-8-14-3 result_ready with narrative at charness-artifacts/release-review/v8143-claims-narrative.md, verdict PASS, no blocking findings
- Review narrative: `charness-artifacts/release-review/v8143-claims-narrative.md`.
- Verdict scope: 481 blocking path(s) gated this tag; 3 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: none recorded by this review.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.14.3`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.083`
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

- `requested_review_gate`: 0.005s
- `cli_skill_surface_gate`: 2.187s
- `quality_command`: 503.754s
- `fresh_checkout_probes_resume`: 6.780s
- `push_create_verify_release`: 503.446s
- `distinct_channel_verification`: 0.566s
- `published_notes_audit`: 0.466s
- `post_publish_install_refresh`: 8.083s
- `post_publish_installed_readback`: 1.011s
- `release_observer`: 0.001s
- `issue_closeout_carrier`: 17.188s
- `issue_closeout`: 2.675s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-09-29-v8.14.3-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal run --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `state-verified`.
- GitHub repo: `corca-ai/charness`
- Issue #877: `CLOSED` (https://github.com/corca-ai/charness/issues/877)
  - carrier: `direct_post_publish_commit_body`
  - manual fallback used: `True`
- Issue #878: `CLOSED` (https://github.com/corca-ai/charness/issues/878)
  - carrier: `direct_post_publish_commit_body`
  - manual fallback used: `False`
- Issue #879: `CLOSED` (https://github.com/corca-ai/charness/issues/879)
  - carrier: `direct_post_publish_commit_body`
  - manual fallback used: `False`

## User Update Steps

- Run `charness update` to fast-forward the managed checkout on its configured branch; that branch carries the latest published Charness release and any commits landed after it, and `charness version` names the installed version.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.


## Bump Rationale

- Bump: `8.14.2` -> `8.14.3` (`publish-current`).
> Patch: three independent single-owner bug fixes (#877 lane checkpoint, #878 reviewer backend, #879 scope evidence) with no API or contract change beyond the reported defects; no migration.