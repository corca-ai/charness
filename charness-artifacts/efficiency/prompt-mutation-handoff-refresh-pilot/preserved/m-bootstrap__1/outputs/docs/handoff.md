# charness Handoff

## Workflow Trigger

- Pickup = session start with no explicit task -> **invoke `charness:handoff`**
  directly (the session-start hook routes it, not `find-skills`); a bare
  `/handoff` runs chunked routing over handoff + open issues.

## Current State

- **#421 (only open issue) is RED again with a NEW cause** (machine comment
  2026-07-09 01:11 UTC, judging `f84eb223`): baseline pytest fails before any
  mutants on
  `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
  (the #422 fix now names the nodeid as designed). CI-only — passes locally at
  HEAD; the CI stderr shows `capture-skill-run.sh` exiting 1 on
  `cp: cannot stat '/home/runner/.claude/.credentials.json'` (the credentials
  copy assumes a populated `~/.claude/`, absent on runners). Log: GitHub
  Actions run `28986563107`.
- #423 CLOSED (`7c09a8ce`: neutral run base + that behavioral test);
  #424/#425 CLOSED (`f84eb223`). D33 RESOLVED — report section extracted to
  [skill_efficiency_report.py](../scripts/skill_efficiency_report.py);
  `run_skill_efficiency_ab.py` sits at 384/480 lines.
- `62b0ffe1` (`chore: snapshot`, unpushed) = origin/main + the Slice-9
  planner-retirement `## Bootstrap` removal from both handoff `SKILL.md`
  surfaces; content is in `d0eb6831`'s declared scope but landed message-less.
- Test-debt rotation baseline stays `8e1fd200` (2026-07-08 cycle done; method:
  [2026-07-08-test-debt-rotation-delta-sweep.md](../charness-artifacts/quality/2026-07-08-test-debt-rotation-delta-sweep.md)).

## Next Session

1. **Fix #421's CI-only baseline failure** in
   [capture-skill-run.sh](../scripts/agent-runtime/capture-skill-run.sh): make the
   `~/.claude/.credentials.json` copy tolerate absence (match the `|| true`
   the adjacent `settings.json` copy already has, and audit sibling host-state
   copies while there), reproduce first under a `HOME` with no `~/.claude/`, prove the behavioral test green both with and without
   credentials, push. Then let the machine-owned scheduled run
   (`17 */12 * * *` UTC) close #421 — never close it manually; if it stays
   red, read the summary's named nodeids first.
2. **Reconcile branches before pushing.** This refresh ran on a detached HEAD
   at `62b0ffe1` (no branch). The shared `main` branch sits at a divergent
   `d7f10be3` (3 unpushed prompt-mutation commits over the same `f84eb223`
   base) and does NOT contain the snapshot's Bootstrap removal — apply
   `62b0ffe1` (and this refresh) onto `main` under a real commit message, e.g.
   cherry-pick after checking out `main`; a plain `git checkout main` + push
   silently drops the Bootstrap removal.
3. **81-site argparse-help debt (run LAST, alone).** The D33 480-line
   trip-wire on `run_skill_efficiency_ab.py` is gone (384/480), so the split
   no longer preempts it.

## Discuss

- D18 disposition is still pending operator decision (reopen trigger fired
  2026-07-05): land the workspace-write carrier + routing-eval `--read-only`
  wiring now, or explicitly re-defer. See
  [deferred-decisions.md](./deferred-decisions.md).

## References

- [2026-07-08-issue-421-nightly-mutation-gate-red.md](../charness-artifacts/debug/2026-07-08-issue-421-nightly-mutation-gate-red.md)
  (the PRIOR #421 cause, fixed by #422 — not today's credentials-cp cause) ·
  [deferred-decisions.md](./deferred-decisions.md) ·
  [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md)
