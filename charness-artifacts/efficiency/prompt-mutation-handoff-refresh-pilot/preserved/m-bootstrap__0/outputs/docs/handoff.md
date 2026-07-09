# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 is RED again with a NEW cause — do not wait for auto-close.** The
  2026-07-09 00:17 UTC machine run (on `f84eb223`) aborted before any mutants:
  baseline pytest failed on
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #423 end-to-end capture test). That test **passes locally at HEAD**, so
  the failure is CI-environment-specific. CI log: GH Actions run 28986563107
  (linked from the latest #421 comment).
- #423/#424/#425 CLOSED this session: capture eval-identity blinding
  (`7c09a8ce`), update from→to version output + single NEXT_ACTION list
  (`f84eb223`). dup-ratchet re-baselined under nose 0.18.0 (`7d345c9b`).
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Resolve the #421 red** (route through `issue`; bug-class, so causal
   review before fix design). Start from the CI log of run 28986563107 — the
   failing test executes the real capture script end-to-end (PATH-shimmed
   `claude`, `/proc/$$/fd` readlink, `TMPDIR` override), so suspect a
   CI-runner environment difference rather than the #423 fix logic. The
   machine run recurs at `17 */12 * * *` UTC with base = the previous
   completed run's head (currently `f84eb223`); #421 stays machine-owned —
   fix the baseline, let the gate close it.
2. **81-site argparse-help debt (run LAST, alone).** D33 resolved this
   session by the #423 slice (see
   [deferred-decisions.md](./deferred-decisions.md));
   `run_skill_efficiency_ab.py` now has headroom at 384/480.

## Discuss

- **RULE_DATE floor practice (retro 2026-07-08)**: on a grandfathered-floor's
  landing day, run the suite as-of tomorrow's enforcement date so truncating
  consumers detonate before push; promote to a gate only on recurrence.
- **D34/D35 DECLINED** (2026-07-04); reopen only if the recorded failure
  materializes. See [deferred-decisions.md](./deferred-decisions.md).
- Deferred from #420 close: nothing pins the `--advisory` flag at
  `run-quality.sh:505`; add a pin only if the hard-block posture regresses.
- `62b0ffe1` ("chore: snapshot") removed the handoff `## Bootstrap` section
  from both skill copies — verified in-sync and gates-green, consistent with
  the Slice-9 substance-judge flip, but it bypassed commit closeout
  discipline. No action unless a planner consumer regresses.

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md) (prior #421 cause — different from the current red) · [deferred-decisions.md](./deferred-decisions.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
