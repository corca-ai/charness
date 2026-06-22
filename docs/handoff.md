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

- **Pin sweep shipped** (`1f58af89`+`18467e56`, 126/128 keep; disciplined
  pin-deletion test in the gate header). Gotcha: editing `check_skill_contracts.py`
  re-rotates the clone family → count-neutral dup-ratchet re-baseline.
- **Skill-structure audit DONE.** Raskin + north-star fan-out, 20 public skills:
  split=0, merge=0, structure healthy. [audit](../charness-artifacts/quality/2026-06-21-skill-structure-raskin-audit.md).
- **Quality reference disposition critiqued + EXECUTED + validated.** 41-ref merit
  map → critique (10-skeptic, corrected 4 anchors + 2 merge targets) → **7 route-it +
  2 merge-retire, 0 deletes**; full pin sweep green + mirror synced; blind A/B
  confirmed routing **7/7 reach-via-pointer** (Cautilus gated, planner
  `next_action: none`; blind-runner capture was the in-policy substitute). Detail:
  [disposition proposal](../charness-artifacts/quality/2026-06-21-quality-reference-disposition-proposal.md).
- **Headless-runner de-risk (B-smoke) DONE.** A real `claude -p` `quality` run
  resolves headless, reads refs via routing, and **spawns the Step-8 fresh-eye
  reviewer as a real subagent** (a subagent-runner can't see this). Gotcha:
  `/quality` loads from the INSTALLED clone `~/.agents/src/charness` (old `f7bf5d2c`).

## Next Session

- **Quality-ref disposition done+validated+pushed** (critique → execute → blind A/B
  7/7). Broader 19-skill rollout stays a verify-first "where to look" map.
- **A: cautilus skill-experiment harness DONE** ([goal](../charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md),
  complete). Built the stream-json capture + the keystone
  transcript→`skill_clone_experiment_input.v1` extractor + wrapper wiring +
  obligations spec; **one real baseline(b01cee6b) vs variant(5ded9f3a) cautilus
  verdict: `discard`** — honest zero source-coverage delta (both arms read the same
  6 refs). KEY FINDING: source-coverage measures *which files*, not
  pointer-directness; this disposition's value (reach-via-pointer, prior A/B 7/7) is
  orthogonal to the lens. Reproduce via [the harness README](../evals/cautilus/skill-experiment/README.md).
  Deferred (operator queue): the full multi-scenario sweep; `reviewer_tiers`. Carried
  nits: DRY findResultEvent/findClaudeResultEvent; a no-name-hint eval task so
  source-coverage can discriminate this disposition class.
- **START HERE — C — #387 one-pass goal-closeout shape report.** Fits
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
