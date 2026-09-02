# Lane brief P4: `evidence`, `task_run`, `issue`, `setup`, `retro_debug`, `premise`, and the flat residue (#770)

Follow `charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md`.
Packages, one commit each: `evidence` (map 2.4, 13), `task_run` (11;
re-point the `charness` CLI `from scripts import task_run` and
`_load_task_run_lib`), `issue` (10), `setup` (9; `doctor` stays a
consumer CLI, moved WITH a root shim `scripts/doctor.py` that delegates,
because `charness tool doctor` and the attention-state registry name it),
`retro_debug` (7), `premise` (5). Final commit: list what remains flat under
`scripts/` (the four pinned files plus shims), remove the `pythonpath`
comment in `pyproject.toml` if no flat dependency remains (P0 rule 6), and
append the measured per-package counts to
`charness-artifacts/quality/2026-09-02-scripts-packaging-premises.md`.
