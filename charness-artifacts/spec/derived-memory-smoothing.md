# Derived Memory Smoothing Contract
Date: 2026-04-23

## Problem

`charness` has several memory surfaces that change over time:
`quality/latest.md`, `retro/recent-lessons.md`, debug incident artifacts, and
`docs/handoff.md`. Textual exponential smoothing is tempting because it can keep
recent signals visible without rereading every record, but applying it directly
to current pointers would blur audit history and current truth.

## Current Slice

Define the safe contract before broad smoothing rollout. The first implementation
slice improved current-pointer freshness; the second added quality runtime EWMA
as an advisory-only derived signal.

## Fixed Decisions

- Original dated artifacts remain the source of truth. Smoothing is derived
  memory only.
- Current pointers may display derived signals only when they still name the raw
  evidence they summarize.
- `quality` gate decisions must keep using raw/latest samples, medians, and
  explicit spikes. EWMA may be advisory only.
- `retro/recent-lessons.md` remains a compact digest, not an opaque decay model.
- `debug` incident records must never be replaced by a seam-risk score.
- Adaptive alpha uses a warmup-based alpha:
  `alpha_t = alpha_base * min(1, sample_count / warmup_n)` so early samples do
  not masquerade as stable trends.

## Probe Questions

- Which exact freshness claim should a deterministic validator check first:
  `docs/handoff.md`, `charness-artifacts/quality/latest.md`, or both?
- Should debug seam-risk start as an index over existing incident files or as a
  stricter validator for the current debug artifact's `Seam Risk` section?
- What operator decision would retro or debug smoothing change beyond existing
  digest and incident records?

## Implemented Slices

- `validate-current-pointer-freshness` rejects known-stale current-pointer
  freshness claims in `docs/handoff.md` and `charness-artifacts/quality/latest.md`.
- Quality runtime EWMA is stored under
  `.charness/quality/runtime-smoothing.json`.
- Runtime EWMA uses `alpha_t = alpha_base * min(1, sample_count / warmup_n)`
  with `alpha_base = 0.35` and `warmup_n = 5`.
- `check_runtime_budget.py` reports EWMA as advisory and does not use it for
  pass/fail budget enforcement.

## Deferred Decisions

- Retro lesson decay stored under `.charness/retro/lesson-signals.json`.
- Debug seam-risk scoring stored under `.charness/debug/seam-signals.json`.
- Exposing derived memory hints through `find-skills` routing.

## Non-Goals

- Do not add smoothing to `recent-lessons.md` in this slice.
- Do not make EWMA part of pass/fail budget enforcement.
- Do not create a new visible artifact family for smoothed memory until a
  current pointer demonstrably needs it.

## Premortem

Execution: bounded subagent premortem ran with skill-coverage, memory-safety,
and counterweight angles.

Act Before Ship:

- Treat `docs/artifact-policy.md`, `docs/handoff.md`, and `init-repo` as
  first-class consumers before making smoothing a reusable repo pattern.
- Keep smoothed values separate from dated history and make every derived
  current pointer trace back to evidence.
- Add a narrow freshness validator before adding memory math.

Bundle Anyway:

- Debug seam-risk is useful, but should stay inside the existing debug artifact
  and validator seam rather than becoming a standalone score surface.

Over-Worry:

- Quality runtime EWMA remains advisory. Current runtime signals and budgets
  still own the main quality decisions.

Valid but Defer:

- Retro decay may help later, but the current problem is deciding which lessons
  survive into the compact digest, not building a decay algorithm.

## Success Criteria

- The freshness validator can fail when `docs/handoff.md` or
  `quality/latest.md` makes stale current-state claims that disagree with live
  inventories.
- Any smoothing implementation records its raw source, sample count, warmup
  policy, and whether the output is advisory or enforcing.
- No current pointer becomes the only place where a historical fact is stored.

## Acceptance Checks

- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`
- Runtime smoothing tests should keep proving EWMA is advisory and raw
  latest/median/spike behavior still owns budget enforcement.

## Deliberately Not Doing

- A three-surface smoothing rollout across `quality`, `retro`, and `debug`.
- A hidden state schema for all memory surfaces before one concrete consumer
  needs it.
- A smoothing-derived failure gate.

## Next Implementation Slice

Extend deterministic freshness checks only when a current pointer makes a
concrete claim that can be checked against live inventory. Keep retro lesson
decay and debug seam-risk scoring deferred until one concrete consumer needs
derived memory beyond the quality runtime EWMA.
