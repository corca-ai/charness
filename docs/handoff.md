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
- **achieve-efficiency effort COMPLETE** (spec
  [achieve-efficiency-improvements](../charness-artifacts/spec/achieve-efficiency-improvements.md)).
  A+C `55631fe8`, B `01104241`, **E (objective waste telemetry) `785908e0`**,
  **D (floor-restraint checklist + closeout-floor audit) `df407a07`**,
  bundle-boundary spec fix `f79abce2`. Bundle re-confirmed green
  (`--verification-lock --produce-mutation-coverage`): 2902 passed, mutation
  coverage produced; E1 telemetry + C gate-runtime advisory dogfooded live. Each
  slice fresh-eye critiqued (E/D found+folded real issues).
- **Open issues (`gh`, 2026-06-13): none.**
- Restart note: active sessions may carry pre-0.44.1 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- **achieve-efficiency is done; no pickup owed.** Live follow-ons (spec Deferred
  Decisions, each with a reopen trigger, none started): **E2b** (chunker ingests
  recurring waste — autonomous-loop closure, likely needs a ceal run), **A2**
  (goal-conditional describe absorbs the conditional `keep` floors), the
  **Coordination-Cues floor merge**, `follow-up:floor-addition-restraint-nudge`.
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
