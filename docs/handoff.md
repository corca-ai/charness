# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- No loop is pre-queued. For the next quality loop, start with `quality` for gate
  posture, then `impl` one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **#405 resolved locally (closeout staged, not pushed).** Added two named
  Behavior-lens bullets
  (`verification-channel fitness` and `guard-propagation across seams`) to
  [quality-lenses.md](../skills/public/quality/references/quality-lenses.md), and
  a `## Distinct Named Lenses` delegation note to
  [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md);
  `plugins/` mirror regenerated. The closeout commit carries `Close #405` + the
  feature resolution ledger, validated via `issue validate-closeout-draft`.
  **#405 is still OPEN — the maintainer's push of the carrier to default branch
  closes it.** Goal:
  [issue-405 goal artifact](../charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md)
  (Status: complete). Two distinct-named-lens fresh-eye reviews + a rung-2
  disposition review all clean.
- **v0.56.8 is published and verified — it resolves D30 (dup-ratchet id-rotation).**
  `origin/main` synced; tag `v0.56.8` points at `2f4e76e1`. (Detail archived; the
  D30 follow-on residuals remain deferred and not urgent.)

## Next Session

- **Push the #405 carrier** to default branch to auto-close #405, then verify
  `gh issue view 405` shows CLOSED. (Out-of-band publication; `achieve` does not
  push.)
- Pre-existing uncommitted churn in `charness-artifacts/find-skills/latest.*`
  (a prior session's inventory refresh, support-skills 7→4) was left out of the
  #405 commit — commit it separately or re-run `find-skills --write-artifact`.
- **Next quality loop:** start with `quality` for gate posture, then `impl` one
  narrow slice. D30 follow-on residuals (S4-Defer-1, S4-Defer-3) reopen only on
  observed re-baseline friction.

## Discuss

- A `nose v0.16.0` upgrade is advisory-available; bumping the installed nose would
  regroup families and trigger the scanner-version skew WARNING -> a one-time
  lockstep re-baseline (by design, not a defect).

## References

- [spec Slice 4 (D30, DONE)](../charness-artifacts/spec/boy-scout-dup-ratchet.md)
- [deferred-decisions D30 (resolved)](./deferred-decisions.md)
- [release notes v0.56.8](../charness-artifacts/release/notes-v0.56.8.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
