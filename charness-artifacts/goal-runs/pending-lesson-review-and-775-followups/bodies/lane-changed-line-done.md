<!-- charness-work-item-key: lane-changed-line-done -->

## Objective

A `charness task run` lane, and any subagent brief that touches `scripts/` or `skills/`, cannot report done while `release_changed_line_coverage.py` would refuse the push. Four refusals for one commit on 2026-09-03 were this class (`green-test-is-not-covered-line`).

## Owned scope

- `scripts/task_run/task_run_completion.py::complete_task` (and the runner that feeds it `base_sha`) runs `scripts/mutation/release_changed_line_coverage.py --base-sha <lane base>` on the candidate diff at completion and writes the verdict and `blocking_detail` into the receipt; the receipt's result state carries the refusal so the parent's read shows it.
- `docs/parallel-execution.md` "Disjoint writers": the definition-of-done sentence for briefs, naming the mechanism and the gate's runtime as measured.
- `.agents/claude-host.md`: the same sentence for in-process subagent briefs, which have no lane receipt.
- Tests: a lane seeded with an uncovered branch ends with the refusal in its receipt; a lane with every changed line proven completes as before.

## Acceptance

- The seeded lane's receipt names the unproven line; the parent's read of the receipt shows the same `blocking_detail` the pre-push hook prints for that tree.
- Runtime of the gate at completion measured and written into the `docs/parallel-execution.md` "Disjoint writers" sentence that names the mechanism.
- `run_standing_pytest.py` green with the skip list read; changed-line gate green on this slice's own diff.

## Focused verification

Standing lane on `tests/test_task_run*.py`, then the standing runner; a manual lane in a worktree with a seeded uncovered branch.

## Dependencies

none

## Non-claims

Does not change what the changed-line gate proves or the pre-push hook. Does not add a gate over brief text itself.
