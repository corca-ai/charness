# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (2026-07-09, later): prompt-mutation pilot goal COMPLETE
  (unpushed).** New pipeline (mutant generator, witness coverage, survival
  scorer + policy doc) proven live on handoff/refresh: bootstrap DETECTED,
  workflow + closeout-vocabulary survived (mutual token redundancy — the A+B
  case), 30-unit coverage-debt list. #426/#427 filed. Report:
  [2026-07-09-handoff-refresh-pilot.md](../charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md);
  goal artifact owns the detail and the operator decision queue (push;
  demotion proposal accept/reject).
- **This session (2026-07-09): #410 queue executed end-to-end and CLOSED.**
  Handoff pickup floor moved to a substance judge (planner `e4f3626d`, flip +
  capture proof), hotl ledger tokens lifted with the floor re-proven
  (`8bdf9fda`), setup/greenfield captured for the first time via the new
  `capture-skill-run.sh --run-cwd` sandbox mode → capture-PROVEN KEEP (census
  MOVE refuted per-condition), spill-targets FINAL keep. Method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- **#423 filed (capture eval-identity blinding leak)**: the captured agent can
  read its own eval identity from the out-dir path; evidence in the Slice-9
  pickup transcript. Harness-owned follow-up, not blocking.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Watch #421 auto-close (machine-owned; do not close manually)**: the
   scheduled run (`17 */12 * * *` UTC) judges `57af3d2b..HEAD`, expected green.
   If red, the summary names the real blocking signal (#422 fix,
   roundtrip-proven) — read it first. As of this session's pickup capture,
   #421 was OPEN with no new comment since 2026-07-08 13:00 UTC.
2. **#423 capture-blinding harness fix** (genericize the run-visible directory
   identity; keep `justification.md` out of the run-visible tree).
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
