# Session Retro: Quality scaffold generalization + testability follow-ups

## Mode

session

## Context

Goal `charness-artifacts/goals/2026-06-05-quality-scaffold-and-testability-followups.md`:
(1) build `scaffold_{handoff,ideation,retro,critique}_artifact.py`, (2) move the
boundary-bypass ratchet to Done in `docs/testability-dsl-initiative.md`, (3) convert
the import-safe `inventory_*` boundary-bypass cluster to in-process. Three slices
landed as commits `54748cd3`, `d2ce3bbd`, `0604f3d2`; read-only quality gate green
(71/0) at every slice boundary; both substantial slices passed bounded fresh-eye
review (ship, no blockers).

## Evidence Summary

- Slice 1: 4 scaffolds + 9 tests; baseline regen 54→57 convertible (new export-test
  keys); read-only gate 71/0.
- Slice 3: 2 inventory_* tests converted in-process; baseline 96→94 candidates,
  57→55 convertible — exactly the 2 converted keys, no exemptions.
- Two `git worktree` clean-HEAD probes isolated pre-existing failures (committed-state
  gates + a parallel-run flake) from real regressions.

## Waste

The goal's stated premise — "mirror the debug/quality scaffold pattern" — was wrong
for 3 of 4 targets (ideation/retro/critique validators are `--paths`-based and
opt-in; none of the four is a current-pointer artifact). Discovery cost ~30m before
any code. The waste was acceptable because surfacing it early via one
`AskUserQuestion` (rather than improvising) kept the build aligned, but a goal-draft
that had verified validator shapes would have saved the detour.

The handoff `SKILL.md` edit hit a hard ≤161-line budget test (`recent-lessons` repeat
trap #1, "the 200-line gate biting twice") and had to be reverted — pure rework that
reading `recent-lessons.md` first would have prevented.

## Critical Decisions

- Build all 4 scaffolds adapting per-validator (user-chosen) rather than narrowing —
  delivered the goal's outcome despite the premise mismatch.
- Keep new consumer-export tests on the baselined subprocess pattern and regenerate
  the baseline (canonical form), rather than diverging to in-process for export setup
  (that is item 3's designated scope, not new scaffold tests).
- Convert only the 2 cleanest dedicated inventory_* tests + document both patterns,
  bounding slice 3 honestly rather than rushing all 7 under the timebox.

## Expert Counterfactuals

- Gary Klein's premortem lens would have asked, before slice 1, "what if the four
  validators are not the same shape?" — exactly the failure that materialized.
  Reading the four validators in the Before phase (not mid-build) was the fix.
- A "read the recent-lessons traps first" discipline (the repo's own contract) would
  have pre-empted the handoff SKILL.md budget revert.

## Sibling Search

- inline-path-reference axis: skills/public/ideation/SKILL.md | decision: same class, diagnostic-only for this slice | proof: validate_skills + ergonomics + check-markdown all flagged one bare `scripts/...` inline reference; fixed by using the `$SKILL_DIR` fenced form | no action needed — other public SKILL.md already use the `$SKILL_DIR` form, so this was a one-off authoring slip, not a repo-wide class.

## Next Improvements

- workflow: before editing any SKILL.md surface, check `recent-lessons.md` and grep
  for a per-skill budget test (`test_<skill>_skill_md_budget`) — both bit this run.
- capability: goal-draft interviews for "mirror an existing pattern" goals should
  verify the target contracts' shapes in the Before phase, not assume parity.
- memory: the boundary-bypass baseline is regenerated to canonical form (not
  hand-edited) when adding/removing boundary-crossing tests; decreases are tolerated
  by `no_increase`, so a stale baseline can lag silently.

## Persisted

yes: `charness-artifacts/retro/2026-06-05-quality-scaffold-and-testability-followups.md`
