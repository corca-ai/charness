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
- A new draft achieve goal is ready to activate:
  [achieve long-goal efficiency and effectiveness](../charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md).
  It targets active-context control, verification cadence, slice review packets,
  and automatic efficiency retro suggestions for intentionally broad goals.

## Next Session

1. Verify local state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. Pick the next issue explicitly: #184 for product-success synthesis, or #261
   for the mutation-standard policy decision around equivalent/low-value
   survivors.
3. Activate the draft efficiency goal only when broad goal workflow work is the
   intended next slice:
   `/goal @charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.
4. During any broad goal, preserve the proof cadence: cheap deterministic checks at
   commit boundaries, higher-cost critique/validation at slice boundaries, and
   final broad proof.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.
- Long goals should treat cached input as a context-pressure signal, not direct
  waste. The stronger efficiency signals are compactions, repeated
  status/diff/check commands, polling, and broad-gate cadence.
- #261's remaining coordination-cues survivors are policy residue after the
  mechanical hardening path, not another #273 coverage fix.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [mutation recovery goal](../charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md),
  [mutation recovery carrier](../charness-artifacts/issue/2026-06-01-273-261-mutation-gate-recovery.md)
- [draft achieve efficiency goal](../charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md)
