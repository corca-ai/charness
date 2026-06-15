# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **Runtime optimization branch is locally committed, not yet published.**
  `origin/main..HEAD`: `d002ccf3`, `d09167a9`, `40d1aa35`, `94b98580`,
  `11101d30`. These centralize standing pytest and remove avoidable duplicate
  quality-gate work. Latest proof in
  [quality latest](../charness-artifacts/quality/latest.md): full
  `run-quality --read-only` **38.1s**; broad standing pytest **3144 passed**;
  `check-test-completeness` **76ms**; `check-current-pointer-writes` **480ms**.
- **Consumer-repo benefit path:** root scripts were mirrored into
  `plugins/charness/scripts/...`, so consumer repos get the speedups only after
  this branch is pushed/released and they update the Charness plugin/runtime.
  Nothing else is needed in `quality` skill code for the two optimized gates.
- **Fresh issue filed:** #377 tracks the broader `latest.md` current-pointer audit
  across skills. Do not resolve the symlink/current-pointer policy as part of
  the speed work unless explicitly reprioritized.
- **Known residual:** post-commit changed-line mutation consumer still fails for
  8 branch-wide files from the earlier speed slices, not for the final
  `check_current_pointer_writes.py` / `check_test_completeness.py` slice. This is
  a real branch-closeout debt before merge/push if the gate must be clean.
- Open issues (`gh`, 2026-06-16): #377, #376, #375, #371.

## Next Session

- **First decision:** publish/release the runtime optimization branch, or first
  pay down the remaining branch-wide changed-line mutation coverage debt.
  If publishing, run `charness:release`; if paying debt down, start with
  [run_standing_pytest.py](../scripts/run_standing_pytest.py),
  [mutation_coverage_producer.py](../scripts/mutation_coverage_producer.py),
  and [run_slice_closeout.py](../scripts/run_slice_closeout.py) blocking targets
  from the consumer output.
- After that, resume the open-issue queue: #377 latest/current-pointer audit,
  #376 helper-output re-judgment, #375 achieve scaffold current-frame
  disposition, and #371 agent-browser orphan lifecycle.
- **Still deferred** (reopen triggers): **E2b** (chunker ingests recurring waste —
  needs real 0.45.0+ usage telemetry) and the **Coordination-Cues floor merge**
  (a floor *removal*, separately critiqued).
- Older deferrals: D28/D29 in [deferred decisions](./deferred-decisions.md); the
  [contract-effectiveness fixture](../evals/cautilus/contract-effectiveness.fixture.json)
  needs a log-backed request.

## Discuss

- Whether to ship these runtime fixes now so Charness consumer repos benefit, or
  hold release until branch-wide mutation coverage is fully clean.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [latest/current-pointer issue #377](https://github.com/corca-ai/charness/issues/377)
