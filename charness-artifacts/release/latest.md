# Release Surface Check
Date: 2026-08-25

## Scope

Advanced `charness` toward release `6.4.1` (tag `v6.4.1`) through the repo-owned release helper.

## Current Version

- previous version: `6.4.0`
- target version: `6.4.1`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 200.0s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release`).
- Version drift check: NOT recorded by this helper invocation, so this record makes no no-drift claim about packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.4.1`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.4.1`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.4.1`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-b659c60ce09b2e6a25bd8a1a95e723602d1b26127a8c6e8b42d2c9c992ceb196`.
- Linked feedback ID: `feedback-97868096b10b5db98ffef12a8bb0f3d4610c316b3db7a629abb633343dc7ca2f`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-24-v6-4-1-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 220.
  - `.charness/release-quality-receipt.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-file-backed-work.md`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.md`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json`
  - `charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.json`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.md`
  - `charness-artifacts/critique/2026-08-24-external-worker-capability-round2-resolution.md`
  - `charness-artifacts/critique/2026-08-24-issue-689-resolution-critique.md`
  - ... 200 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-25-release-6-4-1.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-25-v6.4.1-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Independent read-only claims observer verified the prepared record, version surfaces, typed quality receipt, fresh-checkout probes, packaging, pointer freshness, and immutable v6.4.0..924c7f5d619f delta.
- Review narrative: `charness-artifacts/release-review/2026-08-25-v6.4.1-claims-review.md`.
- Verdict scope: 171 blocking path(s) gated this tag; 47 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 1 defect(s) recorded in the advisory scope and SHIPPED KNOWN-INACCURATE rather than repaired before this tag:
  - The dated release critique narrative is advisory session scope; revalidation after the final release mutation reports stale declared inputs, while the prepared release record claims only its own pre-mutation critique binding.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.4.1`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `10.469`
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
- `cli_skill_surface_gate`: 2.135s
- `quality_command`: 199.993s
- `fresh_checkout_probes_resume`: 4.282s
- `push_create_verify_release`: 168.751s
- `distinct_channel_verification`: 0.508s
- `published_notes_audit`: 0.438s
- `post_publish_install_refresh`: 10.469s
- `post_publish_installed_readback`: 1.456s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `6.4.1`.
- Versions claimed by the baton's routing sections: `6.2.2`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.4.1`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-24-v6.4.1-release-observer.json`.
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

> patch, not minor: this release fixes validation, identity, diagnostic, and packaging/consumer-friction paths without adding or changing a public command or install surface.