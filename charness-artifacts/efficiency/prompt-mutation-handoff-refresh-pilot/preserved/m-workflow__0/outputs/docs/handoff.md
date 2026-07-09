# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 is RED (scheduled run 2026-07-09 01:11 UTC on `f84eb223`)**: the
  coverage baseline aborted before any mutants ran —
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  failed on CI; the StrykerJS missing-report line is collateral (#422's
  real-signal naming worked). The same test passes locally at HEAD, so this is
  a CI-vs-local divergence in the `capture-skill-run.sh` end-to-end run
  (PATH-shimmed `claude`, `/proc` fd readlink, TMPDIR redirect, nested git
  worktree), not a plain local regression.
- **#423 CLOSED 2026-07-08** (`7c09a8ce` keeps eval identity out of the
  captured run's view); the red test above is that fix's behavioral guard.
- #424/#425 CLOSED via `f84eb223` (update-output version transitions + single
  NEXT_ACTION list). #410 queue CLOSED; method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Fix the #421 red; do not close the issue manually (machine-owned)**:
   start from the workflow-run logs linked in the issue's latest comment,
   reproduce the CI-only failure of the test named above, then fix the
   capture-script/CI seam. Auto-close fires when the scheduled judge
   (`17 */12 * * *` UTC, range `57af3d2b..HEAD`) next goes green.
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

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
