# Export boundary

> Status: current
> Source of truth: this page and [packaging_lib.py](../scripts/packaging_lib.py)
> Last verified: 2026-09-02

The plugin export ships the documented bundle trees: [README.md](../README.md), public skills
as `skills/`, shared skills as `shared/`, support skills as `support/`, plus
the declared profiles, presets, integrations, Claude agents, root bootstrap
shims, and host manifests. The complete `scripts/` tree is also exported.

`tools/` is authoring-repository infrastructure. It is never exported and is
not a consumer-facing command surface. Run a tool gate from the repository
root with its module spelling:

```bash
python3 -m tools.<name> --repo-root .
```

Moved tools import shared repository modules using `from scripts.<name> import ...`.
The root `runtime_bootstrap` and `yaml_output` shims remain bare imports;
the module runner places the repository root first on `sys.path`. Moved files
must not mutate `sys.path` or add another shim pair under `tools/`.

To inspect the clean export boundary:

```bash
python3 scripts/export_plugin.py --repo-root . --host claude --output-root /tmp/export-probe
export_root=/tmp/export-probe/plugins/charness
root_tools_count=$(find "$export_root" -maxdepth 1 -type d -name tools -print | wc -l)
test "$root_tools_count" -eq 0
find "$export_root" -path '*/tools/*' ! -path '*/integrations/tools/*' -print
for basename in check_bootstrap_shim_consistency.py check_closeout_classification_parity.py \
  check_consumer_validator_catalog_decisions.py check_coverage.py check_coverage_extra_lib.py \
  check_current_pointer_writes.py check_export_self_sufficiency.py export_self_sufficiency_lib.py \
  check_inventory_declaration_coverage.py check_last_verified.py \
  check_plugin_asset_command_carriers.py check_plugin_doc_links.py check_plugin_import_smoke.py \
  check_public_doc_coupling.py check_quality_tool_fixtures.py check_references_link_inventory.py \
  check_runtime_budget_universe.py check_skill_bootstrap_vars.py check_skill_contracts.py \
  check_timing_layer_completeness.py check_unreferenced_scripts.py eval_issue_scenarios.py \
  eval_registry.py eval_setup.py inventory_skill_script_references.py \
  public_skill_dogfood_validation_lib.py quality_gates_extract.py run_evals.py \
  skill_portability_lib.py suggest_public_skill_validation.py validate_attention_state_visibility.py \
  validate_current_pointer_freshness.py validate_inference_interpretation.py validate_integrations.py \
  validate_inventory_consumption_declaration.py validate_packaging_committed.py validate_presets.py \
  validate_profiles.py validate_public_skill_dogfood.py validate_public_skill_validation.py \
  validate_quality_closeout_contract.py validate_quality_reference_catalog.py validate_skills.py \
  validate_surfaces.py; do
  find "$export_root" -type f \( -path "*/tools/$basename" -o -path "*/scripts/$basename" \) \
    ! -path "$export_root/shared/scripts/validate_skills.py" -print
done
```

The root `tools/` count and all moved-basename checks must be zero. The path
probe deliberately matches a directory named `tools` while excluding the
shipped data under `integrations/tools/`, which is a separate tree.
