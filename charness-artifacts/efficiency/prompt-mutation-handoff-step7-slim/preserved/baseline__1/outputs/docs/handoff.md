# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 went RED on the 2026-07-09 01:11 UTC scheduled run** (run
  [28986563107](https://github.com/corca-ai/charness/actions/runs/28986563107),
  head `f84eb223`): the coverage-baseline pytest failed before any mutants ran
  — `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`;
  the StrykerJS missing-report FAIL is collateral. The failing nodeid **passes
  in isolation locally at both the current tree and `f84eb223`** (verified
  2026-07-09), so suspect full-suite interaction (CI runs the whole coverage
  baseline) or CI-env divergence — not a plain unit regression at that commit.
- **#423 CLOSED (2026-07-08).** Its prompt-mutation pilot left two open
  harness issues: **#426** (mutant-arm captures unblind themselves via
  `git show`/`git diff` on the neutral snapshot commit) and **#427** (scorer
  `stream.jsonl` fallback matches marker mentions anywhere, not only
  command-bearing `tool_use` events). Both issues cite the 2026-07-09
  prompt-mutation pilot report; that artifact is not in this checkout, so
  treat the issue bodies as the working source.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Unblock #421 (machine-owned close; do not close manually)**: the single
   nodeid already passes locally at `f84eb223`, so start with the full
   coverage-baseline pytest at `f84eb223` in a throwaway worktree
   (suite-interaction suspect); if that is green too, read the workflow run
   logs for CI-env divergence. Land the fix and let the scheduled run
   (`17 */12 * * *` UTC) judge and auto-close.
2. **Resolve #426 and #427** (prompt-mutation capture self-unblinding; scorer
   stream fallback over-matching). Issue bodies are the spec; fix shape goes
   through the issue workflow — phrasings here are symptoms, not designs.
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

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
  (prior 2026-07-06..08 red, resolved — reuse its worktree-bisect method, not
  its conclusion; the 2026-07-09 red is a new baseline failure, see Current
  State) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
