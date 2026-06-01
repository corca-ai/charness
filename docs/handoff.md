# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` → **invoke `charness:handoff`**. A bare
  `/handoff` fires chunked routing (#249); the chunker unions the **live
  open-issue backlog** with the list below, so `## Next Session` is a
  curation/sequencing memo, not the full queue. Then read
  [quality latest](../charness-artifacts/quality/latest.md) +
  [recent lessons](../charness-artifacts/retro/recent-lessons.md).
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- Local `main` has #277 closed on `225898a3`; check live
  `git status --short --branch` before assuming the worktree is clean. The
  active workflow-review goal has completed Slice 1's read-only `find-skills`
  recommendation, issue-closeout binding, active-goal handoff filtering, and
  deterministic `Issue closeout:` coordination floor.
- The mutation recovery goal is complete:
  [#273/#261 mutation recovery](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md).
  The carrier closes #273 and leaves #261 open intentionally as a
  mutation-standard policy question.
- #261 and #184 remain the live carry-forward issues; #184 needs product-success
  synthesis from the maintainer's newer thinking and source thread.
- Active workflow-review goal exists:
  [workflow review efficiency and generalization](../charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md).
  Next slice is critique cadence, then invariant-first bug review.

## Next Session

1. Continue
   `/goal @charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`.
   Slice 1 is complete; continue with slice-level critique cadence and
   invariant-first review guidance.
2. After that goal is completed or paused, pick #184 for product-success
   synthesis or #261 for the mutation-standard policy decision.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- Long goals should treat cached input as a context-pressure signal, not direct
  waste. The stronger efficiency signals are compactions, repeated
  status/diff/check commands, polling, and broad-gate cadence.
- #261's remaining coordination-cues survivors are policy residue after the
  mechanical hardening path, not another #273 coverage fix.
- If a future bare handoff pickup offers setup checks, completed goals, or
  cadence constraints as choices, inspect the parser filter before blaming the
  handoff prose.
- For the workflow-improvement goal, decide before activation whether one
  startup `find-skills` pass stays mandatory but quiet/read-only by default, and
  whether fresh-eye critique should run at slice/bundle boundaries rather than
  every commit.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [mutation recovery goal](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md),
  [mutation recovery carrier](../charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md)
- [workflow review efficiency goal](../charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md)
