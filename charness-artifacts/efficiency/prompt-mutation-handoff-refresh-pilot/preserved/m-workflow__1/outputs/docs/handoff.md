# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 went RED** (comment 2026-07-09 01:11 UTC, on `f84eb223`): the coverage
  baseline pytest failed before any mutants ran. Single failing test:
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (added by the #423 fix `7c09a8ce`). It **passes locally** (0.56s) — CI-vs-local
  divergence, undiagnosed. Run:
  <https://github.com/corca-ai/charness/actions/runs/28986563107>.
- **HEAD `ed3cebb8` "chore: snapshot" is unexplained**: author `charness` (not
  the `hotl proof` author of surrounding work), deletes the entire `## Workflow`
  section from both handoff SKILL.md copies (public + plugin) with no rationale,
  issue, or capture proof; no reference-compaction artifact records that
  decision. Treat the deletion as unverified, not as a landed compaction slice.
- #410 queue executed and CLOSED; #423 CLOSED (`7c09a8ce`). Method + results:
  [slice7-census-reconciliation.md](../charness-artifacts/reference-compaction/slice7-census-reconciliation.md).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Verify-or-revert `ed3cebb8` first** (cheap, and pickup itself routes
   through the gutted skill): find what produced the snapshot commit; if the
   handoff `## Workflow` deletion has no owning proof, revert it and re-sync
   the plugin copy. The surviving Guardrails still cite "Workflow step 4" — a
   dangling reference into the deleted section.
2. **Debug the #421 red** (route through `charness:debug`): reproduce the
   capture-blinding test under CI conditions (linked run above has the log);
   the divergence is environmental — the test shims `claude` on PATH, shells
   bash, and reads `/proc/$$/fd/1`. Fix the test or script, push, then let the
   scheduled run (`17 */12 * * *` UTC) judge; **do not close #421 manually**
   (machine-owned auto-close). Note: this is #421's *third distinct* baseline
   failure; the referenced 2026-07-08 debug doc covers an earlier,
   already-fixed cause (StrykerJS grandfather truncation), not this one.
3. **81-site argparse-help debt (run LAST, alone).** Trip-wire D33 already
   fired and was RESOLVED 2026-07-09 (report extraction, see
   [deferred-decisions.md](./deferred-decisions.md) D33);
   `run_skill_efficiency_ab.py` now sits well under the 480 limit.

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
