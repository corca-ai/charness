# Lane brief T1: the root `tools/` tree, its import rule, and the first moves (#769, Goal Run #765)

Read `gh issue view 769` (Owned scope, second bullet; Acceptance; Non-claims),
the table in `charness-artifacts/quality/2026-09-02-gate-classification-769.md`
(`tools` rows), and `charness-artifacts/goal-runs/765/briefs/map-769-export.md`
in full: it has the MOVE and STAY-SHARED lists (2.3, 2.4), the rows that
resist the move (2.5), every reader that globs `scripts/` (section 3), the
module-resolution proof (section 5), the precedents (section 6), and the
ordered risk list (7). Cite the row and the map line for every move.

Outcome: `tools/` exists as a non-exported root tree with one import rule,
every reader in map section 3 marked ADD covers it, the export gates treat it
as consumer-invisible, `SOURCE_ONLY_PLUGIN_SCRIPTS` is retired, and the first
batch of `tools` gates runs from its new home with one seeded failure per
moved gate proving it still bites.

## Design (the parent's; deviate only with the map line that forces it)

1. Import rule (map 5.3, exit 3): a `tools/` module is run as
   `python3 -m tools.<name>` from the repo root, never by path; `tools/__init__.py`
   exists and is empty. Inside a `tools/` module a former bare sibling import
   of a STAY-SHARED module becomes `from scripts.<name> import ...`; the
   two root shims (`runtime_bootstrap`, `yaml_output`) stay importable bare
   because `-m` puts the repo root first on `sys.path`. No `sys.path`
   mutation in any moved file; no third shim pair under `tools/`
   (`check_bootstrap_shim_consistency.py` would have to police it).
   `native_gate_lib.py:29-32` and `inventory_skill_script_references.py:57`
   are the two the map proves break under every other exit; fix them by
   this rule.
2. Batch A moves (this lane): `validate_skills`, `validate_quality_reference_catalog`,
   `check_quality_tool_fixtures`, `validate_surfaces`,
   `validate_inference_interpretation`, `validate_public_skill_validation`,
   `validate_public_skill_dogfood`, `validate_profiles`, `validate_presets`,
   `validate_integrations`, `validate_packaging`, `validate_packaging_committed`,
   `validate_attention_state_visibility`,
   `validate_inventory_consumption_declaration`,
   `check_inventory_declaration_coverage`, `inventory_skill_script_references`,
   `check_unreferenced_scripts`, `validate_quality_closeout_contract`,
   `check_skill_contracts`, `check_skill_bootstrap_vars`,
   `check_bootstrap_shim_consistency`, `check_public_doc_coupling`,
   `check_references_link_inventory`, with the helpers the map lists as
   reachable only from them: `packaging_policy_validators`,
   `validate_packaging_install_surface`, `public_skill_dogfood_validation_lib`,
   `skill_portability_lib`. Use `git mv` so history follows.
   NOT in this lane (lane T2, after lane R1 lands, because R1 is editing
   them now): `check_timing_layer_completeness`, `check_runtime_budget_universe`,
   `validate_current_pointer_freshness`, `check_current_pointer_writes`,
   `check_closeout_classification_parity`, `check_coverage` and
   `check_coverage_extra_lib`, `check_export_self_sufficiency` and
   `export_self_sufficiency_lib`, `check_plugin_asset_command_carriers`,
   `check_plugin_doc_links`, `check_plugin_import_smoke`, `native_gate_lib`,
   `run_evals` and the `eval_*` helpers, `quality_label_universe`.
   STAYS in `scripts/` although the mechanical closure says move (say so in
   the body): `doctor` (consumer CLI, map 2.3 caveat), `packaging_lib`,
   `export_plugin`, `sync_root_plugin_manifests` (the export machinery that
   `charness init/update` runs in the managed checkout; `validate_packaging*`
   import `scripts.packaging_lib` from `tools/`), and every STAY-SHARED
   module in map 2.4.
3. Readers (map section 3, every ADD row): `check_unreferenced_scripts`
   (`NODE_GLOBS`, `_is_node`, the path and module regexes, `_source_class`
   gains a `tools` arm, and the reference graph learns the
   `python3 -m tools.<name>` spelling as a reference to `tools/<name>.py`),
   `check_code_lengths` (globs and the per-tree cap at `:242,:255`),
   `check_python_runtime_inheritance`, `check_subprocess_form`,
   `inventory_gitignore_scan_hygiene` default globs, `run-quality.sh`
   py-compile array and its refusal message (`:1156-1170`),
   `check-python-lint.sh` roots, `check-shell.sh` (a `[[ -d tools ]]`-guarded
   branch), `check_bootstrap_shim_consistency` `SCAN_PATTERNS`,
   `.agents/quality-adapter.yaml` `gate_design_review_globs` and
   `prompt_asset_policy.source_globs`, `export_self_sufficiency_lib.py:82-108`
   `CONSUMER_OWNED_ROOTS` gains `tools` with a one-line reason (a repo-only
   tree, never shipped, so a reference to it from an exported module is a
   shipping gap the gate must keep reporting). `sample_mutation_files.py`
   MUTATION_POOLS: add `tools/**/*.py` (moved gates keep their mutation
   coverage; say so). `helper_provenance_lib`: EXCLUDE, per the map.
   `check_test_production_ratio`: leave as is, note the decision.
4. Runner rows: in `scripts/run-quality.sh` change each moved gate's
   `python3 scripts/<name>.py` to `python3 -m tools.<name>` (labels
   unchanged; the label parsers key on labels, not paths). Lane R1 ships
   `scripts/quality_gates_extract.py`; if it has landed on your base, re-run
   it so `.agents/quality-gates.yaml` matches; if not, say so in the body and
   the parent regenerates.
5. Export: delete `SOURCE_ONLY_PLUGIN_SCRIPTS` and its unlink loop
   (`scripts/packaging_lib.py:42-46,301-302`) and the test that pins it
   (`tests/quality_gates/test_packaging_validation.py`); the exported
   `plugins/charness/scripts/run-quality.sh` now carries `-m tools.` rows a
   consumer cannot run (map 1.5 "the real export hole"): add to
   `check_export_self_sufficiency` (or its lib) a check that an exported `.sh`
   naming `tools/` or `-m tools.` is a shipping gap, with a seeded test.
   Then run `python3 scripts/export_plugin.py` to a tmp root and prove no
   `tools/` file and no moved gate is in it (this is the issue's first
   acceptance line; paste the diff summary).
6. Surfaces and docs: repoint the moved paths in `.agents/surfaces.json`
   (map 3.1 row 17; never add `tools/` to the `materialized-plugin-export`
   entry), `docs/validator-timing-layers.md` links, and any `docs/` page or
   skill reference naming a moved script (`check-doc-links` and
   `check-plugin-dir-references` tell you; in shipped skill prose use the
   `<authoring-repo>/tools/X.py` spelling, map 1.5). Add `docs/export-boundary.md`
   (short, `Last verified: 2026-09-02`, linked from `docs/index.md`) as the
   prose owner of the rule map 6.5 says has none: which root trees ship, the
   `tools/` import rule, and the clean-export probe command.
7. Tests naming a moved script by string (map 3.3): re-point the path; an
   in-process loader now loads `tools/<name>.py`; a `boundary_contract` spawn
   uses `-m tools.<name>` from the repo root. Add one seeded-failure test per
   moved gate if none exists (Acceptance line 2).

## Scope

Everything the design names, plus new `tools/` files and tests. Do not edit
`scripts/quality_label_universe.py`, `scripts/quality_adapter_lib.py`,
`skills/public/quality/scripts/adapter_validators.py`, or the T2 modules
listed above. Do not touch `plugins/**` (generated; regenerate with
`sync_root_plugin_manifests.py`). Do not spawn descendant agents.

## Rules

1. Tests in-process (`tests/script_loader.py` / `script_main.py`); read
   `docs/development.md` "Verification and export" first.
2. Every moved module keeps its length under the root cap the length gate
   now applies to `tools/`.
3. Commit in TWO commits: first the tree, import rule, readers, export
   change, and docs page with NO gate moved yet
   (`quality: add the non-exported tools/ tree, its import rule, and widen every scripts/ reader to it (#769 T1 lane candidate)`),
   then batch A moves with runner rows, surfaces, docs links, and tests
   (`quality: move the first batch of repo-only gates into tools/ (#769 T1 lane candidate)`).

## Verification before you stop

```
python3 -m ruff check <touched .py>; python3 -m ruff format --check <touched .py>
for m in <each moved module>; do python3 -m tools.$m --help; done          # from the repo root; paste any failure
python3 -m tools.check_unreferenced_scripts --repo-root . --strict
python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing
python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing
python3 scripts/check_python_runtime_inheritance.py --repo-root . --require-git-file-listing
python3 scripts/export_plugin.py --repo-root . --host claude --output-root /tmp/export-probe && find /tmp/export-probe -path '*tools*' | wc -l    # expect 0; check the real flag names first
python3 scripts/check_export_self_sufficiency.py --repo-root .
python3 scripts/sync_root_plugin_manifests.py --repo-root .
python3 scripts/run_standing_pytest.py --repo-root .
./scripts/run-quality.sh --full --read-only
./scripts/check-docs.sh
```

Bodies carry per moved gate: old path, new path, the runner row, the seeded
failure test, and the exact commands with verdicts. No close keyword. Stop
after the second commit and report both hashes.
