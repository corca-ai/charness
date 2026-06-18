# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Design north star landed + #386 shipped as v0.52.4** (published/verified;
  [`design-north-star.md`](./design-north-star.md) governs, referenced from
  `AGENTS.md`). #386 fixed by a Rung-2 distinct-observer/distinct-channel
  disposition-review mandate, **no new gate**.
- **Overhaul Step 0 (mechanism investigation) is RESOLVED; remaining work =
  IMPLEMENTATION (next slice).** Mechanism of the #386-class failure = **task
  FRAMING**: an aggregate-disposition sign-off after all-green+CLOSED makes a
  fresh reviewer suppress its own (present) proxy-skepticism and rubber-stamp
  (catch 0/12). The lever that flips it **0.00→1.00** = a **per-unit behavioral
  verdict mandate**; the distinct-channel demand falls out automatically. NOT
  context-load, NOT raw-vs-summary channel. #386's fix is empirically validated.
  Full program + carry-forward lessons + method in
  [`step0-experiment-program-archive`](../charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md)
  (raw records in `charness-artifacts/critique/2026-06-18-*`).
- **#371 remains open by design** — no close without controlled invocation-end
  teardown proof (process tree + `agent-browser-chrome-*` dir) for completion,
  cancellation, provider failure, and timeout.
- Open issues (2026-06-18): #387 (closeout-validator one-pass UX — **not** the
  overhaul pilot, the prior handoff mislabeled it), #371 (browser teardown).
  #388 closed.

## Next Session

- **Primary: the overhaul is SHAPED as a draft `achieve` goal** —
  [`2026-06-18-north-star-overhaul.md`](../charness-artifacts/goals/2026-06-18-north-star-overhaul.md)
  (Track 1a LIGHT = generalize the per-unit behavioral-verdict framing, NO new
  gate; Track 2 SLIM). It is `shape_ready`; `pursue_ready` is held on **4 surfaced
  `Discuss before activation` decisions** (Track-1a in-place method, Track-2
  bundling/spin-out, no external side effects, no tracked issue). Resolve those,
  then activate
  `/goal @charness-artifacts/goals/2026-06-18-north-star-overhaul.md`. First slice
  S1 = read-only boundary audit. A bounded fresh-eye plan premortem is folded.
- **Honor the north star: the fix is FRAMING/task-structure, not prose, not a new
  gate.** Optional/not blocking: a 2nd defect class would harden generality.
- #371 stays on its own track; do not couple it to the overhaul.
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md).

## Discuss

- Who owns the #371 upstream lifecycle proof path.

## References

- [overhaul draft goal (shaped, awaiting activation)](../charness-artifacts/goals/2026-06-18-north-star-overhaul.md)
- [Step 0 experiment program archive — RESOLVED](../charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md)
- [overhaul plan v2 (Track 1a now LIGHT)](../charness-artifacts/critique/2026-06-18-overhaul-plan-v2.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [release latest](../charness-artifacts/release/latest.md)
