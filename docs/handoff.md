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

- **Quality reference disposition SETTLED** (2026-06-21): 41-ref merit map -> **7
  route-it + 2 merge-retire, 0 deletes**; blind A/B **7/7 reach-via-pointer**.
  [disposition](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
- **Quality claim-fidelity shipped (#397 closed).** `quality` now separates
  deterministic gates from judgment/ref pass and preserves engage-always,
  on-demand, and gate-sufficient reference routing.
- **Cautilus diagnostic artifact home shipped (#398).** Negative diagnostics live
  in `charness-artifacts/cautilus/<run-slug>/finding.md`; `latest.md` is passing
  proof only.
- **Quality gate health review DONE** (2026-06-23): full read-only quality was
  78/78 PASS in 38.7s; [nose-baseline.json](../charness-artifacts/quality/nose-baseline.json)
  is re-baselined to nose 0.15.0.
- **Issue planner/core split DONE** (2026-06-24): `issue_tool.py plan` carries
  required/on-demand reads and gate packets; `SKILL.md` core went 148 -> 69 lines.
  Fresh-eye fixed ignored `plan --intent resolve --target` and brittle tests.
- **#399 disposition:** run `28049447961` proved old `Select mutation sample` /
  missing Stryker report failure is gone; still open because StrykerJS score is
  49.7% vs 80%.
- **Gotcha:** `/charness:quality` loads from the INSTALLED clone
  `~/.agents/src/charness` -- isolate per-run via
  [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh) (never edit
  the clone). `cautilus evaluate *` is operator-gated. Cautilus is now **0.17.1**
  (harness re-verified); `charness tool update` warns when a manual tool is behind.

## Next Session

- **START HERE -- resolve or explicitly defer #399's JS mutation-score failure.**
  Body-read #399; latest run changed the problem from missing report to real
  StrykerJS score failure.
- **Then continue fanning out the same quality pattern.** `issue` and `release`
  now have it; neutral issue planner-use fixture is still deferred.
- **Then build per-skill Cautilus fixtures.** Fixtures should not coach the
  target skill; observe the early run shape, keep logs, and stop early if drifting.
- **Then use Cautilus to improve behavior.** Preserve intent while reducing wasted
  time/cost; diagnostic findings go through the #398 bundle path, not `latest.md`.
- **Open issue queue:** #399 JS mutation score, #396 handoff lifecycle/linter,
  #392 gather-X honest failure contract, #387 one-pass goal-closeout shape
  report, #371 upstream agent-browser cleanup.

## Discuss

- **Gate review follow-up:** add aggregate runtime budgets for
  `run-quality-read-only` and `check-duplicates` only after another drift sample.
- **#392 scope (decide at pickup):** attempt a real exact-X route (browser/auth,
  likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale.

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md), [deferred-decisions](./deferred-decisions.md);
  pin-sweep convention lives in the [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
