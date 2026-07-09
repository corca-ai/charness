# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 scheduled mutation gate went RED (2026-07-09 01:11 UTC) on
  `f84eb223`**: coverage-baseline pytest failed before any mutants ran; the one
  failing test is
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`.
  That test **passes locally at the same commit** (verified 2026-07-09), so the
  failure is CI-environment-dependent. Runner log:
  <https://github.com/corca-ai/charness/actions/runs/28986563107>.
- **#423 CLOSED** (capture eval-identity blinding, fixed in `7c09a8ce`); the
  behavioral test guarding that fix is exactly the test now red in CI.
- #410 closed; capture-harness method + census results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 red via `charness:debug`**: local pass vs runner fail on
   the same commit means start from the runner log above, not from the test
   body. Do **not** close #421 manually — the machine owns close on the next
   green `17 */12 * * *` UTC run; a green after the fix is the exit signal.
2. **81-site argparse-help debt (run LAST, alone).** No active trip-wire:
   D33 fired and was RESOLVED 2026-07-09 (report section extracted to
   `skill_efficiency_report.py`; the harness now has real length headroom).

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
