# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-23

## Scope

Advanced `charness` toward release `6.4.0` (tag `v6.4.0`) through the repo-owned release helper.

## Current Version

- previous version: `6.3.0`
- target version: `6.4.0`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` exited 0 in 173.0s at `post-bump, pre-commit`, measured by this helper (`./scripts/run-quality.sh --release`). **That figure is scoped to the tree enumerated under `Evaluated changed paths` below and to nothing else.** Repairs committed after it -- the prepared commit was amended across several bounded claims-review rounds -- are NOT covered by this number. They are covered by the `post-claims-review, pre-push` re-run the publish helper performs immediately before tagging, which HAS NOT RUN at the moment this snapshot is written; a failure there stops the tag, so a reader holding a tagged copy knows it passed, and a reader holding only this record does not. On the claims-review lane the helper deliberately does not rewrite this record before the tag, so the tagged snapshot carries this sentence as written; the record pushed to `main` after publication carries the pre-push figure instead.
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.4.0`, checked at `post-bump, pre-commit`.

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
- Retro artifact: `charness-artifacts/retro/2026-08-22-v6-4-0-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 2.
  - `checked-in-plugin-export`
  - `integrations-and-control-plane`
- Path hits: 0.
- Evaluated changed paths: 66. **A receipt of what the trigger was handed at `final_release_paths`, not an inventory of the shipped delta.** The claims-review rounds amended the prepared commit afterwards, so the shipped delta is larger — `charness-artifacts/release/v6.4.0-notes.md` sorts inside the window printed below and is absent from it. Whether re-evaluating over the larger delta would add a surface hit was not computed.
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
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md`
  - `charness-artifacts/retro/2026-08-22-v6-3-0-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-23-gate-by-property-four-slices-and-the-goal-committing-its-own-defect-twice.md`
  - `charness-artifacts/retro/lesson-ledger.json`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/lesson-session-receipts/2026-08-23-gate-by-property.json`
  - `charness-artifacts/retro/lesson-session-receipts/2026-08-23-gate-by-property.md`
  - ... 46 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-23-release-6-4-0-critique.md`.

## Claims Review

- Claims review: not yet performed AT THE MOMENT THIS SNAPSHOT IS WRITTEN -- THIS record is the subject of the pending independent review, and publication is stopped until that review is committed. Same property as the verification figure above, and the same reason: on the claims-review lane the helper does not rewrite this record before the tag, so the TAGGED copy carries this line verbatim while being false of the published release. A tag existing at all means the review was committed and the publish gates passed; the record pushed to `main` after publication carries the review's identity. Do not read this line off a tagged checkout as the state of the release.

## Requested Review Gate

- Requested-review gate status: `ok`.
- Configuration status: `advisory_only`.
- Policy: `advisory-only`.
- Configured command count: `0`.

## Install Refresh

- Post-publish install refresh: pending final publish verification.

## Release Runtime

- `requested_review_gate`: 0.003s
- `cli_skill_surface_gate`: 2.014s
- `quality_command`: 173.029s
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


## Bump Rationale

> minor, and the call is debatable so here is the tension. Most of this delta is repair -- a status token that repaired a four-day misdiagnosis, a discovery predicate that repaired an under-enumeration, and four gates that repaired greens claiming more coverage than they had -- which reads as patch. It goes minor because runtime_profile_lib.malformed_budget_profile_blocks is newly EXPORTED on a module that installs into consumer repos, and because a new operator-facing status token (UNMEASURED) is now taught in an installed reference. The export claim is measured, not asserted, and here is the command so a reader can falsify it: diff `git show v6.3.0:skills/public/quality/scripts/runtime_profile_lib.py | grep '^def '` against the same grep over the shipped file. It yields exactly one added name and it is that one. Not major, and the argument has to name the exit code that DID move rather than only the one that did not. check_skill_ownership_overlap's allowlist parser now requires the <reason> field that the format line, .agents/surfaces.json, and the installed portable-authoring.md all already declared required, so a repo holding a reasonless waiver whose overlap still exists goes from exit 0 to exit 2. One whose overlap is already gone stays at exit 0 and surfaces only in the new malformed_allowlist_lines field, which is why that field exists. It stays minor because that gate is decided consumer_facing: false, so no wired consumer contract breaks, and because the entry it now refuses was already invalid under three shipped declarations -- the code caught up to the docs rather than the reverse. Otherwise: nothing renamed, nothing removed, no invocation changed, and the one red-to-green class (an external grep for a FAIL status on a baseline abort) sits on a surface documented as non-portable behind an unchanged exit code. An earlier draft of this clause read as a whole-release no-exit-code-moved claim while the notes said in bold that one had; a bounded review caught the pair. Two corrections carried deliberately, because the failure mode they show is this release's own subject. First, an earlier draft named budgeted_label_union as the new export; it is not, it stands unchanged at v6.3.0 line 101, and this release's goal artifact says so. Second, an earlier draft called UNMEASURED a third status when the Status row already emits four tokens. Both were caught by the prepared-claims review, and in both the judgment was right while its stated reason was wrong.
