# Retro: Achieve long-goal efficiency

## Context

Closed the implementation slice for
`charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.
The work changed the `achieve` lifecycle and generated goal shape so broad
goals stay supported while active context, proof cadence, slice critique, and
efficiency retro evidence become more explicit.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.
- Implementation commit: `fe09061 Improve achieve long-goal operating frame`.
- Host log probe:
  `charness-artifacts/probe/2026-06-01-achieve-long-goal-efficiency.json`.
- Slice closeout: `python3 scripts/run_slice_closeout.py --repo-root .
  --ack-cautilus-skill-review` passed.
- Broad pytest in slice closeout: 1930 passed, 4 skipped, 272.0s.

## Waste

- The first implementation made `## Active Operating Frame` a global
  `check_goal` required section. That would have invalidated historical goal
  artifacts. The waste was caught before commit, but it cost an extra full-suite
  run and a compatibility pass.
- Handoff auto-draft failed the new shape because it has an independent goal
  renderer. This was not wasted validation: the broad suite caught a real
  generator-consumer compatibility gap.
- JSON dogfood edits briefly landed under `create-cli` before being corrected.
  The immediate cause was a broad patch anchor in a large repeated JSON
  structure.
- The host probe surfaced thread-wide Codex session metrics. They are useful
  pressure signals, but not a goal-scoped total for this individual goal.

## Critical Decisions

- Generated goals now include `## Active Operating Frame`, but `check_goal`
  does not require it for all historical artifacts. This preserves new-shape
  behavior without retroactive corpus breakage.
- The verification cadence guidance keeps proof strong: cheap deterministic
  checks at commit boundaries, higher-cost/fresh-eye proof at slice boundaries,
  and final broad/live proof at closeout.
- Handoff auto-draft was updated because it creates new goal artifacts; this was
  not a `docs/handoff.md` closeout update.
- Cautilus was not run. `plan_cautilus_proof.py` reported `next_action: none`;
  the required action was dogfood/scenario review and an explicit ack.

## Expert Counterfactuals

- Gary Klein would have run a premortem on "what existing artifact generator
  still emits the old shape?" before the first broad suite. That would have
  found the handoff auto-draft seam earlier.
- W. Edwards Deming would separate common-cause cost from special-cause waste:
  broad validation was expected for prompt-affecting public skills, while the
  reducible waste was the avoidable compatibility overreach and broad JSON
  patch anchor.

## Next Improvements

- applied: Do not make a new generated goal section a global historical
  `check_goal` requirement without an explicit migration/grandfather policy.
  This run narrowed `Active Operating Frame` to generated-shape tests and kept
  old artifacts compatible.
- applied: When a goal artifact shape changes, scan generator consumers, not
  only the primary `achieve` template. This run updated handoff auto-draft and
  pinned it with `tests/test_handoff_chunker_auto_draft.py`.
- applied: When Cautilus planner returns `next_action: none` with
  scenario-review follow-ups, record dogfood/scenario-review decisions before
  acking the aggregate. This run updated `docs/public-skill-dogfood.json`.
- applied: Treat cached input and thread-wide token/tool counts as pressure
  signals, not standalone waste or goal-scoped totals. This run added that
  wording to `phase-aware-efficiency.md` and the achieve metrics guidance.

## Sibling Search

- same waste, fix now: `handoff` auto-draft was the sibling generator and was
  updated in this run.
- diagnostic-only: `goal_artifact_template.md` and plugin mirrors were synced
  and validated.
- intentional boundary: historical goal artifacts were not migrated; this goal
  only required newly generated artifacts to carry the frame.
- deferred follow-up: none. The remaining host-log limitation is handled by
  honest non-claims unless a future goal asks for goal-window telemetry.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`
