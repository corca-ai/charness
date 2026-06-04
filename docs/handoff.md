# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- Portable skill contract quality goal is complete:
  [goal artifact](../charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md).
  It added package-level portable skill text-quality checks, cleaned concrete
  issue/date anchors from portable skill packages, promoted issue/date leakage
  to blocking skill-ergonomics rules, tightened `achieve` phase-routing
  evidence, and added an `achieve` reference index.
- Final locked closeout passed with broad pytest in 297.5s; no live Cautilus run
  or installed-host cleanup is claimed. Retro is persisted at
  [portable skill closeout retro](../charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md).
- Follow-up issues filed from the retro:
  #295 closeout test-selection cost, #296 bounded reviewer cost/tier visibility.
  Existing open work #184, #293, and #294 remains outside the completed goal.
- Local `main` is ahead of `origin/main` by the portable-skill goal commits plus
  this closeout commit once committed; push is still a maintainer/operator
  decision.

## Next Session

1. If publishing this local work, inspect `git log --oneline origin/main..HEAD`
   and run the repo's push path; expect the pre-push read-only quality gate.
2. If continuing quality work instead, route through `find-skills` then
   `quality` for #295. Keep #296 as a separate review-cost visibility issue
   unless the same surface naturally owns both.
3. Do not reopen the completed portable skill goal unless current verification
   contradicts its final evidence.

## Discuss

- #295 should decide how pre-lock slice proof differs from final
  verification-lock broad proof, rather than only increasing budgets.
- #296 should record whether reviewer model/tier is repo-selected,
  host-defaulted, or unavailable, because subagent cost surprised the user in
  this closeout.
- `host_surface_reference=104` is intentionally advisory/deferred, not a
  blocking portability violation from the completed goal.

## References

- [portable skill contract quality goal](../charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md)
- [closeout retro](../charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
