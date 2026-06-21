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

- **Pin sweep shipped** (pushed, `main` clean): validator fold (`1f58af89`) +
  harness-wide pin audit (`18467e56`, **126/128 keep**, 2 wording-freeze deleted,
  disciplined pin-deletion test now a convention in the gate header). Gotcha:
  every `check_skill_contracts.py` edit re-rotates the validator clone family ->
  count-neutral dup-ratchet re-baseline (526->526); expect it on the next edit.
- **Skill-structure audit DONE (read-only, nothing committed but the map).**
  Raskin + north-star fan-out over all 20 public skills:
  **split = 0, merge = 0, structure healthy**; body length is ratchet-capped
  (not a lever). The only recurring flag was reference duplication — but the
  **`quality` ref-dedup pilot proved those flags are mostly false positives**:
  all 3 quality flags are load-bearing/test-pinned (deleting `quality-lenses.md`
  broke 3 tests; `skill-quality`/`skill-ergonomics` are wired into ~15 tests).
  Same outcome as the pin sweep: the surface is already disciplined. Full map +
  per-skill leads: [2026-06-21 audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md).

## Next Session

- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Ref-dedup rollout (deferred, was "B"):** NOT a deletion sweep. Per-skill flags
  in the audit map are a "where to look" hint only — **verify each against the
  test suite first** (pilot false-positive rate was 3/3). Real fixes are
  content-move refactors (move pinned bullets + their tests, then retire), not
  deletes. Low expected yield; metric stays concept clarity.
- **Parked:** #394 (mutation cron-only, auto-closes). #371 (upstream-blocked
  vercel-labs/agent-browser#1334). #391 extraction candidates.

## Discuss

- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale (done again this session).

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md),
  [skill-structure audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md);
  pin-sweep convention lives in the
  [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
