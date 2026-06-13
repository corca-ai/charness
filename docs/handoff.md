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
  [achieve-efficiency-improvements](../charness-artifacts/spec/achieve-efficiency-improvements.md);
  A+C `55631fe8`, B `01104241`, E `785908e0`, D `df407a07`). Bundle green, dogfooded.
- **achieve-efficiency internal follow-ups COMPLETE (2026-06-14)**
  ([goal](../charness-artifacts/goals/2026-06-14-achieve-efficiency-internal-followups.md);
  additive, no floor removed/blocking). **S1 (A2) `e6d1a59a`**:
  `describe_goal_closeout_shape.py --goal-path` emits the goal-conditional
  missing-floor set (reuses live evidence+timebox reports, no drift), folding the
  dry-check into one call. **S2 `c75de40f`**: `advise_floor_addition_restraint`
  gives the Floor-Addition Restraint checklist non-blocking teeth. Closeout
  `0535c79c`: bundle proof green, each slice fresh-eye critiqued (0 Act-Before-Ship).
- **Open issues (`gh`, 2026-06-13): none.**
- Restart note: active sessions may carry pre-0.44.1 plugin cache paths; restart
  Claude/Codex sessions to load the refreshed install.

## Next Session

- **Still deferred** (reopen triggers): **E2b** (chunker ingests recurring waste —
  needs real usage telemetry; waits for natural 0.45.0 usage data) and the
  **Coordination-Cues floor merge** (floor *removal* — a separate critiqued
  change). The `floor-addition-restraint-nudge` deferral is now **resolved** (S2).
- **Heads-up:** a concurrent agent's pry-integration WIP (an untracked pry tool
  manifest + a tool-lifecycle test edit adding `pry`) touched this worktree
  mid-run; it is isolated in `git stash` (`stash@{0}`), not committed —
  `git stash pop`/`drop` per that effort's intent. Not part of this goal.
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
