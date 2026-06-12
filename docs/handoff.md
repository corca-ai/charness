# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.43.0 shipped and public release is verified.** `main`/`origin/main`
  are at `263a767b Record release verification for v0.43.0`; tag `v0.43.0`
  is published, the maintainer install auto-refreshed to 0.43.0, and the
  real-host proof arms are closed on this host (see
  [release latest](../charness-artifacts/release/latest.md)).
- v0.43.0 content summary lives in the
  [goal artifact](../charness-artifacts/goals/2026-06-12-autonomous-structural-quality-bundle.md)
  (#356/#357 closed, two new authoring-repo gates, contract-effectiveness
  fixture, second-machine proof-arm retirement).
- **#184 closed (2026-06-13 baseline review).** Operator-confirmed numeric
  target: conversion rate **≥70% rolling 28d seed-excluded (n≥10) + zero
  falsified conversions**; baseline 76.9% (20/26). The aggregator judges it
  (`target` block); current verdict **not-met** — the first falsified
  conversion (`mutation-dispatch-no-base-sha-false-proof`) is in the window.
  Decision record: [product-success-metrics.md](./product-success-metrics.md)
  (Decisions 2026-06-13) + spec slice 3.
- **Open issues (`gh`, 2026-06-13): #358 only** — tripwire response:
  redesign that falsified conversion's durable artifact (likely gate-shaped).
- Restart note: active sessions carry pre-0.43.0 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- **#358 is the queued implementation candidate** — it is also what flips the
  #184 target verdict honestly (redesign the artifact; do not wait for the
  06-05 recurrence to age out of the rolling window).
- Live deferrals remain D28/D29 in
  [deferred decisions](./deferred-decisions.md) (D29: scorecard helper +
  metric-only closeout guard; reopens on consumer-repo discovery failure or
  operator request).
- Live execution of the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs an explicit log-backed request naming a
  failing-prompt/transcript/operator-log path, then the
  [cautilus eval wrapper](../scripts/run_cautilus_eval.py).

## Discuss

- After #354's fix shipped, decide whether an operator announcement is still
  useful for the v0.40.0 scheduled-mutation-lane change and the v0.41.0
  YouTube/issue retrieval improvements — and now whether the v0.43.0
  scorecard/cadence contracts deserve one consumer-facing announcement.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.43.0 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
