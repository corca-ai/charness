# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- **Primary next action: Batch C of the pytest test-value audit.** Read the owning
  artifact first: [test-value-audit](../charness-artifacts/quality/2026-07-03-pytest-suite-test-value-audit.md)
  (= `quality/latest.md`). Umbrella intent (fewer-is-better; prune what doesn't earn
  its place): [intent.md](../charness-artifacts/reference-compaction/intent.md).

## Current State

- **Test-value audit DONE** (full 46-batch). Removed 23 redundant test fns + 2 dead
  source fns across `a855ce74`..`32b078c9`; collection 3997 -> 3974; standing suite
  green; every deletion fresh-eye reviewed. Verdict: the suite is lean (~1% delete-safe)
  and already disciplined on issue-overfit — the remaining lever is packaging, not deletion.
- **CRITICAL corrected fact**: this repo captures subprocess coverage
  ([mutation_sampling_lib.py](../scripts/mutation_sampling_lib.py) enables
  `coverage.process_startup` via `COVERAGE_PROCESS_START`). "subprocess test = 0% covered"
  is **FALSE** here — do NOT keep or defer a test on that premise (it caused 3
  over-cautious keeps, since deleted).
- Reference-compaction/churn track (separate, still live): deletion track CLOSED
  (0 delete-safe); churn sweep remaining — see its contract in References.

## Next Session

1. Read the audit artifact §"Waste patterns" + §"Deferred — batch C anchors".
2. Batch C = prose-pin parametrize. Take the anchor file list from the audit artifact
   §"Deferred — resolved / remaining" (batch C bullet). For each, first confirm it
   exercises NO Python source (pure markdown-substring assert).
3. Fold N single-substring tests into one `@pytest.mark.parametrize`, keeping every
   asserted substring — rewrite, do NOT delete. Verify: ruff, affected files, standing
   suite, collection delta.
4. Closeout each batch with a fresh-eye review + commit; append to the audit artifact Applied.

## Discuss

- KEPT deliberately (NOT batch C): the 3 usage-episodes plugin bundle smokes — the only
  end-to-end proof the shipped plugin bundle runs. Do not delete.
- Brittle: [test_handoff_plan.py](../tests/test_handoff_plan.py) reds broad pytest on any
  >=60-line handoff — keep this file under 60 lines.

## References

- pickup: [test-value-audit](../charness-artifacts/quality/2026-07-03-pytest-suite-test-value-audit.md) · [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) · [reference-compaction contract](../charness-artifacts/reference-compaction/contract.md)
