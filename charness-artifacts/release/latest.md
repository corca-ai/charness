# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
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

## Release State

- local release mutation: complete
- branch/tag push: pending independent claims review.
- GitHub release record: pending independent claims review before creation
- public release surface verification: pending independent claims review
- audit narrative: durable record written to `charness-artifacts/release/latest.md` and committed with this slice

## Public Release Verification

- GitHub release publication: expected after branch/tag push; not verified yet.

## Lifecycle Usage Capture

- Lifecycle capture status: not recorded by this helper invocation.

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
- Evaluated changed paths: 1332.
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
  - ... 1312 more

## Real-Host Verification

- Release-time real-host verification was triggered for this slice.
- Real-host checklist items remain open until their executed proof is recorded.

## Real-Host Proof

- Release-time real-host proof is required for this slice.
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

- Claims review: not yet performed -- THIS record is the subject of the pending independent review, and publication is stopped until that review is committed.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.002s
- `cli_skill_surface_gate`: 2.019s
- `quality_command`: 138.866s
- `fresh_checkout_probes_initial`: 4.430s

## Baton Reconcile

- Baton reconcile observation: not recorded by this helper invocation.

## Fresh Checkout Probes

- Fresh-checkout probe status: passed.
- `./charness --help >/dev/null`
- `./charness goal check --help >/dev/null`
- `python3 scripts/doctor.py --repo-root . --skip-release-probe >/dev/null`
- `python3 scripts/closeout_bundle.py --help >/dev/null`
- `python3 scripts/validate_retro_handoff_wiring.py --help >/dev/null`

## Issue Closeout

- Issue closeout verification: pending or not requested.

## User Update Steps

- Run `charness update` to install the latest published Charness release.
- Read the GitHub release notes for release-specific behavior changes, migrations, or rollback notes.
