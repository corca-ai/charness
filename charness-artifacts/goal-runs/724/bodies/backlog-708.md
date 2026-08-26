<!-- charness-work-item-key: backlog-708 -->
# Existing Work Item #708 — Report every over-limit Python file

## Purpose and premise

Make the Python-length gate report every over-limit file in deterministic order
and one failing result. Re-read its current traversal and failure aggregation.

## Owned change and acceptance

The two-invalid-file fixture names both files and preserves one reason per file;
fixing the first must not reveal a previously hidden second failure by accident.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_python_length_gates.py`, then changed-line proof. The result is a local gate claim only.

## 2026-08-27 follow-up — aggregate every hard failure

The Python-length gate now evaluates every selected target before returning. It
collects each hard length or syntax failure in deterministic target order, prints
all per-file reasons to stderr, emits one aggregate failure line, and returns
`1`; a first failure no longer hides later files. The source and generated plugin
mirror are identical.

The acceptance fixture creates both a 361-line skill helper and a 481-line repo
script and asserts both paths, both reasons, and `Validation failed for 2 file(s)`.
The in-process interpretation test was updated to the new `main() -> 1` contract
and no longer expects an exception; the boundary-test ratchet remains unchanged.

## Follow-up verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_python_length_gates.py` — `16 passed`.
- Isolated proof commit `8c71951405e04de9bf2bda202b10017129e01f1`: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, one changed mutation-pool file analyzed (`scripts/check_python_lengths.py`), `blocking: []`, `unmapped_changed_pool_files: []`.
- Targeted mutant proof: replacing the accumulation line with `hard_failures.clear()` made `test_check_python_lengths_reports_all_over_limit_files_in_one_run` fail (`returncode 0`, expected `1`); the mutation was restored.
- Path-scoped implementation planner: `status: not-applicable`, `required: false`.
- Source/plugin mirror comparison and the proof worktree pre-commit gates passed.

## Remaining acceptance boundary

This child remains open by policy. The result is a local deterministic gate claim;
it does not claim issue closure, hosted or installed-host behavior, release, tag,
push, or fresh-eye review. The parent worktree still contains unrelated dirty
cutover changes, so the isolated proof is the authoritative changed-line result
for this child.
