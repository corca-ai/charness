# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 went RED on the 2026-07-09 01:11 UTC scheduled run** (commit
  `f84eb223`): the coverage baseline pytest failed before any mutants ran —
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #423 blinding fix's behavioral test). That test passes at this
  checkout's snapshot, so suspect commit- or CI-env-specific breakage.
  Summary + workflow-run link live in the issue comment.
- **#423 CLOSED** (2026-07-08): capture eval-identity blinding fix landed with
  the behavioral test above.
- **Prompt-mutation pilot (2026-07-09) filed two harness follow-ups**: #426
  (mutant-arm captures unblind themselves by diffing the neutral snapshot
  commit) and #427 (scorer `stream.jsonl` fallback matches marker mentions,
  not command executions). The issue bodies carry the evidence pointers.
- **This checkout is a stale squashed snapshot**: `f84eb223` is not an
  ancestor of local HEAD, and the whole prompt-mutation harness the issues
  reference is absent here. Sync to current main before any code work.
- #410 queue executed end-to-end and closed; method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 red** (machine-owned issue; do not close manually): read
   the 2026-07-09 01:11 UTC comment + linked workflow run, then reproduce the
   failing baseline test at `f84eb223` **in a disposable worktree** (it is not
   an ancestor of this snapshot). Treat this as a fresh diagnosis: #421 has
   now carried three unrelated baseline failures, and
   [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
   covers an earlier, already-fixed one (RULE_DATE floor).
2. **#426 + #427 prompt-mutation harness fixes** (on a synced checkout —
   the harness is absent from this snapshot): blind mutant-arm captures to
   the snapshot-commit diff; constrain the scorer stream fallback to
   command-bearing (tool_use) events.
3. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
