# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- No loop is pre-queued. For the next quality loop, start with `quality` for gate
  posture, then `impl` one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.56.9 published and verified; #405 CLOSED.** The release shipped the #405
  doctrine — two named `quality` Behavior-lens bullets
  (`verification-channel fitness`, `guard-propagation across seams`) in
  [quality-lenses.md](../skills/public/quality/references/quality-lenses.md) and a
  `## Distinct Named Lenses` note in
  [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md)
  — plus a `find-skills` inventory refresh. Verified on four distinct channels:
  `git ls-remote` tag `v0.56.9`, `gh release view` (isDraft false),
  `gh issue view 405` CLOSED/COMPLETED, installed packaging `0.56.9`.
- **v0.56.8 (D30 dup-ratchet id-rotation) remains published.** Detail archived;
  D30 follow-on residuals (S4-Defer-1, S4-Defer-3) stay deferred and not urgent.

## Next Session

- **Pinned pickup: [#406](https://github.com/corca-ai/charness/issues/406)** —
  reduce `achieve` closeout authoring churn. Operator-decided approach (recorded
  in the issue): **minimize hooks; prefer better templates, correct code, and
  well-described principles.** Four levers: (A) goal-producer template stubs for
  `Routing:` and `Discuss before activation:`; (B) floor-parser bug-fixes
  (`phase_routing` wrapped-line join) + surface the ODQ-scaffold-clear in the
  closeout describe; (C) an `implementation-discipline` paragraph unifying the
  per-surface aggregate preflights as one guard class; (D) **describe-first gate
  failures** — on rejection, floors render the correct target shape, not just
  "wrong." Touches the producer pinned by
  [test_goal_artifact_producers.py](../tests/quality_gates/test_goal_artifact_producers.py),
  so it is its own shaped slice/goal.
- **Next quality loop:** start with `quality` for gate posture, then `impl` one
  narrow slice. D30 follow-on residuals reopen only on observed re-baseline
  friction.

## Discuss

- A `nose v0.16.0` upgrade is advisory-available; bumping the installed nose would
  regroup families and trigger the scanner-version skew WARNING -> a one-time
  lockstep re-baseline (by design, not a defect).

## References

- [release notes v0.56.9](../charness-artifacts/release/notes-v0.56.9.md)
- [issue #405 goal artifact](../charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md)
- [deferred-decisions D30 (resolved)](./deferred-decisions.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
