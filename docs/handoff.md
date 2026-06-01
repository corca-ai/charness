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

- Local `main` is ahead of `origin/main` with the open-issue closeout tranche;
  no release is planned. Final carrier publication and live issue state updates
  are the remaining active-goal work.
- The active achieve goal is
  [handoff/open-issue generative closeout](../charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md).
  Slices 0-6 are complete. Slice 7 final carrier is in progress: final proof,
  final handoff/goal/retro artifacts, push, and live GitHub close/comment.
- The current issue matrix covers all 12 open issues: #272, #265, #261, #259,
  #258, #252, #243, #241, #237, #236, #185, and #184. #184 product success is
  intentionally left open; #261 mutation-standard policy is intentionally left
  open; #185 closes on necessary engineering-success conditions only.
- Current branch proof at Slice 7 start: branch was
  `main...origin/main [ahead 18]`, HEAD is
  `517b734 Record AI ML success goal progress`.

## Next Session

1. Verify the final local state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. Continue Slice 7 final carrier from
   [2026-06-01-open-issue-final-carrier.md](../charness-artifacts/issue/2026-06-01-open-issue-final-carrier.md):
   run final proof, commit final artifacts, push, then verify/close the live
   issue rows.
3. Close #272/#265/#259/#258/#252/#243/#241/#237/#236/#185 through the final
   carrier. Comment but leave #261 and #184 open intentionally.

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
