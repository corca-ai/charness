# Release Surface Check
Date: 2026-08-23

## Scope

Advanced `charness` toward release `6.4.0` (tag `v6.4.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.3.0`
- target version: `6.4.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 171.6s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release`).
- Version drift check: NOT recorded by this helper invocation, so this record makes no no-drift claim about packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.4.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.4.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.4.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (16509 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-08bda5ddcb12ab89f9ac672a3bcab27f9b61cad21e752745b1871249f9dae2c7`.
- Linked feedback ID: `feedback-afba2ae051e406f2af08148ed99966b7f2b69a919963c2ae396d7ed46d7fa6d7`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-23-v6-4-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 1.
  - `skills/public/release/scripts/plan_release_run.py`
- Evaluated changed paths: 85.
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/mutation-tests.yml`
  - `.github/workflows/quality-core.yml`
  - `charness-artifacts/critique/2026-08-23-release-6-4-0-critique.md`
  - `charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md`
  - `charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`
  - `charness-artifacts/goals/2026-08-24-close-the-scans-this-run-taught-us-to-read.md`
  - `charness-artifacts/probe/2026-08-22-v6.3.0-release-observer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.json`
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.md`
  - `charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.json`
  - `charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/v6.4.0-notes.md`
  - `charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md`
  - `charness-artifacts/retro/2026-08-22-v6-3-0-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-22-v6-4-0-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-23-gate-by-property-four-slices-and-the-goal-committing-its-own-defect-twice.md`
  - ... 65 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-23-release-6-4-0-critique.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Two bounded read-only subagents ran round 12 in separate contexts; the claims lens returned pass on the two blocking documents and the code lens returned BLOCK on two defects the preparer had not seen, including one the claims lens found independently.
- Review narrative: `charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.md`.
- Verdict scope: 73 blocking path(s) gated this tag; 10 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 4 defect(s) recorded in the advisory scope and SHIPPED KNOWN-INACCURATE rather than repaired before this tag:
  - SHOULD-FIX (unrepaired, filed): summarize()'s new_doc_family_count is pinned only on the zero arm, so a mistyped key would report zero new doc families on a run that hard-blocks on doc drift.
  - SHOULD-FIX (unrepaired, filed): dup_ratchet_edit_advisory.in_ratchet_scope reads scope_paths with no normalization, so a consumer scoped ['.'] gets permanent silence from the edit-time advisory.
  - NOTE (unrepaired, filed): the published 'admits X/Y' numerator has no test asserting its value.
  - GAP (recorded, not closed): the second bounded review round over this slice's repaired proof surfaces did not run, including the dup_ratchet_scope module split.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.4.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.703`
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
- `cli_skill_surface_gate`: 2.059s
- `quality_command`: 171.601s
- `fresh_checkout_probes_resume`: 4.304s
- `push_create_verify_release`: 145.346s
- `distinct_channel_verification`: 0.986s
- `published_notes_audit`: 0.373s
- `post_publish_install_refresh`: 9.703s
- `post_publish_installed_readback`: 1.515s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `6.4.0`.
- Versions claimed by the baton's routing sections: `6.2.2`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.4.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-23-v6.4.0-release-observer.json`.
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