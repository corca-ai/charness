# Release Surface Check
Date: 2026-08-26

## Scope

Advanced `charness` toward release `6.5.0` (tag `v6.5.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.4.1`
- target version: `6.5.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 348.7s at `post-claims-review, pre-push`, measured by this helper (`./scripts/run-quality.sh --release`).
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.5.0`, checked at `post-claims-review, pre-push`.
- initial release push carried the release branch update and tag from the release helper.
- post-publish artifact push recorded the verified public release state on the release branch.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.5.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.5.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.5.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `unauthored` (advisory; never blocks a publish).
- The published body carries no authored notes (81 body bytes) — this release shipped with a generated changelog line and nothing else. `gh release edit` is the remedy; the release itself is unaffected.
- Disposition reason: published body carries no authored notes (generated changelog line only); `gh release edit` is the remedy

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
- Retro artifact: `charness-artifacts/retro/2026-08-25-v6-5-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 14.
  - `README.md`
  - `docs/host-packaging.md`
  - `scripts/capability_catalog.py`
  - `scripts/capability_catalog_resolver.py`
  - `skills/public/release/SKILL.md`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_post_create.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
  - `skills/public/release/scripts/publish_release_verification_sections.py`
  - `skills/public/release/scripts/publish_release_verification_state.py`
- Evaluated changed paths: 616.
  - `.agents/cli-side-effect-probes.json`
  - `.agents/command-docs.yaml`
  - `.agents/command-registry.json`
  - `.agents/quality-adapter.yaml`
  - `.agents/surfaces.json`
  - `.agents/t-events-adapter.yaml`
  - `.agents/usage-episodes-adapter.yaml`
  - `.charness/lesson-lanes/round2-actual/receipt.json`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-push`
  - `.gitignore`
  - `AGENTS.md`
  - `README.md`
  - `charness`
  - `charness-artifacts/capability-catalog/latest.json`
  - `charness-artifacts/capability-catalog/latest.md`
  - `charness-artifacts/critique/2026-08-06-041231-packet.json`
  - `charness-artifacts/critique/2026-08-06-041231-packet.md`
  - `charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md`
  - `charness-artifacts/critique/2026-08-25-2026-08-25-715-721-final.md`
  - ... 596 more

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

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-26-4-round-reduction-first-verification-follow-up-for-the-6-4-1-to-6-5-0-release.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-26-v6.5.0-claims-review.json`.
- Claims review verdict: `unproven` -- the distinct-observer property was NOT established for this release.
- This is a recorded absence, not a passing review: no observer independent of the release preparer is claimed to have reviewed the claims in this record.
- Recorded signal: claims-review agent delivery timed out twice; no independent claims-review result was delivered
- Review narrative: none. A `pass` carries the product of its review; this does not.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.5.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `11.034`
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
STEP: source checkout code differs from the running CLI; re-executing the checkout's CLI so the run matches its scripts
STEP: refreshing source checkout
STEP: refreshing install surface
STEP: refreshing Codex host cache
DONE: update complete`

## Release Runtime

- `requested_review_gate`: 0.011s
- `cli_skill_surface_gate`: 2.144s
- `quality_command`: 348.724s
- `fresh_checkout_probes_resume`: 4.517s
- `push_create_verify_release`: 322.576s
- `distinct_channel_verification`: 0.491s
- `published_notes_audit`: 0.485s
- `post_publish_install_refresh`: 11.034s
- `post_publish_installed_readback`: 1.534s
- `release_observer`: 0.009s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `stale` for `docs/handoff.md`.
- Just-published version: `6.5.0`.
- Versions claimed by the baton's routing sections: `6.4.1`.
- RECONCILE REQUIRED: Reconcile `docs/handoff.md` (its `## Current State` / `## Next Session` routing sections) to the just-published `6.5.0`, or record an explicit n/a disposition in the release record, before ending the session.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-25-v6.5.0-release-observer.json`.
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

> minor: additive reduction-first verification and release-claim honesty capability; existing callers retain their invocation and payload shapes