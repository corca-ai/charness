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

- Local `main` is ahead of `origin/main` with the autonomous hardening tranche;
  no push, release, or live GitHub issue mutation has been performed.
- The active achieve goal is
  [handoff/open-issue generative closeout](../charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md).
  Slices 0-3 are complete: #272 report clarity, #265/#261 disposition, and
  workflow-safety issues #258/#259/#237/#236. Slice evidence lives in the goal
  `## Slice Log`.
- The current issue matrix covers all 12 open issues: #272, #265, #261, #259,
  #258, #252, #243, #241, #237, #236, #185, and #184. #184 product success is
  intentionally left open; #185 is limited to necessary engineering-success
  conditions.
- Current branch proof after Slice 3: `main...origin/main [ahead 11]`, HEAD
  `d1970c1 Record workflow safety goal progress`.

## Next Session

1. Verify the final local state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. Continue the active goal at Slice 4: resolve #252/#241 together by making
   setup accept compact AGENTS contracts and making create-skill adapter
   metadata extensible through host-owned fields.
3. Then handle Slice 5 #243 usage episodes, Slice 6 #185 necessary engineering
   success while leaving #184 open, and Slice 7 final carrier. Do not push or
   mutate live GitHub issues before the final carrier.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.
- #184 needs a separate product-success synthesis from the maintainer's newer
  thinking and the source thread; do not collapse it into #185.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [active open-issue closeout goal](../charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md)
