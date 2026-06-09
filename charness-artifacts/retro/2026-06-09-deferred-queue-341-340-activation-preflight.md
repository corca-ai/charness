# Retro — deferred-queue goal (#341 + #340 + activation-preflight)

Mode: session

## Context

One `achieve` goal cleared three independent tracked deferred items in three
per-slice-closed-out slices: #341 (mutation regression on main), #340 (find-skills
not surfacing specdown's shipped support skill), and the activation-preflight
surface. Commits `84dde097` (#341), `c6c0ee9a` (#340), `e30643cc` (slice 3),
`6e751831` (bundle-boundary coverage fixup). What matters next: push (achieve does
not push) so #341's scheduled CI run goes green and #340 closes.

## Evidence Summary

- Slice-1 root-cause: the mutation sampler over `3a42d2e0..HEAD` + per-file
  workload/nodeid diagnostics; targeted-mutant proof of the 5 survived mutants.
- Bundle boundary: changed-line producer `ok: true, blocking: []` over the final
  range (fresh full-suite coverage); sample manifest `selection_excluded_changed_files: []`;
  broad gate `73 passed, 0 failed`; full pytest 2658 passed.
- Two fresh-eye slice critiques (separate agent contexts) returned SHIP; the
  slice-3 critique independently confirmed the already-done finding.

## Waste

- **Coverage-producer DISCOVERED (not confirmed) an uncovered changed line**
  (`mutation_manifest_lib.py:124`, the `if not per_file_budget_excluded: return`
  early-return). The carried lesson said cover new branches IN the introducing
  slice so the bundle producer confirms; I covered 2 of the 3 branches in slice 1
  and missed the empty-result early return. Cost: a fixup commit + a ~7-min
  producer re-run. Same recurring class as the recent-lessons "coverage-producer
  round-trip."
- **#N issue anchor in skill-package files recurred** (`(#340)` in two find-skills
  docstrings) — the slice-2 commit was blocked by `validate_skill_ergonomics`
  (`portable_package_issue_anchor`). Caught at commit time, fixed in ~1 min. This
  is the trap recent-lessons recorded recurring 3× last run (accepted-risk); it
  recurred again here.
- **Length-limit fight (slice 2):** adding a cohesive ~55-line recommendation
  function pushed `list_capabilities_lib.py` over the 360 hard limit and `main()`
  over 100; several trim iterations to fit. The find-skills lib genuinely sits at
  its cohesion limit (the advisory had been flagging it). Mild, partly structural.

## Critical Decisions

- **#341 fix approach (operator-decided via AskUserQuestion).** Slice-1 root-cause
  revealed the 5 survived mutants were a RED HERRING (score was PASS 95%); the real
  blocker was the per-file-cap dropping the module-split files (134/153 mutable
  lines > 80) as a BLOCKING `selection_excluded_changed_files` signal — seed-
  independent and permanent. The operator chose Option A (reclassify a covered
  changed file dropped solely by the per-file cap as non-blocking advisory). This
  pivoted slice 1 from "add a test" to a gate-semantics change. Surfacing it (the
  spec had deferred selection-budget as out-of-scope) was the right call.
- **Classified specdown's layer before wiring (slice 2):** integration that ships
  a support skill (not materialized locally) → feed shipped-support recs to the
  recommendation path only, deduped, leaving the inventory unchanged (no inventory
  regression).
- **Cross-checked the OWNING spec before implementing slice 3:** the spec recorded
  the activation-preflight surface DONE (commit `01021a14`); the handoff "Next
  Session" was STALE. Avoided a redundant re-implementation.

## Expert Counterfactuals

- **Gary Klein (pre-mortem / recognition-primed):** would have asked at slice start
  "what would make the next scheduled run STILL fail after I 'fix' it?" — surfacing
  the selection-budget arm before the sampler discovery, and enumerating ALL
  branches of a new function (incl. empty-result early returns) before writing the
  slice test, pre-empting the line-124 round-trip.
- **A release/packaging reviewer lens:** would have treated "am I editing a
  skill-package file?" as a standing pre-write check, catching the `(#340)` anchor
  at edit time rather than the commit sweep.

## Next Improvements

- **memory:** Before implementing a deferred follow-up named only in `docs/handoff.md`,
  cross-check the OWNING spec's status — the spec was authoritative over the stale
  handoff and saved a redundant re-implementation. (persisted to recent-lessons)
- **memory:** When adding a function with multiple early-returns, enumerate EVERY
  branch — especially empty-result early returns — in the introducing slice's unit
  test, so the bundle-boundary changed-line producer confirms rather than discovers.
- **workflow (applied):** Corrected the stale `goal-activation-preflight-surface`
  item in `docs/handoff.md` so the next session does not re-discover it.
- **capability (re-affirm accepted-risk):** The #N-anchor-in-skill-package trap
  recurred again (`(#340)` in two find-skills docstrings), caught by the commit-time
  `validate_skill_ergonomics` sweep — nothing escaped, as the recent-lessons
  accepted-risk disposition predicted. The persistence across goals strengthens the
  case for an edit/preflight-time guard; recommended to the operator as the next
  structural step (not filed autonomously — outward-facing). Disposition stands:
  accepted-risk, commit-sweep backstop.

## Sibling Search

- Mental model checked: "a new function's branches are covered if its happy path is
  tested." Wrong for empty-result early returns.
- same-boundary (other functions I added this session with early returns/guards):
  `shipped_support_recommendations_for_task` (multiple `continue` guards) and
  `_task_support_recommendations` — covered by the find-skills tests; the
  bundle-boundary producer ran over ALL 9 changed pool files and returned
  `blocking: []`, so no other uncovered changed branch escaped. Proof: producer
  `ok: true`.
- same-class (#N anchor in skill-package files): the only skill-package edits with
  an `#N` anchor were the two find-skills docstrings (fixed); slice-1 touched
  repo-root `scripts/` (where `#N` is allowed) and slice-3 touched `tests/`.
  `validate_skill_ergonomics` passed on re-commit → sibling-clean.
- follow-up: the #N-anchor edit-time guard — recommended to the operator (the
  commit-sweep remains the working backstop; not filed autonomously).

## Persisted

Persisted: yes (written by persist_retro_artifact.py below).
