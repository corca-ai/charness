# Release Surface Check
Date: 2026-08-22

## Scope

Advanced `charness` toward release `6.3.0` (tag `v6.3.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.2.2`
- target version: `6.3.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 193.3s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release`).
- Version drift check: NOT recorded by this helper invocation, so this record makes no no-drift claim about packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.3.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.3.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.3.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (13061 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-eeebcd1cf202dc8ffe1bbc9f0e3112d1fd03bee7f9d729d5dbc0223113d9ce71`.
- Linked feedback ID: `feedback-dab30d7cba2598bed8bfebfa7bb94968cfe4ad75177b4e113d6225a314c7a2d0`.
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
- Retro artifact: `charness-artifacts/retro/2026-08-22-v6-3-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 10.
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/release/scripts/claims_review_scope.py`
  - `skills/public/release/scripts/publish_release_args.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_claims_review.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
- Evaluated changed paths: 120.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `.github/workflows/quality-core.yml`
  - `charness-artifacts/critique/2026-08-22-release-6-3-0-bundle.md`
  - `charness-artifacts/critique/round2-slices-a-b-post-change-packet.md`
  - `charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md`
  - `charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`
  - `charness-artifacts/probe/2026-08-22-changed-line-coverage-context-blowup.json`
  - `charness-artifacts/probe/2026-08-22-v6.2.2-installed-681-replay.json`
  - `charness-artifacts/probe/2026-08-22-v6.2.2-release-observer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-22-v6.2.2-prepared-claims-review.md`
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-prepared-claims-review.md`
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.json`
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/v6.3.0-notes.md`
  - `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`
  - ... 100 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-22-release-6-3-0-bundle.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: bounded-reviewer spawn with Read/Grep/Glob only; boundary window w-20260822T122619Z-1813341
- Review narrative: `charness-artifacts/release-review/2026-08-22-v6.3.0-round5-claims-review.md`.
- Verdict scope: 109 blocking path(s) gated this tag; 9 advisory path(s) (session narrative) were reviewed but did not.
- Advisory findings: 5 defect(s) recorded in the advisory scope and SHIPPED KNOWN-INACCURATE rather than repaired before this tag:
  - `charness-artifacts/release-review/2026-08-22-v6.3.0-prepared-claims-review.md`: ships stale: says UNPROVEN through round 4 and STOPPED, and carries superseded figures 79 paths / 191.5s
  - `charness-artifacts/goals/2026-08-22-claims-review-convergence-then-ship-6-3-0.md`: ships as an unshaped scaffold: Non-Goals, Slice Plan, Slice Log and verification sections empty or scaffold-identical
  - `charness-artifacts/critique/2026-08-22-release-6-3-0-bundle.md`: scope is f5211700a..HEAD (9 commits, 57 paths), so about half the shipped delta was never critiqued; disclosed in the notes
  - `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`: cross-artifact quantity drift is structurally unchecked; markers are per-file only, verified self-consistent within each file
  - `charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`: same per-file marker limit as the retro; issues-filed=6 agrees across both but nothing verifies that agreement

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.3.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `8.655`
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

- `requested_review_gate`: 0.012s
- `cli_skill_surface_gate`: 2.142s
- `quality_command`: 193.327s
- `fresh_checkout_probes_resume`: 4.421s
- `push_create_verify_release`: 174.561s
- `distinct_channel_verification`: 0.681s
- `published_notes_audit`: 0.410s
- `post_publish_install_refresh`: 8.655s
- `post_publish_installed_readback`: 1.472s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `6.3.0`.
- Versions claimed by the baton's routing sections: `6.2.2`, `6.3.0`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-22-v6.3.0-release-observer.json`.
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