# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-22

## Scope

Advanced `charness` toward release `6.3.0` (tag `v6.3.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.2.2`
- target version: `6.3.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 212.0s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release`).
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.3.0`, checked at `post-bump, pre-commit`.

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

- Release adapter focused preflight status: `not_required`.
- Reason: release adapter did not change in the release delta
- Focused preflight commands: none planned.
- Focused preflight execution: `not_run`.
- This is a recorded absence, not a passing preflight: no focused adapter check is claimed to have completed successfully for this release.
  - Reason: focused preflight status is `not_required`; no commands were required

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
- Evaluated changed paths: 117.
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
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/release/v6.3.0-notes.md`
  - `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`
  - `charness-artifacts/retro/2026-08-22-v6-2-2-release-auto-retro.md`
  - `charness-artifacts/retro/lesson-ledger.json`
  - ... 97 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-22-release-6-3-0-bundle.md`.

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

- `requested_review_gate`: 0.004s
- `cli_skill_surface_gate`: 1.942s
- `quality_command`: 211.979s
- `fresh_checkout_probes_initial`: 4.470s

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


## Bump Rationale

> minor, and the major case was argued rather than assumed. Three shipped behaviours refuse input they previously accepted, which is what makes the level debatable and this sentence mandatory under the policy's own Guardrail. None reaches a major trigger, but each is stated with its real blast radius rather than a flat denial. (1) check_spec_evidence_durability is classified consumer_facing:false in the consumer validator catalog and is wired from this repo's own run-quality.sh and .agents/surfaces.json, so its 2339 newly-scanned docs are charness's own history, not a consumer's. (2) The hollow-section refusal reaches the exit code ONLY under --pursue-ready, never the default check_goal path, and skips every non-shaping status. It DOES redden one existing population: draft is a shaping status and this floor has no date grandfather, unlike the backlog floor beside it, so a pre-existing draft goal whose shaping sections are empty or still scaffold-identical passed before and exits 1 now. That is the reported defect and the report came from a consumer repo. Nothing re-grades a corpus; the refusal lands the next time that draft is pursued and names the N/A escape in its own text. The remedy is per-artifact and the level stays minor because no invocation, id, or install surface changes. (3) The claims-review schema moves v2 to v3. This IS a shipped consumer surface, not a maintainer-only one: the release skill ships in the checked-in export and the prepared stop is unconditional, so a consumer who updates and resumes a prepared release must author a v3 record carrying review_scope and advisory_findings. It is additive to a flow no consumer can be mid-way through at update time, which is why it is minor rather than major. Nothing renames a public skill or package id, changes an invocation, or removes an install surface. The node-test reporter and the superseded status are additive, and the cadence change strictly narrows an existing over-fire, so 6.3.0 refuses fewer artifacts than 6.2.2 did on every surface except the hollow draft case named above.