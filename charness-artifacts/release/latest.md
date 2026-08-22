# Release Surface Check
Date: 2026-08-22

## Scope

Advanced `charness` toward release `6.2.2` (tag `v6.2.2`) through the repo-owned release helper.

## Current Version

- previous version: `6.2.1`
- target version: `6.2.2`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.2.2`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.2.2`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.2.2`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-b4ba42a50786efc5a8a2a5649e934b469921191d6e39651d010eb07114d4d1c5`.
- Linked feedback ID: `feedback-981f5c35807607df1b45bf973411d48d88c4d353e8bcd91dcf50d28b1d0f216b`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-22-v6-2-2-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 40.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-22-issue-closeout-critique.md`
  - `charness-artifacts/critique/2026-08-22-release-6-2-2-critique.md`
  - `charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`
  - `charness-artifacts/issues/2026-08-21-current-requalification.md`
  - `charness-artifacts/issues/2026-08-21-repairs-that-carry-their-class-disposition-review.md`
  - `charness-artifacts/issues/2026-08-22-tracker-requalification.md`
  - `charness-artifacts/probe/2026-08-21-v6.2.1-release-observer.json`
  - `charness-artifacts/probe/2026-08-22-v6.2.2-cadence-verdict-differential.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-21-v6.2.1-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-21-v6.2.1-prepared-claims-review.md`
  - `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-21-123706-packet.json`
  - `charness-artifacts/retro/2026-08-21-123706-packet.md`
  - `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`
  - `charness-artifacts/retro/2026-08-21-r2-semantic-packet-final.md`
  - `charness-artifacts/retro/2026-08-21-r3-delivery-review-final.md`
  - ... 20 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-22-release-6-2-2-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Three bounded read-only subagent rounds reviewed successive prepared records; all returned fail. Round 2 found three of round 1's repairs carrying the class they fixed. Round 3 found the post-publish step overwrites the release record wholesale, which is why this narrative exists. A durability gate then refused a citation to a gitignored rolling file whose data had already been overwritten.
- Review narrative: `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.2.2`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.259`
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

- `requested_review_gate`: 0.013s
- `cli_skill_surface_gate`: 2.099s
- `quality_command`: 171.761s
- `fresh_checkout_probes_resume`: 4.458s
- `push_create_verify_release`: 137.294s
- `distinct_channel_verification`: 0.538s
- `published_notes_audit`: 0.392s
- `post_publish_install_refresh`: 9.259s
- `post_publish_installed_readback`: 1.429s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `6.2.2`.
- Versions claimed by the baton's routing sections: `6.2.2`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-22-v6.2.2-release-observer.json`.
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

- Bump rationale: NOT recorded by this helper invocation. `version-policy.md` requires a stated rationale whenever the bump level is debatable; this record carries none, so the level above is an unexplained judgment call.