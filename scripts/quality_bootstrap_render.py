from __future__ import annotations

from typing import Any

from scripts.adapter_lib import load_yaml, render_yaml_mapping


def render_bootstrap_adapter(data: dict[str, Any], field_statuses: dict[str, str]) -> str:
    items: list[tuple[str, Any]] = [
        ("version", data["version"]),
        ("repo", data["repo"]),
        ("language", data["language"]),
        ("output_dir", data["output_dir"]),
        ("preset_id", data["preset_id"]),
        ("customized_from", data["customized_from"]),
    ]
    if data.get("preset_version") or field_statuses.get("preset_version") == "preserved":
        items.append(("preset_version", data["preset_version"]))
    policy_items: list[tuple[str, Any]] = [
        ("preset_lineage", data["preset_lineage"]),
        ("coverage_fragile_margin_pp", data["coverage_fragile_margin_pp"]),
        ("coverage_floor_policy", data["coverage_floor_policy"]),
        ("specdown_smoke_patterns", data["specdown_smoke_patterns"]),
        ("recommendation_defaults_version", data["recommendation_defaults_version"]),
        ("public_spec_section_exemptions", data["public_spec_section_exemptions"]),
        ("public_spec_implementation_ref_density_floor", data["public_spec_implementation_ref_density_floor"]),
        ("public_spec_implementation_guard_min_lines", data["public_spec_implementation_guard_min_lines"]),
        ("public_spec_pointer_proof_markers", data["public_spec_pointer_proof_markers"]),
        ("prompt_asset_roots", data["prompt_asset_roots"]),
        ("adapter_review_sources", data["adapter_review_sources"]),
        ("acknowledged_recommendations", data["acknowledged_recommendations"]),
        ("gate_design_review_globs", data["gate_design_review_globs"]),
        ("product_surfaces", data["product_surfaces"]),
        ("cli_skill_surface_probe_commands", data["cli_skill_surface_probe_commands"]),
        ("cli_skill_surface_command_docs", data["cli_skill_surface_command_docs"]),
        ("cli_skill_surface_skill_paths", data["cli_skill_surface_skill_paths"]),
        ("cli_skill_surface_change_globs", data["cli_skill_surface_change_globs"]),
        ("canonical_markdown_surfaces", data["canonical_markdown_surfaces"]),
        ("prompt_asset_policy", data["prompt_asset_policy"]),
        ("domain_language_contract", data["domain_language_contract"]),
        ("skill_ergonomics_gate_rules", data["skill_ergonomics_gate_rules"]),
        ("skill_ergonomics_skill_paths", data["skill_ergonomics_skill_paths"]),
        ("skill_ergonomics_runtime_install_skill_paths", data["skill_ergonomics_runtime_install_skill_paths"]),
        ("vendored_paths", data["vendored_paths"]),
        ("runtime_profile_default", data["runtime_profile_default"]),
        ("runtime_budgets", data["runtime_budgets"]),
        ("runtime_budget_profiles", data["runtime_budget_profiles"]),
        ("startup_probes", data["startup_probes"]),
        ("quality_phases", data["quality_phases"]),
        ("concept_paths", data["concept_paths"]),
        ("preflight_commands", data["preflight_commands"]),
        ("gate_commands", data["gate_commands"]),
        ("review_commands", data["review_commands"]),
        ("security_commands", data["security_commands"]),
    ]
    if "mutation_testing" in data:
        policy_items.append(("mutation_testing", data["mutation_testing"]))
    optional_empty_fields = set(
        "prompt_asset_roots adapter_review_sources acknowledged_recommendations gate_design_review_globs "
        "product_surfaces cli_skill_surface_probe_commands cli_skill_surface_command_docs "
        "cli_skill_surface_skill_paths cli_skill_surface_change_globs canonical_markdown_surfaces "
        "public_spec_section_exemptions public_spec_pointer_proof_markers "
        "skill_ergonomics_gate_rules skill_ergonomics_skill_paths skill_ergonomics_runtime_install_skill_paths "
        "vendored_paths domain_language_contract runtime_budgets runtime_budget_profiles startup_probes quality_phases concept_paths preflight_commands "
        "gate_commands review_commands security_commands".split()
    )
    policy_items = [
        (key, value)
        for key, value in policy_items
        if not (key in optional_empty_fields and value in ({}, []) and field_statuses.get(key) != "preserved")
    ]
    if data.get("spec_pytest_reference_format") or field_statuses.get("spec_pytest_reference_format") == "preserved":
        policy_items.insert(4, ("spec_pytest_reference_format", data["spec_pytest_reference_format"]))
    items.extend(policy_items)
    for key, value in (data.get("_unknown_fields") or {}).items():
        items.append((key, value))
    return render_yaml_mapping(items)


def diff_is_defaulted_only(existing_text: str, rendered_text: str, statuses: dict[str, str]) -> bool:
    existing = load_yaml(existing_text)
    rendered = load_yaml(rendered_text)
    if not isinstance(existing, dict) or not isinstance(rendered, dict):
        return False
    if any(key not in rendered or rendered[key] != value for key, value in existing.items()):
        return False
    return all(key in existing or statuses.get(key) in {"defaulted", "deferred"} for key in rendered)
