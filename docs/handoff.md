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

- **Essence/deletion rollout — `impl` (`6791cf4f`) + `debug` shipped.** Distill to
  essence and **DELETE** unpinned duplication, not relocate; **gate pins mark the
  load-bearing essence, so delete the unpinned dup around them** (zero
  contract/test edits). debug: 4× `issue resolve` substrate cross-ref → 1×
  (causal-review.md owns the lens↔step map) + helper-bullet fold, 193→185,
  fresh-eye `ESSENCE-PRESERVED`. Open-the-pins is in `## Next Session`. critiques:
  [impl](../charness-artifacts/critique/2026-06-21-impl-essence-deletion.md),
  [debug](../charness-artifacts/critique/2026-06-21-debug-essence-deletion.md).
- **Item A DONE — `main` green + #394 coverage (test-only).** Standing-red was a
  stale fixture (`make_fake_nose` `0.13.3` vs the bumped `>=0.14.0` floor → doctor
  read `version-mismatch`); fixed to `0.14.0`. Suite green (2283 + 1189). #394's
  changed-line target (`nose_report_lib.py:178`) covered + `build_items`
  boundary-default mutants pinned; 1 fresh-eye `HONEST-AND-FAITHFUL`.
  [critique](../charness-artifacts/critique/2026-06-21-green-main-394-coverage.md).
  **#394 closure awaits the next CI mutation run — verify PASS, don't hand-close.**

## Next Session

> Operator agreed to **open the pins**: a gate-pinned skill contract is now
> deletable under a disciplined test — a pin earns deletion only when it (a)
> freezes wording rather than proving behavior, or (b) the behavior is owned
> canonically elsewhere (`CLAUDE.md` / a reference / another gate). Deleting a pin
> deletes its test + contract row. **Body-read each issue — titles undersell.**

- **A — Green `main` + #394 — DONE this session.** Oracle is trustworthy:
  whole suite green; the changed-line blocking target is covered; the
  irreversible-boundary `build_items` mutants are pinned. Remaining: confirm the
  next CI mutation run flips #394 to PASS (do not hand-close).
- **B (now lead) — `quality` as the PIN-OPENING pilot.** `debug` done (safe, no
  pins). `quality` is the consequential first real pin-opening: the anchor-split
  only *relocated* (191 body, **49 refs**) — apply the disciplined pin test, delete
  the anchors that fail it (drop their dispatch entry + test pin), and fold/kill
  reference sprawl, not just trim the body. Surface the specific pinned-contract
  deletions before committing — this is the operator-flagged frontier.
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
