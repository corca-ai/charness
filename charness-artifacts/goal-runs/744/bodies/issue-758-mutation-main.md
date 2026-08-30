<!-- corca-ai/charness-mutation-test-regression -->
Mutation testing failed on `030aa826242d9e077592a1aee70815f8d25a07ec`.

Workflow run: https://github.com/corca-ai/charness/actions/runs/33252724811

## Step outcomes

- `Select mutation sample`: **failure**
- `Run mutation`: **skipped**
- `Summarize mutation report`: **failure**

The mutation commands NEVER RAN — an earlier step failed or was skipped. The summary below describes absent artifacts, not a mutation result; read the `Select mutation sample` outcome above and the workflow logs.


# Mutation Testing Summary

- Status: **UNMEASURED**
- Blocking signal: the sampler's coverage-baseline pytest failed before mutation ran; no mutants ran.
- Failing baseline tests:
  - `tests/quality_gates/test_absent_input_is_not_a_matching_input.py::test_s35_this_repo_declares_its_surfaces_and_has_none_absent`
  - `tests/quality_gates/test_check_doc_links.py::test_the_contradiction_rule_finds_every_live_site_in_the_real_tree`
  - `tests/quality_gates/test_check_doc_links.py::test_the_live_tree_has_no_unmarked_portable_reference`
  - `tests/quality_gates/test_command_dominance.py::test_sc19_and_sc16_ship_to_consumers_rather_than_living_only_here`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_the_export_ships_the_bootstrap_contract_beside_the_installer`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_declaring_a_package_is_not_the_question_the_gate_asks`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_an_unguarded_entrypoint_import_makes_the_gate_fail`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_a_third_party_name_that_collides_with_an_exported_entry_is_still_checked`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_path_findings_alone_do_NOT_fail_the_gate`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_the_instruction_arm_is_still_looking_at_something`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_a_consumer_doc_instruction_FAILS_THE_GATE`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_module_prose_instructions_alone_do_NOT_fail_the_gate`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_the_real_finder_still_emits_consumer_doc_on_the_real_tree`
  - `tests/quality_gates/test_export_self_sufficiency.py::test_every_exemption_is_still_LOAD_BEARING`
  - `tests/quality_gates/test_goal_binding_v1.py::test_clean_process_validates_frozen_pair_and_export_matches_source`
  - `tests/quality_gates/test_hotl_adapter.py::test_staleness_contract_requires_adjudication_before_reproof`
  - `tests/quality_gates/test_issue_closeout_commit_msg_hook.py::test_commit_msg_checker_resolves_exported_plugin_skill_layout`
  - `tests/quality_gates/test_issue_worker_carrier.py::test_collapsed_plugin_issue_loader_works_from_an_unrelated_cwd`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_a_failing_run_headlines_collateral_and_attaches_the_log_despite_a_summary[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_a_skipped_run_says_the_commands_never_ran[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_a_successful_run_attributes_the_verdict_to_the_summary[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_an_unset_run_outcome_is_reported_unexplained[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_an_oversized_body_is_clamped_before_it_is_posted[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_the_clamped_body_reaches_an_existing_issue_too[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_the_run_log_tail_is_clamped_by_characters_not_only_lines[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_every_copy_carries_the_outcome_environment_the_body_reads[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_a_pre_existing_label_and_a_missing_recovery_label_are_swallowed[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_an_empty_run_log_says_so_instead_of_showing_an_empty_fence[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_a_blank_tail_over_a_nonempty_log_does_not_claim_the_run_was_silent[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_an_unexpected_label_error_is_propagated_not_swallowed[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml-HARNESS_CREATE_LABEL_ERROR_STATUS-500-CREATE_LABEL]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_an_unexpected_label_error_is_propagated_not_swallowed[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml-HARNESS_REMOVE_LABEL_ERROR_STATUS-500-REMOVE_LABEL]`
  - `tests/quality_gates/test_mutation_issue_report_body.py::test_the_issue_listing_is_scoped_to_open_issues_carrying_the_label[plugins/charness/skills/quality/scripts/templates/mutation-tests.yml]`
  - `tests/quality_gates/test_mutation_workflow_install.py::test_plugin_copy_renders_the_workflow_into_a_fresh_repo`
  - `tests/quality_gates/test_mutation_workflow_install.py::test_dry_run_reports_a_template_source_that_exists`
  - `tests/quality_gates/test_mutation_workflow_install.py::test_plugin_copy_and_source_render_identical_workflows`
  - `tests/quality_gates/test_parents_index_layout_invariant.py::test_both_trees_are_present_so_this_test_can_mean_anything`
  - `tests/quality_gates/test_packaging_validation.py::test_install_surface_names_the_parser_adapter_lib_loads_by_path`
  - `tests/quality_gates/test_premise_preflight.py::test_cli_emits_shell_free_payload_for_valid_fixture[cli_path1]`
  - `tests/quality_gates/test_premise_preflight.py::test_cli_reports_accepted_and_refused_fixtures[cli_path1]`
  - `tests/quality_gates/test_provider_boundary.py::test_gate_covers_both_source_and_packaged_mirror`
  - `tests/quality_gates/test_public_skill_dogfood.py::test_public_skill_dogfood_wrappers_report_missing_policy_without_a_traceback`
  - `tests/quality_gates/test_public_skill_yaml_output_contract.py::test_quality_dispatch_plugin_commands_match_canonical_source`
  - `tests/quality_gates/test_public_skill_yaml_output_contract.py::test_summary_and_detail_are_mutually_exclusive[plugins/charness/skills/quality/scripts/inventory_skill_ergonomics.py]`
  - `tests/quality_gates/test_public_skill_yaml_output_contract.py::test_every_quality_inventory_exposes_yaml_output_contract`
  - `tests/quality_gates/test_quality_bootstrap_absence.py::test_plugin_bootstrap_matches_source_for_issue_496_fixture`
  - `tests/quality_gates/test_quality_mutation_testing.py::test_mutation_workflows_never_change_issue_state`
  - `tests/quality_gates/test_quality_mutation_testing.py::test_mutation_workflows_pass_workload_budget_envs`
  - `tests/quality_gates/test_quality_mutation_testing.py::test_a7_propose_script_mirrors_to_plugin_export`
  - `tests/quality_gates/test_quality_mutation_testing.py::test_a7_workflow_template_mirrors_to_plugin_export`
  - `tests/quality_gates/test_quality_mutation_testing.py::test_mutation_workflows_scope_issue_selection_to_their_own_marker`
  - `tests/quality_gates/test_quality_run_read_measurement.py::test_quality_required_read_measurement_is_source_plugin_parity_and_never_zero_for_missing`
  - `tests/quality_gates/test_release_publish_resilience.py::test_publish_release_imports_from_exported_plugin_layout`
  - `tests/quality_gates/test_retro_installed_plan_path.py::test_auto_trigger_packet_uses_installed_skill_root[exported-layout]`
  - `tests/quality_gates/test_retro_lesson_selection_index.py::test_the_checked_in_export_is_not_treated_as_a_competing_source_tree`
  - `tests/quality_gates/test_setup_hook_failure_guidance.py::test_default_source_and_plugin_inspectors_carry_the_reader_verdict`
  - `tests/quality_gates/test_setup_hook_failure_guidance.py::test_hook_failure_guidance_is_mirrored_and_names_the_contract`
  - `tests/quality_gates/test_shell_gate_root_resolution.py::test_repo_root_markdown_listing_contains_root_level_files`
  - `tests/quality_gates/test_skill_docs_contracts.py::test_setup_pins_live_spawn_first_execution_contract`
  - `tests/quality_gates/test_skill_docs_contracts.py::test_critique_and_debug_share_the_evidence_led_adversarial_route`
  - `tests/quality_gates/test_skill_docs_contracts.py::test_impl_source_and_checked_in_plugin_export_are_byte_identical`
  - `tests/quality_gates/test_staged_commit_gate_plan.py::test_staged_commit_gate_plan_plugin_mirror_matches_source`
  - `tests/quality_gates/test_standalone_imports.py::test_the_exported_mirror_enumerates_its_own_modules`
  - `tests/test_capability_catalog.py::test_catalog_resolver_refuses_existing_same_version_content_mismatch`
  - `tests/test_capability_catalog.py::test_catalog_resolver_recovers_rotated_cache`
  - `tests/test_capability_catalog.py::test_catalog_cli_dispatches_all_commands_and_direct_script_bootstraps_path`
  - `tests/test_consumer_validator_catalog.py::test_live_catalog_has_a_decision_for_every_packaged_candidate`
  - `tests/test_consumer_validator_catalog.py::test_the_catalog_reports_what_its_predicate_did_not_admit`
  - `tests/test_consumer_validator_catalog.py::test_the_discovery_predicate_is_positional_free_and_lost_nothing`
  - `tests/test_critique_verify_packet.py::test_source_and_generated_plugin_verifier_entrypoints_work`
  - `tests/test_evidence_boundary_crosswalk.py::test_the_installed_plugin_projection_exposes_the_same_authorization_entrypoint`
  - `tests/test_gather_plan.py::test_gather_plan_resolves_support_route_in_exported_plugin_layout`
  - `tests/test_gather_plan.py::test_exported_gather_plan_honors_github_adapter_mode`
  - `tests/test_issue_source_capture.py::test_resolver_is_loaded_from_the_root_and_installed_plugin_layouts`
  - `tests/test_issue_source_capture_backend_delegation.py::test_the_exported_mirror_can_reach_its_own_backend_owner`
  - `tests/test_probe_drift_message.py::test_the_counterfactual_floor_surface_carries_its_own_rerun_command`
  - `tests/test_probe_drift_message.py::test_every_residual_surface_exists_and_carries_the_figures_it_is_named_for`
  - `tests/test_provenance_contract.py::test_registry_has_one_complete_row_per_reviewed_boundary`
  - `tests/test_provenance_contract.py::test_contract_checker_executes_source_fixtures_in_process`
  - `tests/test_provenance_contract.py::test_contract_checker_marks_plugin_layout_shape_only`
  - `tests/test_provenance_contract.py::test_contract_checker_reports_fixture_timeout`
  - `tests/test_provenance_contract.py::test_contract_checker_reports_fixture_failure`
  - `tests/test_provenance_contract.py::test_contract_checker_script_entrypoint_exits_cleanly`
  - `tests/test_scaffold_repo_local_validator.py::test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one[debug]`
  - `tests/test_scaffold_repo_local_validator.py::test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one[quality]`
  - `tests/test_scaffold_repo_local_validator.py::test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one[critique]`
  - `tests/test_scaffold_repo_local_validator.py::test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one[ideation]`
  - `tests/test_scaffold_repo_local_validator.py::test_installed_like_scaffold_prefers_repo_local_validator_when_repo_owns_one[retro]`
  - `tests/test_skill_script_references.py::test_no_authoring_layout_reference_fails_to_resolve`
  - `tests/test_skill_script_references.py::test_no_shipped_reference_is_broken_because_its_file_is_in_the_package`
  - `tests/test_skill_script_references.py::test_shipped_layout_findings_never_grow`
  - `tests/charness_cli/test_codex_cache_refresh.py::test_codex_cache_refresh_accepts_real_initialize_shape_and_lifecycle_notifications`
  - `tests/charness_cli/test_codex_cache_refresh.py::test_charness_catalog_loader_imports_backend_in_process`
  - `tests/charness_cli/test_codex_cache_refresh.py::test_installed_cli_catalog_list_loads_backend_from_managed_checkout`
  - `tests/test_shared_authoring_script_shims.py`

## StrykerJS Mutation Slice

- Status: **UNMEASURED** (StrykerJS JSON report missing)
- Missing report: `/home/runner/work/charness/charness/reports/mutation/stryker-js.json`
- Blocking signal: collateral — the sampler's coverage-baseline pytest failed, so the JS slice was never invoked (see Mutation Testing Summary above).


No mutation sample manifest was generated.

---

<!-- charness-work-item-key: issue-758-mutation-main -->
# Work Item #758 — Reconcile the mutation-main regression

## Purpose and premise

Compare the original failed workflow with a current run at the exact published SHA. Classify the incident as already resolved, stale, or reproduced before implementation.

## Acceptance and proof

An issue-relevant provider-main success produces a no-code closeout; an unrelated green run is rejected. A reproduced failure enters debug before a same-Work-Item fix. Remote behavioral proof precedes closure.

## Non-claims

No claim from local tests alone and no closing keyword before the required remote run.
