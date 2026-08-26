# Goal Run `backlog-708` Python-length aggregation

## Scope

- Work item: `backlog-708` / issue `#708`
- Contract source: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md`
- Owned source: `scripts/check_python_lengths.py` and its generated plugin mirror
- Owned tests: `tests/quality_gates/test_python_length_gates.py` and the updated hard-failure interpretation assertion

## Implemented contract

The length gate now visits every selected target, accumulates hard `ValidationError`
and `SyntaxError` messages, prints every per-file reason in deterministic target
order, prints one aggregate failure line, and returns `1`. A first over-limit file
cannot hide a second one. The source and plugin mirror compare byte-identically.

## Executed verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_python_length_gates.py` — `16 passed`.
- Isolated proof commit `8c71951405e04de9bf2bda202b10017129e01f1` ran `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, one changed mutation-pool file analyzed, `blocking: []`, and `unmapped_changed_pool_files: []`.
- The isolated proof worktree's pre-commit checks passed for the source, mirror, and interpretation test.
- Targeted mutant: changing `hard_failures.append(str(exc))` to `hard_failures.clear()` made the two-invalid-file regression test fail; the source was restored before recording the clean proof.
- Path-scoped planner returned `status: not-applicable`, `required: false`.

## Boundary and non-claims

This is local deterministic verification only. It does not claim GitHub issue
closure, hosted or installed-host behavior, release, tag, push, or fresh-eye
review. The user-authorized implementation path omits forced fresh-eye, handoff,
and micro-slice rituals. Issue `#708` remains open.
