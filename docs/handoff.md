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
- The active achieve goal is in final closeout:
  [current autonomous hardening tranche](../charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md).
  Slices for #268, #269, #264, #270, and the mechanical portion of #265/#261 are
  complete and recorded in the goal `## Slice Log`.
- #265/#261 mechanical mutation triage stopped at clearly real survivor kills.
  Scoped trio inventory finished at 514/514 executed, 467 killed, 47 survived,
  score 90.9%; remaining survivors are recorded as equivalent/low-value or
  policy-bound non-claims.
- Final closeout evidence lives in the goal artifact, retro artifact, host-log
  probe JSON, and disposition review. Remote CI and live GitHub closure remain
  explicit non-claims.

## Next Session

1. Verify the final local state: `git status --short --branch` and
   `git log --oneline origin/main..HEAD`.
2. If publishing is desired, push the branch and open/prepare a PR from the
   local commits; do not silently close live GitHub issues without maintainer
   confirmation.
3. Re-rank the remaining backlog after this tranche. Product/metric work
   (#184/#185), equivalent-mutant policy, release policy, and broad backlog
   grooming remain outside the completed autonomous goal.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.
- The autonomous tranche deliberately deferred #258/#259/#252/#243/#241/#237/#236;
  re-rank them after publish/PR handling.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [current autonomous hardening tranche](../charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md),
  [session retro](../charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md)
