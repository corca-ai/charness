# Issue 337 / structural-follow-up destination floor — disposition + structural-follow-up review
Date: 2026-06-08

Fresh-eye, read-only rung-2 disposition review of the `achieve` goal closeout for
`charness-artifacts/goals/2026-06-08-retro-disposition-structural-followup-classification.md`
(#337). Reviewed its `## Auto-Retro` (the `Retro dispositions:` line + the two
`Structural follow-up:` lines) and `## Final Verification`, the cited retro
`charness-artifacts/retro/2026-06-08-issue-337-structural-followup-destination-floor.md`
(`## Next Improvements`, `## Waste`, `## Sibling Search`), and the 3-commit bundle
`git diff 281fc373..HEAD` (`3dc8e79c` rung-1e floor + mandate, `e3dbd266` shared
destination vocabulary, `101c1f33` guard-branch coverage tests + `.gitignore`).
Verified via `git show`/`git diff`, source inspection of the ergonomics validator,
and a live run of `validate_skill_ergonomics.py`. No index or worktree mutation
performed; the review artifact is my only write.

## Mandate 1 — Per-improvement disposition verdict (rung 2)

The retro's `## Next Improvements` has exactly three entries. The goal `## Auto-Retro`
`Retro dispositions:` line accounts for all three (improvement 3 `applied:`,
improvements 1+2 each `none —`). Per-improvement:

- **Improvement 1 — "for skill-PACKAGE edits, run `validate_skill_ergonomics` at
  the commit boundary; it is a package-level scan."** `Disposition: none — the
  pre-commit `validate_skill_ergonomics` gate already owns this repo-wide; this is
  a Next-Time authoring signal, not a missing gate.` **Verdict: DISPOSITIONED,
  `none —` is HONEST.** I verified the claim is falsifiable and true:
  `skill_ergonomics_lib.py:113` calls `tqlib.issue_anchor_package_findings(repo_root,
  skill_dir)` for every `public`/`support` skill; that function
  (`skill_text_quality_lib.py:98`) walks the WHOLE package via `skill_dir.rglob("*")`
  (`skill_text_quality_lib.py:52`), so an issue anchor in any `references/*.md` or
  `scripts/*.py`, not just SKILL.md, raises `portable_package_issue_anchor`
  (`skill_ergonomics_lib.py:134-135`). The validator is wired into the pre-commit
  boundary: `.githooks/pre-commit` runs `run_slice_closeout.py --predict-commit`,
  whose predict-commit gate set lists `validate-skill-ergonomics`
  (`staged_commit_gate_plan.py:26,275`). A live run at HEAD exits 0 with
  `portable_package_issue_anchor` among the active rules. So there is no missing
  structural fix — the gate genuinely owns it. `none —` is correct.

- **Improvement 2 — "read a gate's exit code with `cmd && echo ok || echo fail`,
  never `cmd | head; echo $?`."** `Disposition: none — a shell-usage discipline;
  not cleanly gateable as a deterministic check.` **Verdict: DISPOSITIONED, `none —`
  is HONEST.** This is an in-session shell-invocation habit (read the gate's exit,
  not the pipe tail's). There is no artifact or repo surface a deterministic floor
  could inspect to catch a future mis-read — it lives in how the operator types a
  command, not in committed state. Nothing to falsify; `none —` is the right form.

- **Improvement 3 — "stop `git add -A` from staging generated coverage data."**
  `Disposition: applied: added `.coverage` / `.coverage.*` to `.gitignore` this
  run.` **Verdict: DISPOSITIONED, `applied:` is HONEST — teeth verified at HEAD.**
  `git show HEAD:.gitignore` carries lines 33-35 (`# Python coverage data`,
  `.coverage`, `.coverage.*`); the entries were added in the test commit
  `101c1f33` (`git show 101c1f33 -- .gitignore`). This is a real committed change
  that prevents `git add -A` from staging the generated coverage file, the exact
  waste recorded in `## Waste`. The disposition has teeth and they landed in the
  bundle.

Teeth summary: 3/3 dispositioned, all three forms honest. Two `none —` are genuine
non-claims (one owned by an existing gate I verified fires package-wide, one a
non-gateable shell habit); the one `applied:` has verifiable committed teeth. No
`issue #N` disposition exists, so there is no `novel:`/`recurs:` lineage to falsify.

## Mandate 2 — Structural-follow-up DESTINATION audit (the #337 mandate)

The retro `## Sibling Search` names the transferable waste item (the in-package
issue-anchor trap) across four sibling rows; the goal `## Auto-Retro` records two
`Structural follow-up:` destinations. Both forms are valid against the rung-1e
enum (`applied:` / `issue #N` / `repo-local guard:` / `none —`, per
`scripts/disposition_form.py:103-107`).

- **Destination 1 — the in-package issue-anchor trap: `none — ... already owned by
  that pre-commit gate repo-wide; no missing structural fix (a falsifiable claim
  the disposition review can contradict).`** **Verdict: VALID FORM, SUBSTANTIVELY
  RIGHT.** This is the audit's load-bearing call: is `none —` an honest structural
  disposition, or a "recorded in recent-lessons" memory note dressed up as a
  destination? It is honest. The claimed structural owner genuinely exists and
  fires on exactly this trap: `validate_skill_ergonomics` scans the whole skill
  package via rglob, raises `portable_package_issue_anchor` on an anchor in any
  in-package file, and runs in the pre-commit predict-commit gate (all four facts
  verified above for improvement 1). This is the very gate that fired on this run's
  `(#337)` anchor — the retro `## Waste` records it tripping, and at HEAD the
  in-package `goal_artifact_disposition.py` carries NO `#337` anchor (removed in
  Slice 1) while the top-level `scripts/disposition_form.py` keeps the traceability
  anchors (allowed in top-level `scripts/`). So the transferable rule ("keep
  charness-internal `#N` anchors out of skill packages") needs no NEW structural
  fix — the gate already enforces it repo-wide. `none —` is a real, falsifiable,
  un-contradicted claim, not a memory dodge.

- **Destination 2 — `applied: added `.coverage`/`.coverage.*` to `.gitignore`.`**
  **Verdict: VALID FORM, SUBSTANTIVELY RIGHT.** Same verified committed teeth as
  improvement 3 (`.gitignore` lines 33-35 at HEAD via commit `101c1f33`). A genuine
  structural change landed this run; `applied:` is correctly used.

Sibling-decision consistency check: the retro `## Sibling Search` maps cleanly to
the two destinations. The `abstraction up` row (the general rule) is
`diagnostic-only` → `none —`, and the `same layer` / `mental-model` rows are
`intentional boundary` / `diagnostic-only` → `none —` — all subsumed by Destination
1's `none —`. The `specialization down` row (the specific
`goal_artifact_disposition.py` anchor) is `same waste, fix now` → `applied:` and
already landed in-slice (anchor removed in `3dc8e79c`), so it is NOT an outstanding
destination owed at closeout — correctly absent from the two Auto-Retro lines. The
decision→destination mapping matches the Slice-2 `waste-sibling-scan.md` taxonomy
(`same waste, fix now`→`applied:`; `diagnostic-only`/`intentional boundary`→`none —`),
which the bundle landed at `e3dbd266`. No memory note is being passed off as a
structural disposition.

## Findings

1. **OVER-WORRY** — The `none —` for the in-package anchor trap could read as a
   memory dodge, but it is the opposite: a falsifiable structural-ownership claim
   that I attempted to contradict and could not. The named owner
   (`validate_skill_ergonomics` package-wide scan, pre-commit-wired) genuinely
   exists and fired on this exact run. No action.

2. **NIT** — The Auto-Retro records two `Structural follow-up:` lines but the
   `## Sibling Search` has four sibling rows; the mapping (one `applied:` for the
   `specialization down` in-slice fix, three `none —` collapsed into one Destination-1
   line) is correct but is reconstructed by the reviewer rather than stated. A reader
   must cross-walk the four rows to the two lines. Not a defect — the destination is
   per-transferable-waste-item, not per-sibling-row, and the floor is dogfooded
   voluntarily here (grandfathered `Created` 2026-06-08 < 2026-06-09 rule date). No
   gate item.

3. **OVER-WORRY** — Behavior-preservation / no over-fire: the goal is grandfathered
   (`Created` 2026-06-08 < the 2026-06-09 rule date), so rung 1e is inert here and
   the two destination lines are voluntary dogfood; enforcement rests on the
   synthetic `test_rung1e_*` tests (bundle commit `101c1f33` added guard-branch
   coverage). This matches `## Final Verification`'s claim. No action.

## Verdicts

Disposition verdict: ALL improvements dispositioned (3/3) — improvement 3 `applied:`
with verified committed `.gitignore` teeth; improvements 1+2 `none —`, both honest
(1 owned by a pre-commit package-wide gate I verified fires on this trap; 2 a
non-gateable shell habit). No `issue #N`/`novel:` lineage to falsify. No overclaim.

Destination verdict: SHIP — both `Structural follow-up:` destinations use a valid
rung-1e form and are substantively right. The load-bearing `none —` for the
transferable in-package issue-anchor trap is a falsifiable, un-contradicted
structural-ownership claim (the `validate_skill_ergonomics` package-wide pre-commit
scan genuinely owns it — it is the gate that fired on this run), NOT a
"recorded in recent-lessons" note dressed up as a destination. The `applied:`
destination has verified committed teeth. No gate item before flip.
