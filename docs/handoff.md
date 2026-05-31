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

- `main` is aligned with `origin/main` before this handoff refresh; no push or
  release action is part of the current pickup.
- A shaped achieve goal is ready:
  [current autonomous hardening tranche](../charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md).
  It is `draft`, passes `check_goal_artifact.py`, and passes `--pursue-ready`.
- The goal intentionally narrows "all autonomous work" to the closed tranche
  #268, #269, #264, #270, and the mechanical portion of #265/#261. It excludes
  product/metric work (#184/#185), broad backlog expansion, live issue mutation,
  push, and release unless a slice stops and re-plans.
- #268 is the hard first phase gate before later issue-closeout work; #269
  follows immediately because stale mutable-HEAD wording can affect this goal's
  own final proof; #270 stays adjacent to #265/#261 mutation triage.

## Next Session

1. Activate and pursue:
   `/goal @charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`.
2. During slice 0, refresh live issue context and re-run pursue-ready before
   mutating. Proceed slice-to-slice only after each slice's expected evidence is
   recorded in the goal `## Slice Log`.
3. If the goal blocks on a product/gate-policy/live-mutation decision, stop and
   update this handoff with the exact blocker instead of expanding scope.

## Discuss

- **Issue-source non-gh path is unproven live** (stub-tested only). If a non-gh
  host adopts charness, exercise the `issue_backend.commands.list_open` override
  before trusting the backlog union there.
- This session hit the #258 echo-flood trap again (batched tool calls under
  delayed output → cascade cancels). Prefer serial tool calls when output
  latency is unstable.
- The autonomous tranche deliberately defers #258/#259/#252/#243/#241/#237/#236;
  re-rank them after the goal completes or blocks.

## References

- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [current autonomous hardening tranche](../charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md)
