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
- Open issues (2026-06-18): #387 (overhaul Phase-1 pilot), #388 (mutation-test
  regression — separate CI track), #371.

## Next Session

- **Primary: implement the overhaul per the RESOLVED Step 0 findings.** Read the
  archive first. Sequence:
  - **Track 1a (LIGHT):** obligate a per-unit behavioral verdict at irreversible
    boundaries (issue/PR close, release publish, external write, deletion). CUT as
    NOT load-bearing: reviewer-PULLs-raw-state, doer-can't-author-brief,
    per-reviewer load caps. Distinct-channel falls out of the mandate.
  - **Track 2 (SLIM):** PUSH→PULL (minimal always-on + skills index, bodies on
    demand) + own-concept compression (SRP); cut judgment-restatement prose.
- **Honor the north star: the fix is FRAMING/task-structure, not prose, not a new
  gate.** Optional (not blocking): re-run Instrument 3 with a 2nd defect class to
  harden generality (single fixture is the one named limit).
- #388 and #371 stay on their own tracks; do not couple them to the overhaul.
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md).

## Discuss

- Who owns the #371 upstream lifecycle proof path.

## References

- [Step 0 experiment program archive — RESOLVED](../charness-artifacts/retro/2026-06-18-step0-experiment-program-archive.md)
- [overhaul plan v2 (Track 1a now LIGHT)](../charness-artifacts/critique/2026-06-18-overhaul-plan-v2.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [release latest](../charness-artifacts/release/latest.md)
