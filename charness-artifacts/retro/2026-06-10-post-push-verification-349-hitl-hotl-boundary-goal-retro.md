# Post-push verification + #349 hitl/hotl boundary goal retro
Date: 2026-06-10

## Mode

session

## Context

Closeout retro for the activated goal
`charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md`
(2.5h timebox, Claude host): slice 1 consumed the operator-executed third
2026-06-10 push + v0.39.0 release lane read-only (fourth iteration of the
deferred-proof pattern), and slice 2 resolved #349 with a deliberate
frozen-contract `preserve` edit to the at-cap hitl skill core.

## Evidence Summary

- Slice 1 all-green on first pass: quality-core run 27275145498 SUCCESS on
  pushed HEAD 768ded84; verify-closeout #346 (carrier 84dc1db3) and #348
  (carrier a65a232c) both `verified`/CLOSED; live probe installed plugin
  0.39.0 == tag v0.39.0 and installed checkout SHA == pushed HEAD; mutation
  arm deferred in-goal to the ~13:40Z cron slot per the pre-resolved fallback.
- Slice 2 commit 763653c7: hitl SKILL.md 200/200 → 196/200 with the
  reciprocal hotl line; mirrors byte-synced; all package gates green; broad
  gate 73/0; changed-line consumer verdict "no eligible mutation-pool files
  changed" (locked producer skipped on evidence, not assumption); carrier
  `Closes #349` validated `draft_verified` before commit.
- Two bounded fresh-eye reviews: slice critique SHIP-WITH-NITS (before any
  producer decision, honoring the prior goal's ordering contract) and
  resolution critique ACCEPT-WITH-PROPOSALS
  (`charness-artifacts/critique/2026-06-10-issue-349-resolution-critique.md`).
- Off-goal finding filed as corca-ai/charness#350 (at-cap propagation
  recurrence guards, bundling critique F2+F5).

## Waste

- Carrier drafting took three `validate-closeout-draft` rounds (missing
  `resolution_critique`, then missing the labeled
  Boundary/Resolution-brief/Implementation/Prevention fields) because the
  draft was hand-shaped from memory. The issue skill ships
  `describe_closeout_draft_shape.py`; one consult would have produced the
  full required shape in a single pass.
- `verify-closeout` was first invoked with the goal text's sketched args and
  failed on required flags (`--repo/--number/--classification/--carrier`) —
  second consecutive goal where the goal-text command sketch omitted required
  args (prior instance: 2026-06-10-postpush-goal-retro). Cost: one `--help`
  round.
- A zsh `===` separator in a compound verify command expanded via `=cmd`
  lookup and aborted the second call; one rerun.

## Critical Decisions

- Trim-target selection by triangulation (prose-pin scan + dogfood
  observed_evidence dump + exact-phrase grep) before touching the reviewed
  core — made the `preserve` claim defensible and the trim uncontested by
  both reviewers.
- Intro-paragraph placement for the reciprocal line, mirroring hotl's own
  intro statement — symmetry argument accepted by the fresh-eye reviewer.
- Bundling the two recurrence guards into one issue (#350) instead of
  editing `create-skill` in-slice — kept the frozen-contract slice scope
  honest.
- Deferring the mutation arm inside the timebox instead of idling on the
  cron slot — closeout work proceeded; the slot is re-checked at completion.

## Expert Counterfactuals

- A "consult the shape describer first" lens (the repo's own
  `describe_closeout_draft_shape.py` / `describe_goal_closeout_shape.py`
  pattern) would have collapsed the three carrier-draft validator rounds to
  one; the validators are consumers of a shape the helpers already print.

## Sibling Search

- structured-draft-before-validator axis: skills/public/issue/scripts/describe_closeout_draft_shape.py and skills/public/achieve (describe_goal_closeout_shape.py) | decision: valid follow-up outside the slice | proof: three draft_failed rounds in this session's carrier drafting vs the helper printing the full field list in one call | follow-up: deferred recent-lessons refresh sourcing this retro (memory destination; no gate change — the validator already fails loudly and cheaply)

## Next Improvements

- workflow: before hand-drafting any structured closeout body or carrier,
  run the owning skill's `describe_*_shape` helper and fill its printed
  field list (this retro is the source; lands in recent-lessons via the
  refresh below).
- capability: at-cap adjacent-skill propagation recurrence guards
  (create-skill checklist line + near-cap preflight warning) — filed as
  issue #350.
- memory: refreshed `charness-artifacts/retro/recent-lessons.md` via
  `refresh_recent_lessons.py` sourcing this retro.

## Persisted

yes: charness-artifacts/retro/2026-06-10-post-push-verification-349-hitl-hotl-boundary-goal-retro.md
