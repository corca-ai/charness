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

- New improvement goal is shaped but not activated:
  [portable skill contract quality and routing](../charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md),
  backed by
  [RCA](../charness-artifacts/debug/2026-06-04-portable-skill-contract-quality-and-routing.md).
  It treats issue-number leakage as one symptom of broader portable skill text
  quality: repo-local history leakage, overfull cores, weak reference
  discoverability, host assumptions, repeated prose ritual, exact-prose/source
  guard risk, and `achieve` absorbing `impl`/`debug`.
- Released **v0.17.0**; real-host follow-up remains unrun for clean
  `charness update` and `tokei` doctor/install.
- Local future-work-efficiency closeout commit `f66d484d` stages close keywords
  for #285, #286, #287, #288, and #289. Those issues remain OPEN until that
  commit is pushed and post-push verification passes.
- #293 and #184 remain open and deferred unless the new text-quality work
  directly trips their owning quality/product surfaces.

## Next Session

1. If branch `main` is still unpushed, push it and verify the prior
   #285/#286/#287/#288/#289 closeout carrier against `f66d484d`:
   `python3 skills/public/issue/scripts/issue_tool.py verify-closeout --repo-root . --repo corca-ai/charness --number 285 --number 286 --number 287 --number 288 --number 289 --classification feature --carrier direct-commit --commit-ref f66d484d --expect-state CLOSED`.
   Then activate
   `/goal @charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md`
   and start Slice 1 with `find-skills` routing, the RCA, and baseline skill
   text-quality inventories. Do not use a memorized exhaustive phase-to-skill
   table; decide the owning skill at each boundary and use short anchors only
   for easy-to-miss cases like implementation -> `impl` and bug/RCA work ->
   `debug`.

## Discuss

- Skill text quality is broader than issue-number leakage. Treat concrete issue
  anchors as one subtype inside the portable skill text contract.
- For future workflow-improvement goals, keep one startup `find-skills` pass,
  read-only recommendation probes at real routing boundaries, and slice/bundle
  fresh-eye critique.
- `achieve` should self-route through `find-skills`, not carry a hard-coded
  list of every skill. The next goal should add anchors only where the prior run
  proved the boundary is easy to miss.
- Long-goal waste signal is not cached input alone. Stronger signals are
  compactions, repeated status/diff/check commands, polling, and broad-gate
  cadence.

## References

- [portable skill contract quality goal](../charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md),
  [RCA](../charness-artifacts/debug/2026-06-04-portable-skill-contract-quality-and-routing.md)
- [quality latest](../charness-artifacts/quality/latest.md),
  [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [testability quality ratchet goal](../charness-artifacts/goals/2026-06-03-testability-quality-skill-ratchet.md)
