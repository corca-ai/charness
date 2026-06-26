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

- **v0.55.1 release is in progress for #401 closeout.** It carries the completed
  `retro`/`critique`/`spec`/`impl` quality-led reviews and critique packet
  ownership fix; active installed sessions need update/restart after publish.
- **Quality claim-fidelity (#397), Cautilus diagnostics (#398), issue planner,
  and gather terminal records have shipped locally.** Planner-first closeout is
  live for `issue`, `handoff`, and adjacent workflows; `cautilus evaluate *`
  remains operator-gated.

## Next Session

- **START HERE -- choose dogfood mode deliberately.** For installed-plugin
  dogfood, cut/push the next release and refresh the install first. If release
  is deferred, use repo-local helper paths and call it source-tree proof.
- **#401 quality run is handled.** `spec`/`impl` evaluator-backed dogfood remains
  a later behavior-proof lane, not #401 scope.
- **Open gather lane remains #392 under `quality`/`gather`.** Durable terminal
  records are done; remaining work is richer verdict taxonomy
  (`auth/browser-required`, `provider-required`, unsupported) and/or a proven
  exact-source acquisition route.
- **Web-fetch route helper split is no longer current:** [route_public_fetch.py](../skills/support/web-fetch/scripts/route_public_fetch.py)
  is 85/360 Python code lines as of the continuation quality pass. Continue
  #392 from current gather/web-fetch behavior evidence instead of splitting
  this helper.
- **Then build per-skill Cautilus fixtures.** Fixtures should not coach the
  target skill; observe the early run shape, keep logs, and stop early if drifting.
- **Open issue queue:** #392 gather-X acquisition/taxonomy, #371 agent-browser
  cleanup; #401 is release-linked closeout only.

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
