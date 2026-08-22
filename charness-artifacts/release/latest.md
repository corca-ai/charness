# Release Surface Check
<!-- charness-release-state:prepared-awaiting-claims-review -->
Date: 2026-08-22

## Scope

Advanced `charness` toward release `6.2.2` (tag `v6.2.2`) through the repo-owned release helper.

## Current Version

- previous version: `6.2.1`
- target version: `6.2.2`
- git branch: `main`
- git remote: `origin`

## Verification

- `./scripts/run-quality.sh --release` passed before publish.
- `current_release.py` reported no version drift across 5 read surface(s) against target `6.2.2`, checked at `post-bump, pre-commit`.

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
- Retro artifact: `charness-artifacts/retro/2026-08-22-v6-2-2-release-auto-retro.md`.
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`.
- Surface hits: 1.
  - `checked-in-plugin-export`
- Path hits: 0.
- Evaluated changed paths: 36.
  - `.claude-plugin/marketplace.json`
  - `charness-artifacts/critique/2026-08-22-issue-closeout-critique.md`
  - `charness-artifacts/critique/2026-08-22-release-6-2-2-critique.md`
  - `charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md`
  - `charness-artifacts/issues/2026-08-21-current-requalification.md`
  - `charness-artifacts/issues/2026-08-21-repairs-that-carry-their-class-disposition-review.md`
  - `charness-artifacts/issues/2026-08-22-tracker-requalification.md`
  - `charness-artifacts/probe/2026-08-21-v6.2.1-release-observer.json`
  - `charness-artifacts/quality/sloc-inventory/latest.json`
  - `charness-artifacts/release-review/2026-08-21-v6.2.1-prepared-claims-review.json`
  - `charness-artifacts/release-review/2026-08-21-v6.2.1-prepared-claims-review.md`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/retro/2026-08-21-123706-packet.json`
  - `charness-artifacts/retro/2026-08-21-123706-packet.md`
  - `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`
  - `charness-artifacts/retro/2026-08-21-r2-semantic-packet-final.md`
  - `charness-artifacts/retro/2026-08-21-r3-delivery-review-final.md`
  - `charness-artifacts/retro/2026-08-21-v6-2-1-release-auto-retro.md`
  - `charness-artifacts/retro/2026-08-22-release-6-2-2-preparation-retro.md`
  - `charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md`
  - ... 16 more

## Real-Host Verification

- No configured release-time real-host proof trigger matched this slice.
- Evaluation scope: `evaluated`

## Real-Host Proof

- No configured release-time real-host proof trigger matched this slice.

## Review Proof

- Review proof: `charness-artifacts/critique/2026-08-22-release-6-2-2-critique.md`.

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

- `requested_review_gate`: 0.003s
- `cli_skill_surface_gate`: 1.912s
- `quality_command`: 176.795s
- `fresh_checkout_probes_initial`: 4.411s

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


## Record Qualifications

Added after three independent claims rounds returned `fail` on this record.
Findings are folded in here or repaired in the artifact each names, so this is
not a complete index of the rounds — the claims-review narrative under
`charness-artifacts/release-review/` is, and it is the DURABLE copy: the
post-publish step rewrites this file wholesale from its generated payload and
pushes it, so everything below survives publication only in the tagged blob and
in that narrative. `## Claims Review` above reads as pending until the binding
record is committed. Most items below are record-level; one discloses a shipped
code limitation and says so.

- **"no verdict change" is measured, not asserted.** The release critique
  recorded that the read establishing it had not been performed, and the Bump
  Rationale stated the conclusion anyway. The differential has since been run:
  the shipped module and `git show v6.2.1:` of the same path, called with
  identical injected dependencies over 400 constructed inputs (5 statuses x 8
  cadence shapes x 5 acceptance shapes x frame present/absent), comparing the
  `(applies, ok)` pair only — **0 divergences**. Evidence:
  `charness-artifacts/probe/2026-08-22-v6.2.2-cadence-verdict-differential.json`.
  **This is parent-authored evidence, not an independent observer's**, and the
  `reason` text changed deliberately and is outside the comparison.
- **"no version drift across 5 read surface(s)" counts surfaces read, not
  version values compared.** `current_release.py` compares three version-bearing
  surfaces against the packaging manifest; the fifth,
  `codex_marketplace_source_path`, carries a path and never a version.
  `.claude-plugin/marketplace.json` holds two version fields and the check reads
  one. All read `6.2.2` — no live drift — but the stated coverage is wider than
  the comparison.
- **The `--release` quality pass is bound to no commit, and every artifact
  written after it ships unvalidated by it.** The lane passed; `## Release Runtime`
  above records `quality_command: 176.795s`, and that line is the durable
  evidence. A claims round independently corroborated the same run, and the
  earlier failure the preparation retro describes, from the repo's rolling
  runtime-signals file — but that file is gitignored and its command table has
  since been overwritten, so the corroboration is recorded here as having
  happened and is no longer reproducible from it. That is the argument against
  citing it, made by the citation itself. The release record, the
  auto-retro, the differential probe, the amended critique, the amended
  `docs/handoff.md` and this section were all written after that lane ran. No
  count is given here because the set kept growing while it was being written —
  which is itself the reason a count would have been wrong.
- **This release ships a known over-fire that HARD-BLOCKS activation, and the
  refusal needs BOTH owners.** An earlier draft of this bullet said a cadence
  line naming a flag "without deferring is refused as contradictory". That is
  false and overshoots in the opposite direction from the defect the critique
  caught: `check` requires a flag-naming cadence line AND a `## User Acceptance`
  line demanding broad proof per slice. With no such acceptance line the result
  is `applies: true, ok: true`. When both are present AND the cadence line never
  defers for an earlier step — naming a flag solely to negate it, or solely for a
  terminal step — the refusal is the over-fire and the artifact is truthful. When
  the cadence line DOES defer earlier, the shape the achieve scaffold seeds, the
  same refusal is CORRECT and the acceptance line is what should change. The
  shipped payload leads with that distinction. 6.2.2 makes that
  refusal explain itself; it does not remove it.
- **The `#681` repair has never been verified on any installed copy.** The
  installed-6.2.1 evidence for `#681` specifically is reproduction of the DEFECT;
  other artifacts in this delta use installed-6.2.1 readbacks for other issues
  and other purposes, so this is a claim about `#681`, not about every installed
  reference in the set. Closing the loop requires replaying the reproduction against the
  installed `6.2.2` plugin on an `active` artifact carrying a soft-wrapped
  non-deferring cadence bullet. A `charness version` or `charness doctor`
  readback is not that branch.
- **`Evaluated changed paths: 36` is stale.** The differential probe JSON was
  added after that census was taken, so the delta is larger than the number the
  record states and the enumeration omits that path.
- **The release auto-retro asserts a publish that has not happened**, and
  records `session_id: "none"` while the preparation retro beside it records
  session `2026-08-22-b-release` with five score events. Both ship in this
  commit. The auto-retro is helper-generated and says in its own body that it
  does not cover the session; the preparation retro is the one that does.
- **`cli_skill_surface_gate` reports a runtime and no verdict.** Its 1.9s in
  `## Release Runtime` is not a pass — that value is recorded in a `finally`, so
  it is written whether the gate passed or raised. Nor is the quality runner's
  similarly-named `check-cli-skill-surface` row its verdict: that is a different
  label with its own elapsed value, produced by a different step. What
  establishes the verdict is structural — the gate shells out with `check=True`,
  so a non-zero exit aborts the prepare and no record is committed. This record
  existing is the evidence.
- **`docs/handoff.md` ships inside this release commit** and is the
  adapter-declared post-publish baton path, reconciled after publication. It
  deliberately names no commit id for this release: a document committed in a
  commit cannot name that commit, and an earlier repair here shipped an id that
  the subsequent amend orphaned.

## Bump Rationale

> Patch: repairs the cadence-owner payload's false denial of a line it parsed and discloses a known literal-match over-fire; no new capability, no verdict change, no flag or schema change.
