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

- Local `main` is clean and synced with `origin/main`.
- The open-issue generative closeout goal is complete:
  [handoff/open-issue generative closeout](../charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md).
  Final carrier closed #272/#265/#259/#258/#252/#243/#241/#237/#236/#185;
  #261 and #184 remain open intentionally with carry-forward comments.
- A new draft achieve goal is ready to activate:
  [achieve long-goal efficiency and effectiveness](../charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md).
  It targets active-context control, verification cadence, slice review packets,
  and automatic efficiency retro suggestions for intentionally broad goals.

## Next Session

1. Verify local state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. Activate the new draft goal when ready:
   `/goal @charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`.
3. During that goal, preserve the proof cadence: cheap deterministic checks at
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
- #184 needs a separate product-success synthesis from the maintainer's newer
  thinking and the source thread; do not collapse it into #185.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [completed open-issue closeout goal](../charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md)
- [draft achieve efficiency goal](../charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md)
