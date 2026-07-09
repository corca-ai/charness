# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 scheduled mutation gate is RED (run 28986563107, 2026-07-09 01:11
  UTC, head `f84eb223`)**: baseline pytest fails on the #423 behavioral test
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`.
  Root cause proven and reproduced locally: unguarded credentials `cp` at
  `scripts/agent-runtime/capture-skill-run.sh:125` aborts on machines without
  `.credentials.json`; the test inherits the operator's `CLAUDE_CONFIG_DIR`,
  so it is green locally and red on CI. Diagnosis, exact repro command, and
  fix shape:
  [2026-07-09-issue-421-red-capture-credentials-cp.md](../charness-artifacts/debug/2026-07-09-issue-421-red-capture-credentials-cp.md).
- #421 is the only open issue. #423 closed (`7c09a8c`), #424/#425 closed
  (`f84eb223`); the #422 blocking-signal fix is now field-proven — the red
  comment named the failing nodeid directly.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Fix the #421 red** per the debug artifact's Fix Shape: make the
   behavioral test hermetic (tmp `CLAUDE_CONFIG_DIR` with stub credentials),
   decide the script's missing-credentials posture deliberately, prove with
   both repro commands (both green after the fix), push. Then let the scheduled run (`17 */12 * * *` UTC)
   auto-close #421 — machine-owned; do not close manually.
2. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
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

- [2026-07-09-issue-421-red-capture-credentials-cp.md](../charness-artifacts/debug/2026-07-09-issue-421-red-capture-credentials-cp.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
