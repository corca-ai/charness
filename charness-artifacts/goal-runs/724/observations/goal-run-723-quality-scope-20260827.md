# Goal Run `backlog-723` quality planning scope

## Scope

- Work item: `backlog-723` / issue `#723`
- Contract source: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md`
- Follow-up source read: live issue `#723` body and its Ceal-shaped comment
- Owned producer boundary: `quality_declaration_lifecycle.py` plus the cohesive
  `quality_skill_scope.py` producer, with byte-identical plugin mirrors
- First consumer: `plan_quality_run.py::build_plan`
- Owned fixture: `tests/quality_gates/test_quality_run_planner_adapter_scope.py`

## Implemented contract

The quality lifecycle now resolves an adapter's explicit
`skill_ergonomics_skill_paths` before default discovery is used as planner
scope. A declared directory resolves its root `SKILL.md` and one-level package
children, while repo-relative and configured external-support paths retain
their canonical display form. The lifecycle reports `skill_scope_source` as
`adapter-declared` or `discovered`, and the planner derives
`skills_in_scope`, samples, structural target resolution, and the structural
packet from that one selected list.

An explicit declaration that resolves no readable `SKILL.md` remains
`unreachable`; it does not become an in-scope skill through path existence
alone. The first quality consumer owns the selection decision, while the
structural packet keeps its quality move card advisory with the default
`advisory-or-no-gate` posture. No heuristic finding creates a fake mirror,
command, receipt, or automatic move.

The live comment's catalog-equivalent-owner and broader heuristic interaction
requests were reviewed and intentionally left outside this child because the
readiness contract defines #723 as a bounded consumer-scope cutover. They are
preserved as follow-up/non-claims rather than represented as implemented.

## Executed verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_quality_run_planner.py` — `39 passed`.
- Combined planner, adapter-scope, and declaration-path tests — `69 passed`.
- Source/plugin planner, lifecycle, and scope producer mirrors compare byte-identically.
- `py_compile`, `ruff`, `git diff --check`, and the proof branch pre-commit checks passed.
- Isolated proof commit `b116e9f3e` ran
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha 3f16d6b4285c6368e0e1af5fc5d7a414c7db407a --refuse-unestablished`:
  `status: clean`, `consumer_returncode: 0`, 3/3 changed mutation-pool files
  analyzed, `blocking: []`, and `unmapped_changed_pool_files: []`.
- The proof worktree was clean after the coverage receipt. No fresh-eye review,
  handoff update, or micro-slice ritual was run under the explicit user override.

## Boundary and non-claims

This observation proves local planner/lifecycle behavior only. It does not
prove package verification execution, catalog-equivalent-owner adoption,
consumer heuristic disposition, installed-host behavior, hosted behavior,
release, tag, push, or issue closure. Issue `#723` remains open.
