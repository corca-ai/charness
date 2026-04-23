# Derived Memory Smoothing Contract
Date: 2026-04-23

## Problem

`charness` has several memory surfaces that change over time:
`quality/latest.md`, `retro/recent-lessons.md`, debug incident artifacts, and
`docs/handoff.md`. Textual exponential smoothing is tempting because it can keep
recent signals visible without rereading every record, but applying it directly
to current pointers would blur audit history and current truth.

## Current Slice

Define the safe contract before adding any smoothing implementation. The first
implementation slice should improve current-pointer freshness rather than add a
new smoothing model.

## Fixed Decisions

- Original dated artifacts remain the source of truth. Smoothing is derived
  memory only.
- Current pointers may display derived signals only when they still name the raw
  evidence they summarize.
- `quality` gate decisions must keep using raw/latest samples, medians, and
  explicit spikes. EWMA may be advisory only.
- `retro/recent-lessons.md` remains a compact digest, not an opaque decay model.
- `debug` incident records must never be replaced by a seam-risk score.
- If adaptive alpha is used later, use a warmup-based alpha such as
  `alpha_t = alpha_base * min(1, sample_count / warmup_n)` so early samples do
  not masquerade as stable trends.

## Probe Questions

- Which exact freshness claim should a deterministic validator check first:
  `docs/handoff.md`, `charness-artifacts/quality/latest.md`, or both?
- Should debug seam-risk start as an index over existing incident files or as a
  stricter validator for the current debug artifact's `Seam Risk` section?
- What operator decision would EWMA change beyond the existing runtime budget,
  latest sample, and recent median?

## Deferred Decisions

- Quality runtime EWMA stored under `.charness/quality/runtime-ewma.json`.
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

- Quality runtime EWMA is not urgent. Current runtime signals and budgets
  already support the main quality decisions.

Valid but Defer:

- Retro decay may help later, but the current problem is deciding which lessons
  survive into the compact digest, not building a decay algorithm.

## Success Criteria

- A future freshness validator can fail when `docs/handoff.md` or
  `quality/latest.md` makes stale current-state claims that disagree with live
  inventories.
- Any future smoothing implementation records its raw source, sample count,
  warmup policy, and whether the output is advisory or enforcing.
- No current pointer becomes the only place where a historical fact is stored.

## Acceptance Checks

- `python3 scripts/check_doc_links.py --repo-root .`
- `./scripts/check-markdown.sh`
- Next implementation slice should add a focused test for the first freshness
  check before wiring it into `run-quality.sh`.

## Deliberately Not Doing

- A three-surface smoothing rollout across `quality`, `retro`, and `debug`.
- A hidden state schema for all memory surfaces before one concrete consumer
  needs it.
- A smoothing-derived failure gate.

## First Implementation Slice

Add a deterministic freshness check for the rolling current pointers already
called out as weak: `docs/handoff.md` and `charness-artifacts/quality/latest.md`.
Keep the check narrow enough to compare concrete claims against current repo
inventory, and leave EWMA/decay work deferred until that validator proves where
derived memory would change an operator decision.
