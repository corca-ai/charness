# Scripts packaging premises and measurements

This record is the P0 correction for issue #770. The historical critique
artifacts remain frozen; this dated quality artifact records the on-disk facts
that shaped the packaging foundation.

## Stale issue premises

- `scripts/__init__.py` already exists and is tracked.
- `import_repo_module` already passes dotted names to
  `importlib.import_module`; dotted package resolution was not the blocker.
- `scripts/` already has the tracked non-package directories
  `agent-runtime/` and `templates/`.
- The actual nested-script blockers were the bare sibling imports at the top of
  185 files and `repo_root_from_script` using `parent.parent`, which resolves a
  nested script to `<repo>/scripts`.
- The proposed package names `packaging` and `coverage` are import-name
  collisions with installed distributions, so the filename gate must inspect
  directories as well as Python files.

## Measurements from map-770 §2.2

These are the map's post-#769 counts, retained here as the planning baseline;
they are not claims that P0 moved files. The package lanes use these families
when measuring later diffs.

| Family | Issue claim | Measured count | Measurement rule |
| --- | ---: | ---: | --- |
| gates | ~106 | 65 | `check_` / `validate_` |
| mutation | 15 | 26 | `*mutation*` or `mutate_*` |
| coverage | 12 | 9 | `*coverage*` |
| worktree | 14 | 14 | `worktree_*` |
| review | 14 | 16 | `*critique*` / `reviewed_input_*` |
| lessons | 14 | 14 | lesson family |
| hooks | 10 | 5 | `*hook*` |
| packaging | 7 | 3 | `*packag*` / `*plugin*` |

## P0 outcome

- The committed rewrite summary was 183 files and 242 rewritten import
  statements. A rerunnable `rewrite_script_preambles.py --check` now reports
  `changed_files: 0`, `rewritten_imports: 0`, and
  `already_normalized_files: 0`.
- No script moved into a package in this lane.
- The before-snapshot is
  [`2026-09-02-gate-universes-before-770.yaml`](./2026-09-02-gate-universes-before-770.yaml);
  the current snapshot is byte-identical, so later package lanes have a
  diffable file-set baseline.

## P4 package measurements and flat residue

Measured at the P4 lane tip (`ccb861a2e`) from the six package commits. Counts
exclude each package's `__init__.py` marker; the issue package also carries its
`rca_event.schema.json` sibling data file.

| Package | Moved Python modules | Commit |
| --- | ---: | --- |
| evidence | 13 | `b38093b59` |
| task_run | 11 | `30b439223` |
| issue | 10 | `33eb4eed0` |
| setup | 9 | `07b4720f5` |
| retro_debug | 7 | `4459692ca` |
| premise | 5 | `ccb861a2e` |
| **Total** | **55** | 6 package markers |

The intended integrated flat residue under `scripts/` is:

- `scripts/adapter_lib.py` (pinned flat carrier)
- `scripts/runtime_bootstrap.py` (pinned flat carrier)
- `scripts/skill_runtime_bootstrap.py` (pinned flat carrier)
- `scripts/yaml_output.py` (pinned flat carrier)
- `scripts/doctor.py` (root compatibility shim delegating to `scripts.setup.doctor`)

This P4 branch is based on P0 while the independent P1–P3 lanes remain
unmerged. The measured lane-tip inventory therefore still contains 309
top-level `scripts/*.py` files; the five-file list above is the post-integration
residue target, not a claim that those companion lane moves are present here.
The `pyproject.toml` `pythonpath` comment is retained because flat dependencies
remain at this lane tip.
