# Lane brief P0: the packaging foundation for scripts/ (#770, Goal Run #765)

Read `gh issue view 770`, then `charness-artifacts/goal-runs/765/briefs/map-770.md`
sections 0, 1, 2.5, 4, 5 in full. Section 0 shows four premises of the issue
are stale on disk: `scripts/__init__.py` exists, `import_repo_module` already
resolves dotted names, `scripts/` already has two non-package subdirectories,
and the real blockers are (a) the bare sibling import on line 1 of 185 files
that only resolves because `sys.path[0]` is `scripts/` when a flat script
runs, and (b) `repo_root_from_script` (`scripts/runtime_bootstrap.py:209-216`)
computing `parent.parent`, which silently returns `<repo>/scripts` for a
nested script. Section 2.5 proves two proposed package names, `packaging`
and `coverage`, shadow installed third-party distributions.

Outcome: a script can live at `scripts/<pkg>/<name>.py` and behave exactly
as at `scripts/<name>.py` in every shape the repo uses (direct run from the
repo root, `-m`, in-process loaders under pytest, the exported plugin); the
acceptance criterion "every gate's file set is identical before and after"
is a diffable artifact; and a directory name that collides with an
importable top-level module is refused. NO package move happens in this
lane (lanes P1 to P4 move, one package per commit).

## Design (the parent's; cite the map line when you deviate)

1. `repo_root_from_script` finds the root by marker walk (the way
   `repo_root_from_skill_script` does at `scripts/skill_runtime_bootstrap.py:98-123`),
   so depth is irrelevant; a test proves `scripts/a/b/x.py` reports the repo
   root. Keep the flat case byte-identical in behaviour.
2. The preamble: replace the bare `from runtime_bootstrap import ...` /
   `from yaml_output import ...` on line 1 of the 185 files (map 1.4) with the
   ancestor-walking shim the repo already machine-enforces for skill scripts
   (`tools/check_bootstrap_shim_consistency.py` CANONICAL_SHIM, map 5.5 option
   1), or a repo-script variant of it that the same gate enforces under
   `scripts/**`. Bare imports of OTHER `scripts/` siblings become
   `from scripts.<name> import ...` only where the module is imported by a
   script that will move; do not touch skill scripts. Do this with a script
   you commit under `tools/` (`rewrite_script_preambles.py`) so the change is
   mechanical and re-runnable, and paste its summary.
3. `python3 scripts/quality_universes_lib.py --repo-root . --files [--key K]`
   prints the matched files per family (map 4.5, one-flag change), and
   `tools/snapshot_gate_universes.py` writes ONE artifact combining that
   output with the six bespoke commands of map 4.6 (unreferenced-scripts node
   list, `check_code_lengths --headroom`, `inventory_adapter_gate_design
   --detail` reviewed paths, the py-compile array, check-shell discovery, the
   empty-scope-honesty detector set) so a before/after diff is one command:
   `python3 -m tools.snapshot_gate_universes --repo-root . --out <path>`.
   Commit the current snapshot under `charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml`
   (the "before" the package lanes diff against).
4. FLAT-pattern repairs (map 4.3, the gates whose globs are still
   single-star `scripts/*.py` only): widen each to recursive with a seeded
   test, or route it through the universes family it belongs to.
5. Name collisions: `scripts/check_python_filenames.py` also inspects
   DIRECTORY names under `scripts/` and refuses one that resolves through
   `importlib.util.find_spec` to an installed or stdlib module, with a
   seeded test using `scripts/packaging/`; the acceptance line in the issue
   is corrected in the closeout, not here.
6. `pyproject.toml` `pythonpath` (map 1.5): keep it until P4 removes the
   last flat dependency; add one comment line saying so.
7. Record, in a new "Corrections" section appended to
   `charness-artifacts/critique/2026-08-07-*` (the artifact map section 6
   names) is NOT allowed: historical artifacts are frozen. Instead write
   `charness-artifacts/quality/2026-09-02-scripts-packaging-premises.md`
   stating which issue premises were stale and the measured counts per
   package (map 2.2), linked from the closeout later.

## Scope

Everything the design names plus tests under `tests/`. Do not move any
script into a package. Do not touch `plugins/**` (regenerate with
`sync_root_plugin_manifests.py`). Do not spawn descendant agents.

## Rules

1. Tests in-process (`tests/script_loader.py`); read `docs/development.md`
   "Verification and export" first; a test proving a nested script resolves
   must run it in BOTH shapes (direct `python3 scripts/<pkg>/x.py` from the
   repo root as a `boundary_contract` case, and the in-process loader).
2. Every touched CLI gets `python3 <file> --help` from the repo root in the
   verification (the 39-file defect class).
3. Commit in FOUR commits, in this order: root resolution and preamble
   rewrite; snapshot flag and tool plus the before-snapshot; FLAT repairs;
   name-collision check and the premises record. Subjects start with
   `scripts:` and end with `(#770 P0 lane candidate)`.

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
python3 -m tools.check_bootstrap_shim_consistency --repo-root .
python3 -m tools.snapshot_gate_universes --repo-root . --out /tmp/after.yaml && diff charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml /tmp/after.yaml   # empty: P0 moves nothing
python3 scripts/check_python_filenames.py --repo-root .
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 -m tools.check_unreferenced_scripts --repo-root . --strict
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh --full --read-only
./scripts/check-docs.sh
```

Bodies carry the exact commands with verdicts. No close keyword. Stop after
the fourth commit and report the hashes.
