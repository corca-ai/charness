# Retro — #253 improvement-disposition closeout gate (achieve)

## Mode

session

## Context

Implemented the #253 improvement-disposition closeout gate for `achieve` as a
four-slice `achieve` run: the gate-and-intelligence design — a deterministic
rung-1 floor (block-the-blank + a `Disposition review:` review-ran-evidence
line, grandfathered by `Created` date) plus a rung-2 fresh-eye reviewer that
records a per-improvement verdict. This retro feeds the goal's own closeout,
which dogfoods the very gate it ships.

## Evidence Summary

- Host-log probe: `charness-artifacts/probe/2026-05-30-issue-253-disposition-gate.json`
  (claude project JSONL detected; `token_count` available but `input_tokens`
  understated because cache-read tokens are not summed; tool-call/duration
  derivable). Measured tool mix this session: ~106 tool_uses — Bash 39, Edit 30,
  Read 18, TaskUpdate 7, TaskCreate 4 — a focused implement/verify loop, no
  obvious thrash.
- Corpus-discovery runner output: 7 pre-rule goals grandfathered → 0 rung-1a
  refusals; goal `2026-05-30-issue-251` in-scope (the documented R6 case).
- Test suite: 58 passing (21 new disposition cases + existing goal-artifact +
  before-activation), no regression.
- `git log` slices b8eb588 (rung-1 code) + 32aac22 (rung-2 mandate/docs).

## Waste

1. **Inline-then-extract redo (the largest waste).** I wrote the ~180-line
   rung-1 logic *inline* into `goal_artifact_closeout_evidence.py` because the
   goal boundary said its home was "231 lines, ample (129 headroom)". The
   additions pushed it to 411 (> the 360 hard limit), the length gate fired, and
   I reverted + extracted a leaf module. Cost: ~one edit/revert cycle. It was
   foreseeable — `recent-lessons` flags the near-limit-file trap **twice
   already**, and a back-of-envelope "180 added vs 129 headroom" before writing
   would have sent me straight to the leaf module.
2. **Partial mirror stage → post-commit packaging drift.** On the doc commit I
   staged the *source* allowlist (`scripts/…allowlist.txt`) but not its plugin
   *mirror* (`plugins/charness/scripts/…`), so `validate_packaging_committed`
   failed *after* the commit and I had to `--amend`. Repo `scripts/` is part of
   the export; a partial stage passes pre-commit but breaks the committed mirror.

## Critical Decisions

- **Leaf-module extraction** (`goal_artifact_disposition.py`) over cramming the
  home file — kept both closeout files and the 358/360 lib off the line gate and
  unblocked slice 2. The same separable-concept split that created
  `closeout_evidence` from the lib.
- **Created-keyed grandfather + accept the 251 retroactive diagnostic** rather
  than completion-date keying (explicitly rejected in the goal) or backfilling a
  closed goal (revisionist). 251 is diagnosed on re-check, never re-refused.
- **Bundle slices 1–2 into one `mutate→sync→verify→publish` commit** (they share
  `check_complete_evidence`/`_EVIDENCE_LINE`) instead of per-slice syncs.

## Expert Counterfactuals

- **A build/release engineer (line-budget discipline).** Would estimate an
  addition's size against the *actual* headroom (`limit − current`) before
  choosing the home file, not after the gate fails. Changed action: pick the new
  module first whenever additions approach headroom — the concrete improvement
  below.
- **Engelbart (the goal's own lens).** Would insist the deterministic rung never
  classify prose and that judgment live in the recorded reviewer. The design
  already held this (rung-1b stays presence/binding-only; the simplicity-lens
  "drop 1b" dissent was rejected because rung-1a provably cannot fire on the live
  all-non-blank corpus, so 1b is the only deterministic teeth). No change — the
  counterfactual confirms the decision rather than overturning it.

## Next Improvements

- **capability:** the near-limit-file trap has now recurred a 3rd time. The hard
  `check_python_lengths` gate prevents the *bad commit* but not the *wasted
  edit*; a pre-write headroom signal (a tiny `limit − current` reporter, or an
  edit-time warn) would remove the redo. File as a tracked capability follow-up.
- **workflow:** after `sync_root_plugin_manifests.py`, stage the mirror too
  (`git add` the `plugins/…` paths, or run `validate_packaging_committed` before
  committing) — repo `scripts/` + skill `SKILL.md`/`references/` all mirror, so a
  partial stage passes pre-commit but fails the committed-packaging check.
- **memory:** fold both into `recent-lessons` so the next session inherits the
  pre-write headroom estimate and the stage-the-mirror habit.

## Sibling Search

The near-limit-file trap is a transferable waste pattern (any skill helper near
`SKILL_HELPER_FILE_MAX = 360`). Four-axis scan: (script) `goal_artifact_lib.py`
is the known near-limit file at 358 — this run kept it at 358 with zero
re-export growth, no new breach; other achieve scripts are well under 330.
(doc/workflow) the stage-the-mirror miss is transferable to any slice touching
mirrored `scripts/`/`references/`, but the durable fix is the pre-push gate that
already exists plus the workflow habit above, not a code sibling. Decision:
**memory-only** — record both in `recent-lessons`; no separate sibling code
change is warranted beyond the filed capability follow-up.

## Persisted

(filled by persist helper)
