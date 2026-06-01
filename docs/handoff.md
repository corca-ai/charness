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

- Local `main` contains the #273/#261 mutation gate recovery carrier and should
  be clean/synced after the closeout push.
- The mutation recovery goal is complete:
  [#273/#261 mutation recovery](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md).
  The carrier closes #273 and leaves #261 open intentionally as a
  mutation-standard policy question.
- #261 and #184 remain the live carry-forward issues; #184 needs product-success
  synthesis from the maintainer's newer thinking and source thread.
- Draft next-session goal exists:
  [workflow review efficiency and generalization](../charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md).

## Next Session

1. Discuss and, if accepted, activate
   `/goal @charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`.
   It targets reduced `find-skills` noise, slice-level critique cadence,
   invariant-first bug review, sibling-pattern scans, and disposition of
   improvements.
2. After that goal is accepted or deferred, pick #184 for product-success
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
