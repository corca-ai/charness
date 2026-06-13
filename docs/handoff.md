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

- **v0.44.1 shipped and public release is verified.** Release commit
  `ac0d8063 Release charness 0.44.1`; release-verification commit
  `b0f06462 Record release verification for v0.44.1`; tag `v0.44.1`
  is published and the maintainer install auto-refreshed to 0.44.1 (see
  [release latest](../charness-artifacts/release/latest.md)).
- **#359 + #358 resolved, CLOSED, shipped in v0.44.1.** #359: `achieve`
  complete-state closeout blocks pending section placeholders. #358: the
  dispatch/no-base-sha mutation-proof false conversion is gate-backed + RCA-upgraded.
- **#184 verdict stays not-met by design** until the 06-05 recurrence ages out of
  the rolling 28d window (the upgrade annotates, never clears).
- **achieve-efficiency effort in flight** (spec
  [achieve-efficiency-improvements](../charness-artifacts/spec/achieve-efficiency-improvements.md),
  the canonical contract and resumption surface). Slice 1 (A describe-first
  closeout, C gate-baseline-runtime waste lens) landed `55631fe8`; Slice 2 (B
  over-slice advisory, `Current slice intent:` frame) landed `01104241`. Direction
  **E** (objective waste telemetry — the loop-observability fix) is **designed and
  critiqued, implementation deferred to this/next session by operator call**.
- **Open issues (`gh`, 2026-06-13): none.**
- Restart note: active sessions may carry pre-0.44.1 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- **Prioritized pickup: implement Slice 3 = E** of the
  [achieve-efficiency spec](../charness-artifacts/spec/achieve-efficiency-improvements.md)
  — read its `## Resumption` section first (names on-disk inputs, files to touch,
  and the E → D → bundle-broad-pytest order). E1 records `gate_runtime`/`over_slice`
  into a sibling closeout-telemetry stream; E2a mines it in the weekly retro and
  routes recurring waste to filed issues (not the decaying digest). Then Slice 4 =
  D, then the bundle-boundary `run_slice_closeout.py --verification-lock`.
- The #184 verdict flips on its own as the window rolls forward if no new
  falsified conversion lands — check `python3 scripts/aggregate_rca_ledger.py`.
- Deferred (valid-but-defer, not filed): run-id-mode refusal class key for
  schedule runs; consumer template-drift advisory; mutation-score skip denominator.
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

- Decide whether a consumer-facing announcement is still useful for recent
  scheduled-mutation, YouTube/issue retrieval, and scorecard/cadence changes.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.44.1 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
