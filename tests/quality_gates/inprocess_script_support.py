from __future__ import annotations

import os
import subprocess
from functools import cache
from pathlib import Path

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

# Keep this exception narrow: only deliberately reviewed quality-gate semantic
# entry points are listed here. Other scripts retain their process contract
# unless they are explicitly reviewed and added to this mapping.
_IN_PROCESS_SCRIPT_MODULES = {
    "charness": (
        "tests.quality_gates.support_charness_cli",
        ROOT / "charness",
    ),
    "scripts/gates/check_docs_graph.py": (
        "tests.quality_gates.support_check_docs_graph",
        ROOT / "scripts" / "gates" / "check_docs_graph.py",
    ),
    "scripts/check_skill_script_references.py": (
        "tests.quality_gates.support_check_skill_script_references",
        ROOT / "scripts" / "check_skill_script_references.py",
    ),
    "scripts/check_supply_chain_online.py": (
        "tests.quality_gates.support_check_supply_chain_online",
        ROOT / "scripts" / "check_supply_chain_online.py",
    ),
    "scripts/gates_support/list_external_links.py": (
        "tests.quality_gates.support_list_external_links",
        ROOT / "scripts" / "gates_support" / "list_external_links.py",
    ),
    "scripts/gates/measure_inventory_marker_rule.py": (
        "tests.quality_gates.support_measure_inventory_marker_rule",
        ROOT / "scripts" / "gates" / "measure_inventory_marker_rule.py",
    ),
    "scripts/post_edit_skill_anchor_guard.py": (
        "tests.quality_gates.support_post_edit_skill_anchor_guard",
        ROOT / "scripts" / "post_edit_skill_anchor_guard.py",
    ),
    "skills/public/critique/scripts/run_review.py": (
        "tests.quality_gates.support_run_review",
        ROOT / "skills" / "public" / "critique" / "scripts" / "run_review.py",
    ),
    "scripts/mutation/check_mutation_score.py": (
        "tests.quality_gates.support_check_mutation_score",
        ROOT / "scripts" / "mutation" / "check_mutation_score.py",
    ),
    "scripts/mutation/check_mutation_run_proof.py": (
        "tests.quality_gates.support_check_mutation_run_proof",
        ROOT / "scripts" / "mutation" / "check_mutation_run_proof.py",
    ),
    "skills/public/quality/scripts/plan_quality_run.py": (
        "tests.quality_gates.support_plan_quality_run",
        ROOT / "skills" / "public" / "quality" / "scripts" / "plan_quality_run.py",
    ),
    "scripts/gates/check_changed_surfaces.py": (
        "tests.quality_gates.support_check_changed_surfaces",
        ROOT / "scripts" / "gates" / "check_changed_surfaces.py",
    ),
    "scripts/gates_support/command_plan_preflight.py": (
        "tests.quality_gates.support_command_plan_preflight",
        ROOT / "scripts" / "gates_support" / "command_plan_preflight.py",
    ),
    "tools/check_bootstrap_shim_consistency.py": (
        "tests.quality_gates.support_check_bootstrap_shim_consistency",
        ROOT / "tools" / "check_bootstrap_shim_consistency.py",
    ),
    "skills/shared/scripts/reviewer_boundary_fingerprint.py": (
        "tests.quality_gates.support_reviewer_boundary_fingerprint",
        ROOT / "skills" / "shared" / "scripts" / "reviewer_boundary_fingerprint.py",
    ),
    "scripts/gates/validate_adapters.py": (
        "tests.quality_gates.support_validate_adapters",
        ROOT / "scripts" / "gates" / "validate_adapters.py",
    ),
    "skills/public/quality/scripts/render_runtime_summary.py": (
        "tests.quality_gates.support_render_runtime_summary",
        ROOT / "skills" / "public" / "quality" / "scripts" / "render_runtime_summary.py",
    ),
    "skills/public/quality/scripts/inventory_sloc.py": (
        "tests.quality_gates.support_inventory_sloc",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_sloc.py",
    ),
    "scripts/gates/check_code_lengths.py": (
        "tests.quality_gates.support_check_code_lengths",
        ROOT / "scripts" / "gates" / "check_code_lengths.py",
    ),
    "scripts/gates/validate_retro_artifact.py": (
        "tests.quality_gates.support_validate_retro_artifact",
        ROOT / "scripts" / "gates" / "validate_retro_artifact.py",
    ),
    "skills/public/retro/scripts/audit_codex_session.py": (
        "tests.quality_gates.support_audit_codex_session",
        ROOT / "skills" / "public" / "retro" / "scripts" / "audit_codex_session.py",
    ),
    "skills/public/quality/scripts/check_dup_ratchet.py": (
        "tests.quality_gates.support_check_dup_ratchet",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_dup_ratchet.py",
    ),
    "scripts/gates/check_issue_closeout_commit_msg.py": (
        "tests.quality_gates.support_check_issue_closeout_commit_msg",
        ROOT / "scripts" / "gates" / "check_issue_closeout_commit_msg.py",
    ),
    "tools/validate_skills.py": (
        "tests.quality_gates.support_validate_skills",
        ROOT / "tools" / "validate_skills.py",
    ),
    "scripts/gates/check_spec_evidence_durability.py": (
        "tests.quality_gates.support_check_spec_evidence_durability",
        ROOT / "scripts" / "gates" / "check_spec_evidence_durability.py",
    ),
    "tools/validate_current_pointer_freshness.py": (
        "tests.quality_gates.support_validate_current_pointer_freshness",
        ROOT / "tools" / "validate_current_pointer_freshness.py",
    ),
    "skills/public/quality/scripts/check_changed_line_coverage.py": (
        "tests.quality_gates.support_check_changed_line_coverage",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_changed_line_coverage.py",
    ),
    "scripts/validate_critique_artifacts.py": (
        "tests.quality_gates.support_validate_critique_artifacts",
        ROOT / "scripts" / "validate_critique_artifacts.py",
    ),
    "skills/public/quality/scripts/check_runtime_budget.py": (
        "tests.quality_gates.support_check_runtime_budget",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py",
    ),
    "scripts/mutation/check_changed_line_mutation_coverage.py": (
        "tests.quality_gates.support_check_changed_line_mutation_coverage",
        ROOT / "scripts" / "mutation" / "check_changed_line_mutation_coverage.py",
    ),
    "scripts/gates/validate_debug_artifact.py": (
        "tests.quality_gates.support_validate_debug_artifact",
        ROOT / "scripts" / "gates" / "validate_debug_artifact.py",
    ),
    "scripts/gates/validate_quality_artifact.py": (
        "tests.quality_gates.support_validate_quality_artifact",
        ROOT / "scripts" / "gates" / "validate_quality_artifact.py",
    ),
    "tools/check_quality_tool_fixtures.py": (
        "tests.quality_gates.support_check_quality_tool_fixtures",
        ROOT / "tools" / "check_quality_tool_fixtures.py",
    ),
    "scripts/quality_label_universe.py": (
        "tests.quality_gates.support_quality_label_universe",
        ROOT / "scripts" / "quality_label_universe.py",
    ),
    "tools/check_runtime_budget_universe.py": (
        "tests.quality_gates.support_check_runtime_budget_universe",
        ROOT / "tools" / "check_runtime_budget_universe.py",
    ),
    "scripts/gates/validate_inventory_consumption.py": (
        "tests.quality_gates.support_validate_inventory_consumption",
        ROOT / "scripts" / "gates" / "validate_inventory_consumption.py",
    ),
    "skills/public/release/scripts/audit_public_release_narrative.py": (
        "tests.quality_gates.support_audit_public_release_narrative",
        ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    ),
    "skills/shared/scripts/reviewer_worker_report.py": (
        "tests.quality_gates.support_reviewer_worker_report",
        ROOT / "skills" / "shared" / "scripts" / "reviewer_worker_report.py",
    ),
    "skills/public/quality/scripts/inventory_nose_clones.py": (
        "tests.quality_gates.support_inventory_nose_clones",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_nose_clones.py",
    ),
    "skills/public/quality/scripts/inventory_doc_duplicates.py": (
        "tests.quality_gates.support_inventory_doc_duplicates",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_doc_duplicates.py",
    ),
    "skills/public/quality/scripts/inventory_structural_waste.py": (
        "tests.quality_gates.support_inventory_structural_waste",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_structural_waste.py",
    ),
    "skills/public/quality/scripts/check_regenerable_facts.py": (
        "tests.quality_gates.support_check_regenerable_facts",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_regenerable_facts.py",
    ),
    "scripts/gates/validate_ideation_artifact.py": (
        "tests.quality_gates.support_validate_ideation_artifact",
        ROOT / "scripts" / "gates" / "validate_ideation_artifact.py",
    ),
    "scripts/gates/check_artifact_referents.py": (
        "tests.quality_gates.support_check_artifact_referents",
        ROOT / "scripts" / "gates" / "check_artifact_referents.py",
    ),
    "scripts/gates/check_cli_skill_surface.py": (
        "tests.quality_gates.support_check_cli_skill_surface",
        ROOT / "scripts" / "gates" / "check_cli_skill_surface.py",
    ),
    "scripts/gates_support/select_verifiers.py": (
        "tests.quality_gates.support_select_verifiers",
        ROOT / "scripts" / "gates_support" / "select_verifiers.py",
    ),
    "skills/public/retro/scripts/check_auto_trigger.py": (
        "tests.quality_gates.support_check_auto_trigger",
        ROOT / "skills" / "public" / "retro" / "scripts" / "check_auto_trigger.py",
    ),
    "skills/public/announcement/scripts/preflight_sources.py": (
        "tests.quality_gates.support_preflight_sources",
        ROOT / "skills" / "public" / "announcement" / "scripts" / "preflight_sources.py",
    ),
    "skills/public/announcement/scripts/record_announcement.py": (
        "tests.quality_gates.support_record_announcement",
        ROOT / "skills" / "public" / "announcement" / "scripts" / "record_announcement.py",
    ),
    "skills/public/impl/scripts/init_adapter.py": (
        "tests.quality_gates.support_init_adapter",
        ROOT / "skills" / "public" / "impl" / "scripts" / "init_adapter.py",
    ),
    "skills/public/quality/scripts/measure_startup_probes.py": (
        "tests.quality_gates.support_measure_startup_probes",
        ROOT / "skills" / "public" / "quality" / "scripts" / "measure_startup_probes.py",
    ),
    "skills/public/issue/scripts/validate_proposal_fields.py": (
        "tests.quality_gates.support_validate_proposal_fields",
        ROOT / "skills" / "public" / "issue" / "scripts" / "validate_proposal_fields.py",
    ),
    "skills/public/hitl/scripts/bootstrap_review.py": (
        "tests.quality_gates.support_bootstrap_review",
        ROOT / "skills" / "public" / "hitl" / "scripts" / "bootstrap_review.py",
    ),
    "skills/public/hitl/scripts/check_chunk_contract.py": (
        "tests.quality_gates.support_check_chunk_contract",
        ROOT / "skills" / "public" / "hitl" / "scripts" / "check_chunk_contract.py",
    ),
    "skills/public/gather/scripts/gather_plan.py": (
        "tests.quality_gates.support_gather_plan",
        ROOT / "skills" / "public" / "gather" / "scripts" / "gather_plan.py",
    ),
    "skills/public/release/scripts/check_requested_review_gate.py": (
        "tests.quality_gates.support_check_requested_review_gate",
        ROOT / "skills" / "public" / "release" / "scripts" / "check_requested_review_gate.py",
    ),
    "skills/public/quality/scripts/propose_mutation_testing.py": (
        "tests.quality_gates.support_propose_mutation_testing",
        ROOT / "skills" / "public" / "quality" / "scripts" / "propose_mutation_testing.py",
    ),
    "scripts/gates/check_probe_record.py": (
        "tests.quality_gates.support_check_probe_record",
        ROOT / "scripts" / "gates" / "check_probe_record.py",
    ),
    "skills/public/quality/scripts/scaffold_quality_artifact.py": (
        "tests.quality_gates.support_scaffold_quality_artifact",
        ROOT / "skills" / "public" / "quality" / "scripts" / "scaffold_quality_artifact.py",
    ),
    "skills/public/retro/scripts/scaffold_retro_artifact.py": (
        "tests.quality_gates.support_scaffold_retro_artifact",
        ROOT / "skills" / "public" / "retro" / "scripts" / "scaffold_retro_artifact.py",
    ),
    "skills/public/debug/scripts/scaffold_debug_artifact.py": (
        "tests.quality_gates.support_scaffold_debug_artifact",
        ROOT / "skills" / "public" / "debug" / "scripts" / "scaffold_debug_artifact.py",
    ),
    "skills/public/critique/scripts/scaffold_critique_artifact.py": (
        "tests.quality_gates.support_scaffold_critique_artifact",
        ROOT / "skills" / "public" / "critique" / "scripts" / "scaffold_critique_artifact.py",
    ),
    "skills/public/ideation/scripts/scaffold_ideation_artifact.py": (
        "tests.quality_gates.support_scaffold_ideation_artifact",
        ROOT / "skills" / "public" / "ideation" / "scripts" / "scaffold_ideation_artifact.py",
    ),
    "skills/public/gather/scripts/write_record.py": (
        "tests.quality_gates.support_write_record",
        ROOT / "skills" / "public" / "gather" / "scripts" / "write_record.py",
    ),
    "skills/public/retro/scripts/prepare_packet.py": (
        "tests.quality_gates.support_retro_prepare_packet",
        ROOT / "skills" / "public" / "retro" / "scripts" / "prepare_packet.py",
    ),
    "skills/public/critique/scripts/prepare_packet.py": (
        "tests.quality_gates.support_critique_prepare_packet",
        ROOT / "skills" / "public" / "critique" / "scripts" / "prepare_packet.py",
    ),
    "skills/public/narrative/scripts/map_sources.py": (
        "tests.quality_gates.support_map_sources",
        ROOT / "skills" / "public" / "narrative" / "scripts" / "map_sources.py",
    ),
    "skills/public/release/scripts/bump_version.py": (
        "tests.quality_gates.support_bump_version",
        ROOT / "skills" / "public" / "release" / "scripts" / "bump_version.py",
    ),
    "skills/public/quality/scripts/inventory_ci_recoverable_gates.py": (
        "tests.quality_gates.support_inventory_ci_recoverable_gates",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_ci_recoverable_gates.py",
    ),
    "skills/public/quality/scripts/resolve_quality_artifact.py": (
        "tests.quality_gates.support_resolve_quality_artifact",
        ROOT / "skills" / "public" / "quality" / "scripts" / "resolve_quality_artifact.py",
    ),
    "skills/public/setup/scripts/init_adapter.py": (
        "tests.quality_gates.support_setup_init_adapter",
        ROOT / "skills" / "public" / "setup" / "scripts" / "init_adapter.py",
    ),
    "skills/public/create-skill/scripts/init_adapter.py": (
        "tests.quality_gates.support_create_skill_init_adapter",
        ROOT / "skills" / "public" / "create-skill" / "scripts" / "init_adapter.py",
    ),
    "skills/public/critique/scripts/init_adapter.py": (
        "tests.quality_gates.support_critique_init_adapter",
        ROOT / "skills" / "public" / "critique" / "scripts" / "init_adapter.py",
    ),
    "skills/public/announcement/scripts/init_adapter.py": (
        "tests.quality_gates.support_announcement_init_adapter",
        ROOT / "skills" / "public" / "announcement" / "scripts" / "init_adapter.py",
    ),
    "skills/public/impl/scripts/survey_verification.py": (
        "tests.quality_gates.support_survey_verification",
        ROOT / "skills" / "public" / "impl" / "scripts" / "survey_verification.py",
    ),
    "skills/shared/scripts/reviewer_delivery.py": (
        "tests.quality_gates.support_reviewer_delivery",
        ROOT / "skills" / "shared" / "scripts" / "reviewer_delivery.py",
    ),
    "skills/public/announcement/scripts/collect_commits.py": (
        "tests.quality_gates.support_collect_commits",
        ROOT / "skills" / "public" / "announcement" / "scripts" / "collect_commits.py",
    ),
    "scripts/seed_lesson_transitions.py": (
        "tests.quality_gates.support_seed_lesson_transitions",
        ROOT / "scripts" / "seed_lesson_transitions.py",
    ),
    "skills/public/quality/references/find_inline_prompt_bulk.py": (
        "tests.quality_gates.support_find_inline_prompt_bulk",
        ROOT / "skills" / "public" / "quality" / "references" / "find_inline_prompt_bulk.py",
    ),
    "scripts/build_retro_lesson_selection_index.py": (
        "tests.quality_gates.support_build_retro_lesson_selection_index",
        ROOT / "scripts" / "build_retro_lesson_selection_index.py",
    ),
    "skills/public/achieve/scripts/upsert_goal.py": (
        "tests.quality_gates.support_upsert_goal",
        ROOT / "skills" / "public" / "achieve" / "scripts" / "upsert_goal.py",
    ),
    "scripts/render_critique_section_changed_surfaces.py": (
        "tests.quality_gates.support_render_critique_section_changed_surfaces",
        ROOT / "scripts" / "render_critique_section_changed_surfaces.py",
    ),
    "scripts/gates/measure_evidence_residual.py": (
        "tests.quality_gates.support_measure_evidence_residual",
        ROOT / "scripts" / "gates" / "measure_evidence_residual.py",
    ),
    "skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py": (
        "tests.quality_gates.support_inventory_gitignore_scan_hygiene",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_gitignore_scan_hygiene.py",
    ),
    "scripts/gates/check_upstream_support_drift.py": (
        "tests.quality_gates.support_check_upstream_support_drift",
        ROOT / "scripts" / "gates" / "check_upstream_support_drift.py",
    ),
    "scripts/resolve_artifact_path.py": (
        "tests.quality_gates.support_resolve_artifact_path",
        ROOT / "scripts" / "resolve_artifact_path.py",
    ),
    "skills/support/web-fetch/scripts/route_public_fetch.py": (
        "tests.quality_gates.support_route_public_fetch",
        ROOT / "skills" / "support" / "web-fetch" / "scripts" / "route_public_fetch.py",
    ),
    "skills/support/web-fetch/scripts/classify_fetch_response.py": (
        "tests.quality_gates.support_classify_fetch_response",
        ROOT / "skills" / "support" / "web-fetch" / "scripts" / "classify_fetch_response.py",
    ),
    "skills/support/web-fetch/scripts/acquire_public_url.py": (
        "tests.quality_gates.support_acquire_public_url",
        ROOT / "skills" / "support" / "web-fetch" / "scripts" / "acquire_public_url.py",
    ),
    "skills/public/gather/scripts/gather_public_url.py": (
        "tests.quality_gates.support_gather_public_url",
        ROOT / "skills" / "public" / "gather" / "scripts" / "gather_public_url.py",
    ),
    "tools/validate_attention_state_visibility.py": (
        "tests.quality_gates.support_validate_attention_state_visibility",
        ROOT / "tools" / "validate_attention_state_visibility.py",
    ),
    "scripts/gates/check_doc_links.py": (
        "tests.quality_gates.support_check_doc_links",
        ROOT / "scripts" / "gates" / "check_doc_links.py",
    ),
    "skills/public/critique/scripts/verify_packet.py": (
        "tests.quality_gates.support_verify_packet",
        ROOT / "skills" / "public" / "critique" / "scripts" / "verify_packet.py",
    ),
    "scripts/parity_harness.py": (
        "tests.quality_gates.support_parity_harness",
        ROOT / "scripts" / "parity_harness.py",
    ),
    "skills/public/setup/scripts/seed_dependencies.py": (
        "tests.quality_gates.support_setup_seed_dependencies",
        ROOT / "skills" / "public" / "setup" / "scripts" / "seed_dependencies.py",
    ),
    "skills/public/retro/scripts/refresh_recent_lessons.py": (
        "tests.quality_gates.support_refresh_recent_lessons",
        ROOT / "skills" / "public" / "retro" / "scripts" / "refresh_recent_lessons.py",
    ),
    "scripts/gates/check_markdown_inline_code.py": (
        "tests.quality_gates.support_check_markdown_inline_code",
        ROOT / "scripts" / "gates" / "check_markdown_inline_code.py",
    ),
    "tools/check_current_pointer_writes.py": (
        "tests.quality_gates.support_check_current_pointer_writes",
        ROOT / "tools" / "check_current_pointer_writes.py",
    ),
    "tools/validate_profiles.py": (
        "tests.quality_gates.support_validate_profiles",
        ROOT / "tools" / "validate_profiles.py",
    ),
    "scripts/check_supply_chain.py": (
        "tests.quality_gates.support_check_supply_chain",
        ROOT / "scripts" / "check_supply_chain.py",
    ),
    "scripts/gates/check_command_docs.py": (
        "tests.quality_gates.support_check_command_docs",
        ROOT / "scripts" / "gates" / "check_command_docs.py",
    ),
    "scripts/gates/suggest_public_skill_dogfood.py": (
        "tests.quality_gates.support_suggest_public_skill_dogfood",
        ROOT / "scripts" / "gates" / "suggest_public_skill_dogfood.py",
    ),
    "skills/public/quality/scripts/suggest_public_skill_dogfood.py": (
        "tests.quality_gates.support_quality_suggest_public_skill_dogfood",
        ROOT / "skills" / "public" / "quality" / "scripts" / "suggest_public_skill_dogfood.py",
    ),
    "scripts/staged_commit_gate_plan.py": (
        "tests.quality_gates.support_staged_commit_gate_plan",
        ROOT / "scripts" / "staged_commit_gate_plan.py",
    ),
    "skills/public/quality/scripts/check_standing_doc_provenance.py": (
        "tests.quality_gates.support_check_standing_doc_provenance",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_standing_doc_provenance.py",
    ),
    "scripts/gates/check_test_production_ratio.py": (
        "tests.quality_gates.support_check_test_production_ratio",
        ROOT / "scripts" / "gates" / "check_test_production_ratio.py",
    ),
    "scripts/gates/check_git_identity.py": (
        "tests.quality_gates.support_check_git_identity",
        ROOT / "scripts" / "gates" / "check_git_identity.py",
    ),
    "tools/check_plugin_doc_links.py": (
        "tests.quality_gates.support_check_plugin_doc_links",
        ROOT / "tools" / "check_plugin_doc_links.py",
    ),
    "tools/check_public_doc_coupling.py": (
        "tests.quality_gates.support_check_public_doc_coupling",
        ROOT / "tools" / "check_public_doc_coupling.py",
    ),
    "scripts/check_staged_reversion.py": (
        "tests.quality_gates.support_check_staged_reversion",
        ROOT / "scripts" / "check_staged_reversion.py",
    ),
    "scripts/gates/check_documented_command_flags.py": (
        "tests.quality_gates.support_check_documented_command_flags",
        ROOT / "scripts" / "gates" / "check_documented_command_flags.py",
    ),
    "skills/public/quality/scripts/seed_dup_review.py": (
        "tests.quality_gates.support_seed_dup_review",
        ROOT / "skills" / "public" / "quality" / "scripts" / "seed_dup_review.py",
    ),
    "skills/public/quality/scripts/inventory_empty_scope_honesty.py": (
        "tests.quality_gates.support_inventory_empty_scope_honesty",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_empty_scope_honesty.py",
    ),
    "skills/public/quality/scripts/inventory_ci_local_gate_parity.py": (
        "tests.quality_gates.support_inventory_ci_local_gate_parity",
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_ci_local_gate_parity.py",
    ),
    "scripts/gates/check_python_filenames.py": (
        "tests.quality_gates.support_check_python_filenames",
        ROOT / "scripts" / "gates" / "check_python_filenames.py",
    ),
    "scripts/gates/check_github_actions.py": (
        "tests.quality_gates.support_check_github_actions",
        ROOT / "scripts" / "gates" / "check_github_actions.py",
    ),
    "scripts/gates/check_skill_ownership_overlap.py": (
        "tests.quality_gates.support_check_skill_ownership_overlap",
        ROOT / "scripts" / "gates" / "check_skill_ownership_overlap.py",
    ),
    "scripts/gates/check_symbol_residue.py": (
        "tests.quality_gates.support_check_symbol_residue",
        ROOT / "scripts" / "gates" / "check_symbol_residue.py",
    ),
    "scripts/gates/check_python_runtime_inheritance.py": (
        "tests.quality_gates.support_check_python_runtime_inheritance",
        ROOT / "scripts" / "gates" / "check_python_runtime_inheritance.py",
    ),
    "scripts/gates_support/render_cli_reference.py": (
        "tests.quality_gates.support_render_cli_reference",
        ROOT / "scripts" / "gates_support" / "render_cli_reference.py",
    ),
    "scripts/build_debug_seam_risk_index.py": (
        "tests.quality_gates.support_build_debug_seam_risk_index",
        ROOT / "scripts" / "build_debug_seam_risk_index.py",
    ),
    "skills/public/narrative/scripts/review_adapter.py": (
        "tests.quality_gates.support_narrative_review_adapter",
        ROOT / "skills" / "public" / "narrative" / "scripts" / "review_adapter.py",
    ),
    "scripts/validate_presets.py": (
        "tests.quality_gates.support_validate_presets",
        ROOT / "tools" / "validate_presets.py",
    ),
    "scripts/mutation/release_changed_line_coverage.py": (
        "tests.quality_gates.support_release_changed_line_coverage",
        ROOT / "scripts" / "mutation" / "release_changed_line_coverage.py",
    ),
    "scripts/gates_support/removed_name_consumers.py": (
        "tests.quality_gates.support_removed_name_consumers",
        ROOT / "scripts" / "gates_support" / "removed_name_consumers.py",
    ),
    "scripts/gates/check_test_repo_copy_invariants.py": (
        "tests.quality_gates.support_check_test_repo_copy_invariants",
        ROOT / "scripts" / "gates" / "check_test_repo_copy_invariants.py",
    ),
    "skills/public/setup/scripts/inspect_repo.py": (
        "tests.quality_gates.support_setup_inspect_repo_cli",
        ROOT / "skills" / "public" / "setup" / "scripts" / "inspect_repo.py",
    ),
    "tools/check_skill_contracts.py": (
        "tests.quality_gates.support_check_skill_contracts",
        ROOT / "tools" / "check_skill_contracts.py",
    ),
    **{
        f"skills/public/{skill}/scripts/resolve_adapter.py": (
            f"tests.quality_gates.support_resolve_adapter_{skill.replace('-', '_')}",
            ROOT / "skills" / "public" / skill / "scripts" / "resolve_adapter.py",
        )
        for skill in (
            "achieve",
            "announcement",
            "create-skill",
            "critique",
            "debug",
            "gather",
            "hitl",
            "hotl",
            "impl",
            "issue",
            "narrative",
            "quality",
            "release",
            "retro",
            "setup",
        )
    },
}

for _tool_path in sorted((ROOT / "tools").glob("*.py")):
    if _tool_path.name == "__init__.py":
        continue
    _IN_PROCESS_SCRIPT_MODULES.setdefault(
        f"tools/{_tool_path.name}",
        (f"tests.quality_gates.support_tool_{_tool_path.stem}", _tool_path),
    )


def _repo_script_key(script: Path) -> str | None:
    """Return the stable allowlist key for a repo-owned script path."""
    candidate = script if script.is_absolute() else ROOT / script
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    for key, (_module_name, module_path) in _IN_PROCESS_SCRIPT_MODULES.items():
        try:
            if resolved == module_path.resolve():
                return key
        except OSError:
            continue
    return None


@cache
def _load_allowlisted_script(key: str) -> object:
    """Lazily load one allowlisted module, once per test worker."""
    module_name, module_path = _IN_PROCESS_SCRIPT_MODULES[key]
    return load_script_module(module_name, module_path)


def run_allowlisted_script(
    script: Path,
    args: tuple[str, ...],
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
) -> subprocess.CompletedProcess[str] | None:
    """Run an allowlisted CLI main while retaining subprocess-like isolation."""
    key = _repo_script_key(script)
    if key is None:
        return None
    previous_cwd = Path.cwd()
    try:
        # `run_script` defaults child processes to ROOT; mirror that when pytest
        # itself was launched from another directory, then restore it on failure too.
        os.chdir(cwd or ROOT)
        result = run_loaded_script_main(
            str(script),
            _load_allowlisted_script(key),
            *args,
            env=env,
        )
    finally:
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        [str(script), *args],
        result.returncode,
        result.stdout,
        result.stderr,
    )
