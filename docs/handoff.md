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

- **Local skill-improvement bundle is committed but not released.** `main` is
  clean and `origin/main..HEAD` has four commits:
  `29bb95d8` retro quality review, `ff1d8bee` quality structural review,
  `14859b64` branch coverage, and `62b41b32` release update-instructions
  decoupling. Full `./scripts/run-quality.sh --read-only` passed 79/79 after
  the final commit.
- **Installed plugin sessions still see 0.54.2 until release/update.** A fresh
  Codex/Claude session that invokes `charness:quality` from the installed plugin
  cache will not automatically include these local skill changes.
- **Quality claim-fidelity shipped (#397 closed).** `quality` now separates
  deterministic gates from judgment/ref pass and preserves engage-always,
  on-demand, and gate-sufficient reference routing.
- **Cautilus diagnostic artifact home shipped (#398).** Negative diagnostics live in `charness-artifacts/cautilus/<run-slug>/finding.md`; `latest.md` is passing proof only.
- **Issue planner/core split DONE** (2026-06-24): `issue_tool.py plan` carries required/on-demand reads and gate packets; fresh-eye fixed target handling and brittle tests.
- **Gather planner / Reddit / exact-X terminal records SHIPPED** (2026-06-24):
  `gather_plan.py` fronts public URL gather; Reddit uses RSS -> JSON; X/Twitter
  status `exact-blocked` / `exact-unavailable` writes trace-only terminal records
  while non-status X and generic blocked/degraded URLs do not refresh `latest.md`.
  Critique: [2026-06-24-gather-exact-terminal-records.md](../charness-artifacts/critique/2026-06-24-gather-exact-terminal-records.md).
- **Planner-first closeout is live** for `issue`, `handoff`, and adjacent workflows; `cautilus evaluate *` remains operator-gated.

## Next Session

- **START HERE -- choose dogfood mode deliberately.** If the goal is to rerun the
  improved installed `quality` skill against `retro`, first cut/push the next
  release and run the install refresh/update path. If release is still deferred,
  use repo-local quality helper paths explicitly and treat the result as
  source-tree proof, not installed-plugin dogfood.
- **Continue #401 after that.** Run the improved `quality` skill against
  `retro`, then `critique`, `spec`, and `impl` one at a time; treat any
  `quality` miss as evidence about `quality` itself.
- **Open gather lane remains #392 under `quality`/`gather`.** Durable terminal
  records are done; remaining work is richer verdict taxonomy
  (`auth/browser-required`, `provider-required`, unsupported) and/or a proven
  exact-source acquisition route.
- **Continue the same planner-first pattern.** `issue`, `release`, `gather`, `handoff`, and `achieve` closeout affordances now carry the pattern; neutral issue planner-use fixture is still deferred.
- **Split remaining near-limit web-fetch helper before more route behavior:** [route_public_fetch.py](../skills/support/web-fetch/scripts/route_public_fetch.py).
- **Then build per-skill Cautilus fixtures.** Fixtures should not coach the
  target skill; observe the early run shape, keep logs, and stop early if drifting.
- **Open issue queue:** #401 quality-led skill improvements, #392 gather-X
  acquisition/taxonomy, #371 agent-browser cleanup.

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
