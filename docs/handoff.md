# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues. `## Next Session` is sequencing
  judgment, not the full queue: **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Local #401 skill-improvement bundle is committed locally but not released.**
  It includes the quality-led `retro` pass, retro prepare-packet support, the
  follow-up correction to the quality review finding, and this validator slice:
  future/current retro artifacts now have a machine-readable persisted-status
  floor, and quality artifacts now fail stale explicit skill ergonomics counts.
- **Installed plugin sessions still see 0.54.2 until release/update.** A fresh
  Codex/Claude session that invokes `charness:quality` from the installed plugin
  cache will not automatically include these local skill changes.
- **Quality claim-fidelity (#397), Cautilus diagnostics (#398), issue planner,
  and gather terminal records have shipped locally.** Planner-first closeout is
  live for `issue`, `handoff`, and adjacent workflows; `cautilus evaluate *`
  remains operator-gated.

## Next Session

- **START HERE -- choose dogfood mode deliberately.** For installed-plugin
  dogfood, cut/push the next release and refresh the install first. If release
  is deferred, use repo-local helper paths and call it source-tree proof.
- **Continue #401 with `spec` next.** The `retro` and `critique` quality passes
  have been handled; next run improved `quality` against `spec`, then `impl`,
  and treat any `quality` miss as evidence about `quality` itself.
- **Open gather lane remains #392 under `quality`/`gather`.** Durable terminal
  records are done; remaining work is richer verdict taxonomy
  (`auth/browser-required`, `provider-required`, unsupported) and/or a proven
  exact-source acquisition route.
- **Split remaining near-limit web-fetch helper before more route behavior:** [route_public_fetch.py](../skills/support/web-fetch/scripts/route_public_fetch.py).
- **Then build per-skill Cautilus fixtures.** Fixtures should not coach the
  target skill; observe the early run shape, keep logs, and stop early if drifting.
- **Open issue queue:** #401 continues with `critique`/`spec`/`impl`, #392
  gather-X acquisition/taxonomy, #371 agent-browser cleanup.

## Discuss

- **Gate review follow-up:** add aggregate runtime budgets for
  `run-quality-read-only` and `check-duplicates` only after another drift sample.
- **#392 scope:** typed durable terminal records exist; auth/browser/provider
  states remain. Decide whether to handle in `support/web-fetch` or via #371.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale.

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md), [deferred-decisions](./deferred-decisions.md);
  pin-sweep convention lives in the [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
