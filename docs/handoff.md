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

- **v0.45.0 shipped and public release is verified.** Release commit
  `48b9c1c4 Release charness 0.45.0`; verification commit
  `f18a30cb Record release verification for v0.45.0`; tag `v0.45.0` is published
  ([url](https://github.com/corca-ai/charness/releases/tag/v0.45.0)) and the
  maintainer install auto-refreshed to 0.45.0. Ships the achieve-efficiency
  effort; E is framed in `update_instructions` as **internal instrumentation**
  (the emitter is NOT in the plugin, so consumers do not auto-collect telemetry).
- **#184 verdict stays not-met by design** until the 06-05 recurrence ages out of
  the rolling 28d window (the upgrade annotates, never clears).
- **achieve-efficiency effort COMPLETE + shipped in v0.45.0** (spec
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

- **Prioritized pickup: achieve-efficiency internal follow-ups (DRAFT, pursue-ready).**
  [goal](../charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md)
  — charness-internal only (operator dropped the ceal cross-repo dogfood). Two
  additive slices: **A2** (make describe-first goal-conditional so it absorbs the
  conditional `keep` floors the static catalog misses) and
  **floor-addition-restraint-nudge** (give D's prose checklist non-blocking teeth).
  `shape_ready: true`, `pursue_ready: true` — activate with `/goal @...`.
- **Still deferred** (reopen triggers, NOT in the goal above): **E2b** (chunker
  ingests recurring waste — needs real usage telemetry; charness's own stream is
  thin and we did not dogfood ceal, so it waits for natural 0.45.0 usage data), and
  the **Coordination-Cues floor merge** (floor *removal* — a separate critiqued change).
- The #184 verdict flips on its own as the window rolls forward if no new
  falsified conversion lands — check `python3 scripts/aggregate_rca_ledger.py`.
- Older deferrals (unchanged): D28/D29 in
  [deferred decisions](./deferred-decisions.md); the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs a log-backed request + the [cautilus wrapper](../scripts/run_cautilus_eval.py);
  valid-but-defer (not filed): run-id-mode refusal key, consumer template-drift
  advisory, mutation-score skip denominator.

## Discuss

- Whether a consumer-facing announcement is worth it for 0.45.0 (achieve-efficiency)
  plus the earlier scheduled-mutation / scorecard / cadence changes.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.45.0 release record](../charness-artifacts/release/latest.md)
- [overnight bundle critique](../charness-artifacts/critique/2026-06-12-autonomous-structural-quality-bundle.md)
