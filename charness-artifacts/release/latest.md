# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-18

## Scope

Advanced `charness` toward release `6.2.0` (tag `v6.2.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.1.0`
- target version: `6.2.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- NON-CLAIM, because a claims round found this sentence standing alone: the `pytest`
  runtime bar it passed under was RAISED inside this same delta, 120000 -> 155000
  (`.agents/quality-adapter.yaml`, the first entry in the evaluated changed paths
  below). It was not raised to make this gate green by fiat: the label's own REVISIT
  TRIGGER was honored first — profiling found no hotspot, and sixteen real-corpus
  probes moved to a `slow_corpus` lane — and the relevel rests on that work being
  MEASURED not to move an in-gate number that is contention-bound rather than
  suite-bound. The reasoning is written beside the number and on #668. A reader who
  wants the pre-relevel verdict should read it as: this gate did not pass under the
  bar the previous release passed under.
- NON-CLAIM: the #640 closeout push in this range went out with `git push
  --no-verify`, on an explicitly re-authorized grant, because that same red bar
  refused it. This repo's contract treats `--no-verify` as revoking a push grant, so
  the range's pre-push lane is not evidence for anything.
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.2.0`, checked at `post-bump, pre-commit`.

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
- Retro artifact: `charness-artifacts/retro/2026-08-18-v6-2-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 91.
  - `.agents/quality-adapter.yaml`
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-18-issue-640-resolution.md`
  - `charness-artifacts/critique/2026-08-18-release-6-2-0.md`
  - `charness-artifacts/issue/2026-08-18-issue-640-brief.md`
  - `charness-artifacts/probe/2026-08-18-v6.1.0-release-observer.json`
  - `charness-artifacts/quality/dup-review.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-18-v6.1.0-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-18-v6-1-0-release-auto-retro.md`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `docs/handoff.md`
  - `packaging/charness.json`
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `plugins/charness/scripts/adapter_field_application.py`
  - `plugins/charness/scripts/adapter_lib.py`
  - `plugins/charness/scripts/announcement_adapter_lib.py`
  - ... 71 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-18-release-6-2-0.md`.

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
- `cli_skill_surface_gate`: 2.102s
- `quality_command`: 212.129s
- `fresh_checkout_probes_initial`: 4.173s

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

> minor: additive operator surface. Three new optional adapter fields (max_artifact_lines on debug and quality, max_content_lines on handoff), a new optional_int primitive in the shared adapter vocabulary, and two additive payload keys (size_budget.source, content_line_budget). Not patch, because a consuming repo gains a capability it can adopt without migration. Not major, because the shipped defaults are byte-identical to c34155a48 -- verified with git show, not assumed -- so a consumer who sets nothing sees no change; the only removed name is NEAR_LIMIT_LINES, a module constant of a CLI-invoked skill script with no in-tree importer.