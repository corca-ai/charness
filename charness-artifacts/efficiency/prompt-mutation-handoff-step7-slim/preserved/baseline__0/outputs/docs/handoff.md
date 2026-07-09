# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> the session-start hook routes
  straight into **`charness:handoff`** (not `find-skills`), which — given no
  task directive — runs chunked routing over handoff + open issues. A bare
  `/handoff` mid-session is the same no-task flow.

## Current State

- **#421 is RED with a new cause (not the #422 regression)**: the 2026-07-09
  01:11 UTC run on `f84eb223` failed baseline pytest before any mutants ran —
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`.
  That test is the behavioral proof for the #423 capture-blinding fix; #423
  itself is CLOSED (2026-07-08 18:28), so the fix landed but its test fails in
  CI. The test **passes locally** (re-proven 2026-07-09 on this checkout), so
  suspect CI-environment sensitivity, not a plain logic break.
- **2026-07-09 prompt-mutation pilot filed two harness bugs**: #426 (mutant-arm
  captures unblind themselves via `git show`/`git diff` of the neutral
  `chore: snapshot` mutant commit; m-workflow NO-OBSERVED-EFFECT attribution is
  confounded, m-closeout stayed clean) and #427 (scorer `stream.jsonl` fallback
  matches marker mentions anywhere in the stream, not command-bearing tool_use
  events; one stream-based fire already withdrawn). Evidence and verdicts live
  in the pilot artifact both issues cite — it may not exist in your checkout;
  read it via `gh issue view 426` / `427`, not by path.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Diagnose the #421 baseline red (CI-only failure).** Read the failing run
   (<https://github.com/corca-ai/charness/actions/runs/28986563107>), then find
   why `test_capture_script_behavioral_no_identity_in_run_view` fails in CI
   while passing locally. #421 stays machine-owned — do not close manually; the
   next scheduled run (`17 */12 * * *` UTC) is the green observer.
2. **#426 capture-unblinding fix**: make the mutant snapshot commit
   non-disclosing from inside the captured run (no readable removed-diff one
   `git show` away); this gates blinding validity for every future
   prompt-mutation run.
3. **#427 scorer fix**: constrain the `stream.jsonl` trace-marker fallback to
   command-bearing (tool_use) events.
4. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33:
   `run_skill_efficiency_ab.py` at 479/480 (counts as of 2026-07-09; re-verify
   before acting since items 1-3 land first).

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) (prior #421 red — different cause; read to avoid conflating) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
