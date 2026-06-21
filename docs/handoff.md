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
- **Skill-structure audit DONE (read-only).** Raskin + north-star fan-out over
  all 20 public skills: **split = 0, merge = 0, structure healthy**; body length
  is ratchet-capped (not a lever). Map:
  [2026-06-21 audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md).
- **Quality reference merit-disposition DRAFT ready for critique (read-only).**
  Per-ref merit assessment of all 41 quality `.md` refs against the skill's
  current purpose (routing = signal, not value): **keep 34 / route-it 5 /
  merge 2 / delete 0 — nothing is meaningless.** The defect is a discoverability
  gap (valuable refs un-routed), not bloat; the routing heuristic over-flagged
  (many "orphans" had eval/doc/script consumers). Proposal (with critique hooks):
  [disposition proposal](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).

## Next Session

- **START HERE — critique the quality reference disposition proposal**, then
  execute the approved items. The proposal carries explicit critique hooks
  (keep-bias, no-holistic-dedup, merge-target bloat, route targets). Route/merge
  edits touch SKILL.md References + dispatch + maybe tests — apply the pin-sweep
  discipline (validate_skills + check_skill_contracts + quality docs tests +
  doc-links + dup-ratchet, adversarial verify each; a moved test-pinned phrase
  moves its test too). The broader 19-skill rollout stays a "where to look" map
  only — verify each flag against tests first (this session's false-positive rate
  was high); metric is concept clarity, never line count.
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
