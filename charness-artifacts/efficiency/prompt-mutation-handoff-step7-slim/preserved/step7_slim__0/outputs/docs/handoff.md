# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`). This is the
  same no-task trigger as a bare `/handoff`: both run chunked routing over
  handoff + open issues.

## Current State

- **#421 nightly mutation gate went RED again (2026-07-09 01:11 UTC, run
  [28986563107](https://github.com/corca-ai/charness/actions/runs/28986563107),
  head `f84eb223`).** The #422 fix is working — the summary now names the real
  blocker: baseline pytest fails on
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #423 blinding guard) before any mutants run. That test **passes locally
  at this snapshot**, so the split is CI-environment-specific or the CI head
  predates a fix. Prior #421 root-cause history:
  [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md).
- #410 (handoff pickup floor + capture queue) and #423 (capture eval-identity
  blinding) are both CLOSED; method and per-condition results live in
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 CI-only red (route through `debug`; the issue is
   machine-owned — do not close it manually).** Reproduce the CI-vs-local split
   on the #423 guard test first; the scheduled run (`17 */12 * * *` UTC) stays
   red until the CI run's baseline passes (cause still open: a main-content
   fix, or a CI-environment-specific fix).
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
