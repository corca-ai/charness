# Release Surface Check
Date: 2026-08-28

## Scope

Advanced `charness` toward release `7.0.0` (tag `v7.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.5.0`
- target version: `7.0.0`
- git branch: `release/v7.0.0-cutover-20260828`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 187.4s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release`).
- `current_release.py` reported no version drift across 5 read surface(s) against target `7.0.0`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v7.0.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v7.0.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v7.0.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (9158 body bytes).

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v6.5.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `fresh_checkout_probes`
  - `post_publish_baton_path`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes tests/quality_gates/test_release_backend.py::test_release_adapter_rejects_invalid_fresh_checkout_probes -q`
- Focused preflight execution: NOT recorded by this helper invocation; this record does not establish that the commands above ran.

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-27-v7-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 18.
- Evaluated changed paths: 2210.

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Remaining real-host checklist items, if any, still require explicit proof before full closeout.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class. Use `charness doctor` here and NOT `python3 scripts/doctor.py --repo-root .`, which is the external-tool doctor and reports nothing about managed-checkout or plugin-root skew; discharging this item with it would record a verification that measured none of what the item is about.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: blocking-install-needed` with an actionable install `next_step`, and that the command itself exits 1. Blocking is CORRECT here: nose.json `degradation.when_missing` records that a missing nose makes the quality `doc-duplicates` phase fail closed with no fallback, and `integrations/tools/README.md` permits `doctor_policy: advisory` only where the consuming workflow has a degraded path. Do NOT read this verdict from `charness doctor`, which is the managed-install doctor and returns 0 regardless of external-tool state; the external-tool verdict comes from `charness tool doctor` or `python3 scripts/doctor.py --repo-root .`. Quoted because the unquoted form parses as a mapping under standard YAML.
- Run `charness tool install nose --dry-run --detail` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata. `--detail` is REQUIRED, not optional polish; the summary response level prints neither the installer command nor the release metadata this item asks you to confirm, so the plain `--dry-run` form cannot discharge it.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --detail` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Status

- Review proof: not recorded in this helper invocation.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-28-v7.0.0-claims-review.json`.
- Claims review verdict: `unproven` -- the distinct-observer property was NOT established for this release.
- This is a recorded absence, not a passing review: no observer independent of the release preparer is claimed to have reviewed the claims in this record.
- Recorded signal: Prior unnamed bounded release-review spawns remained running without returning a result or artifact; the current sidecars did not review this prepared release record.
- Review narrative: none. A `pass` carries the product of its review; this does not.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v7.0.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `12.662`
- Stdout tail: `gin-install-succeeded
  delivery_verified: true
  verification: same-version-content-readback
  source_content_sha256: 35bdfd5f8fc8a549c59f09c40ea02f4e1c4e82da5b74b8994767143404ab01cb
  cache_content_sha256: 35bdfd5f8fc8a549c59f09c40ea02f4e1c4e82da5b74b8994767143404ab01cb
  post_refresh_cache_manifest_version: 6.5.0
  post_refresh_drift: false
  post_refresh_host_status: installed
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
  source: codex_host_guidance`
- Stderr tail: `STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.010s
- `cli_skill_surface_gate`: 1.957s
- `quality_command`: 187.358s
- `fresh_checkout_probes_resume`: 4.259s
- `push_create_verify_release`: 177.750s
- `distinct_channel_verification`: 0.566s
- `published_notes_audit`: 0.482s
- `post_publish_install_refresh`: 12.662s
- `post_publish_installed_readback`: 1.400s
- `release_observer`: 0.001s
- `issue_closeout`: 0.000s

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-27-v7.0.0-release-observer.json`.
- Installed readback disposition: `version-mismatch`.
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

> Major release: the execution-contract cutover removes obsolete ceremony, unifies owned runtime isolation, and changes the default consumer workflow; release surfaces and operator instructions are updated together.