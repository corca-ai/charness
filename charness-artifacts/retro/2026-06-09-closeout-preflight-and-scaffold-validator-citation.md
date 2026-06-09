# Session Retro
Date: 2026-06-09

## Mode

session

## Context

One `achieve` goal closed the recurring authoring-preflight-skip class on its two
remaining surfaces, in two independently-committed slices: (1) author-time
closeout preflight — a new `closeout-draft` surface + an enriched `goal-closeout`
surface in `check_artifact_surface_preflight`, each rendering its required shape
LIVE from the owning validators' constants via two new `describe_*_shape.py`
sibling scripts (commit `bebdaa2d`); (2) verify-first scaffold repo-validator
citation audit — CONFIRMED already shipped in v0.29.0, no residual gap, stale
handoff Discuss item resolved (commit `c2efa288`). Both slices carried a fresh-eye
critique; the bundle broad gate is green with changed-line coverage refreshed.

## Evidence Summary

- Commits: `bebdaa2d` (slice 1), `c2efa288` (slice 2) over `origin/main..HEAD`.
- Tests: 50 dispatcher tests + 232 issue/achieve verdict-preservation tests; 100%
  line coverage on the 3 new/changed source files; round-trip parity (a closeout
  body built from the surfaced headers satisfies the validator's own ledger/keyword
  helpers for every classification).
- Broad gate: `run-quality.sh --read-only` = 73 passed / 0 failed; changed-line
  mutation coverage produced + fingerprint-stamped (confirmed, not discovered).
- Host log probe (thread-wide, Claude host): 429 function calls, 149 custom tool
  calls, 139 patch applications, 4 compactions, 4 subagent spawns, no repeated
  broad gates; git status x26 (system-reminder-driven). No goal metric window
  recorded, so these are thread-wide pressure, not a per-goal total.
- Two fresh-eye subagent critiques: slice 1 REVISE (folded), slice 2 CONFIRMED-NO-GAP.

## Waste

- **Slice-1 disposition-form conflation (the main rework).** The goal-closeout
  describe script first rendered the `Retro dispositions:` form from the goal
  template's `## Auto-Retro` *Structural follow-up* prose (`repo-local guard:`
  etc.), which is a DIFFERENT floor (`DESTINATION_FORM_SUMMARY`) than the one that
  judges `Retro dispositions:` (`VALID_FORM_SUMMARY`). The surfaced shape would
  have mis-directed an author into a REJECTED line — the exact failure class the
  slice closes, reintroduced. Caught by the fresh-eye reviewer (B1), not my own
  tests, because the form was hand-prose with no drift pin (B2). Cost: one fold
  cycle + the realization that "read from the validator" must cover EVERY
  enumerable form, not just the easy enum.
- **Minor friction, each caught at its gate:** the describe scripts tripped the
  attention-state `skipped` ban (reworded the issue script; declared the achieve
  script's literal `skipped:` author-syntax token); the handoff RESOLVED note grew
  past the 70-line floor (trimmed to a one-liner); the coverage producer defaults
  to the working-tree diff and reported "Changed paths: none" post-commit (had to
  pass `--paths` for the committed range).

## Critical Decisions

- **Verify-first slice 2 (the goal's structural win).** Structuring slice 2 as a
  read-only audit BEFORE any change caught the stale handoff Discuss item (already
  shipped in v0.29.0) with zero make-work — exactly the slice-3 stale-handoff trap
  the goal was built to avoid. Confirmed independently by a fresh-eye reviewer.
- **Extend the dispatcher, render from live constants.** Extending
  `check_artifact_surface_preflight` (vs a standalone script) kept the
  artifact-authoring family cohesive; rendering shape from live constants + drift
  tests is what made the B1/B2 fix a one-constant change rather than a rewrite.

## Expert Counterfactuals

- **Rich Hickey ("place vs value" / single source of truth).** Would have insisted
  that if a surface claims "read from the validator," EVERY enumerable form is a
  value pulled from the validator's own constant — never a hand-copied prose form
  living in a second place. Applying that from the start renders the disposition
  form from `disposition_form.VALID_FORM_SUMMARY` immediately, and B1/B2 never
  happen. The changed action: "single source" is binary per-field, not "mostly".

## Sibling Search

- axis: code | location: the ORIGIN site B1 copied from — `goal_artifact_template.md`'s `Structural follow-up:` seed line | decision: valid follow-up — sibling FOUND and fixed in-slice | proof: the fresh-eye disposition review falsified an initial too-narrow "no sibling" (which had audited only the fix-site describe scripts): the template's hand-quoted destination form had already DRIFTED from the live `disposition_form.DESTINATION_FORM_SUMMARY` (`applied: <change>` vs `applied: <gate/hook/validator/test/contract change>`); folded by rendering the live form verbatim + a drift-pin guard (`tests/quality_gates/test_disposition_form_floor.py::test_goal_template_structural_followup_form_matches_live_constant`) | follow-up: applied this run
- axis: docs | location: other author-facing form quoters (`retro-issue-destination-split.md`, `lifecycle.md`, `waste-sibling-scan.md`, `prescribed-skill-closeout-contract.md`) | decision: no sibling — context-specific prose, not verbatim seeds | proof: `lifecycle.md` already matches the live constant; the rest define the form arms as prose by context (one-arm-per-bullet definitions), not a single concatenated seed an author copies — a repo-wide verbatim pin would flatten intentional prose | follow-up: none

## Next Improvements

- workflow: applied — when surfacing an enforced form/shape, render EVERY
  enumerable piece from the OWNING validator's live constant and drift-test each;
  never hand-copy a form from a nearby template (it may be a different floor's
  form). Encoded as the drift tests pinning VALID_FORM_SUMMARY / DESTINATION_FORM_SUMMARY
  in commit `bebdaa2d`.
- capability: recommend to operator (not auto-filed; outward-facing) — the
  changed-line coverage producer (`run_slice_closeout.py --produce-mutation-coverage`)
  defaults to the working-tree diff and no-ops post-commit; a `--base <ref>` /
  origin/main..HEAD auto-detect would remove the "pass --paths for the committed
  range" friction at the bundle boundary.
- memory: applied — this retro records that the per-improvement disposition floor
  and the structural-follow-up destination floor are two distinct gates with two
  distinct valid-form summaries (VALID_FORM_SUMMARY vs DESTINATION_FORM_SUMMARY);
  the summary refresh surfaces it to recent-lessons.

## Persisted

yes: charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md
