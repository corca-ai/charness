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

- **Pin sweep DONE (A+B), `ahead 2` on `origin/main` — UNPUSHED.**
  - A (`1f58af89`): folded the 3 twin validators in `check_skill_contracts.py`
    into one `_assert_snippet_membership` helper. Behavior byte-identical; this is
    the F4 "stabilize the file" cleanup.
  - B (`18467e56`): harness-wide audit of **all 128** CORE/PACKAGE/FORBIDDEN pins
    via a classify + adversarial-refute fan-out — **126/128 KEEP** (the set is
    already tight). Only 2 wording-freeze fragments deleted: spec CORE
    `keep the contract`, create-skill PACKAGE `keep manifest` (both fully owned by
    surviving sibling pins; no SKILL.md prose change). The **disciplined
    pin-deletion test is now a durable convention in the gate header** — judgment,
    not a self-classifying gate; fewer-pins is explicitly NOT the metric.
  - Gotcha: every `check_skill_contracts.py` edit re-rotates the validator clone
    family -> count-neutral dup-ratchet re-baseline (526->526, delta 4). Expect it
    again on the next edit; it's case-2 rotation, not new duplication.
  - Verified: broad pytest **2287 passed**; fresh-eye `SAFE TO COMMIT` on both slices.

## Next Session

- **Push A+B first** (see Discuss) — outward call, pre-push **full** gate applies
  (touches `scripts/` + `charness-artifacts/`).
- **C — #387 one-pass goal-closeout shape report.** Fits
  `describe_goal_closeout_shape.py` (describe-first preflight), not a new floor.
- **D — #392 gather-X honest-failure contract.** Typed result
  (`exact-acquired | blocked-by-X | auth/browser-route-required | unsupported`) +
  route-level trace + a regression fixture. Scope call at pickup (see Discuss).
- **Parked:** #394 (mutation cron-only, auto-closes). #371 (upstream-blocked
  vercel-labs/agent-browser#1334). #391 extraction candidates.

## Discuss

- **Push A+B?** 2 local commits await an outward push decision; nothing blocks them.
- **#392 scope (decide at pickup of D):** attempt a real exact-X route
  (browser/auth — likely infeasible) vs commit to the typed-unsupported contract.
- **D31 still manual:** the chunker does not reconcile against recent commits, so
  pickup reads `git log` by hand to de-stale (done again this session).

## References

- [recent-lessons](../charness-artifacts/retro/recent-lessons.md),
  [deferred-decisions](./deferred-decisions.md); pin-sweep convention lives in
  the [`check_skill_contracts.py`](../scripts/check_skill_contracts.py) gate header.
