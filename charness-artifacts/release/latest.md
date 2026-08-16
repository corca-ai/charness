# Release Surface Check
Date: 2026-08-16

## Scope

Advanced `charness` toward release `6.0.0` (tag `v6.0.0`) through the repo-owned release helper.

## Current Version

- previous version: `5.2.0`
- target version: `6.0.0`
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
- GitHub release record: verified URL `https://github.com/corca-ai/charness/releases/tag/v6.0.0`
- public release surface verification: verified
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: verified by the release backend.

## Distinct-Channel Verification

- Rung-2 distinct-channel verdict: `confirmed` via `https-fetch` (a channel distinct from `gh release view`).
- Response content checked for: `v6.0.0`
- What this confirms: public-page-reachable-and-names-the-tag
- What it does NOT confirm: that a GitHub RELEASE exists for this tag — the same page returns 200 for a pushed tag with no release, and the tag is pushed before the release is created
- Observer identity: unauthenticated-http (credential-free; same host/process as publisher)
- Channel URL: `https://github.com/corca-ai/charness/releases/tag/v6.0.0`
- HTTP status: `200`
- Rung-1 floor: a per-surface verdict is recorded (presence), so issue closeout was not silent; the honesty of this verdict is the human rung-2 disposition review.

## Published Notes Audit

- Published release body audit: `clean` (advisory; never blocks a publish).
- No mutable source-tree pointers found (31390 body bytes).

## Lifecycle Usage Capture

- Lifecycle capture status: `appended`.
- Local telemetry pair appended: `True`.
- Delivery episode ID: `episode-06c63ee10309de8c1003745ba0ecc2287316037fb877c070a5fe5421ed271c70`.
- Linked feedback ID: `feedback-1654773cf35d82de2327da855d018a9548f96593d83b7129846f240143ebcb56`.
- Capture error count: `0`.
- Non-claim: objective lifecycle capture is not human approval or general satisfaction evidence.

## Release Adapter Preflight

- Release adapter focused preflight status: `required`.
- Reason: release adapter changed in the release delta; focused adapter preflight is required before release mutation
- Previous release ref: `refs/tags/v5.2.0`
- Adapter paths in release delta:
  - `.agents/release-adapter.yaml`
- Changed adapter fields:
  - `cli_skill_surface_probe_commands`
  - `fresh_checkout_probes`
  - `real_host_checklist`
- Focused preflight commands:
  - `python3 skills/public/release/scripts/resolve_adapter.py --repo-root .`
  - `pytest tests/quality_gates/test_release_real_host.py -q`
  - `pytest tests/quality_gates/test_release_backend.py::test_release_adapter_preserves_fresh_checkout_probes tests/quality_gates/test_release_backend.py::test_release_adapter_rejects_invalid_fresh_checkout_probes -q`

## Retro Trigger Evaluation

- Triggered: `True`.
- Evaluated at: `final_release_paths`.
- Input mode: `explicit_paths`.
- Reason: Changed surfaces hit configured install/update/support/export/discovery retro triggers.
- Closeout status: `written`.
- Retro artifact: `charness-artifacts/retro/2026-08-16-v6-0-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 42.
  - `README.md`
  - `docs/host-packaging.md`
  - `scripts/capability_catalog.py`
  - `scripts/capability_catalog_sources.py`
  - `skills/public/release/SKILL.md`
  - `skills/public/release/references/adapter-contract.md`
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/release/references/real-host-proof.md`
  - `skills/public/release/scripts/audit_public_release_narrative.py`
  - `skills/public/release/scripts/bump_version.py`
  - `skills/public/release/scripts/check_fresh_checkout_probes.py`
  - `skills/public/release/scripts/check_real_host_proof.py`
  - `skills/public/release/scripts/check_requested_review_gate.py`
  - `skills/public/release/scripts/current_release.py`
  - `skills/public/release/scripts/generate_release_notes.py`
  - `skills/public/release/scripts/lint_release_narrative.py`
  - `skills/public/release/scripts/plan_release_run.py`
  - `skills/public/release/scripts/plan_release_run_packets.py`
  - `skills/public/release/scripts/publish_release_adapter_preflight.py`
  - `skills/public/release/scripts/publish_release_artifact_sections.py`
  - `skills/public/release/scripts/publish_release_claims_review.py`
  - `skills/public/release/scripts/publish_release_cli.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_execute.py`
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/publish_release_narrative_gate.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
  - `skills/public/release/scripts/publish_release_resume_state.py`
  - `skills/public/release/scripts/publish_release_retro.py`
  - `skills/public/release/scripts/publish_release_runtime.py`
  - `skills/public/release/scripts/release_claim_surfaces.py`
  - `skills/public/release/scripts/release_issue_closeout_artifact.py`
  - `skills/public/release/scripts/release_notes_claims.py`
  - `skills/public/release/scripts/release_observer.py`
  - `skills/public/release/scripts/resolve_adapter.py`
  - `skills/support/markdown-preview/scripts/check_glow_backend.py`
  - `skills/support/markdown-preview/scripts/render_markdown_preview.py`
  - `skills/support/web-fetch/scripts/acquire_public_url.py`
  - `skills/support/web-fetch/scripts/classify_fetch_response.py`
  - `skills/support/web-fetch/scripts/route_public_fetch.py`
- Evaluated changed paths: 1335.
  - `.agents/command-dominance.yaml`
  - `.agents/inference-interpretation-surfaces.json`
  - `.agents/quality-adapter.yaml`
  - `.agents/release-adapter.yaml`
  - `.agents/retro-adapter.yaml`
  - `.agents/surfaces.json`
  - `.claude-plugin/marketplace.json`
  - `.githooks/pre-push`
  - `.github/workflows/quality-core.yml`
  - `.gitignore`
  - `AGENTS.md`
  - `README.md`
  - `charness`
  - `charness-artifacts/audit/2026-08-15-s5-umbrella-guards.md`
  - `charness-artifacts/audit/2026-08-16-sc16-sc19-consumer-surface.md`
  - `charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.json`
  - `charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.md`
  - `charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md`
  - `charness-artifacts/critique/2026-08-14-current-contract-cleanup-round2-packet.json`
  - `charness-artifacts/critique/2026-08-14-current-contract-cleanup-round2-packet.md`
  - ... 1315 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Adapter-declared maintainer install-refresh proof was executed by the release helper for installed-vs-repo skew.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
- Executed maintainer install refresh: `charness update` (status `refreshed`, return code `0`).
- Remaining real-host checklist items, if any, still require explicit proof before full closeout.
- On THIS maintainer/dev machine, run `charness update` after publish so the installed plugin at `~/.agents/src/charness` stays `== repo`, then re-verify with `charness doctor` (or `python3 scripts/doctor.py --repo-root .`) and a cited-check == repo-gate spot check; record the `charness update` output as executed proof. This closes the installed-vs-repo version-skew class.
- Run `charness tool doctor nose --no-write-locks` before installing `nose` and confirm missing `nose` reports `doctor_disposition: advisory-install-needed`, not a blocking install failure.
- Run `charness tool install nose --dry-run` and confirm it points at the upstream `nose-cli-installer.sh` release path and latest `v0.4.0` or newer metadata.
- Install `nose` through the manifest-supported path (`charness tool install nose`, the upstream release installer, or `brew install corca-ai/tap/nose`), then verify `nose --version`.
- Re-run `charness tool doctor nose --no-write-locks` and confirm the binary is detected on PATH.
- Run `charness tool sync-support nose` and confirm it reports no materialized support skill requirement; `nose` is an integration-only validation binary consumed by the public `quality` skill.
- Run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --detail` once with `nose` available and confirm findings, if any, are advisory refactoring candidates rather than standing quality failures.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md`.

## Claims Review

- Claims review record: `charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.json`.
- Claims review verdict: `pass`.
- Observer distinctness: `separate-agent-context`.
- Recorded signal: Each round ran as a separately spawned bounded-reviewer subagent whose envelope exposed only Read, Grep and Glob; each independently reported that Bash, Edit, Write and Agent were absent, and each returned findings the preparer had not written. Round 1 returned unproven on a false claim the preparer authored, and rounds 2 and 3 each found further defects in the preparer's repairs, which a same-agent reread of the preparer's own prose could not have produced.
- Review narrative: `charness-artifacts/release-review/2026-08-16-v6.0.0-prepared-claims-review.md`.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Post-Publish Proof

- Public release check: `gh release view v6.0.0`.

## Install Refresh

- Post-publish install refresh status: `refreshed`.
- Command: `charness update`
- Return code: `0`
- Elapsed seconds: `19.783`
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

- `requested_review_gate`: 0.006s
- `cli_skill_surface_gate`: 1.911s
- `quality_command`: 134.426s
- `fresh_checkout_probes_resume`: 4.447s
- `push_create_verify_release`: 127.752s
- `distinct_channel_verification`: 0.668s
- `published_notes_audit`: 0.399s
- `post_publish_install_refresh`: 19.783s
- `post_publish_installed_readback`: 1.589s
- `release_observer`: 0.000s
- `issue_closeout`: 0.000s

## Baton Reconcile

- Baton reconcile observation: `observed-current` for `docs/handoff.md`.
- Just-published version: `6.0.0`.
- Versions claimed by the baton's routing sections: `6.0.0`.
- This is an observation, not completion: the populated record forces the reconcile question; the release critique/retro reviewers judge the disposition.

## Release Observer Record

- Durable observer record: `charness-artifacts/probe/2026-08-16-v6.0.0-release-observer.json`.
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
