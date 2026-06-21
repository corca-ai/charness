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

- **Essence/deletion rollout — `impl`, `debug`, `quality` shipped.** Distill to
  essence and **DELETE** duplication, not relocate. `impl`/`debug`: unpinned-dup
  only (zero contract/test edits). **`quality` opened the pins** — deleted 2 CORE
  rows in `check_skill_contracts.py` that froze doubled step-7 wording (CORE 7→5),
  cautilus guard kept; fresh-eye `DISCIPLINED-PIN-DELETION` **licenses a
  harness-wide sweep** (`## Next Session`). critiques:
  [impl](../charness-artifacts/critique/2026-06-21-impl-essence-deletion.md),
  [debug](../charness-artifacts/critique/2026-06-21-debug-essence-deletion.md),
  [quality](../charness-artifacts/critique/2026-06-21-quality-pin-opening.md).
- **Item A DONE — `main` green + #394 coverage (test-only).** Stale `make_fake_nose`
  fixture (`0.13.3` vs the `>=0.14.0` floor) fixed; suite green (2283 + 1189);
  #394 changed-line target covered + `build_items` boundary mutants pinned. The
  mutation gate is cron-only (auto-closes #394 on the next tick) — operator
  dropped it as a blocker; it no longer gates the sweep.

## Next Session

> Operator agreed to **open the pins**: a gate-pinned skill contract is now
> deletable under a disciplined test — a pin earns deletion only when it (a)
> freezes wording rather than proving behavior, or (b) the behavior is owned
> canonically elsewhere (`CLAUDE.md` / a reference / another gate). Deleting a pin
> deletes its test + contract row. **Body-read each issue — titles undersell.**

- **A (lead) — harness-wide pin sweep (licensed by the `quality` pilot).** Apply
  the disciplined pin test to every CORE/PACKAGE row in `check_skill_contracts.py`:
  delete pins that freeze wording or are owned canonically elsewhere; **keep**
  destructive-boundary guards (cautilus, publish confirmation). Promote the
  pin-deletion test to a durable convention. **Friction:** each pin edit
  re-partitions `check_skill_contracts.py` clones → count-neutral
  `check_dup_ratchet.py --write-baseline` per push (or extract the 3 twin
  validators once to stabilize it). The quality 49-ref reduction is a separate
  per-file deletion audit (`validate_skills` locks the list to the directory —
  not a trim, and `index.md` relocation is the rejected not-the-point move).
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
