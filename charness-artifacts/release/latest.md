# Release Surface Check
Date: 2026-08-06

## Scope

Advanced `charness` toward release `3.3.0` (tag `v3.3.0`) through the repo-owned release helper.

## Current Version

- previous version: `3.2.0`
- target version: `3.3.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across packaging and generated install surfaces.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v3.3.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v3.3.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v3.3.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (3439 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-289c1d7ed74df70be32280aacfd6c8708e1b98005260c62d56c3b57a296d0cfe`.
- Linked feedback ID: `feedback-fb5ac9b9721625650f6bbaffa0f61e27bc4764c8f54559a6c66c244c54764870`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none executed.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-06-v3-3-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 6.
  - `skills/support/web-fetch/scripts/acquire_public_url.py`
  - `skills/support/web-fetch/scripts/acquire_public_url_io.py`
  - `skills/support/web-fetch/scripts/classify_fetch_response.py`
  - `skills/support/web-fetch/scripts/markdown_negotiation_stage.py`
  - `skills/support/web-fetch/scripts/route_public_fetch.py`
  - `skills/support/web-fetch/scripts/route_stage_catalog.py`
- Evaluated changed paths: 605.
  - `.agents/quality-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-04-053842-packet.json`
  - `charness-artifacts/critique/2026-08-04-053842-packet.md`
  - `charness-artifacts/critique/2026-08-04-065640-packet.json`
  - `charness-artifacts/critique/2026-08-04-065640-packet.md`
  - `charness-artifacts/critique/2026-08-04-070908-packet.json`
  - `charness-artifacts/critique/2026-08-04-070908-packet.md`
  - `charness-artifacts/critique/2026-08-04-071431-packet.json`
  - `charness-artifacts/critique/2026-08-04-071431-packet.md`
  - `charness-artifacts/critique/2026-08-04-071725-packet.json`
  - `charness-artifacts/critique/2026-08-04-071725-packet.md`
  - `charness-artifacts/critique/2026-08-04-110830-packet.json`
  - `charness-artifacts/critique/2026-08-04-110830-packet.md`
  - `charness-artifacts/critique/2026-08-04-111122-packet.json`
  - `charness-artifacts/critique/2026-08-04-111122-packet.md`
  - `charness-artifacts/critique/2026-08-04-111233-packet.json`
  - `charness-artifacts/critique/2026-08-04-111233-packet.md`
  - `charness-artifacts/critique/2026-08-04-111554-packet.json`
  - ... 585 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Remaining real-host checklist items, if any, still require explicit proof before full closeout.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root . --json`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/release-3-3-0-prepublish.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v3.3.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `9.809`
- Stdout tail: `  action: refresh
  method: codex-app-server-plugin-install
  reason: plugin-install-succeeded
codex_host_guidance:
  status: installed
  manual_action_required: false
  message: Codex host install markers are present. Start a new Codex session to load
    charness.
claude_host_guidance:
  status: installed
  manual_action_required: false
  message: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
host_next_steps:
  codex: Codex host install markers are present. Start a new Codex session to load
    charness.
  claude: Claude host install markers are present. Restart Claude Code to load or
    refresh charness.
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

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 1.872s
- `quality_command`: 81.944s
- `fresh_checkout_probes_initial`: 3.711s
- `fresh_checkout_probes_after_amend`: 3.682s
- `push_create_verify_release`: 60.174s
- `distinct_channel_verification`: 0.603s
- `published_notes_audit`: 0.511s
- `post_publish_install_refresh`: 9.809s
- `post_publish_installed_readback`: 1.367s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Remote CI Verification

- Remote `main` readback: `c86d13298cc70f9eab7a4ea249eeb27f58e16407`.
- GitHub Actions Quality Core run: `31087834647` completed with `success` on
  the post-publish verification commit.
- Jobs independently read back as successful: `Core deterministic gates` and
  `Changed-line mutation coverage (push/PR mirror)`.
- Tag `v3.3.0` remains at release commit `7eed13ec9b819e6d581ea08ea244820579c08935`;
  the post-publish verification commit is on `main` after the tag.
- Observer channel: GitHub Actions API readback, distinct from the release
  helper's push exit code.

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `3.3.0`.
- The baton's routing sections now claim the published `3.3.0` release.
- Reconciled in `docs/handoff.md`; future release or tag work still requires its own gated phase.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-06-v3.3.0-release-observer.json`.
- Installed readback disposition: `observed`.
- Verdict ownership: this record embeds `distinct_channel_verification`; it does not declare a second release-success verdict.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --json --skip-release-probe >/dev/null`

## Issue Closeout

- Issue closeout verification: `not_requested`.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
