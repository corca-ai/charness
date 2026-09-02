# #769 export boundary map: `scripts/` -> non-exported `tools/`

Repo: `/home/hwidong/codes/charness`. Date: 2026-09-02. Read-only investigation.
Input: `charness-artifacts/quality/2026-09-02-gate-classification-769.md`.
Every claim below is cited `file:line`. Facts marked **VERIFIED** were executed.

---

## 0. Three findings that change the shape of the move

1. **A `tools/` script cannot use the repo's own import spelling.** 38 of the 47
   scripts in the MOVE set import a sibling by bare name (`from runtime_bootstrap
   import ...`, `from yaml_output import ...`). That resolves only because
   `sys.path[0]` is the script's own directory and `scripts/runtime_bootstrap.py`
   / `scripts/yaml_output.py` sit there. From `tools/` it raises
   `ModuleNotFoundError` (**VERIFIED**, section 5). The root shim
   `runtime_bootstrap.py:8` hardcodes `parent / "scripts" / ...`, so copying the
   root shim into `tools/` does **not** work (**VERIFIED**).
2. **Non-export costs nothing; keeping the gates running costs ~20 edits.**
   `export_plugin_tree` (`scripts/packaging_lib.py:227-320`) is an allowlist, so
   a new root tree is non-exported by absence with zero exporter change. But ~20
   hardcoded scan roots name `scripts/` literally and would silently stop
   covering the moved files (section 3).
3. **`SOURCE_ONLY_PLUGIN_SCRIPTS` retirement is not free.** All three entries
   (`scripts/packaging_lib.py:42-46`) are `tools` rows, so deleting the constant
   is correct - but two of the three (`validate_public_skill_validation`,
   `validate_public_skill_dogfood`) import `public_skill_validation_lib` /
   `public_skill_dogfood_lib`, which a **shipped** skill script imports
   (`skills/public/quality/scripts/suggest_public_skill_dogfood.py`). Those
   helpers must stay in `scripts/` and will keep shipping.

---

## 1. Export mechanics

### 1.1 How `scripts/` is exported

`scripts/packaging_lib.py:298-300`:

```python
scripts_root = repo_root / "scripts"
exported_scripts_root = plugin_root / "scripts"
replace_tree_if_present(scripts_root, exported_scripts_root)
```

The **whole tree**, recursively, minus cache dirs. `replace_tree_if_present`
(`:95-99`) rmtree's the destination then `copy_tree` (`:79-86`) with
`shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache")`.
There is no include list and no exclude list beyond the three names below. After
#769 the rule becomes exactly what these three lines already do.

### 1.2 The three `SOURCE_ONLY_PLUGIN_SCRIPTS`

`scripts/packaging_lib.py:42-46`, deleted post-copy at `:301-302`:

| Script | #769 row |
| --- | --- |
| `suggest_public_skill_validation.py` | not a queued gate label; sibling of the two below |
| `validate_public_skill_dogfood.py` | `tools` |
| `validate_public_skill_validation.py` | `tools` |

Retiring the constant means removing `:42-46` and the loop at `:301-302`. All
three files move to `tools/`, so the export loses them by relocation instead of
by deletion. Note `suggest_public_skill_validation.py` is source-only here but a
**shipped** near-twin exists at
`skills/public/quality/scripts/suggest_public_skill_dogfood.py`, which imports
`scripts.public_skill_dogfood_lib` and `scripts.public_skill_validation_lib`.

### 1.3 Bootstrap shims and root files the export carries

`scripts/packaging_lib.py:303-315` copies three repo-root files into the plugin
root:

| Root file | Line | Reason recorded in source |
| --- | --- | --- |
| `runtime_bootstrap.py` | `:303-305` | shim so `scripts.<name>` package-imports resolve |
| `yaml_output.py` | `:310-312` | comment `:306-309`: "~96 exported `scripts/` modules import `yaml_output` bare, which only resolves from the repo root when this shim is present" |
| `skill_runtime_bootstrap.py` | `:313-315` | skill-side equivalent |

Plus the dependency contract, `:205-208` + `:211-224` + call at `:317`: exactly
`packaging/bootstrap-python.json` and `packaging/bootstrap-requirements.txt`.
The comment at `:201-204` is the sharpest statement of the export boundary rule
anywhere in the repo: *"Only these - the rest of `packaging/` is this repo's own
release plumbing and means nothing to a consumer, and shipping a directory
wholesale is how an export grows surface nobody can point at."*

Other trees copied by `export_plugin_tree`: README with rewritten links
(`:230-243`), `skills/public/*` flattened to `skills/*` (`:245-252`),
`skills/shared` -> `shared` (`:254-255`), `.claude/agents` -> `agents`
(`:261-262`), `skills/support` -> `support` (`:264-284`), `profiles_dir`,
`presets_dir`, `integrations_dir` (`:286-288`), `integrations/locks` metadata
only (`:142-151`, called `:290-292`), `integrations/worktree` (`:294-296`), and
the two host manifests (`:319-320`).

### 1.4 Entry points

- `scripts/export_plugin.py` - CLI. Loads the manifest (`:64`, via
  `load_manifest`, `packaging_lib.py:49-61`), applies a version override
  (`:67`), rmtree's the plugin root and calls `export_plugin_tree`
  (`export_plugin.py:29-33`), optionally writes the Codex marketplace
  (`:35-43`). Emits a YAML receipt (`:70-78`).
- `scripts/sync_root_plugin_manifests.py` - the committed-artifact generator.
  Digest-snapshots the plugin root before and after (`:29-37`, `:73`, `:85`),
  rmtree + `export_plugin_tree` (`:74-76`), deletes stale root manifests
  (`:78-81`), writes `expected_root_artifacts` (`:82-84`), and reports an
  added/changed/removed diff (`:40-52`, `:89-96`). This is the command
  `validate-packaging-committed` proves is a no-op.

Neither entry point needs a change for #769: both delegate the whole tree
decision to `export_plugin_tree`.

### 1.5 What each export gate asserts, and what it would assert about `tools/`

| Gate | Script | What it asserts about `scripts/` | Behaviour toward a non-exported `tools/` |
| --- | --- | --- | --- |
| `check-export-safe-imports` | `scripts/native_gate_lib.py ... export-safe` (`run-quality.sh:1090`) | Static lint over `EXPORT_SAFE_PATTERNS = ["scripts/*.py", "skills/public/*/scripts/*.py", "skills/support/*/scripts/*.py", "skills/shared/scripts/*.py"]` (`native/repograph/src/export_safe.rs:16-21`); forbids `skills.public` imports (`:23`) and dev-tree-only path chains rooted at the module's own `REPO_ROOT` | **Must NOT gain `tools/`.** Export-safety is an obligation of shipped trees only. Leave `EXPORT_SAFE_PATTERNS` alone; a `tools/` file legitimately reads `skills/public/...` |
| `check-export-self-sufficiency` | `scripts/check_export_self_sufficiency.py` (`run-quality.sh:1096`) | Two arms (`check_export_self_sufficiency.py:9-25`): a **blocking** arm on unguarded third-party imports in documented consumer entrypoints, and an **advisory** arm listing exported modules that read repo-root paths the export does not ship (`PATH_ADVISORY_NOTE`, `:47-56`) | The advisory arm will list every exported module that reads `tools/...`. `CONSUMER_OWNED_ROOTS` (`scripts/export_self_sufficiency_lib.py:82-100`) is the escape: it needs a `"tools"` entry with a reason string, or `tools/` reads read as shipping gaps. **This is the one export-gate edit #769 must make.** |
| `check-plugin-import-smoke` | `scripts/check_plugin_import_smoke.py` (`run-quality.sh:1097`) | Execs every `.py` in the materialized plugin export via `spec_from_file_location`, skipping `__main__` blocks (`:1-12`); resolves the plugin root from `packaging/charness.json` (`:35-47`) | Nothing to change. `tools/` is not in the plugin root, so it is not exec'd. It **proves** the retirement: after the move, a stale import of a moved module from a still-shipped script fails here |
| `validate-packaging` | `scripts/validate_packaging.py` (`run-quality.sh:1016`) | Manifest shape against `packaging/plugin.schema.json`; also called re-entrantly by `load_manifest` (`packaging_lib.py:53-58`) with `validate_root_artifacts=False` | No `scripts/` glob; no change unless the manifest gains a `tools` field (it should not) |
| `validate-packaging-committed` | `scripts/validate_packaging_committed.py` (`run-quality.sh:1020`) | Re-runs the export and asserts the committed `plugins/charness` tree is byte-identical | **This is the clean-export probe for #769.** After the move it should show `removed_paths` for every moved script under `plugins/charness/scripts/`, and nothing else |
| `check-plugin-dir-references` | `scripts/native_gate_lib.py ... plugin-refs` (`run-quality.sh:1122`; `native/repograph/src/plugin_refs.rs`, schema `repograph.plugin_refs.v1` at `:204`) | Catches references that break after the export flattens `skills/public/<s>` to `skills/<s>` | No `tools/` change needed; `tools/` is never flattened |
| `check-plugin-asset-command-carriers` | `scripts/check_plugin_asset_command_carriers.py` (`run-quality.sh:1123`) | Scans `ASSET_GLOBS = ("plugins/**/*.json", "plugins/**/*.yaml", "plugins/**/*.yml")` (`:24`) for command strings matching `skills/(public|support)/...\.(py|sh)` (`COMMAND_RE`, `:25-31`) | Nothing to change: it reads the exported tree only. But note it **only** matches `skills/` targets, so a shipped asset naming `tools/...` would pass silently. Widening `COMMAND_RE` to refuse `tools/` in an exported asset is a cheap new guard |

---

## 2. Import closures for every `tools` row

### 2.1 Method

Import edges only: `import x`, `from x import`, `import scripts.x`,
`import_repo_module(__file__, "scripts.x")`, `load_path_module(..., ".../x.py")`,
`load_local_skill_module(..., "x")`, `load_repo_module_from_skill_script(...)`.
Path-string and subprocess references are excluded from the closure and called
out separately where they matter. Closure restricted to modules under
`scripts/`. Scripts run under `/tmp/closure2.py` + `/tmp/split2.py`.

- Tools-gate closure: **122 modules** before restriction, **103** distinct after.
- Shared universe = closure of every `ship` gate entry + every `scripts/` module
  imported by any `skills/**/scripts/**.py`: **skill-reachable 81**, **ship
  closure 140**.
- **MOVE = 47**, **STAY-SHARED = 56**.

Every row in the classification table was processed. **No row was skipped.**

### 2.2 Per-row closure (label -> script -> closure split)

Command paths are from `scripts/run-quality.sh` at the cited line.

| Label | Script invoked (`run-quality.sh` line) | MOVE part of closure | STAY-SHARED part |
| --- | --- | --- | --- |
| validate-skills | `scripts/validate_skills.py` (`:991`) | `validate_skills`, `skill_portability_lib` | `env_bypass`, `helper_provenance_lib`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `skill_markdown_lib` |
| validate-quality-reference-catalog | `scripts/validate_quality_reference_catalog.py` (`:992`) | `validate_quality_reference_catalog` | `adapter_lib`, `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout` |
| quality-tool-fixtures | `scripts/check_quality_tool_fixtures.py` (`:994`) | `check_quality_tool_fixtures` | (none - self-contained) |
| validate-surfaces | `scripts/validate_surfaces.py` (`:1008`) | `validate_surfaces` | `env_bypass`, `git_checkout`, `git_status_snapshot`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard`, `surfaces_lib` |
| validate-inference-interpretation | `scripts/validate_inference_interpretation.py` (`:1009`) | `validate_inference_interpretation` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| validate-public-skill-validation | `scripts/validate_public_skill_validation.py` (`:1010`) | `validate_public_skill_validation` | `env_bypass`, `helper_provenance_lib`, **`public_skill_validation_lib`**, `runtime_bootstrap`, `script_timeout`, `skill_iter` |
| validate-public-skill-dogfood | `scripts/validate_public_skill_dogfood.py` (`:1011`) | `validate_public_skill_dogfood`, `public_skill_dogfood_validation_lib` | `env_bypass`, `helper_provenance_lib`, **`public_skill_dogfood_lib`**, **`public_skill_validation_lib`**, `runtime_bootstrap`, `script_timeout`, `skill_iter` |
| validate-profiles | `scripts/validate_profiles.py` (`:1012`) | `validate_profiles`, `eval_registry` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| validate-presets | `scripts/validate_presets.py` (`:1013`) | `validate_presets` | `adapter_lib`, `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| validate-integrations | `scripts/validate_integrations.py` (`:1015`) | `validate_integrations` | `agent_browser_probe_policy`, `control_plane_lib`, `env_bypass`, `helper_provenance_lib`, `repo_layout`, `repo_path_display`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| validate-packaging | `scripts/validate_packaging.py` (`:1016`) | `validate_packaging`, `packaging_lib`, `packaging_policy_validators`, `validate_packaging_install_surface` | `control_plane_lib`, `control_plane_render`, `env_bypass`, `git_checkout`, `git_status_snapshot`, `helper_provenance_lib`, `public_skill_validation_lib`, `repo_layout`, `repo_path_display`, `runtime_bootstrap`, `script_timeout`, `skill_iter`, `subprocess_guard`, `support_sync_lib`, `surfaces_lib` |
| validate-packaging-committed | `scripts/validate_packaging_committed.py` (`:1020`) | `validate_packaging_committed` | `subprocess_guard` |
| validate-attention-state-visibility | `scripts/validate_attention_state_visibility.py` (`:1027`) | `validate_attention_state_visibility` | `yaml_output` |
| validate-inventory-consumption-declaration | `scripts/validate_inventory_consumption_declaration.py` (`:1246`) | `validate_inventory_consumption_declaration` | `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout` |
| check-inventory-declaration-coverage | `scripts/check_inventory_declaration_coverage.py` (`:1029`) | `check_inventory_declaration_coverage` | (none) |
| inventory-skill-script-references | `scripts/inventory_skill_script_references.py` (`:1037`) | `inventory_skill_script_references` | 23 modules incl. **`check_doc_links`** (a `ship` gate), `doc_file_population`, `quality_adapter_lib`, `quality_bootstrap_*`, `quality_policy_*`, `markdown_doc_scan`, `portable_command_carrier` |
| check-unreferenced-scripts | `scripts/check_unreferenced_scripts.py` (`:1038`) | `check_unreferenced_scripts`, `export_self_sufficiency_lib`, `inventory_skill_script_references` | 31 modules, superset of the row above plus `artifact_*`, `checkout_view`, `critique_enforcement_scope`, `markdown_sections` |
| validate-quality-closeout-contract | `scripts/validate_quality_closeout_contract.py` (`:1039`) | `validate_quality_closeout_contract` | `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout` |
| validate-current-pointer-freshness | `scripts/validate_current_pointer_freshness.py` (`:1065`) | `validate_current_pointer_freshness` | (none) |
| check-current-pointer-writes | `scripts/check_current_pointer_writes.py` (`:1287`) | `check_current_pointer_writes` | `git_checkout`, `repo_file_listing`, `repo_layout`, `subprocess_guard`, `yaml_output` |
| check-skill-contracts | `scripts/check_skill_contracts.py` (`:1071`) | `check_skill_contracts` | `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout` |
| check-skill-bootstrap-vars | `scripts/check_skill_bootstrap_vars.py` (`:1072`) | `check_skill_bootstrap_vars` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| check-bootstrap-shim-consistency | `scripts/check_bootstrap_shim_consistency.py` (`:1073`) | `check_bootstrap_shim_consistency` | `git_checkout`, `repo_file_listing`, `repo_layout`, `subprocess_guard`, `yaml_output` |
| check-public-doc-coupling | `scripts/check_public_doc_coupling.py` (`:1074`) | `check_public_doc_coupling` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard`, `yaml_output` |
| check-timing-layer-completeness | `scripts/check_timing_layer_completeness.py` (`:1076`) | `check_timing_layer_completeness`, `quality_label_universe` | `adapter_lib`, `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout`, `yaml_output` |
| check-runtime-budget-universe | `scripts/check_runtime_budget_universe.py` (`:1081`) | `check_runtime_budget_universe`, `quality_label_universe` | 15 modules incl. **`check_command_dominance`** (a `ship` gate, loaded via `load_path_module` at `check_runtime_budget_universe.py:187`) |
| check-export-safe-imports | `scripts/native_gate_lib.py` (`:1090`) | `native_gate_lib` | `subprocess_guard` |
| check-export-self-sufficiency | `scripts/check_export_self_sufficiency.py` (`:1096`) | `check_export_self_sufficiency`, `export_self_sufficiency_lib`, `packaging_lib` | 23 modules incl. `control_plane_*`, `support_sync_lib`, `surfaces_lib`, `artifact_*` |
| check-plugin-import-smoke | `scripts/check_plugin_import_smoke.py` (`:1097`) | `check_plugin_import_smoke`, `packaging_lib`, `validate_packaging_install_surface` | 14 modules incl. `control_plane_*`, `support_sync_lib`, `surfaces_lib`, `skill_iter` |
| check-plugin-doc-links (also the `check-docs` tools half) | `scripts/check_plugin_doc_links.py` (`:1113`; component at `check-docs.sh:38`) | `check_plugin_doc_links` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `markdown_doc_scan`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| check-last-verified (the other `check-docs` tools half) | **no script** - inline bash loop, `scripts/check-docs.sh:24-35` | n/a | n/a. Moving it means moving the loop out of `check-docs.sh` into a `tools/` gate and deleting the entry from `checks` (`check-docs.sh:54-63`) |
| check-plugin-dir-references | `scripts/native_gate_lib.py` (`:1122`) | `native_gate_lib` | `subprocess_guard` |
| check-plugin-asset-command-carriers | `scripts/check_plugin_asset_command_carriers.py` (`:1123`) | `check_plugin_asset_command_carriers` | `env_bypass`, `git_checkout`, `helper_provenance_lib`, `repo_file_listing`, `repo_layout`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard` |
| check-references-link-inventory | `scripts/check_references_link_inventory.py` (`:1132`) | `check_references_link_inventory` | `git_checkout`, `repo_file_listing`, `repo_layout`, `subprocess_guard`, `yaml_output` |
| check-coverage | `scripts/check_coverage.py` (`:1180`) | `check_coverage`, `check_coverage_extra_lib`, **`doctor`** (see caveat) | 20 modules incl. `check_coverage_lib`, `control_plane_lib`, `control_plane_lifecycle_lib`, `control_plane_render`, `doctor_lib`, `install_provenance_lib`, `install_tools`, `mutation_line_coverage_lib`, `support_sync_lib`, `sync_support`, `update_tools`, `upstream_release_lib` |
| check-consumer-validator-catalog (catalog half) | `scripts/check_consumer_validator_catalog.py` (`:1204`) | **(none)** | `adapter_lib`, `check_consumer_validator_catalog`, `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout`, `subprocess_guard`, `yaml_output` |
| check-provenance-contract | `skills/public/quality/scripts/check_provenance_contract.py` (`run-quality.sh:1206-1215`) | **not a `scripts/` script** | n/a - see caveat below |
| check-closeout-classification-parity | `scripts/check_closeout_classification_parity.py` (`:1236`) | `check_closeout_classification_parity` | `env_bypass`, `helper_provenance_lib`, `runtime_bootstrap`, `script_timeout`, `yaml_output` |
| run-evals | `scripts/run_evals.py` (`:1241`) | `run_evals`, `eval_setup`, `eval_registry`, `eval_issue_scenarios` | `env_bypass`, `helper_provenance_lib`, **`run_standing_pytest`** (`run_evals.py:21`), `runtime_bootstrap`, `script_timeout`, `standing_pytest_basetemp`, `standing_pytest_environment`, `standing_pytest_run_record`, `subprocess_guard` |

### 2.3 MOVE list (47 modules)

Gate entrypoints (33):
`check_bootstrap_shim_consistency`, `check_closeout_classification_parity`,
`check_coverage`, `check_current_pointer_writes`, `check_export_self_sufficiency`,
`check_inventory_declaration_coverage`, `check_plugin_asset_command_carriers`,
`check_plugin_doc_links`, `check_plugin_import_smoke`, `check_public_doc_coupling`,
`check_quality_tool_fixtures`, `check_references_link_inventory`,
`check_runtime_budget_universe`, `check_skill_bootstrap_vars`, `check_skill_contracts`,
`check_timing_layer_completeness`, `check_unreferenced_scripts`,
`inventory_skill_script_references`, `native_gate_lib`, `run_evals`,
`validate_attention_state_visibility`, `validate_current_pointer_freshness`,
`validate_inference_interpretation`, `validate_integrations`,
`validate_inventory_consumption_declaration`, `validate_packaging`,
`validate_packaging_committed`, `validate_presets`, `validate_profiles`,
`validate_public_skill_dogfood`, `validate_public_skill_validation`,
`validate_quality_closeout_contract`, `validate_quality_reference_catalog`,
`validate_skills`, `validate_surfaces`.

Helpers reachable only from `tools` gates (12):
`check_coverage_extra_lib`, `doctor`*, `eval_issue_scenarios`, `eval_registry`,
`eval_setup`, `export_self_sufficiency_lib`, `packaging_lib`,
`packaging_policy_validators`, `public_skill_dogfood_validation_lib`,
`quality_label_universe`, `skill_portability_lib`,
`validate_packaging_install_surface`.

**Two caveats on the MOVE list.**

- `doctor` is a **false positive - it must STAY.** The only `scripts/` importer is
  `check_coverage.py:237` (`import scripts.doctor as doctor` inside
  `exercise_doctor_scenarios`), a coverage exercise rather than a dependency. But
  `scripts/doctor.py` is a consumer-facing CLI: `charness tool doctor` runs it
  (`charness-artifacts/design-studies/issue-746-747/install_lifecycle.md:25`) and
  it is a declared attention-state surface
  (`skills/public/quality/references/attention-state-visibility.json:292`). Treat
  the MOVE set as **46 modules**.
- `packaging_lib` moving is the load-bearing decision. It is the module that
  performs the export (`:227-320`), and `sync_root_plugin_manifests.py:20` and
  `export_plugin.py:19` both import it. Both of those are maintainer entry points
  and both would move with it; neither is a queued gate, so neither has a
  classification row. **Flagged as a gap in the table.**

### 2.4 STAY-SHARED list (56 modules)

These are in a `tools` closure **and** in a `ship` gate closure or imported by a
shipped skill script, so they stay in `scripts/`:

`adapter_lib`, `agent_browser_probe_policy`, `artifact_naming_lib`,
`artifact_run_scope`, `artifact_size_budget`, `artifact_validator`,
`artifact_violation_report`, `check_command_dominance`,
`check_consumer_validator_catalog`, `check_coverage_lib`, `check_doc_links`,
`checkout_view`, `control_plane_lib`, `control_plane_lifecycle_lib`,
`control_plane_render`, `critique_enforcement_scope`, `doc_file_population`,
`doctor_lib`, `env_bypass`, `git_checkout`, `git_status_snapshot`,
`helper_provenance_lib`, `install_provenance_lib`, `install_tools`,
`markdown_doc_scan`, `markdown_sections`, `mutation_line_coverage_lib`,
`portable_command_carrier`, `public_skill_dogfood_lib`,
`public_skill_validation_lib`, `quality_adapter_lib`,
`quality_bootstrap_absence`, `quality_bootstrap_common`,
`quality_bootstrap_detect`, `quality_bootstrap_lib`, `quality_dup_ratchet_policy`,
`quality_policy_defaults`, `quality_policy_merge`, `repo_file_listing`,
`repo_layout`, `repo_path_display`, `run_standing_pytest`, `runtime_bootstrap`,
`script_timeout`, `skill_iter`, `skill_markdown_lib`, `standing_pytest_basetemp`,
`standing_pytest_environment`, `standing_pytest_run_record`, `subprocess_guard`,
`support_sync_lib`, `surfaces_lib`, `sync_support`, `update_tools`,
`upstream_release_lib`, `yaml_output`.

Evidence for the ones a reader would question (shipped skill importers):

| Helper | Shipped skill script that imports it |
| --- | --- |
| `adapter_lib` | `skills/public/{announcement,create-skill,critique,debug}/scripts/resolve_adapter.py` |
| `artifact_naming_lib` | `skills/public/{debug,hitl,hotl}/scripts/resolve_adapter.py`, `skills/public/quality/scripts/resolve_quality_artifact.py` |
| `control_plane_lib` | `skills/public/setup/scripts/seed_dependencies.py` |
| `git_checkout` | `skills/public/quality/scripts/dup_ratchet_git.py`, `skills/public/release/scripts/publish_release_runtime.py`, `skills/public/setup/scripts/seed_worktree_adapter_lib.py`, `skills/shared/scripts/reviewer_boundary_state.py` |
| `git_status_snapshot` | `skills/public/quality/scripts/dup_ratchet_git.py`, `skills/public/release/scripts/scaffold_claims_review.py`, `skills/support/markdown-preview/scripts/markdown_preview_lib.py` |
| `public_skill_dogfood_lib`, `public_skill_validation_lib` | `skills/public/quality/scripts/suggest_public_skill_dogfood.py` |
| `quality_adapter_lib` | `skills/public/quality/scripts/{check_changed_line_coverage,check_dup_ratchet,check_standing_doc_provenance,inventory_cli_ergonomics}.py` |
| `quality_bootstrap_lib` | `skills/public/quality/scripts/bootstrap_adapter.py` |
| `quality_policy_defaults` | `skills/public/quality/scripts/{adapter_validators,init_adapter}.py` |
| `repo_file_listing` | `skills/public/issue/scripts/issue_critique_observer_support.py`, `skills/public/quality/scripts/{dup_ratchet_git,git_inventory_lib,inventory_entrypoint_docs_ergonomics}.py` |
| `skill_markdown_lib` | `skills/public/quality/scripts/inventory_skill_ergonomics.py` |
| `surfaces_lib` | `skills/public/retro/scripts/{check_auto_trigger,plan_retro_run}.py` |
| `subprocess_guard`, `yaml_output` | dozens of shipped skill scripts |

Cross-lane edges a `tools/` script keeps into `scripts/` (these are the ones that
make `tools/` structurally dependent on `scripts/`, not independent):

| `tools` module | imports `scripts/` module | Site |
| --- | --- | --- |
| `run_evals` | `run_standing_pytest` | `scripts/run_evals.py:21` |
| `inventory_skill_script_references` | `check_doc_links` | `scripts/inventory_skill_script_references.py:57` |
| `check_runtime_budget_universe` | `check_command_dominance` | `scripts/check_runtime_budget_universe.py:187` (`load_path_module`) |
| `check_coverage` | `check_coverage_lib` | splits the coverage libs across two trees; `validate_adapters.py:44` (a `ship` gate) imports `check_coverage_lib` |
| `validate_public_skill_*` | `public_skill_{validation,dogfood}_lib` | shipped skill imports them |

### 2.5 Rows that resist the move

- **`check-provenance-contract` is not a `scripts/` script.** The runner resolves
  it from the shipped quality skill (`run-quality.sh:1206-1215`), preferring
  `skills/public/quality/scripts/check_provenance_contract.py` and falling back
  to the exported `skills/quality/...` spelling. Classifying it `tools` means
  removing a script from the shipped quality skill, which changes what a consumer
  gets, not just where a repo file lives. The runner's else-branch
  (`:1216-1234`) already treats an absent checker as `status: unestablished` and
  refuses at the release boundary, so the move is possible - but it is a
  consumer-visible change, unlike every other `tools` row.
- **`check-consumer-validator-catalog` cannot split by file.** Both halves are
  one script with one `--require-adoption` flag (`run-quality.sh:1204`;
  `scripts/check_consumer_validator_catalog.py:77-96,371-436`). The split needs a
  second invocation, not a second file.
- **`check-last-verified` has no script** (`scripts/check-docs.sh:24-35`).
- **`check-coverage` splits `check_coverage.py` from `check_coverage_lib.py`**
  because `validate_adapters.py:44` imports the lib to keep the adapter's
  coverage-floor literals in sync (`validate_adapters.py:267,277`).
- **`check-subprocess-form` is queued (`run-quality.sh:1070`) but has no row in
  the classification table.** Flagged as a gap.

---

## 3. Readers that enumerate or glob `scripts/`

Verdict key: **ADD** = must gain `tools/` or the moved files escape the gate;
**EXCLUDE** = must not gain `tools/`; **NONE** = already whole-repo or unaffected.

### 3.1 The list from the task

| # | Reader | Site | Literal | Verdict |
| --- | --- | --- | --- | --- |
| 1 | `check_unreferenced_scripts.py` roots | `:27-32` `NODE_GLOBS` | `scripts/**`, `skills/public/*/scripts/**`, `skills/support/*/scripts/**`, `skills/shared/scripts/**` | **ADD `tools/**`** |
| 1b | same, node predicate | `:63-67` `_is_node`: `if parts[0] == "scripts": return len(parts) > 1` | - | **ADD.** `_is_node` gates the universe independently of `NODE_GLOBS`; widening only the globs looks right and does nothing |
| 1c | same, path regex | `:34-35` `_PATH_RE` alternation `(?:scripts\|skills)/...`; `:36` `_MODULE_RE = ^scripts\.(...)$`; `:155` quoted-path regex; further prefixes at `:186-203,245,271,300,310,317,319,339` | - | **ADD `tools`** to each, or a reference to `tools/x.py` is invisible and reads as a false orphan |
| 1d | same, referrer classes | `:266-274` `_source_class`: `tests/` -> `tests-only`, `skills/` -> `skill`, `scripts/` -> `quality-lane`, else `surface` | - | **ADD** a `tools/` arm, otherwise every `tools/` referrer classifies as `surface` and the `quality-lane` class silently changes meaning (this is the class section 4 counts) |
| 2 | `check_code_lengths.py` globs | `:183-199` `GATED_GLOBS` opens with `scripts/*.py`, `scripts/**/*.py`, `scripts/*.sh`, `scripts/**/*.sh` | - | **ADD** the four `tools/` mirrors |
| 2b | same, per-tree cap | `:242` `if relative.parts[:1] == ("scripts",): return REPO_SCRIPT_FILE_MAX`; `:255` same for `REPO_SCRIPT_FILE_WARN` | - | **ADD `("tools",)`** or moved files silently fall to the looser `SKILL_HELPER_FILE_MAX` |
| 2c | same, exemption | `:263` `SHELL_LENGTH_EXEMPTIONS = {"scripts/run-quality.sh": "2026-09-02; retired by #769"}` | - | Dead key if `run-quality.sh` moves. `:220-224` `gated_globs_summary()` derives roots and needs no change |
| 3 | `check_python_runtime_inheritance.py` | `:14-23` `DEFAULT_SCAN_GLOBS`, no override flag | `scripts/*.py`, `scripts/**/*.py`, skills globs | **ADD** |
| 4 | `check_subprocess_form.py` | `:28-37` `DEFAULT_SCAN_GLOBS`; `:38` `GUARD_RELATIVE = "scripts/subprocess_guard.py"` | - | **ADD** the globs; guard path unchanged (`subprocess_guard` is STAY) |
| 5 | `check_python_filenames.py` | `:22` `iter_matching_repo_files(repo_root, ("**/*.py",))`, dir-name skips at `:16-17` | - | **NONE** - whole-repo |
| 6 | `sample_mutation_files.py` | `:53-69` `MUTATION_POOLS` / mutation globs `scripts/*.py`, `scripts/**/*.py`, skills globs; eligibility `:96` `parts[0] == "scripts"`; pathspecs `:117-123,130` | - | **DECIDE.** Silence = moved gates leave the mutation pool and `release-changed-line-coverage`. `mutation_changed_files_lib.py:337-340` derives from it; `:25-31` root anchor unaffected |
| 7 | `helper_provenance_lib.py` | `:222` `_TREE_SCAN_ROOTS = ("scripts", "skills", "support", "shared")`, walked at `:245-251`; `:49` `_OWN_ROOT_MARKER = scripts/runtime_bootstrap.py` | - | **EXCLUDE.** This walks the own/exported tree; adding `tools/` makes repo and export disagree. Marker must stay in `scripts/` |
| 8 | `inventory_gitignore_scan_hygiene.py` | actual path `skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py:34-45` `DEFAULT_PATH_GLOBS` includes six `scripts/*{inventory,quality,scan}*.py` forms; queued `run-quality.sh:1282-1285` | - | **ADD** six `tools/` mirrors - this advisory detects unguarded repo-wide walks, exactly the shape gate scripts carry |
| 9 | `run-quality.sh` py-compile | `:1156-1167` `python_files=( scripts/*.py scripts/**/*.py skills/... )` under `nullglob globstar`; refusal message repeats the list verbatim at `:1169` | - | **ADD `tools/*.py tools/**/*.py`** to both, or the message lies about what was validated |
| 9b | ruff roots | `scripts/check-python-lint.sh:66-72` `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts skills/shared/scripts`; header at `:17` says "change the path list HERE and nowhere else" | - | **ADD `tools`.** CI inherits it: `.github/workflows/quality-core.yml:99` just calls the script |
| 10 | `check-shell.sh` | `:52-61` `collect_shell_files()`: root maxdepth1, `find scripts -maxdepth 1 ... '*.sh'` at `:54`, plus `tests`, `.githooks`; message at `:68` restates the command | - | **ADD** a `[[ -d tools ]]`-guarded branch. Note `-maxdepth 1`: nested `tools/**/*.sh` still unscanned |
| 11 | `check_bootstrap_shim_consistency.py` | `:37` `SCAN_PATTERNS = ("skills/**/*.py", "scripts/**/*.py")` | - | **ADD `tools/**/*.py`**. Doubly important: this gate is itself a MOVE script and it is the gate that would police any new `tools/` shim pair (section 5) |
| 12 | `check_skill_bootstrap_vars.py` | `:131-141` patterns are `skills/{public,support}/*/SKILL.md` | - | **NONE** - scans SKILL.md, never `scripts/` |
| 13 | `inventory_sloc.py` | `skills/public/quality/scripts/inventory_sloc.py:30-42` `DEFAULT_EXCLUDES` (caches only); `:61-66` runs `tokei <repo_root>` | - | **NONE** - `tools/` counted automatically |
| 14 | `check_test_production_ratio.py` | `:22-34` `IGNORED_DIRS` contains `tests`, `plugins`, `evals`, caches - not `tools`; `:56-59` patterns `**/*.py`; `:121-125` test bucket is `parts[0] == "tests"`; `:152-153` `.sh` counted as production | - | **DECIDE.** Post-move `tools/**` counts as production either way, so the ratio is unchanged by the move itself. Add `"tools"` to `IGNORED_DIRS` only if `tools/` should stop diluting it |
| 15 | `.agents/quality-adapter.yaml` | `:48-49` `gate_design_review_globs: [.agents/*-adapter.yaml, skills/public/*/adapter.example.yaml, scripts/*.py, scripts/**/*.py]` | - | **ADD `tools/*.py`, `tools/**/*.py`** |
| 15b | same | `:77` `prompt_asset_policy.source_globs: [scripts/**/*.py, skills/**/*.py, tests/**/*.py]` | - | **ADD `tools/**/*.py`** |
| 15c | same | `:62` `cli_skill_surface_change_globs: ... scripts/** ...` | - | Optional; `tools/` carries no user-facing CLI surface |
| 15d | same | `:16-17` `exemption_list_path: scripts/coverage-floor-exemptions.txt`, `gate_script_pattern: scripts/check_coverage.py`; `:739-760` command literals | - | **Re-path per file.** `check_coverage.py` is a MOVE script, so `:17` breaks. `validate_adapters.py:285-288` asserts this exact literal (`third pass` note in the table) |
| 16 | `docs/validator-timing-layers.md` | markdown links relative to `docs/`: `:17-18`, `:23`, `:26`, `:100`, `:102`, `:104`, `:111`, `:113`, `:114`, `:142` all of the form `[x.py](../scripts/x.py)`; prose class literals at `:54`, `:106`, `:111` | - | **Rewrite `../scripts/` -> `../tools/` per moved file** or `check-doc-links` breaks. The gate that reads it, `check_timing_layer_completeness.py:36` `RUN_QUALITY_PATH = Path("scripts/run-quality.sh")`, is itself a MOVE script |
| 17 | `.agents/surfaces.json` | 38 of 42 surface entries name at least one `scripts/...` path. Occurrences by field: `source_paths` 94, `verify_commands` 61, `derived_paths` 47, `sync_commands` 10, `notes` 6, plus 3 singletons - 221 raw `scripts/` substrings. `:16` `"scripts/**"` is the only directory-glob form | - | **17 MOVE scripts appear here across 30 occurrences** (measured): `packaging_lib` 4, `check_export_self_sufficiency` 3, then 2 each for `doctor`, `export_self_sufficiency_lib`, `validate_inference_interpretation`, `validate_integrations`, `validate_packaging`, `validate_packaging_committed`, `validate_public_skill_dogfood`, `validate_public_skill_validation`, and 1 each for `check_quality_tool_fixtures`, `validate_attention_state_visibility`, `validate_current_pointer_freshness`, `validate_presets`, `validate_profiles`, `validate_skills`, `validate_surfaces`. `:7-20` is the `materialized-plugin-export` entry - `tools/` must **NOT** be added there |

### 3.2 Additional readers found in the sweep

| Reader | Site | Verdict |
| --- | --- | --- |
| `removed_name_consumers.py` | `:61` `SCAN_GLOBS = ("scripts/**/*.py", "skills/**/scripts/**/*.py", "tests/**/*.py")` | **ADD** |
| `command_carrier_discovery.py` | `:97` `ARGV_SOURCE_GLOBS` includes `scripts/**/*.py`; feeds `check_documented_command_flags.py:86-89` | **ADD** |
| `check_documented_subcommands.py` | `:168` `SOURCE_GLOBS = (CLI_NAME, "scripts/**/*.py")` | **ADD** if a moved script documents subcommands |
| `check_current_pointer_writes.py` | `:35-44` `SCAN_ROOTS = (scripts, skills/public, skills/support, skills/shared)`; the comment at `:39-42` records that omitting a root already produced a false-clean verdict | **ADD `Path("tools")`.** Documented prior recurrence of exactly this omission - and this script is itself a MOVE script |
| `validate_attention_state_visibility.py` | `:26` `DEFAULT_SCAN_ROOTS`; `:173` `roots = [_scan_root(repo_root, Path("scripts"))]`; invoked with `--scan-root scripts --scan-root skills` at `run-quality.sh:1027` and `staged_commit_gate_plan.py:414-417` | **ADD** in all four places |
| `discovery_filter_scan_lib.py` | `skills/public/quality/scripts/discovery_filter_scan_lib.py:28` `DEFAULT_SCAN_ROOTS = ("skills/public", "scripts")` | **ADD** |
| `inventory_empty_scope_honesty.py` | `skills/public/quality/scripts/inventory_empty_scope_honesty.py:88-94` `DETECTOR_GLOBS = ("scripts/check_*.py", "scripts/validate_*.py", ...)` | **ADD `tools/check_*.py`, `tools/validate_*.py`** - #769 moves exactly those two name families |
| `structural_waste_lib.py` | `skills/public/quality/scripts/structural_waste_lib.py:166` iterates `("scripts/run_standing_pytest.py", "scripts/run-quality.sh")` | Re-path if either moves |
| `staged_commit_gate_plan.py` (commit-time triggers) | `:156` `startswith(("scripts/", "skills/public/", "plugins/charness/"))`; `:253`; `:326`; `:405`; `:414-417` literal `--scan-root scripts`; `:546`. Single-file validator paths at `:73,84,93,106,119,150,173,183,193,205,241-246,319,333,347,395`; `:111` names `scripts/run-quality.sh`; `:154` `plugins/charness/scripts/` | **ADD `"tools/"`** to the six predicates, re-path the singles. `:154` stays as is (export mirror). Without this, editing a moved gate stops triggering that gate at commit time |
| `native/repograph/src/standalone.rs` | `:9-18` `SCAN_PATTERNS` includes `"scripts/*.py"` | **ADD `"tools/*.py"`** |
| `native/repograph/src/graph.rs` | `:569-571` `if path == "scripts" \|\| path.starts_with("scripts/") { packages.push(("scripts", PackageKind::Scripts)) }` | **ADD** a `tools` arm, else moved files classify into no package |
| `native/repograph/src/graph_imports.rs` | `:59-61` import-resolution roots `vec![".", "scripts"]` | **ADD `tools`** if `tools/` modules are importable by bare name |
| `native/repograph/src/export_safe.rs` | `:16-21` `EXPORT_SAFE_PATTERNS` | **EXCLUDE** (section 1.5) |
| `native/repograph/src/graph_mirrors.rs` | `:101` `source: "scripts/* minus SOURCE_ONLY_PLUGIN_SCRIPTS"` | Update the description string when the constant retires |
| `export_self_sufficiency_lib.py` | `:82-100` `CONSUMER_OWNED_ROOTS` | **ADD `"tools"`** with a reason string (section 1.5) |
| `pyproject.toml` | `:8` `pythonpath = [".", "scripts"]` | **ADD `"tools"`** so tests can import moved modules |
| `pyproject.toml` | `:59` `[tool.vulture] paths = ["runtime_bootstrap.py", "skill_runtime_bootstrap.py", "scripts", "skills", "tests"]` | **ADD `"tools"`** |
| `pyproject.toml` | `:2` `testpaths = ["tests"]` | Only if `tools/` gains tests |
| `doc_file_population.py` | `:16-25` `DOC_GLOBS` (README, AGENTS.md, `docs/**`, `presets/**`, `profiles/**`, `skills/**`) | **ADD** only if `tools/` gains `.md` |
| `.agents/surfaces.json` | `:74-91` `repo-markdown` `source_paths` (includes `evals/*.md`, `packaging/*.md`; convention `<dir>/*.md` documented at `:102`) | **ADD `tools/*.md`** if `tools/` gains `.md` |
| `packaging_lib.py` | `:31-40` `PLUGIN_README_SOURCE_ONLY_PREFIXES` | **ADD `./tools/`** if the plugin README ever links into `tools/` |
| `cosmic-ray.toml:2`, `stryker.config.mjs:1,29-37` | single-file / `.mjs` scope | **NONE** |

### 3.3 Tests that name a moved script by string

Count is distinct test files under `tests/` matching `<name>.py`, `scripts.<name>`,
`from <name> import`, or `import <name>`, excluding `__pycache__`.
**73 distinct test files** touch at least one MOVE script.

| `validate_skills` | 11 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_quality_runner_progress.py, tests/quality_gates/test_quality_runner_release_order.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py, tests/quality_gates/test_quality_runner_unproven.py, tests/quality_gates/test_skill_reference_index.py, tests/quality_gates/test_skill_validation.py, tests/quality_gates/test_surface_obligations.py, tests/test_shared_authoring_script_shims.py |
| `check_coverage` | 10 | tests/quality_gates/support.py, tests/quality_gates/test_check_coverage_inventory.py, tests/quality_gates/test_coverage_floor_inventory_reference.py, tests/quality_gates/test_current_pointer_freshness.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_profile_and_preset_validation.py, tests/quality_gates/test_quality_runner_coverage_selection.py, tests/quality_gates/test_repo_copy_invariants.py, tests/test_debug_artifact.py, tests/test_debug_persistence.py |
| `doctor` | 10 | tests/charness_cli/test_update_flow_unit.py, tests/control_plane/test_integrations_validation.py, tests/control_plane/test_lock_schema_resilience.py, tests/control_plane/test_sync_support.py, tests/quality_gates/test_adapter_version_reconciliation.py, tests/quality_gates/test_argparse_surface_lib.py, tests/quality_gates/test_quality_tool_recommendations.py, tests/quality_gates/test_subprocess_only_coverage_advisory.py, tests/test_agent_browser_runtime_guard.py, tests/test_doctor_lock_payload.py |
| `check_current_pointer_writes` | 6 | tests/coverage_debt/test_batch8.py, tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_current_pointer_writes.py, tests/test_unhappy_path_branches.py, tests/test_write_artifact_path_single_owner.py |
| `check_runtime_budget_universe` | 5 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_command_dominance.py, tests/quality_gates/test_runtime_budget_universe.py, tests/quality_gates/test_s6b2_changed_line_gaps.py |
| `packaging_lib` | 5 | tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_staged_commit_gate_plan.py, tests/test_consumer_validator_catalog.py, tests/test_gather_plan.py, tests/test_issue_source_capture.py |
| `validate_attention_state_visibility` | 5 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_attention_state_visibility.py, tests/test_authoring_preflight_reference.py, tests/test_degradation_branch_coverage.py |
| `validate_current_pointer_freshness` | 5 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_current_pointer_freshness.py, tests/quality_gates/test_prepush_runtime_regime.py, tests/quality_gates/test_staged_commit_gate_plan.py |
| `check_bootstrap_shim_consistency` | 4 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_check_bootstrap_shim_consistency.py, tests/quality_gates/test_empty_scope_refusals.py |
| `check_public_doc_coupling` | 4 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_check_public_doc_coupling.py, tests/quality_gates/test_public_skill_yaml_output_contract.py |
| `native_gate_lib` | 4 | tests/quality_gates/support.py, tests/quality_gates/test_native_gate_lib.py, tests/quality_gates/test_plugin_dir_references.py, tests/quality_gates/test_standalone_imports.py |
| `quality_label_universe` | 4 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_quality_runner_label_universe.py, tests/quality_gates/test_runtime_budget_universe.py |
| `validate_integrations` | 4 | tests/control_plane/test_integrations_validation.py, tests/quality_gates/support.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_skill_docs_contracts.py |
| `validate_packaging` | 4 | tests/quality_gates/support.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_surface_obligations.py |
| `validate_presets` | 4 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_profile_and_preset_validation.py, tests/quality_gates/test_quality_declaration_path_resolution.py |
| `check_closeout_classification_parity` | 3 | tests/coverage_debt/test_batch3.py, tests/quality_gates/support.py, tests/test_closeout_classification_parity.py |
| `check_export_self_sufficiency` | 3 | tests/coverage_debt/test_batch3.py, tests/quality_gates/support.py, tests/quality_gates/test_export_self_sufficiency.py |
| `check_plugin_doc_links` | 3 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_check_plugin_doc_links.py |
| `check_quality_tool_fixtures` | 3 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_quality_tool_fixtures.py |
| `check_skill_bootstrap_vars` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_skill_bootstrap_vars.py |
| `check_skill_contracts` | 3 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_skill_contracts_validation.py |
| `inventory_skill_script_references` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_public_skill_yaml_output_contract.py, tests/test_skill_script_references.py |
| `validate_inference_interpretation` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_inference_interpretation_meta_validator.py, tests/quality_gates/test_staged_commit_gate_plan.py |
| `validate_inventory_consumption_declaration` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_inventory_consumption.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py |
| `validate_packaging_committed` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_surface_obligations.py |
| `validate_profiles` | 3 | tests/quality_gates/inprocess_script_support.py, tests/quality_gates/support.py, tests/quality_gates/test_profile_and_preset_validation.py |
| `validate_public_skill_validation` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_surface_obligations.py, tests/test_public_skill_validation.py |
| `validate_quality_reference_catalog` | 3 | tests/quality_gates/support.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_staged_commit_gate_plan.py |
| `check_plugin_asset_command_carriers` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_plugin_asset_command_carriers.py |
| `check_timing_layer_completeness` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_timing_layer_completeness.py |
| `check_unreferenced_scripts` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_unreferenced_scripts.py |
| `eval_registry` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_packaging_validation.py |
| `export_self_sufficiency_lib` | 2 | tests/coverage_debt/test_batch6.py, tests/quality_gates/test_export_self_sufficiency.py |
| `run_evals` | 2 | tests/coverage_debt/test_batch3.py, tests/quality_gates/support.py |
| `validate_packaging_install_surface` | 2 | tests/quality_gates/test_packaging_validation.py, tests/test_packaging_install_surface_orphan_dirs.py |
| `validate_public_skill_dogfood` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_surface_obligations.py |
| `validate_quality_closeout_contract` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_script_inprocess_behaviors.py |
| `validate_surfaces` | 2 | tests/quality_gates/support.py, tests/quality_gates/test_surface_obligations.py |
| `check_coverage_extra_lib` | 1 | tests/quality_gates/test_check_coverage_inventory.py |
| `check_inventory_declaration_coverage` | 1 | tests/quality_gates/support.py |
| `check_plugin_import_smoke` | 1 | tests/quality_gates/support.py |
| `check_references_link_inventory` | 1 | tests/quality_gates/support.py |
| `public_skill_dogfood_validation_lib` | 1 | tests/test_public_skill_dogfood.py |
| `eval_issue_scenarios` | 0 | (none) |
| `eval_setup` | 0 | (none) |

Two test-side registries dominate the tail and should be edited once rather than
per test:

- `tests/quality_gates/support.py:277` `QUALITY_PYTHON_STUBS` - 68 `(label,
  filename)` pairs used to seed a fake quality lane. **35 of the MOVE scripts are
  named there.** Sample rows: `:278` `("validate-skills", "validate_skills.py")`,
  `:343` `("check-unreferenced-scripts", "check_unreferenced_scripts.py")`. It
  also eagerly loads `scripts/eval_registry.py` (`:25-26`, a MOVE module) and
  `scripts/adapter_lib.py` (`:29-30`, STAY).
- `tests/quality_gates/inprocess_script_support.py` - the allowlisted in-process
  script runner; it appears in the reference list for 14 MOVE scripts.
