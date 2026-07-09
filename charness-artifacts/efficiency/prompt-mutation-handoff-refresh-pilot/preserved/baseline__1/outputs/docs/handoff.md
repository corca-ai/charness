# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 scheduled run went RED again with a NEW cause (2026-07-09 01:11 UTC,
  run 28986563107, HEAD `f84eb223`)**: baseline test
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  fails CI-only (passes locally, verified 2026-07-09). Root cause:
  `scripts/agent-runtime/capture-skill-run.sh:125` unconditionally `cp`s
  `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.credentials.json`, absent on the CI
  runner, so the real-script behavioral test aborts (`cp: cannot stat ...`).
- #410 queue executed end-to-end and CLOSED 2026-07-09; method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
  #423 capture-blinding fixed (`7c09a8ce`) and CLOSED — its new regression
  test is the one now red in CI.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Fix the #421 red**: make the missing-credentials copy at
   `capture-skill-run.sh:125` non-fatal, and shim `CLAUDE_CONFIG_DIR` in the
   behavioral test so it never depends on operator credentials. This is the
   second consecutive CI-only baseline abort from an environment-coupled
   dependency (nose absence `28d76718`, now credentials), so sweep sibling
   tests that execute real scripts for other host-state couplings. Then let
   the scheduled run (`17 */12 * * *` UTC) judge; #421 close stays
   machine-owned — do not close manually.
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

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) (prior #421 cause, resolved — does NOT cover the new credentials red) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
