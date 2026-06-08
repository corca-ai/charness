# Retro: #337 structural-follow-up destination floor (rung 1e)

Date: 2026-06-08

## Context

Goal `charness-artifacts/goals/2026-06-08-retro-disposition-structural-followup-classification.md`
(#337): make the waste-retro disposition gate classify a structural-follow-up
*destination* per transferable waste item — a presence/form-enum-only floor (rung
1e) plus a fresh-eye reviewer mandate — so "recorded in recent-lessons" can no
longer be mistaken for a structural fix. Three slices: rung 1e + mandate (code);
one shared destination vocabulary (prose); bundle proof + closeout. Bundle of 4
commits (`3dc8e79c`, `e3dbd266`, `101c1f33`, + this closeout) on top of
`origin/main` base `281fc373`.

## Waste

- **The in-package issue-anchor regression (the sharp one).** Slice 1 added a
  `(#337)` traceability anchor to the in-package script
  `goal_artifact_disposition.py`. `validate_skill_ergonomics` scans the WHOLE
  skill package (keyed by SKILL.md), so the anchor tripped
  `portable_package_issue_anchor` — even though SKILL.md itself had no anchor.
  Caught by running the cheap structural sweep myself before commit (the
  pre-commit hook also owns it); cost one re-edit + re-sync. The fresh-eye Slice-1
  reviewer missed it (it optimized the length angle, which was a non-issue).
- **Piped exit-code misread.** I checked a validator's exit with
  `cmd 2>&1 | head; echo $?`, which reports the pipe tail's (`head`) exit, not the
  validator's — so a real exit-1 ergonomics failure read as exit 0, costing a
  confused "is this pre-existing?" detour before I re-checked with `&&`/`||`.
- **`git add -A` staged a generated `.coverage` file** (not gitignored) into the
  test commit; caught on my own `git show --stat` read and amended out.
- **Minor:** ran `run_slice_closeout.py --verification-lock` expecting it to
  validate the committed bundle, but it diffs the working tree → noop; switched to
  the changed-line producer over `merge-base origin/main..HEAD`.

## Critical Decisions

- **Rule date 2026-06-09 (landing-day + 1), not 2026-06-08.** Following the
  rung-1c/1d precedent grandfathers every existing goal (including same-day
  completes and this goal) so the broad gate stays green; the floor's enforcement
  is proven by synthetic tests instead of by forcing this goal into scope. This
  goal dogfoods the *vocabulary* voluntarily (it is grandfathered, not
  floor-forced).
- **Grammar + judgment in the shared `disposition_form.py`; thin wrapper in
  `goal_artifact_disposition.py`.** Keeps the gate-and-intelligence split and the
  rung wrapper under the 360-line budget (the wrapper needs file-local
  `goal_created_date`/`_section_body`, so moving it would increase coupling).
- **A distinct `Structural follow-up:` marker, not reusing `Retro dispositions:`.**
  Reusing the existing marker adds no teeth (`applied: persisted to
  recent-lessons` still passes); the distinct marker forces the explicit
  destination call the reviewer then audits.
- **Cover the new/moved guard branches in-bundle before the producer ran.** Made
  the mutation-coverage producer a confirmation (`blocking: []`), not a discovery.

## Expert Counterfactuals

- **A gate-design reviewer (presence-only-floor discipline, à la the existing
  #329 author).** Would confirm the presence/form-enum-only design is correct and
  warn against any future tightening into a content classifier — which is exactly
  the Non-Goal the floor is built around. Lens applied: the floor proves a valid
  destination *form* is present; the reviewer/human judge substance.
- **A shell-discipline lens (read exit codes with `&&`/`||`, never through a
  pipe).** Would have avoided the piped-exit-code detour outright — the single
  highest-leverage habit fix this session.

## Next Improvements

- workflow: for skill-PACKAGE edits, run `validate_skill_ergonomics` at the
  commit boundary — it is a package-level scan, so an issue anchor / dated
  incident / host-surface ref in ANY in-package file (`references/*.md`,
  `scripts/*.py`), not just SKILL.md, trips it; keep charness-internal `#N`
  traceability anchors in top-level `scripts/` (outside any skill package).
  Disposition: none — the pre-commit `validate_skill_ergonomics` gate already
  owns this repo-wide; this is a Next-Time authoring signal, not a missing gate.
- workflow: read a gate's exit code with `cmd && echo ok || echo fail`, never
  `cmd | head; echo $?` (the pipe reports the tail's exit and masks the gate's).
  Disposition: none — a shell-usage discipline; not cleanly gateable as a
  deterministic check.
- capability: stop `git add -A` from staging generated coverage data.
  Disposition: applied: added `.coverage` / `.coverage.*` to `.gitignore` this run.

## Sibling Search

- same layer: other public-skill packages' `references/*.md` and `scripts/*.py` | decision: intentional boundary | proof: `validate_skill_ergonomics` scans every package repo-wide in pre-commit, so the same anchor trap is already caught everywhere, not just here
- abstraction up: the general rule "charness-internal `#N` anchors belong in top-level `scripts/`, not skill-package files" | decision: diagnostic-only | proof: the gate enforces it; the rule is the Next-Time authoring signal above, with no separate code fix owed
- specialization down: the specific `goal_artifact_disposition.py` anchor | decision: same waste, fix now | proof: removed the `(#337)` anchor in Slice 1; traceability preserved in top-level `scripts/disposition_form.py`
- mental-model siblings: my prior model "issue anchors only matter in SKILL.md core" | decision: diagnostic-only | proof: corrected — the ergonomics scan is package-wide; the gate is the durable enforcer of the corrected model

## Persisted

yes — `charness-artifacts/retro/2026-06-08-issue-337-structural-followup-destination-floor.md`
