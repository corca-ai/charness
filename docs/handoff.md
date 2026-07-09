# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **This session (2026-07-09, latest): #427 local fix COMPLETE (unpushed).**
  `trace_command_marker` scoring now accepts only Bash command-bearing evidence
  from both `trace-digest.jsonl` and `stream.jsonl`; prose, non-command tool
  inputs, non-Bash `input.command`, and non-Bash trace `args` stay non-fires.
  Commits: `87963dab`, `9e97902f`, `2f988fff`. Focused proof:
  `python3 -m pytest -q tests/test_score_prompt_mutation_survival.py` = 29
  passed. Fresh-eye causal/review found and bundled the trace + stream sibling.
- **This session (2026-07-09, later): prompt-mutation pilot goal COMPLETE
  (unpushed).** New pipeline (mutant generator, witness coverage, survival
  scorer + policy doc) proven live on handoff/refresh: bootstrap DETECTED,
  workflow + closeout-vocabulary survived (mutual token redundancy — the A+B
  case), 30-unit coverage-debt list. #426/#427 filed. Report:
  [2026-07-09-handoff-refresh-pilot.md](../charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md);
  goal artifact owns demotion proposal accept/reject.
- **This session (2026-07-09): #410 queue executed end-to-end and CLOSED.**
  Handoff pickup floor moved to a substance judge (planner `e4f3626d`, flip +
  capture proof), hotl ledger tokens lifted with the floor re-proven
  (`8bdf9fda`), setup/greenfield captured for the first time via the new
  `capture-skill-run.sh --run-cwd` sandbox mode → capture-PROVEN KEEP (census
  MOVE refuted per-condition), spill-targets FINAL keep. Method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- **#423 capture eval-identity leak is CLOSED.** Do not carry it as next work.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Watch #421 auto-close (machine-owned; do not close manually)**: the
   scheduled run (`17 */12 * * *` UTC) judges `57af3d2b..HEAD`, expected green.
   If red, read the summary first. Latest local spot check of the most recent
   failing baseline test plus mutation-abort marker tests: 26 passed.
2. **Push/verify #427 closeout** after local closeout commit: carrier should
   close #427 and then verify CLOSED through `issue_tool.py verify-closeout`;
   do not treat local pytest alone as remote issue resolution.
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

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [prompt-mutation-policy.md](./prompt-mutation-policy.md)
