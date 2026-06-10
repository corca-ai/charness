# Next-queue goal retro
Date: 2026-06-10

## Mode

session

## Context

Goal: charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md

Closeout retro for the 2026-06-10 next-queue goal (push/release-lane
verification + #346 Claude-host metric scoping + #348 portable hotl skill),
run as three independently closed-out slices inside a 4h timebox on a Claude
host. All three slices landed: slice 1 consumed the operator-executed v0.38.0
push/release lane read-only; slice 2 shipped the corrected-mechanism #346 fix
(carrier 84dc1db3); slice 3 shipped the new `hotl` public skill (carrier
a65a232c).

## Evidence Summary

- Slice 1: quality-core run 27264481707 green on fd3c2c6c; live
  installed-surface probe (installed SHA == pushed HEAD, plugin 0.38.0 ==
  tag); scheduled mutation run 27261418055 green over 39ff5432 (retired the
  carried deferred proof).
- Slice 2: 47+ related tests green; two fresh-eye-critique cycles
  (activation: PROCEED-WITH-ADJUSTMENTS with the corrected B1 mechanism;
  slice: HOLD with a live repro of the dropped `last_event_at`), both folded;
  changed-line consumer confirmed 0 uncovered post-refresh.
- Slice 3: all skill-package and registry gates green; SHIP-WITH-NITS
  fresh-eye verdict with a line-by-line port comparison (no lost concepts,
  zero host-fact leaks); changed-line consumer confirmed 0 uncovered
  post-refresh; off-goal #349 filed.
- Broad read-only gate at closeout: 73 passed, 0 failed.

## Waste

- One redundant locked producer run per mutating slice (~7 min each, twice):
  the instrumented broad-pytest producer ran BEFORE the fresh-eye slice
  critique (slice 2) and BEFORE the changed-line self-check surfaced
  uncovered new branches (slice 3), so critique-driven fixes and late
  branch-coverage tests invalidated the coverage fingerprint and forced full
  reruns. The ordering lesson is now a contract line in
  `docs/conventions/implementation-discipline.md`.
- A small fold-then-revert cycle on `hitl` SKILL.md: the reciprocal boundary
  line hit the 200/200 total-line ceiling; reverted deliberately and routed
  as #349 instead of trimming reviewed prose under time pressure.

## Critical Decisions

- Trusting the activation critique's B1 over the issue body: the
  misattributed measured block was a stale Codex rollout, not a Claude
  project-dir aggregate; the slice was redesigned around the render path and
  a new Claude auditor, and the carrier records the corrected root cause.
- Reverting the hitl nit fold rather than eroding a frozen, at-cap contract
  mid-slice (became #349).
- Covering the hotl helper entry points in-process (runpy run_name=__main__ +
  degrade-branch tests) instead of re-adding subprocess smokes or ratchet
  exemptions, keeping the boundary-bypass ratchet flat.

## Expert Counterfactuals

- The slice-2 reviewer's refute-by-execution discipline (live repro of the
  dual-host misordering) is the lens that caught what 113 green tests missed:
  synthetic render fixtures carried the very field the real probe dropped.
  Applying "integration-test the boundary you just changed, with both real
  producers populated" BEFORE handing the slice to review would have turned a
  HOLD cycle into a green first pass.

## Sibling Search

- axis: closeout sequencing (locked producer vs fresh-eye critique vs late
  branch tests) | decision: transferable — recurred twice within this goal
  across different slices | proof: two `--refresh-broad-pytest-proof` reruns
  recorded in the slice logs | follow-up: applied — ordering contract line
  added to docs/conventions/implementation-discipline.md in this closeout.

## Next Improvements

- workflow: run the fresh-eye slice critique before the locked producer run
  (applied: contract line in docs/conventions/implementation-discipline.md).
- capability: per-goal metrics now scope on Claude hosts via
  `--claude-session-file` and the dual-key `Host metric window:` grammar
  (applied in slice 2; this goal's own closeout dogfoods it).
- memory: cross-host audit selection must be pinned by probe-to-render
  integration tests with both hosts populated (applied: two integration
  tests in slice 2); the at-cap adjacent-skill propagation block is tracked
  as issue #349 (novel: first instance of the class).

## Persisted

yes: charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md
