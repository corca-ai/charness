# Release Surface Check
Date: 2026-11-05

## Scope

Advanced `charness` toward release `8.16.0` (tag `v8.16.0`) through the repo-owned release helper.

## Current Version

- previous version: `8.15.0`
- target version: `8.16.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release --read-only` exited 0 in 1088.6s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release --read-only --receipt-json=/home/hwidong/.cache/tmp/charness/runtime/811b9f8f8a808bfa/scratch/release-prepush-quality/3120845-1793841240195086560/semantic-quality.json`).
- pre-push quality receipt: `charness-artifacts/release/8.16.0-prepush-quality.json` (sha256: `361b5f7b0006572cc567393afc2d9c38bf42e1d6a9dcd9665927cc773c60cd52`).
- `current_release.py` reported no version drift across 4 versioned surface(s), with 1 presence-only surface(s) not version-checked against target `8.16.0`, checked at `post-claims-review, pre-push`.
- Validated tree: commit `8263036bd6bdb907789a16c38f9353a3263a95ed` (tree `34a2c7e4833462669a2af0b1db997c540230f233`); a pushed tag or branch that does not contain this tree was not what this check validated.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v8.16.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v8.16.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v8.16.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (11083 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-11-05-release-critique-charness-v8-16-0.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-11-05-v8.16.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: native Claude Code charness:bounded-reviewer subagent with only Read, Grep and Glob, spawned by the release parent
- Review narrative: `charness-artifacts/release-review/2026-11-05-v8.16.0-claims-review.md`.
- Verdict scope: 744 blocking path(s) gated this tag; 2 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 12 finding(s) recorded in advisory scope and carried into this release record without gating this tag:
  - A1: no docs page mentions CHARNESS_TASK_RUN_CACHE_HOME or the writable_roots migration; only the notes carry them
  - A2: the critique says no option or field was removed but cites no diff
  - A3: the critique lists the full release lane as proof while latest.md records pytest-release pending
  - A4: the writable_roots closure is pinned by an argv test only; no live Codex probe is recorded
  - A5: latest.md names the pre-bump tree as validated while recording the run as post-bump, pre-commit
  - A6: the critique records the verify_packet command but not its result
  - A7: the critique says notes and docs changed for the first three claims rounds (round 4 too) and calls test-only dd9ac98a2 a code change
  - A8: one change can break a launcher omits that lanes now override caller-set GOCACHE, GOPATH and GOMODCACHE
  - A9: notes and docs imply every Claude lane runs the Codex preflight; it runs only with prelaunch gates on, also for Codex-first orders listing Claude
  - A10: the critique claim under test links remaining gaps to #889 only and misses the failed-deletion case F12 discloses
  - A11: repeat --bump-rationale on --resume so the published latest.md keeps its Bump Rationale (applied at publish)
  - A12: the bodies of #888 and #890 were not supplied; their tracked-in claims are confirmed only as open issues

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v8.16.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `7.577`
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

- `requested_review_gate`: 0.005s
- `cli_skill_surface_gate`: 5.635s
- `quality_command`: 1088.641s
- `fresh_checkout_probes_resume`: 14.174s
- `push_create_verify_release`: 794.260s
- `distinct_channel_verification`: 0.567s
- `published_notes_audit`: 0.459s
- `post_publish_install_refresh`: 7.577s
- `post_publish_installed_readback`: 1.098s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-11-05-v8.16.0-release-observer.json`.
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

- Bump: `8.15.0` -> `8.16.0` (`publish-current`).
> minor, not major: the release adds the opt-in Claude task-run executor and the --claude-model option and widens --grant-writable to Claude lanes, which the version policy names minor. One change can break a launcher: Codex lanes no longer inherit writable_roots from the operator's own Codex configuration, so a launcher that relied on it must pass the directory with --grant-writable. The version policy lists forced migration steps under major; this release departs from that line because the inherited grant was unintended ambient authority and closing it is a security fix. The notes state it under Security with the migration step.