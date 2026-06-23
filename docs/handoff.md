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
  route-it + 2 merge-retire, 0 deletes**; "un-routed != worthless, defect is a
  discoverability gap not bloat"; blind A/B **7/7 reach-via-pointer**. Treat ref
  value as decided; deletion reopens only on the gate-sufficiency axis.
  [disposition](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
- **Quality skill claim-fidelity remediation shipped (#397 closed).** The real
  isolated `/charness:quality` reject exposed execution shape, not reference
  value. The skill now separates deterministic gates from the judgment/ref pass
  and preserves the 3-way reference lens: engage-always, on-demand, and
  gate-sufficient.
- **Cautilus diagnostic artifact home shipped by the current closeout (#398).**
  Negative or diagnostic Cautilus verdicts live in
  `charness-artifacts/cautilus/<run-slug>/finding.md` plus machine evidence,
  validated by
  [validate_cautilus_diagnostics.py](../scripts/validate_cautilus_diagnostics.py);
  `latest.md` remains only the passing proof carrier.
- **Quality gate health review DONE** (2026-06-23): full read-only quality was
  78/78 PASS in 38.7s; current deterministic gates are healthy as evidence
  packets, not a replacement for judgment.
  [nose-baseline.json](../charness-artifacts/quality/nose-baseline.json) was
  re-baselined to nose 0.15.0; next budget work needs another drift observation.
- **Gotcha:** `/charness:quality` loads from the INSTALLED clone
  `~/.agents/src/charness` -- isolate per-run via
  [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh) (never edit
  the clone). `cautilus evaluate *` is operator-gated. Cautilus is now **0.17.1**
  (harness re-verified); `charness tool update` warns when a manual tool is behind.

## Next Session

- **START HERE -- fan out the same quality pattern to other skills.** Do not
  start by mass-editing; first identify which skill references are engage-always,
  on-demand, or gate-sufficient, and whether a repo script should tell the agent
  the next review action.
- **Then build per-skill Cautilus fixtures.** Fixtures should not coach the
  target skill; observe the early run shape, keep logs, and stop early if drifting.
- **Then use Cautilus to improve behavior.** Preserve intent while reducing wasted
  time/cost; diagnostic findings go through the #398 bundle path, not `latest.md`.
- **Open issue queue:** #396 handoff lifecycle/linter, #392 gather-X honest
  failure contract, #387 one-pass goal-closeout shape report, #371 upstream
  agent-browser cleanup.

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
