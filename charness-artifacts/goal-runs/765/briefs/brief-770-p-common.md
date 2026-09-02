# Shared rules for the #770 package lanes (P1 to P4)

Read `gh issue view 770` and `charness-artifacts/goal-runs/765/briefs/map-770.md`
sections 2.3, 2.4, 2.6, 3, 5. Lane P0 has landed: nested scripts resolve
their repo root by marker walk, the canonical repo-script preamble is
enforced under `scripts/**`, `python3 -m tools.snapshot_gate_universes`
writes the gate-universe snapshot, and
`charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml` is the
"before". Read those AS LANDED first.

Package names (the parent's; `packaging` and `coverage` are renamed because
they shadow installed distributions, map 2.5): `core` (the `_lib` core minus
the four pinned files `runtime_bootstrap`, `skill_runtime_bootstrap`,
`yaml_output`, `adapter_lib`, which stay flat), `gates`, `gates_support`,
`mutation` (coverage folded in), `worktree`, `review`, `lessons`, `hooks`,
`plugin_export`, `adapters`, `evidence`, `artifacts`, `task_run`, `issue`,
`setup`, `retro_debug`, `premise`. Membership is map 2.3 and 2.4; ambiguous
modules (map 2.6) go to Candidate A unless your brief says otherwise.

Rules for every package move:

1. ONE package per commit: `git mv scripts/<name>.py scripts/<pkg>/<name>.py`
   with `scripts/<pkg>/__init__.py` (one-line docstring), then every carrier:
   `python3 scripts/<name>.py` and `scripts/<name>.py` strings in SKILL.md,
   references, `.agents/*.yaml`, `.agents/surfaces.json`, `.githooks/*`,
   `.github/workflows/*`, `docs/*.md`, `README.md`, `AGENTS.md`, `packaging/*`,
   tests, and `.agents/quality-gates.yaml` rows (then
   `python3 scripts/quality_gates_extract.py --repo-root . --check` if the
   shell queue still exists, else the parity test). Never edit
   `charness-artifacts/**` history.
2. Imports: a moved module imports siblings as `from scripts.<pkg>.<name>`
   (or `from scripts.<other_pkg>.<name>`); the four pinned files stay bare.
   `import_repo_module(__file__, "scripts.<pkg>.<name>")` in skill scripts.
3. After EACH package commit:
   `python3 -m tools.snapshot_gate_universes --repo-root . --out /tmp/after.yaml`
   and diff against the before-snapshot: the only differences allowed are
   path renames of the moved files (paste the diff summary in the body);
   any file that FELL OUT of a universe is a blocker to fix in that commit.
4. No behaviour change in any moved script (issue Non-claims); if a move
   forces one, stop and report instead.
5. `check_export_self_sufficiency`, `check_plugin_import_smoke`, and
   `tools/check_unreferenced_scripts --strict` green after each commit;
   regenerate the plugin mirror before pytest.
6. Tests in-process; every touched CLI `python3 <file> --help` from the repo
   root; the direct-run shape for one moved script per package as a
   `boundary_contract` case.
7. Do not touch `plugins/**`. Do not spawn descendant agents.

Verification before you stop (after the last commit):

```
python3 -m tools.snapshot_gate_universes --repo-root . --out /tmp/after.yaml; diff charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml /tmp/after.yaml | grep -v "^[<>] .*scripts/" | head
python3 scripts/check_export_self_sufficiency.py --repo-root .
python3 -m tools.check_unreferenced_scripts --repo-root . --strict
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh --full --read-only
./scripts/check-docs.sh
```

Subjects: `scripts: move <pkg> into scripts/<pkg>/ with gate-universe parity (#770 <lane> lane candidate)`.
No close keyword. Stop after the last commit and report every hash.
