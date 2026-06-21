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
- **Skill-structure audit DONE.** Raskin + north-star fan-out, 20 public skills:
  split=0, merge=0, structure healthy. [audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md).
- **Quality reference disposition critiqued + EXECUTED.** The 41-ref merit map was
  adversarially critiqued (10-skeptic fan-out) then applied: **7 route-it + 2
  merge-retire (files deleted), 0 deletes.** The critique corrected 4 anchors
  (incl. a non-existent dispatch target), redirected both merges off the largest
  ref, and added 2 route-it the draft missed. Full pin sweep green (validate_skills
  / check_skill_contracts / 2283 quality_gates tests / doc-links / dup-ratchet);
  mirror synced. Outcome + corrections:
  [disposition proposal `## EXECUTED`](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).

## Next Session

- **START HERE — empirical validation (LOCKED plan step 2).** Critique + apply are
  DONE; run `cautilus evaluate skill-experiment` on the post-fix quality skill: a
  few BLIND per-lens scenarios, per-scenario `sourceCoverageObligations` (NOT all
  41 — all-in-one-run is the anti-goal), baseline-vs-variant. Eval-only/
  ask-before-run — consult `plan_cautilus_proof.py`, refuse on `next_action: none`,
  route via `run_cautilus_eval.py`. A ref uncovered ACROSS scenarios is only then a
  candidate (same disciplined verify, never auto-delete). Full design:
  [proposal LOCKED plan](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
  **Push is HELD:** the 4 local commits (`ahead 4`) stay unpushed until this
  validation confirms the routing — operator chose strict fix→validate→publish.
  The broader 19-skill rollout stays a verify-first "where to look" map.
- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
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
  [skill-structure audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md),
  [quality ref disposition proposal](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md);
  pin-sweep convention lives in the
  [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
