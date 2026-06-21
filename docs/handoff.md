# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff entries + live open issues. `## Next Session` is
  sequencing judgment, not the full queue — **body-read the issues, don't trust it flat.**
- Refresh: `git status -sb`, `git log --oneline origin/main..HEAD`,
  `gh issue list --state open --limit 50`, and skim `git log --oneline -10`
  (de-stale the queue against what recently shipped). Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) +
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Essence/deletion redesign — `impl` exemplar EXECUTED + PUSHED** (@ `6791cf4f`).
  Distill to essence and **DELETE** duplication, not relocate. Lever: **the gate
  pins mark the load-bearing essence, so delete the unpinned duplication around
  them** (zero `check_skill_contracts.py`/test edits). Guardrails 9→2 via
  `achieve`'s name-the-rule template; step 4 13→4 by deferring to
  `verification-ladder.md`; 194→187; 2 fresh-eye `ESSENCE-PRESERVED`/`CONTRACT-HONEST`.
  [critique](../charness-artifacts/critique/2026-06-21-impl-essence-deletion.md).
- **Operator agreed (2026-06-21) to OPEN THE PINS** next — see `## Next Session`.
  The impl cut was modest (7 lines) because unpinned-dup-only is the safe ceiling;
  the deeper "less is more" is challenging the pins themselves.
- **`main` red by one (environmental):** the `nose doctor` version-mismatch test
  fails on clean HEAD too (this machine's nose vs the manifest). Item A owns it.

## Next Session

> Operator agreed to **open the pins**: a gate-pinned skill contract is now
> deletable under a disciplined test — a pin earns deletion only when it (a)
> freezes wording rather than proving behavior, or (b) the behavior is owned
> canonically elsewhere (`CLAUDE.md` / a reference / another gate). Deleting a pin
> deletes its test + contract row. **Body-read each issue — titles undersell.**

- **A — Green `main` + #394 (FIRST — protect the oracle).** Opening pins deletes
  tests, and the green suite is the losslessness oracle, so it must be trustworthy
  before any pin comes out. Diagnose the standing-red `nose doctor`
  version-mismatch (machine nose vs manifest); triage #394's 12 survived
  *config-literal* mutants (`init_adapter.py` / `resolve_adapter.py` `...: True`).
  Score passes (90% vs 80%).
- **B — Essence rollout with pin-opening.** `debug` first (safe: the thrice-printed
  `issue resolve invokes the same substrate` cross-ref + helper-duplicating
  Bootstrap prose — unpinned dup, re-proves the recipe). Then **`quality` as the
  pin-opening pilot:** the anchor-split only *relocated* (191 body, **49 refs**) —
  delete the anchors that fail the pin test (drop their dispatch entry + test pin)
  and fold/kill reference sprawl, not just trim the body.
- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Parked:** #371 (upstream-blocked vercel-labs/agent-browser#1334). #391
  extraction candidates. D30/D31 in [deferred-decisions.md](./deferred-decisions.md).

## Discuss

- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale (done again this session).

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [north-star sweep goal](../charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md),
  [deferred-decisions](./deferred-decisions.md)
