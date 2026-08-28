# Lane brief: quality-lengths-refactor

`scripts/check_python_lengths.py` fails on four files (pre-existing debt
the operator has asked to clear now):

- `scripts/task_run.py` — 547 code lines (limit 480)
- `scripts/task_run_support.py` — 655 (limit 480)
- `tests/charness_cli/test_task_run.py` — 897 (limit 800)
- `tests/quality_gates/test_runtime_budget_gate.py` — 810 (limit 800)

Per the gate's own message and `docs/deferred-decisions.md` D33: split on
a COHESIVE concept boundary or delete dead code — do NOT mechanically
spill into an `_extra_lib`/`_lib` companion to dodge the cap. Read each
file and find the real seam (e.g. task_run_support already mixes scope
resolution, codex command building, runtime paths, and result
persistence — those are separable owners; the test files may carry
deletable duplication or a coherent scenario split). Preserve ALL current
behavior: `charness task run/status` is live infrastructure (it runs the
very lanes this repo works with) and `tests/charness_cli/test_task_run.py`
plus `tests/quality_gates/test_runtime_budget_gate.py` pin it.

Requirements:

- After the split: `python3 scripts/check_python_lengths.py --repo-root .`
  reports zero hard failures.
- `python3 -m pytest -q tests/charness_cli/test_task_run.py
  tests/quality_gates/test_runtime_budget_gate.py` green, plus any module
  that imports the split code.
- `ruff check` clean on touched files. New modules need snake_case names
  and must respect the 480 cap themselves with headroom.
- Do not change any public CLI behavior, result schema, or receipt
  format; imports of `task_run`/`task_run_support` from other modules and
  tests must keep working (check callers with grep before moving
  symbols).
- Do not spawn descendant agents.

Scope: `scripts/task_run*.py` (glob keeps new split modules in scope),
`tests/charness_cli/test_task_run*.py`,
`tests/quality_gates/test_runtime_budget*.py`, and new `scripts/*.py`
modules created by the split — name them within `scripts/task_run_*.py`
so they stay inside the scope glob. Touch nothing else.

Stop: gates above green in your worktree. One coherent commit, prefix
`refactor(task):`. Final message: the seam you chose per file and why,
commands + observed results, any caller updates made.
