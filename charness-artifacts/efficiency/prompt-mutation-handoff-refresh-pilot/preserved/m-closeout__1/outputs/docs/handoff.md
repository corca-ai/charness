# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 is RED (comment 2026-07-09 01:11 UTC)**: the scheduled mutation run on
  `f84eb223` aborted before sampling — baseline test
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  fails in CI but **passes locally** (re-verified 2026-07-09). That test is the
  behavioral guard added with the #423 fix (`7c09a8ce`); #423 itself is CLOSED.
- #410 queue executed end-to-end and CLOSED; method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Debug the #421 red** (route: `charness:debug`). Start from the CI log:
   <https://github.com/corca-ai/charness/actions/runs/28986563107> (also linked
   in the latest #421 comment). Local-pass/CI-fail means environment-sensitive:
   the test shells out to
   [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh) with a
   PATH-shimmed fake `claude` (`tests/test_skill_efficiency_ab.py:284`), so
   suspect runner environment (PATH shim, `/proc/$$/fd` readlink, git
   defaults) before suspecting the #423 fix itself. Do **not** close #421
   manually — it is machine-owned; the scheduled run (`17 */12 * * *` UTC)
   re-judges `57af3d2b..HEAD` after a fix lands.
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

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
  (prior #421 red — RULE_DATE-floor cause, resolved by `38219d95`; **not** the
  current 2026-07-09 red) · [deferred-decisions.md](./deferred-decisions.md) ·
  [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
