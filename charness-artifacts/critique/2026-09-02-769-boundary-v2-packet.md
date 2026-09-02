# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-02T14:32:27Z
- **Prepared for**: 769 export boundary and gate classification
- **Substrate mode**: `committed-ref`
- **Changed ref**: `a5002ffc9..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `67629b7b2a65e80d86bd89c56c01f43b7f0da2c1b64caf8019ca78f0f916e6aa`
- **Reviewed paths**: 649
  - `.agents/command-dominance.yaml`
  - `.agents/consumer-validator-adoption.yaml`
  - `.agents/quality-adapter.yaml`
  - `.agents/quality-gates.yaml`
  - `.agents/retro-adapter.yaml`
  - `.agents/surfaces.json`
  - `.githooks/pre-commit`
  - `.githooks/pre-push`
  - `.github/workflows/quality-core.yml`
  - `README.md`
  - `charness`
  - `charness-artifacts/critique/2026-09-02-769-boundary-packet.json`
  - `charness-artifacts/critique/2026-09-02-769-boundary-packet.md`
  - `charness-artifacts/goal-runs/765/2026-09-02-session-record.md`
  - `charness-artifacts/goal-runs/765/bodies/ledger-only-lessons.md`
  - `charness-artifacts/goal-runs/765/bodies/parent-amended-774.md`
  - `charness-artifacts/goal-runs/765/bodies/parent-progress-768.md`
  - `charness-artifacts/goal-runs/765/bodies/parent-progress-769.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-768-production.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-768-ratchet.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-768-repair.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-768-tests.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-r2a-runner-lib.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-r2b-wire-runner.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-r3-native-reader.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-s-consumer-scope.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-t1-tools-tree.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-t2-tools-batch-b.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-u0-universes.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-u1-sources.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-u2-docs-artifacts.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-769-u3-scanners-configs.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p0-foundation.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p1-core-gates.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p2-mutation-worktree-hooks.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p3-review-lessons-adapters.md`
  - `charness-artifacts/goal-runs/765/briefs/brief-770-p4-remaining.md`
  - `charness-artifacts/goal-runs/765/briefs/design-critique-769.md`
  - `charness-artifacts/goal-runs/765/briefs/map-769-conditional.md`
  - `charness-artifacts/goal-runs/765/briefs/map-769-export.md`
  - `charness-artifacts/goal-runs/765/briefs/map-769-runner.md`
  - `charness-artifacts/goal-runs/765/briefs/map-770.md`
  - `charness-artifacts/goal-runs/765/briefs/map-772.md`
  - `charness-artifacts/goal-runs/765/briefs/repair-batch-r0.txt`
  - `charness-artifacts/goal-runs/765/briefs/repair-batch-r1.txt`
  - `charness-artifacts/goal-runs/765/briefs/repair-batch-r2.txt`
  - `charness-artifacts/goal-runs/765/briefs/reword-768-wip-subjects.sh`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.started.json`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.terminal.json`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.started.json`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.terminal.json`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.started.json`
  - `charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.terminal.json`
  - `charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.started.json`
  - `charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.terminal.json`
  - `charness-artifacts/goal-runs/765/observations/amend-parent-774-1.started.json`
  - `charness-artifacts/goal-runs/765/observations/amend-parent-774-1.terminal.json`
  - `charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.json`
  - `charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.out.yaml`
  - `charness-artifacts/goal-runs/765/operations/update-parent-amended-774.json`
  - `charness-artifacts/goal-runs/765/operations/update-parent-amended-774.out.yaml`
  - `charness-artifacts/goal-runs/765/operations/update-parent-progress-768.json`
  - `charness-artifacts/goal-runs/765/operations/update-parent-progress-768.out.yaml`
  - `charness-artifacts/goal-runs/765/operations/update-parent-progress-769.json`
  - `charness-artifacts/metrics/rca-ledger.jsonl`
  - `charness-artifacts/quality/2026-09-02-gate-classification-769.md`
  - `charness-artifacts/retro/2026-09-02-session-retro.md`
  - `charness-artifacts/retro/lesson-ledger.json`
  - `charness-artifacts/retro/lesson-selection-index.json`
  - `charness-artifacts/retro/recent-lessons.md`
  - `docs/artifact-policy.md`
  - `docs/authoring-preflight.md`
  - `docs/deferred-decisions.md`
  - `docs/development.md`
  - `docs/export-boundary.md`
  - `docs/external-integrations.md`
  - `docs/index.md`
  - `docs/operator-acceptance.md`
  - `docs/provenance-placement.md`
  - `docs/public-skill-dogfood.json`
  - `docs/public-skill-dogfood.md`
  - `docs/public-skill-validation.md`
  - `docs/validator-timing-layers.md`
  - `evals/README.md`
  - `integrations/tools/awiki.json`
  - `native/repograph/fixtures/carriers/expected/quality_label_universe.yaml`
  - `native/repograph/src/graph.rs`
  - `native/repograph/src/graph_carriers.rs`
  - `native/repograph/src/graph_imports.rs`
  - `native/repograph/src/graph_mirrors.rs`
  - `native/repograph/src/quality_gate_shell.rs`
  - `native/repograph/src/quality_gate_yaml.rs`
  - `native/repograph/src/standalone.rs`
  - `native/repograph/tests/carriers_quality_gates.rs`
  - `profiles/README.md`
  - `pyproject.toml`
  - `scripts/announcement_verification_lib.py`
  - `scripts/artifact_referents.py`
  - `scripts/artifact_run_scope.py`
  - `scripts/artifact_shape_source.py`
  - `scripts/bootstrap_runtime.py`
  - `scripts/boundary-bypass-baseline.json`
  - `scripts/boundary-bypass-exemptions.txt`
  - `scripts/boundary_bypass_ratchet_lib.py`
  - `scripts/build_retro_lesson_selection_index.py`
  - `scripts/changed_line_run_trust.py`
  - `scripts/check-docs.sh`
  - `scripts/check-python-lint.sh`
  - `scripts/check-secrets.sh`
  - `scripts/check-shell.sh`
  - `scripts/check_artifact_referents.py`
  - `scripts/check_artifact_surface_preflight.py`
  - `scripts/check_boundary_bypass_ratchet.py`
  - `scripts/check_cli_skill_surface.py`
  - `scripts/check_code_lengths.py`
  - `scripts/check_command_dominance.py`
  - `scripts/check_consumer_validator_catalog.py`
  - `scripts/check_coverage_lib.py`
  - `scripts/check_doc_links.py`
  - `scripts/check_docs_graph.py`
  - `scripts/check_documented_subcommands.py`
  - `scripts/check_git_identity.py`
  - `scripts/check_issue_closeout_commit_msg.py`
  - `scripts/check_lesson_ledger.py`
  - `scripts/check_mutation_run_proof.py`
  - `scripts/check_mutation_suite_score.py`
  - `scripts/check_prose_pin.py`
  - `scripts/check_python_runtime_inheritance.py`
  - `scripts/check_skill_ownership_overlap.allowlist.txt`
  - `scripts/check_skill_surface_preflight.py`
  - `scripts/check_spec_evidence_durability.py`
  - `scripts/check_staged_reversion.py`
  - `scripts/check_staged_router_change.py`
  - `scripts/check_staged_test_boundaries.py`
  - `scripts/check_staged_worktree_consistency.py`
  - `scripts/check_standalone_imports.py`
  - `scripts/check_subprocess_form.py`
  - `scripts/check_supply_chain_online.py`
  - `scripts/check_symbol_residue.py`
  - `scripts/check_test_production_ratio.py`
  - `scripts/check_upstream_support_drift.py`
  - `scripts/classify_push_diff_lib.py`
  - `scripts/classify_t_signal.py`
  - `scripts/command_carrier_discovery.py`
  - `scripts/command_plan_inputs.py`
  - `scripts/command_plan_preflight.py`
  - `scripts/control_plane_lib.py`
  - `scripts/critique_artifact_paths.py`
  - `scripts/critique_artifact_universe.py`
  - `scripts/critique_packet_lib.py`
  - `scripts/debug_persistence_lib.py`
  - `scripts/doc_file_population.py`
  - `scripts/dup_ratchet_edit_advisory.py`
  - `scripts/eval_support_sync_contracts.py`
  - `scripts/exported-copy-guard.sh`
  - `scripts/git_status_snapshot.py`
  - `scripts/install_provenance_lib.py`
  - `scripts/inventory_boundary_bypass_lib.py`
  - `scripts/inventory_cli_ergonomics_unavailable.py`
  - `scripts/inventory_current_pointer_layouts.py`
  - `scripts/inventory_gitignore_scan_hygiene_unavailable.py`
  - `scripts/inventory_nose_clones_unavailable.py`
  - `scripts/issue_source_capture_lib.py`
  - `scripts/lesson_ledger_lib.py`
  - `scripts/lesson_selection_preview_lib.py`
  - `scripts/markdown_preview_bootstrap_lib.py`
  - `scripts/markdownlint_probe.py`
  - `scripts/mutate_and_restore.py`
  - `scripts/mutation_changed_files_lib.py`
  - `scripts/mutation_changed_line_diff.py`
  - `scripts/mutation_coverage_producer.py`
  - `scripts/mutation_recovery.py`
  - `scripts/mutation_sampling_lib.py`
  - `scripts/mutation_sampling_selection.py`
  - `scripts/mutation_sweep_report.py`
  - `scripts/native_gate_lib.py`
  - `scripts/packaging_lib.py`
  - `scripts/parity_harness.py`
  - `scripts/premise_git_snapshot.py`
  - `scripts/premise_tree_observation.py`
  - `scripts/prepush_close_keyword_scan.py`
  - `scripts/prepush_quality_receipt.py`
  - `scripts/probe_record_parse.py`
  - `scripts/probe_stimulus_replay.py`
  - `scripts/quality_adapter_lib.py`
  - `scripts/quality_artifact_skill_ergonomics.py`
  - `scripts/quality_gate_provenance_fallback.py`
  - `scripts/quality_label_universe.py`
  - `scripts/quality_universes_lib.py`
  - `scripts/recent_lesson_selection.py`
  - `scripts/recent_lessons_lib.py`
  - `scripts/release_changed_line_coverage.py`
  - `scripts/release_changed_line_coverage_unavailable.py`
  - `scripts/removed_name_consumers.py`
  - `scripts/render_cli_reference.py`
  - `scripts/render_lesson_selection_preview.py`
  - `scripts/render_validator_timing_layers.py`
  - `scripts/repo_file_listing.py`
  - `scripts/resolve_artifact_path.py`
  - `scripts/retro_output_dir_lib.py`
  - `scripts/retro_persistence_lib.py`
  - `scripts/reviewed_input_identity.py`
  - `scripts/reviewed_input_nonblob.py`
  - `scripts/run-quality.sh`
  - `scripts/run_cosmic_ray_mutation.py`
  - `scripts/run_js_mutation.py`
  - `scripts/run_quality_engine.py`
  - `scripts/run_quality_engine_model.py`
  - `scripts/run_quality_engine_output.py`
  - `scripts/run_quality_engine_phase.py`
  - `scripts/run_quality_engine_receipt.py`
  - `scripts/run_quality_engine_runtime.py`
  - `scripts/run_quality_engine_selection.py`
  - `scripts/run_specdown.py`
  - `scripts/run_standing_pytest.py`
  - `scripts/rust_changed_line_coverage.py`
  - `scripts/sample_mutation_files.py`
  - `scripts/setup_adapter_inspect_lib.py`
  - `scripts/setup_inspect_quality_lib.py`
  - `scripts/specdown_ephemeral_config.py`
  - `scripts/staged_commit_gate_plan.py`
  - `scripts/staged_commit_gate_plan_helpers.py`
  - `scripts/standing_pytest_basetemp.py`
  - `scripts/subprocess_guard.py`
  - `scripts/subprocess_only_coverage_advisory.py`
  - `scripts/surfaces_lib.py`
  - `scripts/task_run.py`
  - `scripts/task_run_execution.py`
  - `scripts/task_run_git.py`
  - `scripts/upstream_release_lib.py`
  - `scripts/validate_adapters.py`
  - `scripts/validate_critique_artifacts.py`
  - `scripts/validate_ideation_artifact.py`
  - `scripts/validate_inventory_consumption.py`
  - `scripts/validate_maintainer_setup.py`
  - `scripts/validate_packaging_install_surface.py`
  - `scripts/validate_presets.py`
  - `scripts/validate_quality_artifact.py`
  - `scripts/waiver_file_lines.py`
  - `scripts/worktree_audit_lib.py`
  - `scripts/worktree_cleanup_lib.py`
  - `scripts/worktree_create_lib.py`
  - `scripts/worktree_doctor_checks.py`
  - `scripts/worktree_doctor_lib.py`
  - `scripts/worktree_doctor_manifest.py`
  - `scripts/worktree_exec_lib.py`
  - `skills/public/achieve/SKILL.md`
  - `skills/public/achieve/scripts/goal_run_pickup.py`
  - `skills/public/achieve/scripts/goal_run_pickup_lessons.py`
  - `skills/public/announcement/scripts/collect_commits.py`
  - `skills/public/announcement/scripts/infer_audience_tags.py`
  - `skills/public/create-skill/references/portable-authoring.md`
  - `skills/public/critique/references/code-critique.md`
  - `skills/public/critique/scripts/run_review_support.py`
  - `skills/public/critique/scripts/semantic_review_input.py`
  - `skills/public/debug/references/sibling-search.md`
  - `skills/public/gather/scripts/gather_public_execution.py`
  - `skills/public/gather/scripts/gather_public_url.py`
  - `skills/public/issue/scripts/issue_backend.py`
  - `skills/public/issue/scripts/issue_closeout_classification_ledger.py`
  - `skills/public/issue/scripts/issue_critique_observer_support.py`
  - `skills/public/issue/scripts/issue_runtime.py`
  - `skills/public/issue/scripts/issue_state_readback.py`
  - `skills/public/issue/scripts/issue_verify_closeout.py`
  - `skills/public/issue/scripts/issue_verify_closeout_authorization.py`
  - `skills/public/issue/scripts/issue_verify_closeout_carrier.py`
  - `skills/public/narrative/scripts/map_sources.py`
  - `skills/public/quality/SKILL.md`
  - `skills/public/quality/adapter.example.yaml`
  - `skills/public/quality/references/adapter-contract.md`
  - `skills/public/quality/references/attention-state-visibility.json`
  - `skills/public/quality/references/boundary-bypass-payload.example.json`
  - `skills/public/quality/references/boundary-bypass-ratchet.md`
  - `skills/public/quality/references/catalog.yaml`
  - `skills/public/quality/references/consumer-validator-catalog.yaml`
  - `skills/public/quality/references/coverage-floor-policy.md`
  - `skills/public/quality/references/index.md`
  - `skills/public/quality/references/inventory-consumer-fields.json`
  - `skills/public/quality/references/inventory-dispatch.md`
  - `skills/public/quality/references/testability-and-selection.md`
  - `skills/public/quality/references/validate_spec_pytest_references.py`
  - `skills/public/quality/scripts/adapter_validators.py`
  - `skills/public/quality/scripts/changed_line_coverage_gate_lib.py`
  - `skills/public/quality/scripts/check_provenance_contract.py`
  - `skills/public/quality/scripts/ci_local_gate_parity_lib.py`
  - `skills/public/quality/scripts/cli_side_effect_probe_lib.py`
  - `skills/public/quality/scripts/discovery_filter_scan_lib.py`
  - `skills/public/quality/scripts/doc_duplicate_scan.py`
  - `skills/public/quality/scripts/draft_dup_ratchet_triage.py`
  - `skills/public/quality/scripts/dup_ratchet_git.py`
  - `skills/public/quality/scripts/dup_ratchet_lib.py`
  - `skills/public/quality/scripts/dup_ratchet_scan.py`
  - `skills/public/quality/scripts/inventory_ci_local_gate_parity.py`
  - `skills/public/quality/scripts/inventory_doc_duplicates.py`
  - `skills/public/quality/scripts/inventory_empty_scope_honesty.py`
  - `skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py`
  - `skills/public/quality/scripts/inventory_sloc.py`
  - `skills/public/quality/scripts/measure_startup_probes.py`
  - `skills/public/quality/scripts/nose_tool_lib.py`
  - `skills/public/quality/scripts/plan_quality_run.py`
  - `skills/public/quality/scripts/pytest_temp_scan_lib.py`
  - `skills/public/quality/scripts/quality_declaration_lifecycle.py`
  - `skills/public/quality/scripts/quality_declared_gate_source.py`
  - `skills/public/quality/scripts/quality_preset_reconciliation.py`
  - `skills/public/quality/scripts/regenerable_facts_lib.py`
  - `skills/public/quality/scripts/run_dead_code_advisory.py`
  - `skills/public/quality/scripts/runtime_budget_universe_lib.py`
  - `skills/public/quality/scripts/seed_dup_review.py`
  - `skills/public/quality/scripts/standing_gate_discovery_lib.py`
  - `skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py`
  - `skills/public/quality/scripts/standing_gate_verbosity_lib.py`
  - `skills/public/quality/scripts/standing_test_economics_lib.py`
  - `skills/public/quality/scripts/test_discovery_lib.py`
  - `skills/public/quality/scripts/validate_boundary_bypass_payload.py`
  - `skills/public/release/scripts/bump_version.py`
  - `skills/public/release/scripts/check_fresh_checkout_probes.py`
  - `skills/public/release/scripts/check_requested_review_gate.py`
  - `skills/public/release/scripts/claims_review_scope.py`
  - `skills/public/release/scripts/current_release.py`
  - `skills/public/release/scripts/plan_release_prepared_stop.py`
  - `skills/public/release/scripts/publish_release_adapter_preflight.py`
  - `skills/public/release/scripts/publish_release_commands.py`
  - `skills/public/release/scripts/publish_release_helpers.py`
  - `skills/public/release/scripts/publish_release_preflight.py`
  - `skills/public/release/scripts/publish_release_runtime.py`
  - `skills/public/release/scripts/publish_release_scope.py`
  - `skills/public/release/scripts/release_delta.py`
  - `skills/public/retro/SKILL.md`
  - `skills/public/retro/adapter.example.yaml`
  - `skills/public/retro/references/waste-sibling-scan.md`
  - `skills/public/retro/scripts/check_auto_trigger.py`
  - `skills/public/retro/scripts/plan_retro_run.py`
  - `skills/public/retro/scripts/retro_plan_reads.py`
  - `skills/public/setup/references/greenfield-flow.md`
  - `skills/public/setup/references/retro-memory-seam.md`
  - `skills/public/setup/scripts/seed_worktree_adapter_lib.py`
  - `skills/shared/references/binary-preflight.md`
  - `skills/shared/scripts/authoring_script_shim.py`
  - `skills/shared/scripts/reviewer_boundary_state.py`
  - `skills/shared/scripts/reviewer_process.py`
  - `skills/shared/scripts/reviewer_worker_runner_support.py`
  - `skills/shared/scripts/run_reviewer_worker.py`
  - `skills/shared/scripts/validate_skills.py`
  - `skills/support/markdown-preview/scripts/markdown_preview_render.py`
  - `skills/support/web-fetch/scripts/acquire_public_url_io.py`
  - `tests/charness_cli/support.py`
  - `tests/charness_cli/test_bootstrap_runtime.py`
  - `tests/charness_cli/test_codex_cache_refresh.py`
  - `tests/charness_cli/test_codex_managed_install.py`
  - `tests/charness_cli/test_doctor_next_action.py`
  - `tests/charness_cli/test_managed_install.py`
  - `tests/charness_cli/test_managed_install_extended.py`
  - `tests/charness_cli/test_managed_install_release_checks.py`
  - `tests/charness_cli/test_task_run.py`
  - `tests/charness_cli/test_task_run_lib_root.py`
  - `tests/charness_cli/test_update_flow_unit.py`
  - `tests/charness_cli/test_update_output.py`
  - `tests/charness_cli/test_update_propagation.py`
  - `tests/charness_cli/test_version_surface.py`
  - `tests/charness_cli/test_worktree_audit.py`
  - `tests/charness_cli/test_worktree_cleanup.py`
  - `tests/charness_cli/test_worktree_create.py`
  - `tests/charness_cli/test_worktree_doctor.py`
  - `tests/charness_cli/test_worktree_exec.py`
  - `tests/conftest.py`
  - `tests/control_plane/support.py`
  - `tests/control_plane/test_integrations_validation.py`
  - `tests/control_plane/test_monorepo_layout.py`
  - `tests/control_plane/test_upstream_release.py`
  - `tests/control_plane/test_upstream_release_helpers.py`
  - `tests/coverage_debt/test_batch3.py`
  - `tests/coverage_debt/test_batch4.py`
  - `tests/coverage_debt/test_batch5.py`
  - `tests/coverage_debt/test_batch6.py`
  - `tests/coverage_debt/test_batch8.py`
  - `tests/quality_gates/fixtures/.agents/quality-gates.yaml`
  - `tests/quality_gates/fixtures/consumer-quality-gates.yaml`
  - `tests/quality_gates/fixtures/engine_gate.py`
  - `tests/quality_gates/fixtures/quality-gates-engine.yaml`
  - `tests/quality_gates/fixtures/scripts/run-quality.sh`
  - `tests/quality_gates/inprocess_script_support.py`
  - `tests/quality_gates/quality_runner_seed.py`
  - `tests/quality_gates/release_publish_fixtures.py`
  - `tests/quality_gates/support.py`
  - `tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py`
  - `tests/quality_gates/test_absent_input_is_not_a_matching_input.py`
  - `tests/quality_gates/test_achieve_goal_run_pickup.py`
  - `tests/quality_gates/test_argparse_surface_lib.py`
  - `tests/quality_gates/test_artifact_naming.py`
  - `tests/quality_gates/test_artifact_referents.py`
  - `tests/quality_gates/test_attention_state_visibility.py`
  - `tests/quality_gates/test_boundary_bypass_payload_validator.py`
  - `tests/quality_gates/test_changed_line_run_trust.py`
  - `tests/quality_gates/test_check_artifact_surface_preflight.py`
  - `tests/quality_gates/test_check_bootstrap_shim_consistency.py`
  - `tests/quality_gates/test_check_coverage_inventory.py`
  - `tests/quality_gates/test_check_git_identity.py`
  - `tests/quality_gates/test_check_last_verified.py`
  - `tests/quality_gates/test_check_mutation_run_proof.py`
  - `tests/quality_gates/test_check_plugin_doc_links.py`
  - `tests/quality_gates/test_check_prose_pin.py`
  - `tests/quality_gates/test_check_public_doc_coupling.py`
  - `tests/quality_gates/test_check_skill_cut_safety.py`
  - `tests/quality_gates/test_check_staged_worktree_consistency.py`
  - `tests/quality_gates/test_check_test_completeness.py`
  - `tests/quality_gates/test_classify_push_diff.py`
  - `tests/quality_gates/test_cli_skill_surface.py`
  - `tests/quality_gates/test_closeout_authorization_ingress.py`
  - `tests/quality_gates/test_code_length_gates.py`
  - `tests/quality_gates/test_command_docs_gate.py`
  - `tests/quality_gates/test_command_dominance.py`
  - `tests/quality_gates/test_coverage_floor_inventory_reference.py`
  - `tests/quality_gates/test_critique_boundary_ownership_presence.py`
  - `tests/quality_gates/test_critique_delivery_state_floor.py`
  - `tests/quality_gates/test_current_pointer_freshness.py`
  - `tests/quality_gates/test_current_pointer_writers.py`
  - `tests/quality_gates/test_current_pointer_writes.py`
  - `tests/quality_gates/test_current_release_version_refusal.py`
  - `tests/quality_gates/test_docs_and_misc.py`
  - `tests/quality_gates/test_dup_ratchet_triage.py`
  - `tests/quality_gates/test_dup_ratchet_triage_draft.py`
  - `tests/quality_gates/test_dup_review_seed.py`
  - `tests/quality_gates/test_empty_scope_refusals.py`
  - `tests/quality_gates/test_every_resolver_answers_a_refused_document.py`
  - `tests/quality_gates/test_export_self_sufficiency.py`
  - `tests/quality_gates/test_gather_provider.py`
  - `tests/quality_gates/test_gather_symlink_safety.py`
  - `tests/quality_gates/test_goal_binding_v1.py`
  - `tests/quality_gates/test_hitl_chunk_contract.py`
  - `tests/quality_gates/test_inference_interpretation_meta_validator.py`
  - `tests/quality_gates/test_inventory_ci_local_gate_parity.py`
  - `tests/quality_gates/test_inventory_consumption.py`
  - `tests/quality_gates/test_issue_closeout_commit_msg_hook.py`
  - `tests/quality_gates/test_issue_read.py`
  - `tests/quality_gates/test_issue_worker_carrier.py`
  - `tests/quality_gates/test_js_mutation_tooling.py`
  - `tests/quality_gates/test_maintainer_hooks.py`
  - `tests/quality_gates/test_mutate_and_restore.py`
  - `tests/quality_gates/test_mutate_and_restore_call_sites.py`
  - `tests/quality_gates/test_mutation_baseline_abort.py`
  - `tests/quality_gates/test_mutation_changed_line_targets.py`
  - `tests/quality_gates/test_mutation_coverage_probe.py`
  - `tests/quality_gates/test_mutation_coverage_producer.py`
  - `tests/quality_gates/test_mutation_recovery.py`
  - `tests/quality_gates/test_mutation_sampling_line_coverage.py`
  - `tests/quality_gates/test_mutation_test_reporters.py`
  - `tests/quality_gates/test_native_gate_lib.py`
  - `tests/quality_gates/test_packaging_validation.py`
  - `tests/quality_gates/test_parents_index_layout_invariant.py`
  - `tests/quality_gates/test_parity_harness.py`
  - `tests/quality_gates/test_plugin_asset_command_carriers.py`
  - `tests/quality_gates/test_premise_preflight.py`
  - `tests/quality_gates/test_prepush_close_keyword_guard.py`
  - `tests/quality_gates/test_prepush_runtime_regime.py`
  - `tests/quality_gates/test_prescribed_skill_executed.py`
  - `tests/quality_gates/test_profile_and_preset_validation.py`
  - `tests/quality_gates/test_public_skill_yaml_output_contract.py`
  - `tests/quality_gates/test_python_and_security_gates.py`
  - `tests/quality_gates/test_quality_bootstrap_absence.py`
  - `tests/quality_gates/test_quality_bootstrap_absence_paths.py`
  - `tests/quality_gates/test_quality_declaration_path_resolution.py`
  - `tests/quality_gates/test_quality_doc_duplicates.py`
  - `tests/quality_gates/test_quality_dual_implementation.py`
  - `tests/quality_gates/test_quality_gate_list_fixture_parity.py`
  - `tests/quality_gates/test_quality_gitignore_scan_hygiene.py`
  - `tests/quality_gates/test_quality_markdown_preview_bootstrap.py`
  - `tests/quality_gates/test_quality_mutation_coverage.py`
  - `tests/quality_gates/test_quality_mutation_sampling.py`
  - `tests/quality_gates/test_quality_mutation_testing.py`
  - `tests/quality_gates/test_quality_policy_merge_import.py`
  - `tests/quality_gates/test_quality_run_planner.py`
  - `tests/quality_gates/test_quality_run_planner_declared.py`
  - `tests/quality_gates/test_quality_runner.py`
  - `tests/quality_gates/test_quality_runner_coverage_selection.py`
  - `tests/quality_gates/test_quality_runner_exit_status.py`
  - `tests/quality_gates/test_quality_runner_label_universe.py`
  - `tests/quality_gates/test_quality_runner_progress.py`
  - `tests/quality_gates/test_quality_runner_release_order.py`
  - `tests/quality_gates/test_quality_runner_runtime_aggregate.py`
  - `tests/quality_gates/test_quality_runner_unproven.py`
  - `tests/quality_gates/test_quality_runtime_recorder.py`
  - `tests/quality_gates/test_quality_skill_docs.py`
  - `tests/quality_gates/test_quality_standing_gate_verbosity.py`
  - `tests/quality_gates/test_quality_tool_fixtures.py`
  - `tests/quality_gates/test_quality_tool_recommendations.py`
  - `tests/quality_gates/test_quality_universes.py`
  - `tests/quality_gates/test_release_changed_line_coverage.py`
  - `tests/quality_gates/test_release_fresh_checkout_probes.py`
  - `tests/quality_gates/test_release_issue_closeout_preflight.py`
  - `tests/quality_gates/test_release_only_sentinel_inventory.py`
  - `tests/quality_gates/test_release_planner_version_refusal.py`
  - `tests/quality_gates/test_release_publish.py`
  - `tests/quality_gates/test_release_publish_post_create.py`
  - `tests/quality_gates/test_release_publish_provenance.py`
  - `tests/quality_gates/test_release_publish_requested_review.py`
  - `tests/quality_gates/test_release_publish_rollback.py`
  - `tests/quality_gates/test_release_publish_tag_history.py`
  - `tests/quality_gates/test_release_quality_status_binding.py`
  - `tests/quality_gates/test_release_run_planner.py`
  - `tests/quality_gates/test_release_run_planner_prepared_stop.py`
  - `tests/quality_gates/test_repo_copy_invariants.py`
  - `tests/quality_gates/test_retro_artifact_validation.py`
  - `tests/quality_gates/test_retro_auto_trigger.py`
  - `tests/quality_gates/test_retro_installed_plan_path.py`
  - `tests/quality_gates/test_retro_lesson_selection_index.py`
  - `tests/quality_gates/test_retro_memory.py`
  - `tests/quality_gates/test_retro_persistence.py`
  - `tests/quality_gates/test_reviewer_runner.py`
  - `tests/quality_gates/test_reviewer_worker.py`
  - `tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py`
  - `tests/quality_gates/test_run_quality_engine.py`
  - `tests/quality_gates/test_runtime_budget_universe.py`
  - `tests/quality_gates/test_s6_changed_line_gaps.py`
  - `tests/quality_gates/test_s6b2_changed_line_gaps.py`
  - `tests/quality_gates/test_scaffold_claims_review.py`
  - `tests/quality_gates/test_scaffold_version_refusal.py`
  - `tests/quality_gates/test_script_inprocess_behaviors.py`
  - `tests/quality_gates/test_seed_worktree_adapter.py`
  - `tests/quality_gates/test_semantic_review_command.py`
  - `tests/quality_gates/test_setup_hook_failure_guidance.py`
  - `tests/quality_gates/test_setup_inspect_adapters.py`
  - `tests/quality_gates/test_setup_inspect_policy.py`
  - `tests/quality_gates/test_setup_retro_memory.py`
  - `tests/quality_gates/test_shared_script_gate_scope.py`
  - `tests/quality_gates/test_shell_gate_root_resolution.py`
  - `tests/quality_gates/test_skill_bootstrap_vars.py`
  - `tests/quality_gates/test_skill_contracts_validation.py`
  - `tests/quality_gates/test_skill_docs_contracts.py`
  - `tests/quality_gates/test_skill_ergonomics_gate.py`
  - `tests/quality_gates/test_skill_reference_index.py`
  - `tests/quality_gates/test_skill_surface_preflight.py`
  - `tests/quality_gates/test_skill_validation.py`
  - `tests/quality_gates/test_specdown_ephemeral_config.py`
  - `tests/quality_gates/test_staged_commit_gate_plan.py`
  - `tests/quality_gates/test_staged_test_boundaries.py`
  - `tests/quality_gates/test_standalone_imports.py`
  - `tests/quality_gates/test_standing_pytest_run_execution.py`
  - `tests/quality_gates/test_standing_pytest_runner.py`
  - `tests/quality_gates/test_subprocess_form_gate.py`
  - `tests/quality_gates/test_subprocess_only_coverage_advisory.py`
  - `tests/quality_gates/test_surface_obligations.py`
  - `tests/quality_gates/test_test_production_ratio.py`
  - `tests/quality_gates/test_timing_layer_completeness.py`
  - `tests/quality_gates/test_u2_doc_artifact_universes.py`
  - `tests/quality_gates/test_universe_consumers.py`
  - `tests/quality_gates/test_unreferenced_scripts.py`
  - `tests/test_achieve_lesson_citation.py`
  - `tests/test_adversarial_evidence.py`
  - `tests/test_agent_browser_runtime_guard.py`
  - `tests/test_announcement_delivery_verification.py`
  - `tests/test_authoring_preflight_reference.py`
  - `tests/test_boundary_bypass_ratchet.py`
  - `tests/test_changed_path_enumerator_agreement.py`
  - `tests/test_classify_t_signal.py`
  - `tests/test_closeout_classification_parity.py`
  - `tests/test_committed_packet_refusal.py`
  - `tests/test_consumer_validator_catalog.py`
  - `tests/test_critique_section_changed_surfaces.py`
  - `tests/test_critique_verify_packet.py`
  - `tests/test_debug_artifact.py`
  - `tests/test_debug_artifact_scope.py`
  - `tests/test_debug_persistence.py`
  - `tests/test_degradation_branch_coverage.py`
  - `tests/test_doc_duplicates_inprocess_coverage.py`
  - `tests/test_docs_graph_gate.py`
  - `tests/test_evidence_boundary_crosswalk.py`
  - `tests/test_gather_plan.py`
  - `tests/test_impl_survey_verification.py`
  - `tests/test_inventory_marker_rule_measurement.py`
  - `tests/test_issue_source_capture.py`
  - `tests/test_lesson_ledger.py`
  - `tests/test_lesson_ledger_refusals.py`
  - `tests/test_lesson_lifecycle.py`
  - `tests/test_lesson_selection_preview.py`
  - `tests/test_list_external_links.py`
  - `tests/test_markdown_preview_support.py`
  - `tests/test_public_skill_dogfood.py`
  - `tests/test_public_skill_validation.py`
  - `tests/test_quality_delegated_review.py`
  - `tests/test_retro_help.py`
  - `tests/test_reviewed_input_identity_binding.py`
  - `tests/test_reviewed_input_nonblob_binding.py`
  - `tests/test_scaffold_inprocess_coverage.py`
  - `tests/test_script_timeout.py`
  - `tests/test_seed_lesson_transitions.py`
  - `tests/test_shared_authoring_script_shims.py`
  - `tests/test_skill_anchor_guard_hook.py`
  - `tests/test_skill_script_references.py`
  - `tests/test_subprocess_guard.py`
  - `tests/test_supply_chain_online.py`
  - `tests/test_twitter_exact_source.py`
  - `tests/test_unhappy_path_branches.py`
  - `tests/test_validate_adapters_integration_schema.py`
  - `tests/test_validate_critique_artifacts_dates.py`
  - `tests/test_web_fetch_cleanup.py`
  - `tests/test_web_fetch_content_persistence.py`
  - `tests/test_web_fetch_route_and_classify.py`
  - `tests/test_web_fetch_support.py`
  - `tests/test_web_fetch_trace_quality.py`
  - `tests/test_write_artifact_path_single_owner.py`
  - `tools/__init__.py`
  - `tools/check_bootstrap_shim_consistency.py`
  - `tools/check_closeout_classification_parity.py`
  - `tools/check_consumer_validator_catalog_decisions.py`
  - `tools/check_coverage.py`
  - `tools/check_coverage_extra_lib.py`
  - `tools/check_current_pointer_writes.py`
  - `tools/check_export_self_sufficiency.py`
  - `tools/check_inventory_declaration_coverage.py`
  - `tools/check_last_verified.py`
  - `tools/check_plugin_asset_command_carriers.py`
  - `tools/check_plugin_doc_links.py`
  - `tools/check_plugin_import_smoke.py`
  - `tools/check_public_doc_coupling.py`
  - `tools/check_quality_tool_fixtures.py`
  - `tools/check_references_link_inventory.py`
  - `tools/check_runtime_budget_universe.py`
  - `tools/check_skill_bootstrap_vars.py`
  - `tools/check_skill_contracts.py`
  - `tools/check_skill_cut_safety.py`
  - `tools/check_timing_layer_completeness.py`
  - `tools/check_unreferenced_scripts.py`
  - `tools/eval_issue_scenarios.py`
  - `tools/eval_registry.py`
  - `tools/eval_setup.py`
  - `tools/export_self_sufficiency_lib.py`
  - `tools/export_tools_reference_lib.py`
  - `tools/inventory_skill_script_references.py`
  - `tools/public_skill_dogfood_validation_lib.py`
  - `tools/quality_gates_extract.py`
  - `tools/run_evals.py`
  - `tools/skill_portability_lib.py`
  - `tools/suggest_public_skill_validation.py`
  - `tools/validate_attention_state_visibility.py`
  - `tools/validate_current_pointer_freshness.py`
  - `tools/validate_inference_interpretation.py`
  - `tools/validate_integrations.py`
  - `tools/validate_inventory_consumption_declaration.py`
  - `tools/validate_packaging_committed.py`
  - `tools/validate_profiles.py`
  - `tools/validate_public_skill_dogfood.py`
  - `tools/validate_public_skill_validation.py`
  - `tools/validate_quality_closeout_contract.py`
  - `tools/validate_quality_reference_catalog.py`
  - `tools/validate_skills.py`
  - `tools/validate_surfaces.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/2026-09-02-769-boundary-v2-packet.json --packet-sha256 8813f0f509d4d7042c9933502a5ba2f89cd0fdf02fd14307f93128167951e265 --identity-sha256 67629b7b2a65e80d86bd89c56c01f43b7f0da2c1b64caf8019ca78f0f916e6aa
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Execution mode**: `file-backed-worker`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `a5002ffc9..HEAD`:
- .agents/command-dominance.yaml
- .agents/consumer-validator-adoption.yaml
- .agents/quality-adapter.yaml
- .agents/quality-gates.yaml
- .agents/retro-adapter.yaml
- .agents/surfaces.json
- .githooks/pre-commit
- .githooks/pre-push
- .github/workflows/quality-core.yml
- README.md
- charness
- charness-artifacts/critique/2026-09-02-769-boundary-packet.json
- charness-artifacts/critique/2026-09-02-769-boundary-packet.md
- charness-artifacts/goal-runs/765/2026-09-02-session-record.md
- charness-artifacts/goal-runs/765/bodies/ledger-only-lessons.md
- charness-artifacts/goal-runs/765/bodies/parent-amended-774.md
- charness-artifacts/goal-runs/765/bodies/parent-progress-768.md
- charness-artifacts/goal-runs/765/bodies/parent-progress-769.md
- charness-artifacts/goal-runs/765/briefs/brief-768-production.md
- charness-artifacts/goal-runs/765/briefs/brief-768-ratchet.md
- charness-artifacts/goal-runs/765/briefs/brief-768-repair.md
- charness-artifacts/goal-runs/765/briefs/brief-768-tests.md
- charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md
- charness-artifacts/goal-runs/765/briefs/brief-769-r2a-runner-lib.md
- charness-artifacts/goal-runs/765/briefs/brief-769-r2b-wire-runner.md
- charness-artifacts/goal-runs/765/briefs/brief-769-r3-native-reader.md
- charness-artifacts/goal-runs/765/briefs/brief-769-s-consumer-scope.md
- charness-artifacts/goal-runs/765/briefs/brief-769-t1-tools-tree.md
- charness-artifacts/goal-runs/765/briefs/brief-769-t2-tools-batch-b.md
- charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md
- charness-artifacts/goal-runs/765/briefs/brief-769-u0-universes.md
- charness-artifacts/goal-runs/765/briefs/brief-769-u1-sources.md
- charness-artifacts/goal-runs/765/briefs/brief-769-u2-docs-artifacts.md
- charness-artifacts/goal-runs/765/briefs/brief-769-u3-scanners-configs.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p0-foundation.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p1-core-gates.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p2-mutation-worktree-hooks.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p3-review-lessons-adapters.md
- charness-artifacts/goal-runs/765/briefs/brief-770-p4-remaining.md
- charness-artifacts/goal-runs/765/briefs/design-critique-769.md
- charness-artifacts/goal-runs/765/briefs/map-769-conditional.md
- charness-artifacts/goal-runs/765/briefs/map-769-export.md
- charness-artifacts/goal-runs/765/briefs/map-769-runner.md
- charness-artifacts/goal-runs/765/briefs/map-770.md
- charness-artifacts/goal-runs/765/briefs/map-772.md
- charness-artifacts/goal-runs/765/briefs/repair-batch-r0.txt
- charness-artifacts/goal-runs/765/briefs/repair-batch-r1.txt
- charness-artifacts/goal-runs/765/briefs/repair-batch-r2.txt
- charness-artifacts/goal-runs/765/briefs/reword-768-wip-subjects.sh
- charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.started.json
- charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.terminal.json
- charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.started.json
- charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.terminal.json
- charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.started.json
- charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.terminal.json
- charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.started.json
- charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.terminal.json
- charness-artifacts/goal-runs/765/observations/amend-parent-774-1.started.json
- charness-artifacts/goal-runs/765/observations/amend-parent-774-1.terminal.json
- charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.json
- charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.out.yaml
- charness-artifacts/goal-runs/765/operations/update-parent-amended-774.json
- charness-artifacts/goal-runs/765/operations/update-parent-amended-774.out.yaml
- charness-artifacts/goal-runs/765/operations/update-parent-progress-768.json
- charness-artifacts/goal-runs/765/operations/update-parent-progress-768.out.yaml
- charness-artifacts/goal-runs/765/operations/update-parent-progress-769.json
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/quality/2026-09-02-gate-classification-769.md
- charness-artifacts/retro/2026-09-02-session-retro.md
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md  (DELETED — judge what depended on it)
- docs/artifact-policy.md
- docs/authoring-preflight.md
- docs/deferred-decisions.md
- docs/development.md
- docs/export-boundary.md
- docs/external-integrations.md
- docs/index.md
- docs/operator-acceptance.md
- docs/provenance-placement.md
- docs/public-skill-dogfood.json
- docs/public-skill-dogfood.md
- docs/public-skill-validation.md
- docs/validator-timing-layers.md
- evals/README.md
- integrations/tools/awiki.json
- native/repograph/fixtures/carriers/expected/quality_label_universe.yaml
- native/repograph/src/graph.rs
- native/repograph/src/graph_carriers.rs
- native/repograph/src/graph_imports.rs
- native/repograph/src/graph_mirrors.rs
- native/repograph/src/quality_gate_shell.rs
- native/repograph/src/quality_gate_yaml.rs
- native/repograph/src/standalone.rs
- native/repograph/tests/carriers_quality_gates.rs
- profiles/README.md
- pyproject.toml
- scripts/announcement_verification_lib.py
- scripts/artifact_referents.py
- scripts/artifact_run_scope.py
- scripts/artifact_shape_source.py
- scripts/bootstrap_runtime.py
- scripts/boundary-bypass-baseline.json  (DELETED — judge what depended on it)
- scripts/boundary-bypass-exemptions.txt  (DELETED — judge what depended on it)
- scripts/boundary_bypass_ratchet_lib.py  (DELETED — judge what depended on it)
- scripts/build_retro_lesson_selection_index.py
- scripts/changed_line_run_trust.py
- scripts/check-docs.sh
- scripts/check-python-lint.sh
- scripts/check-secrets.sh
- scripts/check-shell.sh
- scripts/check_artifact_referents.py
- scripts/check_artifact_surface_preflight.py
- scripts/check_boundary_bypass_ratchet.py  (DELETED — judge what depended on it)
- scripts/check_cli_skill_surface.py
- scripts/check_code_lengths.py
- scripts/check_command_dominance.py
- scripts/check_consumer_validator_catalog.py
- scripts/check_coverage_lib.py
- scripts/check_doc_links.py
- scripts/check_docs_graph.py
- scripts/check_documented_subcommands.py
- scripts/check_git_identity.py
- scripts/check_issue_closeout_commit_msg.py
- scripts/check_lesson_ledger.py
- scripts/check_mutation_run_proof.py
- scripts/check_mutation_suite_score.py
- scripts/check_prose_pin.py
- scripts/check_python_runtime_inheritance.py
- scripts/check_skill_ownership_overlap.allowlist.txt
- scripts/check_skill_surface_preflight.py
- scripts/check_spec_evidence_durability.py
- scripts/check_staged_reversion.py
- scripts/check_staged_router_change.py
- scripts/check_staged_test_boundaries.py
- scripts/check_staged_worktree_consistency.py
- scripts/check_standalone_imports.py
- scripts/check_subprocess_form.py
- scripts/check_supply_chain_online.py
- scripts/check_symbol_residue.py
- scripts/check_test_production_ratio.py
- scripts/check_upstream_support_drift.py
- scripts/classify_push_diff_lib.py
- scripts/classify_t_signal.py
- scripts/command_carrier_discovery.py
- scripts/command_plan_inputs.py
- scripts/command_plan_preflight.py
- scripts/control_plane_lib.py
- scripts/critique_artifact_paths.py
- scripts/critique_artifact_universe.py
- scripts/critique_packet_lib.py
- scripts/debug_persistence_lib.py
- scripts/doc_file_population.py
- scripts/dup_ratchet_edit_advisory.py
- scripts/eval_support_sync_contracts.py
- scripts/exported-copy-guard.sh
- scripts/git_status_snapshot.py
- scripts/install_provenance_lib.py
- scripts/inventory_boundary_bypass_lib.py
- scripts/inventory_cli_ergonomics_unavailable.py
- scripts/inventory_current_pointer_layouts.py
- scripts/inventory_gitignore_scan_hygiene_unavailable.py
- scripts/inventory_nose_clones_unavailable.py
- scripts/issue_source_capture_lib.py
- scripts/lesson_ledger_lib.py
- scripts/lesson_selection_preview_lib.py
- scripts/markdown_preview_bootstrap_lib.py
- scripts/markdownlint_probe.py
- scripts/mutate_and_restore.py
- scripts/mutation_changed_files_lib.py
- scripts/mutation_changed_line_diff.py
- scripts/mutation_coverage_producer.py
- scripts/mutation_recovery.py
- scripts/mutation_sampling_lib.py
- scripts/mutation_sampling_selection.py
- scripts/mutation_sweep_report.py
- scripts/native_gate_lib.py
- scripts/packaging_lib.py
- scripts/parity_harness.py
- scripts/premise_git_snapshot.py
- scripts/premise_tree_observation.py
- scripts/prepush_close_keyword_scan.py
- scripts/prepush_quality_receipt.py
- scripts/probe_record_parse.py
- scripts/probe_stimulus_replay.py
- scripts/quality_adapter_lib.py
- scripts/quality_artifact_skill_ergonomics.py
- scripts/quality_gate_provenance_fallback.py
- scripts/quality_label_universe.py
- scripts/quality_universes_lib.py
- scripts/recent_lesson_selection.py
- scripts/recent_lessons_lib.py
- scripts/release_changed_line_coverage.py
- scripts/release_changed_line_coverage_unavailable.py
- scripts/removed_name_consumers.py
- scripts/render_cli_reference.py
- scripts/render_lesson_selection_preview.py
- scripts/render_validator_timing_layers.py
- scripts/repo_file_listing.py
- scripts/resolve_artifact_path.py
- scripts/retro_output_dir_lib.py
- scripts/retro_persistence_lib.py
- scripts/reviewed_input_identity.py
- scripts/reviewed_input_nonblob.py
- scripts/run-quality.sh
- scripts/run_cosmic_ray_mutation.py
- scripts/run_js_mutation.py
- scripts/run_quality_engine.py
- scripts/run_quality_engine_model.py
- scripts/run_quality_engine_output.py
- scripts/run_quality_engine_phase.py
- scripts/run_quality_engine_receipt.py
- scripts/run_quality_engine_runtime.py
- scripts/run_quality_engine_selection.py
- scripts/run_specdown.py
- scripts/run_standing_pytest.py
- scripts/rust_changed_line_coverage.py
- scripts/sample_mutation_files.py
- scripts/setup_adapter_inspect_lib.py
- scripts/setup_inspect_quality_lib.py
- scripts/specdown_ephemeral_config.py
- scripts/staged_commit_gate_plan.py
- scripts/staged_commit_gate_plan_helpers.py
- scripts/standing_pytest_basetemp.py
- scripts/subprocess_guard.py
- scripts/subprocess_only_coverage_advisory.py
- scripts/surfaces_lib.py
- scripts/task_run.py
- scripts/task_run_execution.py
- scripts/task_run_git.py
- scripts/upstream_release_lib.py
- scripts/validate_adapters.py
- scripts/validate_critique_artifacts.py
- scripts/validate_ideation_artifact.py
- scripts/validate_inventory_consumption.py
- scripts/validate_maintainer_setup.py
- scripts/validate_packaging_install_surface.py
- scripts/validate_presets.py
- scripts/validate_quality_artifact.py
- scripts/waiver_file_lines.py
- scripts/worktree_audit_lib.py
- scripts/worktree_cleanup_lib.py
- scripts/worktree_create_lib.py
- scripts/worktree_doctor_checks.py
- scripts/worktree_doctor_lib.py
- scripts/worktree_doctor_manifest.py
- scripts/worktree_exec_lib.py
- skills/public/achieve/SKILL.md
- skills/public/achieve/scripts/goal_run_pickup.py
- skills/public/achieve/scripts/goal_run_pickup_lessons.py
- skills/public/announcement/scripts/collect_commits.py
- skills/public/announcement/scripts/infer_audience_tags.py
- skills/public/create-skill/references/portable-authoring.md
- skills/public/critique/references/code-critique.md
- skills/public/critique/scripts/run_review_support.py
- skills/public/critique/scripts/semantic_review_input.py
- skills/public/debug/references/sibling-search.md
- skills/public/gather/scripts/gather_public_execution.py
- skills/public/gather/scripts/gather_public_url.py
- skills/public/issue/scripts/issue_backend.py
- skills/public/issue/scripts/issue_closeout_classification_ledger.py
- skills/public/issue/scripts/issue_critique_observer_support.py
- skills/public/issue/scripts/issue_runtime.py
- skills/public/issue/scripts/issue_state_readback.py
- skills/public/issue/scripts/issue_verify_closeout.py
- skills/public/issue/scripts/issue_verify_closeout_authorization.py
- skills/public/issue/scripts/issue_verify_closeout_carrier.py
- skills/public/narrative/scripts/map_sources.py
- skills/public/quality/SKILL.md
- skills/public/quality/adapter.example.yaml
- skills/public/quality/references/adapter-contract.md
- skills/public/quality/references/attention-state-visibility.json
- skills/public/quality/references/boundary-bypass-payload.example.json  (DELETED — judge what depended on it)
- skills/public/quality/references/boundary-bypass-ratchet.md  (DELETED — judge what depended on it)
- skills/public/quality/references/catalog.yaml
- skills/public/quality/references/consumer-validator-catalog.yaml
- skills/public/quality/references/coverage-floor-policy.md
- skills/public/quality/references/index.md
- skills/public/quality/references/inventory-consumer-fields.json
- skills/public/quality/references/inventory-dispatch.md
- skills/public/quality/references/testability-and-selection.md
- skills/public/quality/references/validate_spec_pytest_references.py
- skills/public/quality/scripts/adapter_validators.py
- skills/public/quality/scripts/changed_line_coverage_gate_lib.py
- skills/public/quality/scripts/check_provenance_contract.py
- skills/public/quality/scripts/ci_local_gate_parity_lib.py
- skills/public/quality/scripts/cli_side_effect_probe_lib.py
- skills/public/quality/scripts/discovery_filter_scan_lib.py
- skills/public/quality/scripts/doc_duplicate_scan.py
- skills/public/quality/scripts/draft_dup_ratchet_triage.py
- skills/public/quality/scripts/dup_ratchet_git.py
- skills/public/quality/scripts/dup_ratchet_lib.py
- skills/public/quality/scripts/dup_ratchet_scan.py
- skills/public/quality/scripts/inventory_ci_local_gate_parity.py
- skills/public/quality/scripts/inventory_doc_duplicates.py
- skills/public/quality/scripts/inventory_empty_scope_honesty.py
- skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py
- skills/public/quality/scripts/inventory_sloc.py
- skills/public/quality/scripts/measure_startup_probes.py
- skills/public/quality/scripts/nose_tool_lib.py
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/pytest_temp_scan_lib.py
- skills/public/quality/scripts/quality_declaration_lifecycle.py
- skills/public/quality/scripts/quality_declared_gate_source.py
- skills/public/quality/scripts/quality_preset_reconciliation.py
- skills/public/quality/scripts/regenerable_facts_lib.py
- skills/public/quality/scripts/run_dead_code_advisory.py
- skills/public/quality/scripts/runtime_budget_universe_lib.py
- skills/public/quality/scripts/seed_dup_review.py
- skills/public/quality/scripts/standing_gate_discovery_lib.py
- skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py
- skills/public/quality/scripts/standing_gate_verbosity_lib.py
- skills/public/quality/scripts/standing_test_economics_lib.py
- skills/public/quality/scripts/test_discovery_lib.py
- skills/public/quality/scripts/validate_boundary_bypass_payload.py  (DELETED — judge what depended on it)
- skills/public/release/scripts/bump_version.py
- skills/public/release/scripts/check_fresh_checkout_probes.py
- skills/public/release/scripts/check_requested_review_gate.py
- skills/public/release/scripts/claims_review_scope.py
- skills/public/release/scripts/current_release.py
- skills/public/release/scripts/plan_release_prepared_stop.py
- skills/public/release/scripts/publish_release_adapter_preflight.py
- skills/public/release/scripts/publish_release_commands.py
- skills/public/release/scripts/publish_release_helpers.py
- skills/public/release/scripts/publish_release_preflight.py
- skills/public/release/scripts/publish_release_runtime.py
- skills/public/release/scripts/publish_release_scope.py
- skills/public/release/scripts/release_delta.py
- skills/public/retro/SKILL.md
- skills/public/retro/adapter.example.yaml
- skills/public/retro/references/waste-sibling-scan.md
- skills/public/retro/scripts/check_auto_trigger.py
- skills/public/retro/scripts/plan_retro_run.py
- skills/public/retro/scripts/retro_plan_reads.py
- skills/public/setup/references/greenfield-flow.md
- skills/public/setup/references/retro-memory-seam.md
- skills/public/setup/scripts/seed_worktree_adapter_lib.py
- skills/shared/references/binary-preflight.md
- skills/shared/scripts/authoring_script_shim.py
- skills/shared/scripts/reviewer_boundary_state.py
- skills/shared/scripts/reviewer_process.py
- skills/shared/scripts/reviewer_worker_runner_support.py
- skills/shared/scripts/run_reviewer_worker.py
- skills/shared/scripts/validate_skills.py
- skills/support/markdown-preview/scripts/markdown_preview_render.py
- skills/support/web-fetch/scripts/acquire_public_url_io.py
- tests/charness_cli/support.py
- tests/charness_cli/test_bootstrap_runtime.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/charness_cli/test_codex_managed_install.py
- tests/charness_cli/test_doctor_next_action.py
- tests/charness_cli/test_managed_install.py
- tests/charness_cli/test_managed_install_extended.py
- tests/charness_cli/test_managed_install_release_checks.py
- tests/charness_cli/test_task_run.py
- tests/charness_cli/test_task_run_lib_root.py
- tests/charness_cli/test_update_flow_unit.py
- tests/charness_cli/test_update_output.py
- tests/charness_cli/test_update_propagation.py
- tests/charness_cli/test_version_surface.py
- tests/charness_cli/test_worktree_audit.py
- tests/charness_cli/test_worktree_cleanup.py
- tests/charness_cli/test_worktree_create.py
- tests/charness_cli/test_worktree_doctor.py
- tests/charness_cli/test_worktree_exec.py
- tests/conftest.py
- tests/control_plane/support.py
- tests/control_plane/test_integrations_validation.py
- tests/control_plane/test_monorepo_layout.py
- tests/control_plane/test_upstream_release.py
- tests/control_plane/test_upstream_release_helpers.py
- tests/coverage_debt/test_batch3.py
- tests/coverage_debt/test_batch4.py
- tests/coverage_debt/test_batch5.py
- tests/coverage_debt/test_batch6.py
- tests/coverage_debt/test_batch8.py
- tests/quality_gates/fixtures/.agents/quality-gates.yaml
- tests/quality_gates/fixtures/consumer-quality-gates.yaml
- tests/quality_gates/fixtures/engine_gate.py
- tests/quality_gates/fixtures/quality-gates-engine.yaml
- tests/quality_gates/fixtures/scripts/run-quality.sh
- tests/quality_gates/inprocess_script_support.py
- tests/quality_gates/quality_runner_seed.py
- tests/quality_gates/release_publish_fixtures.py
- tests/quality_gates/support.py
- tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py
- tests/quality_gates/test_absent_input_is_not_a_matching_input.py
- tests/quality_gates/test_achieve_goal_run_pickup.py
- tests/quality_gates/test_argparse_surface_lib.py
- tests/quality_gates/test_artifact_naming.py
- tests/quality_gates/test_artifact_referents.py
- tests/quality_gates/test_attention_state_visibility.py
- tests/quality_gates/test_boundary_bypass_payload_validator.py  (DELETED — judge what depended on it)
- tests/quality_gates/test_changed_line_run_trust.py
- tests/quality_gates/test_check_artifact_surface_preflight.py
- tests/quality_gates/test_check_bootstrap_shim_consistency.py
- tests/quality_gates/test_check_coverage_inventory.py
- tests/quality_gates/test_check_git_identity.py
- tests/quality_gates/test_check_last_verified.py
- tests/quality_gates/test_check_mutation_run_proof.py
- tests/quality_gates/test_check_plugin_doc_links.py
- tests/quality_gates/test_check_prose_pin.py
- tests/quality_gates/test_check_public_doc_coupling.py
- tests/quality_gates/test_check_skill_cut_safety.py
- tests/quality_gates/test_check_staged_worktree_consistency.py
- tests/quality_gates/test_check_test_completeness.py
- tests/quality_gates/test_classify_push_diff.py
- tests/quality_gates/test_cli_skill_surface.py
- tests/quality_gates/test_closeout_authorization_ingress.py
- tests/quality_gates/test_code_length_gates.py
- tests/quality_gates/test_command_docs_gate.py
- tests/quality_gates/test_command_dominance.py
- tests/quality_gates/test_coverage_floor_inventory_reference.py
- tests/quality_gates/test_critique_boundary_ownership_presence.py
- tests/quality_gates/test_critique_delivery_state_floor.py
- tests/quality_gates/test_current_pointer_freshness.py
- tests/quality_gates/test_current_pointer_writers.py
- tests/quality_gates/test_current_pointer_writes.py
- tests/quality_gates/test_current_release_version_refusal.py
- tests/quality_gates/test_docs_and_misc.py
- tests/quality_gates/test_dup_ratchet_triage.py
- tests/quality_gates/test_dup_ratchet_triage_draft.py
- tests/quality_gates/test_dup_review_seed.py
- tests/quality_gates/test_empty_scope_refusals.py
- tests/quality_gates/test_every_resolver_answers_a_refused_document.py
- tests/quality_gates/test_export_self_sufficiency.py
- tests/quality_gates/test_gather_provider.py
- tests/quality_gates/test_gather_symlink_safety.py
- tests/quality_gates/test_goal_binding_v1.py
- tests/quality_gates/test_hitl_chunk_contract.py
- tests/quality_gates/test_inference_interpretation_meta_validator.py
- tests/quality_gates/test_inventory_ci_local_gate_parity.py
- tests/quality_gates/test_inventory_consumption.py
- tests/quality_gates/test_issue_closeout_commit_msg_hook.py
- tests/quality_gates/test_issue_read.py
- tests/quality_gates/test_issue_worker_carrier.py
- tests/quality_gates/test_js_mutation_tooling.py
- tests/quality_gates/test_maintainer_hooks.py
- tests/quality_gates/test_mutate_and_restore.py
- tests/quality_gates/test_mutate_and_restore_call_sites.py
- tests/quality_gates/test_mutation_baseline_abort.py
- tests/quality_gates/test_mutation_changed_line_targets.py
- tests/quality_gates/test_mutation_coverage_probe.py
- tests/quality_gates/test_mutation_coverage_producer.py
- tests/quality_gates/test_mutation_recovery.py
- tests/quality_gates/test_mutation_sampling_line_coverage.py
- tests/quality_gates/test_mutation_test_reporters.py
- tests/quality_gates/test_native_gate_lib.py
- tests/quality_gates/test_packaging_validation.py
- tests/quality_gates/test_parents_index_layout_invariant.py
- tests/quality_gates/test_parity_harness.py
- tests/quality_gates/test_plugin_asset_command_carriers.py
- tests/quality_gates/test_premise_preflight.py
- tests/quality_gates/test_prepush_close_keyword_guard.py
- tests/quality_gates/test_prepush_runtime_regime.py
- tests/quality_gates/test_prescribed_skill_executed.py
- tests/quality_gates/test_profile_and_preset_validation.py
- tests/quality_gates/test_public_skill_yaml_output_contract.py
- tests/quality_gates/test_python_and_security_gates.py
- tests/quality_gates/test_quality_bootstrap_absence.py
- tests/quality_gates/test_quality_bootstrap_absence_paths.py
- tests/quality_gates/test_quality_declaration_path_resolution.py
- tests/quality_gates/test_quality_doc_duplicates.py
- tests/quality_gates/test_quality_dual_implementation.py
- tests/quality_gates/test_quality_gate_list_fixture_parity.py
- tests/quality_gates/test_quality_gitignore_scan_hygiene.py
- tests/quality_gates/test_quality_markdown_preview_bootstrap.py
- tests/quality_gates/test_quality_mutation_coverage.py
- tests/quality_gates/test_quality_mutation_sampling.py
- tests/quality_gates/test_quality_mutation_testing.py
- tests/quality_gates/test_quality_policy_merge_import.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_quality_run_planner_declared.py
- tests/quality_gates/test_quality_runner.py
- tests/quality_gates/test_quality_runner_coverage_selection.py
- tests/quality_gates/test_quality_runner_exit_status.py
- tests/quality_gates/test_quality_runner_label_universe.py
- tests/quality_gates/test_quality_runner_progress.py
- tests/quality_gates/test_quality_runner_release_order.py
- tests/quality_gates/test_quality_runner_runtime_aggregate.py
- tests/quality_gates/test_quality_runner_unproven.py
- tests/quality_gates/test_quality_runtime_recorder.py
- tests/quality_gates/test_quality_skill_docs.py
- tests/quality_gates/test_quality_standing_gate_verbosity.py
- tests/quality_gates/test_quality_tool_fixtures.py
- tests/quality_gates/test_quality_tool_recommendations.py
- tests/quality_gates/test_quality_universes.py
- tests/quality_gates/test_release_changed_line_coverage.py
- tests/quality_gates/test_release_fresh_checkout_probes.py
- tests/quality_gates/test_release_issue_closeout_preflight.py
- tests/quality_gates/test_release_only_sentinel_inventory.py
- tests/quality_gates/test_release_planner_version_refusal.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_release_publish_post_create.py
- tests/quality_gates/test_release_publish_provenance.py
- tests/quality_gates/test_release_publish_requested_review.py
- tests/quality_gates/test_release_publish_rollback.py
- tests/quality_gates/test_release_publish_tag_history.py
- tests/quality_gates/test_release_quality_status_binding.py
- tests/quality_gates/test_release_run_planner.py
- tests/quality_gates/test_release_run_planner_prepared_stop.py
- tests/quality_gates/test_repo_copy_invariants.py
- tests/quality_gates/test_retro_artifact_validation.py
- tests/quality_gates/test_retro_auto_trigger.py
- tests/quality_gates/test_retro_installed_plan_path.py
- tests/quality_gates/test_retro_lesson_selection_index.py
- tests/quality_gates/test_retro_memory.py
- tests/quality_gates/test_retro_persistence.py
- tests/quality_gates/test_reviewer_runner.py
- tests/quality_gates/test_reviewer_worker.py
- tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py
- tests/quality_gates/test_run_quality_engine.py
- tests/quality_gates/test_runtime_budget_universe.py
- tests/quality_gates/test_s6_changed_line_gaps.py
- tests/quality_gates/test_s6b2_changed_line_gaps.py
- tests/quality_gates/test_scaffold_claims_review.py
- tests/quality_gates/test_scaffold_version_refusal.py
- tests/quality_gates/test_script_inprocess_behaviors.py
- tests/quality_gates/test_seed_worktree_adapter.py
- tests/quality_gates/test_semantic_review_command.py
- tests/quality_gates/test_setup_hook_failure_guidance.py
- tests/quality_gates/test_setup_inspect_adapters.py
- tests/quality_gates/test_setup_inspect_policy.py
- tests/quality_gates/test_setup_retro_memory.py
- tests/quality_gates/test_shared_script_gate_scope.py
- tests/quality_gates/test_shell_gate_root_resolution.py
- tests/quality_gates/test_skill_bootstrap_vars.py
- tests/quality_gates/test_skill_contracts_validation.py
- tests/quality_gates/test_skill_docs_contracts.py
- tests/quality_gates/test_skill_ergonomics_gate.py
- tests/quality_gates/test_skill_reference_index.py
- tests/quality_gates/test_skill_surface_preflight.py
- tests/quality_gates/test_skill_validation.py
- tests/quality_gates/test_specdown_ephemeral_config.py
- tests/quality_gates/test_staged_commit_gate_plan.py
- tests/quality_gates/test_staged_test_boundaries.py
- tests/quality_gates/test_standalone_imports.py
- tests/quality_gates/test_standing_pytest_run_execution.py
- tests/quality_gates/test_standing_pytest_runner.py
- tests/quality_gates/test_subprocess_form_gate.py
- tests/quality_gates/test_subprocess_only_coverage_advisory.py
- tests/quality_gates/test_surface_obligations.py
- tests/quality_gates/test_test_production_ratio.py
- tests/quality_gates/test_timing_layer_completeness.py
- tests/quality_gates/test_u2_doc_artifact_universes.py
- tests/quality_gates/test_universe_consumers.py
- tests/quality_gates/test_unreferenced_scripts.py
- tests/test_achieve_lesson_citation.py
- tests/test_adversarial_evidence.py
- tests/test_agent_browser_runtime_guard.py
- tests/test_announcement_delivery_verification.py
- tests/test_authoring_preflight_reference.py
- tests/test_boundary_bypass_ratchet.py  (DELETED — judge what depended on it)
- tests/test_changed_path_enumerator_agreement.py
- tests/test_classify_t_signal.py
- tests/test_closeout_classification_parity.py
- tests/test_committed_packet_refusal.py
- tests/test_consumer_validator_catalog.py
- tests/test_critique_section_changed_surfaces.py
- tests/test_critique_verify_packet.py
- tests/test_debug_artifact.py
- tests/test_debug_artifact_scope.py
- tests/test_debug_persistence.py
- tests/test_degradation_branch_coverage.py
- tests/test_doc_duplicates_inprocess_coverage.py
- tests/test_docs_graph_gate.py
- tests/test_evidence_boundary_crosswalk.py
- tests/test_gather_plan.py
- tests/test_impl_survey_verification.py
- tests/test_inventory_marker_rule_measurement.py
- tests/test_issue_source_capture.py
- tests/test_lesson_ledger.py
- tests/test_lesson_ledger_refusals.py
- tests/test_lesson_lifecycle.py
- tests/test_lesson_selection_preview.py
- tests/test_list_external_links.py
- tests/test_markdown_preview_support.py
- tests/test_public_skill_dogfood.py
- tests/test_public_skill_validation.py
- tests/test_quality_delegated_review.py
- tests/test_retro_help.py
- tests/test_reviewed_input_identity_binding.py
- tests/test_reviewed_input_nonblob_binding.py
- tests/test_scaffold_inprocess_coverage.py
- tests/test_script_timeout.py
- tests/test_seed_lesson_transitions.py
- tests/test_shared_authoring_script_shims.py
- tests/test_skill_anchor_guard_hook.py
- tests/test_skill_script_references.py
- tests/test_subprocess_guard.py
- tests/test_supply_chain_online.py
- tests/test_twitter_exact_source.py
- tests/test_unhappy_path_branches.py
- tests/test_validate_adapters_integration_schema.py
- tests/test_validate_critique_artifacts_dates.py
- tests/test_web_fetch_cleanup.py
- tests/test_web_fetch_content_persistence.py
- tests/test_web_fetch_route_and_classify.py
- tests/test_web_fetch_support.py
- tests/test_web_fetch_trace_quality.py
- tests/test_write_artifact_path_single_owner.py
- tools/__init__.py
- tools/check_bootstrap_shim_consistency.py
- tools/check_closeout_classification_parity.py
- tools/check_consumer_validator_catalog_decisions.py
- tools/check_coverage.py
- tools/check_coverage_extra_lib.py
- tools/check_current_pointer_writes.py
- tools/check_export_self_sufficiency.py
- tools/check_inventory_declaration_coverage.py
- tools/check_last_verified.py
- tools/check_plugin_asset_command_carriers.py
- tools/check_plugin_doc_links.py
- tools/check_plugin_import_smoke.py
- tools/check_public_doc_coupling.py
- tools/check_quality_tool_fixtures.py
- tools/check_references_link_inventory.py
- tools/check_runtime_budget_universe.py
- tools/check_skill_bootstrap_vars.py
- tools/check_skill_contracts.py
- tools/check_skill_cut_safety.py
- tools/check_timing_layer_completeness.py
- tools/check_unreferenced_scripts.py
- tools/eval_issue_scenarios.py
- tools/eval_registry.py
- tools/eval_setup.py
- tools/export_self_sufficiency_lib.py
- tools/export_tools_reference_lib.py
- tools/inventory_skill_script_references.py
- tools/public_skill_dogfood_validation_lib.py
- tools/quality_gates_extract.py
- tools/run_evals.py
- tools/skill_portability_lib.py
- tools/suggest_public_skill_validation.py
- tools/validate_attention_state_visibility.py
- tools/validate_current_pointer_freshness.py
- tools/validate_inference_interpretation.py
- tools/validate_integrations.py
- tools/validate_inventory_consumption_declaration.py
- tools/validate_packaging_committed.py
- tools/validate_profiles.py
- tools/validate_public_skill_dogfood.py
- tools/validate_public_skill_validation.py
- tools/validate_quality_closeout_contract.py
- tools/validate_quality_reference_catalog.py
- tools/validate_skills.py
- tools/validate_surfaces.py

10 of 649 changed path(s) were DELETED in the ref `a5002ffc9..HEAD`. Their pre-image bytes are bound in the reviewed-input identity, so what was removed is recoverable.

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: README.md, integrations/tools/awiki.json, profiles/README.md, scripts/announcement_verification_lib.py, scripts/artifact_referents.py, scripts/artifact_run_scope.py, scripts/artifact_shape_source.py, scripts/bootstrap_runtime.py, scripts/boundary-bypass-baseline.json, scripts/boundary-bypass-exemptions.txt, scripts/boundary_bypass_ratchet_lib.py, scripts/build_retro_lesson_selection_index.py, scripts/changed_line_run_trust.py, scripts/check-docs.sh, scripts/check-python-lint.sh, scripts/check-secrets.sh, scripts/check-shell.sh, scripts/check_artifact_referents.py, scripts/check_artifact_surface_preflight.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_cli_skill_surface.py, scripts/check_code_lengths.py, scripts/check_command_dominance.py, scripts/check_consumer_validator_catalog.py, scripts/check_coverage_lib.py, scripts/check_doc_links.py, scripts/check_docs_graph.py, scripts/check_documented_subcommands.py, scripts/check_git_identity.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_lesson_ledger.py, scripts/check_mutation_run_proof.py, scripts/check_mutation_suite_score.py, scripts/check_prose_pin.py, scripts/check_python_runtime_inheritance.py, scripts/check_skill_ownership_overlap.allowlist.txt, scripts/check_skill_surface_preflight.py, scripts/check_spec_evidence_durability.py, scripts/check_staged_reversion.py, scripts/check_staged_router_change.py, scripts/check_staged_test_boundaries.py, scripts/check_staged_worktree_consistency.py, scripts/check_standalone_imports.py, scripts/check_subprocess_form.py, scripts/check_supply_chain_online.py, scripts/check_symbol_residue.py, scripts/check_test_production_ratio.py, scripts/check_upstream_support_drift.py, scripts/classify_push_diff_lib.py, scripts/classify_t_signal.py, scripts/command_carrier_discovery.py, scripts/command_plan_inputs.py, scripts/command_plan_preflight.py, scripts/control_plane_lib.py, scripts/critique_artifact_paths.py, scripts/critique_artifact_universe.py, scripts/critique_packet_lib.py, scripts/debug_persistence_lib.py, scripts/doc_file_population.py, scripts/dup_ratchet_edit_advisory.py, scripts/eval_support_sync_contracts.py, scripts/exported-copy-guard.sh, scripts/git_status_snapshot.py, scripts/install_provenance_lib.py, scripts/inventory_boundary_bypass_lib.py, scripts/inventory_cli_ergonomics_unavailable.py, scripts/inventory_current_pointer_layouts.py, scripts/inventory_gitignore_scan_hygiene_unavailable.py, scripts/inventory_nose_clones_unavailable.py, scripts/issue_source_capture_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_preview_bootstrap_lib.py, scripts/markdownlint_probe.py, scripts/mutate_and_restore.py, scripts/mutation_changed_files_lib.py, scripts/mutation_changed_line_diff.py, scripts/mutation_coverage_producer.py, scripts/mutation_recovery.py, scripts/mutation_sampling_lib.py, scripts/mutation_sampling_selection.py, scripts/mutation_sweep_report.py, scripts/native_gate_lib.py, scripts/packaging_lib.py, scripts/parity_harness.py, scripts/premise_git_snapshot.py, scripts/premise_tree_observation.py, scripts/prepush_close_keyword_scan.py, scripts/prepush_quality_receipt.py, scripts/probe_record_parse.py, scripts/probe_stimulus_replay.py, scripts/quality_adapter_lib.py, scripts/quality_artifact_skill_ergonomics.py, scripts/quality_gate_provenance_fallback.py, scripts/quality_label_universe.py, scripts/quality_universes_lib.py, scripts/recent_lesson_selection.py, scripts/recent_lessons_lib.py, scripts/release_changed_line_coverage.py, scripts/release_changed_line_coverage_unavailable.py, scripts/removed_name_consumers.py, scripts/render_cli_reference.py, scripts/render_lesson_selection_preview.py, scripts/render_validator_timing_layers.py, scripts/repo_file_listing.py, scripts/resolve_artifact_path.py, scripts/retro_output_dir_lib.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/reviewed_input_nonblob.py, scripts/run-quality.sh, scripts/run_cosmic_ray_mutation.py, scripts/run_js_mutation.py, scripts/run_quality_engine.py, scripts/run_quality_engine_model.py, scripts/run_quality_engine_output.py, scripts/run_quality_engine_phase.py, scripts/run_quality_engine_receipt.py, scripts/run_quality_engine_runtime.py, scripts/run_quality_engine_selection.py, scripts/run_specdown.py, scripts/run_standing_pytest.py, scripts/rust_changed_line_coverage.py, scripts/sample_mutation_files.py, scripts/setup_adapter_inspect_lib.py, scripts/setup_inspect_quality_lib.py, scripts/specdown_ephemeral_config.py, scripts/staged_commit_gate_plan.py, scripts/staged_commit_gate_plan_helpers.py, scripts/standing_pytest_basetemp.py, scripts/subprocess_guard.py, scripts/subprocess_only_coverage_advisory.py, scripts/surfaces_lib.py, scripts/task_run.py, scripts/task_run_execution.py, scripts/task_run_git.py, scripts/upstream_release_lib.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_maintainer_setup.py, scripts/validate_packaging_install_surface.py, scripts/validate_presets.py, scripts/validate_quality_artifact.py, scripts/waiver_file_lines.py, scripts/worktree_audit_lib.py, scripts/worktree_cleanup_lib.py, scripts/worktree_create_lib.py, scripts/worktree_doctor_checks.py, scripts/worktree_doctor_lib.py, scripts/worktree_doctor_manifest.py, scripts/worktree_exec_lib.py, skills/public/achieve/SKILL.md, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_lessons.py, skills/public/announcement/scripts/collect_commits.py, skills/public/announcement/scripts/infer_audience_tags.py, skills/public/create-skill/references/portable-authoring.md, skills/public/critique/references/code-critique.md, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/debug/references/sibling-search.md, skills/public/gather/scripts/gather_public_execution.py, skills/public/gather/scripts/gather_public_url.py, skills/public/issue/scripts/issue_backend.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_runtime.py, skills/public/issue/scripts/issue_state_readback.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_authorization.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/narrative/scripts/map_sources.py, skills/public/quality/SKILL.md, skills/public/quality/adapter.example.yaml, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/coverage-floor-policy.md, skills/public/quality/references/index.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/testability-and-selection.md, skills/public/quality/references/validate_spec_pytest_references.py, skills/public/quality/scripts/adapter_validators.py, skills/public/quality/scripts/changed_line_coverage_gate_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/cli_side_effect_probe_lib.py, skills/public/quality/scripts/discovery_filter_scan_lib.py, skills/public/quality/scripts/doc_duplicate_scan.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/dup_ratchet_git.py, skills/public/quality/scripts/dup_ratchet_lib.py, skills/public/quality/scripts/dup_ratchet_scan.py, skills/public/quality/scripts/inventory_ci_local_gate_parity.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py, skills/public/quality/scripts/inventory_sloc.py, skills/public/quality/scripts/measure_startup_probes.py, skills/public/quality/scripts/nose_tool_lib.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/pytest_temp_scan_lib.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_declared_gate_source.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/regenerable_facts_lib.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/runtime_budget_universe_lib.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/standing_gate_discovery_lib.py, skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/test_discovery_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/bump_version.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/claims_review_scope.py, skills/public/release/scripts/current_release.py, skills/public/release/scripts/plan_release_prepared_stop.py, skills/public/release/scripts/publish_release_adapter_preflight.py, skills/public/release/scripts/publish_release_commands.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/publish_release_scope.py, skills/public/release/scripts/release_delta.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/waste-sibling-scan.md, skills/public/retro/scripts/check_auto_trigger.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/setup/references/greenfield-flow.md, skills/public/setup/references/retro-memory-seam.md, skills/public/setup/scripts/seed_worktree_adapter_lib.py, skills/shared/references/binary-preflight.md, skills/shared/scripts/authoring_script_shim.py, skills/shared/scripts/reviewer_boundary_state.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/run_reviewer_worker.py, skills/shared/scripts/validate_skills.py, skills/support/markdown-preview/scripts/markdown_preview_render.py, skills/support/web-fetch/scripts/acquire_public_url_io.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: README.md, charness-artifacts/critique/2026-09-02-769-boundary-packet.md, charness-artifacts/goal-runs/765/2026-09-02-session-record.md, charness-artifacts/goal-runs/765/bodies/ledger-only-lessons.md, charness-artifacts/goal-runs/765/bodies/parent-amended-774.md, charness-artifacts/goal-runs/765/bodies/parent-progress-768.md, charness-artifacts/goal-runs/765/bodies/parent-progress-769.md, charness-artifacts/goal-runs/765/briefs/brief-768-production.md, charness-artifacts/goal-runs/765/briefs/brief-768-ratchet.md, charness-artifacts/goal-runs/765/briefs/brief-768-repair.md, charness-artifacts/goal-runs/765/briefs/brief-768-tests.md, charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md, charness-artifacts/goal-runs/765/briefs/brief-769-r2a-runner-lib.md, charness-artifacts/goal-runs/765/briefs/brief-769-r2b-wire-runner.md, charness-artifacts/goal-runs/765/briefs/brief-769-r3-native-reader.md, charness-artifacts/goal-runs/765/briefs/brief-769-s-consumer-scope.md, charness-artifacts/goal-runs/765/briefs/brief-769-t1-tools-tree.md, charness-artifacts/goal-runs/765/briefs/brief-769-t2-tools-batch-b.md, charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md, charness-artifacts/goal-runs/765/briefs/brief-769-u0-universes.md, charness-artifacts/goal-runs/765/briefs/brief-769-u1-sources.md, charness-artifacts/goal-runs/765/briefs/brief-769-u2-docs-artifacts.md, charness-artifacts/goal-runs/765/briefs/brief-769-u3-scanners-configs.md, charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md, charness-artifacts/goal-runs/765/briefs/brief-770-p0-foundation.md, charness-artifacts/goal-runs/765/briefs/brief-770-p1-core-gates.md, charness-artifacts/goal-runs/765/briefs/brief-770-p2-mutation-worktree-hooks.md, charness-artifacts/goal-runs/765/briefs/brief-770-p3-review-lessons-adapters.md, charness-artifacts/goal-runs/765/briefs/brief-770-p4-remaining.md, charness-artifacts/goal-runs/765/briefs/design-critique-769.md, charness-artifacts/goal-runs/765/briefs/map-769-conditional.md, charness-artifacts/goal-runs/765/briefs/map-769-export.md, charness-artifacts/goal-runs/765/briefs/map-769-runner.md, charness-artifacts/goal-runs/765/briefs/map-770.md, charness-artifacts/goal-runs/765/briefs/map-772.md, charness-artifacts/quality/2026-09-02-gate-classification-769.md, charness-artifacts/retro/2026-09-02-session-retro.md, charness-artifacts/retro/recent-lessons.md, docs/artifact-policy.md, docs/authoring-preflight.md, docs/deferred-decisions.md, docs/development.md, docs/export-boundary.md, docs/external-integrations.md, docs/index.md, docs/operator-acceptance.md, docs/provenance-placement.md, docs/public-skill-dogfood.md, docs/public-skill-validation.md, docs/validator-timing-layers.md, evals/README.md, skills/public/achieve/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/critique/references/code-critique.md, skills/public/debug/references/sibling-search.md, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/coverage-floor-policy.md, skills/public/quality/references/index.md, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/testability-and-selection.md, skills/public/retro/SKILL.md, skills/public/retro/references/waste-sibling-scan.md, skills/public/setup/references/greenfield-flow.md, skills/public/setup/references/retro-memory-seam.md, skills/shared/references/binary-preflight.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/quality/2026-09-02-gate-classification-769.md
  verify: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/validate_quality_artifact.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_lessons.py, skills/public/announcement/scripts/collect_commits.py, skills/public/announcement/scripts/infer_audience_tags.py, skills/public/create-skill/references/portable-authoring.md, skills/public/critique/references/code-critique.md, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/debug/references/sibling-search.md, skills/public/gather/scripts/gather_public_execution.py, skills/public/gather/scripts/gather_public_url.py, skills/public/issue/scripts/issue_backend.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_runtime.py, skills/public/issue/scripts/issue_state_readback.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_authorization.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/narrative/scripts/map_sources.py, skills/public/quality/SKILL.md, skills/public/quality/adapter.example.yaml, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/coverage-floor-policy.md, skills/public/quality/references/index.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/testability-and-selection.md, skills/public/quality/references/validate_spec_pytest_references.py, skills/public/quality/scripts/adapter_validators.py, skills/public/quality/scripts/changed_line_coverage_gate_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/cli_side_effect_probe_lib.py, skills/public/quality/scripts/discovery_filter_scan_lib.py, skills/public/quality/scripts/doc_duplicate_scan.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/dup_ratchet_git.py, skills/public/quality/scripts/dup_ratchet_lib.py, skills/public/quality/scripts/dup_ratchet_scan.py, skills/public/quality/scripts/inventory_ci_local_gate_parity.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py, skills/public/quality/scripts/inventory_sloc.py, skills/public/quality/scripts/measure_startup_probes.py, skills/public/quality/scripts/nose_tool_lib.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/pytest_temp_scan_lib.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_declared_gate_source.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/regenerable_facts_lib.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/runtime_budget_universe_lib.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/standing_gate_discovery_lib.py, skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/test_discovery_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/bump_version.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/claims_review_scope.py, skills/public/release/scripts/current_release.py, skills/public/release/scripts/plan_release_prepared_stop.py, skills/public/release/scripts/publish_release_adapter_preflight.py, skills/public/release/scripts/publish_release_commands.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/publish_release_scope.py, skills/public/release/scripts/release_delta.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/waste-sibling-scan.md, skills/public/retro/scripts/check_auto_trigger.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/setup/references/greenfield-flow.md, skills/public/setup/references/retro-memory-seam.md, skills/public/setup/scripts/seed_worktree_adapter_lib.py, skills/shared/references/binary-preflight.md, skills/shared/scripts/authoring_script_shim.py, skills/shared/scripts/reviewer_boundary_state.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/run_reviewer_worker.py, skills/shared/scripts/validate_skills.py, skills/support/markdown-preview/scripts/markdown_preview_render.py, skills/support/web-fetch/scripts/acquire_public_url_io.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 -m tools.validate_current_pointer_freshness --repo-root ., python3 -m json.tool .agents/surfaces.json
- consumer-validator-catalog: Explicit packaged consumer-validator inventory, adoption decisions, and the installed/source-layout checker that enforces the contract.
  source matches: .agents/consumer-validator-adoption.yaml, scripts/check_consumer_validator_catalog.py, scripts/packaging_lib.py, scripts/run-quality.sh, scripts/staged_commit_gate_plan.py, skills/public/quality/references/consumer-validator-catalog.yaml
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_consumer_validator_catalog.py --repo-root . --adoption-path .agents/consumer-validator-adoption.yaml --require-adoption, python3 -m pytest -q tests/test_consumer_validator_catalog.py tests/test_capability_catalog.py
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: docs/public-skill-validation.md, skills/public/achieve/SKILL.md, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_lessons.py, skills/public/announcement/scripts/collect_commits.py, skills/public/announcement/scripts/infer_audience_tags.py, skills/public/create-skill/references/portable-authoring.md, skills/public/critique/references/code-critique.md, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/debug/references/sibling-search.md, skills/public/gather/scripts/gather_public_execution.py, skills/public/gather/scripts/gather_public_url.py, skills/public/issue/scripts/issue_backend.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_runtime.py, skills/public/issue/scripts/issue_state_readback.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_authorization.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/narrative/scripts/map_sources.py, skills/public/quality/SKILL.md, skills/public/quality/adapter.example.yaml, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/coverage-floor-policy.md, skills/public/quality/references/index.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/testability-and-selection.md, skills/public/quality/references/validate_spec_pytest_references.py, skills/public/quality/scripts/adapter_validators.py, skills/public/quality/scripts/changed_line_coverage_gate_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/cli_side_effect_probe_lib.py, skills/public/quality/scripts/discovery_filter_scan_lib.py, skills/public/quality/scripts/doc_duplicate_scan.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/dup_ratchet_git.py, skills/public/quality/scripts/dup_ratchet_lib.py, skills/public/quality/scripts/dup_ratchet_scan.py, skills/public/quality/scripts/inventory_ci_local_gate_parity.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py, skills/public/quality/scripts/inventory_sloc.py, skills/public/quality/scripts/measure_startup_probes.py, skills/public/quality/scripts/nose_tool_lib.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/pytest_temp_scan_lib.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_declared_gate_source.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/regenerable_facts_lib.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/runtime_budget_universe_lib.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/standing_gate_discovery_lib.py, skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/test_discovery_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/bump_version.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/claims_review_scope.py, skills/public/release/scripts/current_release.py, skills/public/release/scripts/plan_release_prepared_stop.py, skills/public/release/scripts/publish_release_adapter_preflight.py, skills/public/release/scripts/publish_release_commands.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/publish_release_scope.py, skills/public/release/scripts/release_delta.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/waste-sibling-scan.md, skills/public/retro/scripts/check_auto_trigger.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/setup/references/greenfield-flow.md, skills/public/setup/references/retro-memory-seam.md, skills/public/setup/scripts/seed_worktree_adapter_lib.py, skills/shared/references/binary-preflight.md, skills/shared/scripts/authoring_script_shim.py, skills/shared/scripts/reviewer_boundary_state.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/run_reviewer_worker.py, skills/shared/scripts/validate_skills.py, tools/suggest_public_skill_validation.py, tools/validate_public_skill_validation.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, docs/public-skill-dogfood.md, skills/public/achieve/SKILL.md, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_lessons.py, skills/public/announcement/scripts/collect_commits.py, skills/public/announcement/scripts/infer_audience_tags.py, skills/public/create-skill/references/portable-authoring.md, skills/public/critique/references/code-critique.md, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/debug/references/sibling-search.md, skills/public/gather/scripts/gather_public_execution.py, skills/public/gather/scripts/gather_public_url.py, skills/public/issue/scripts/issue_backend.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_runtime.py, skills/public/issue/scripts/issue_state_readback.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_authorization.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/narrative/scripts/map_sources.py, skills/public/quality/SKILL.md, skills/public/quality/adapter.example.yaml, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/coverage-floor-policy.md, skills/public/quality/references/index.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/testability-and-selection.md, skills/public/quality/references/validate_spec_pytest_references.py, skills/public/quality/scripts/adapter_validators.py, skills/public/quality/scripts/changed_line_coverage_gate_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/cli_side_effect_probe_lib.py, skills/public/quality/scripts/discovery_filter_scan_lib.py, skills/public/quality/scripts/doc_duplicate_scan.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/dup_ratchet_git.py, skills/public/quality/scripts/dup_ratchet_lib.py, skills/public/quality/scripts/dup_ratchet_scan.py, skills/public/quality/scripts/inventory_ci_local_gate_parity.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py, skills/public/quality/scripts/inventory_sloc.py, skills/public/quality/scripts/measure_startup_probes.py, skills/public/quality/scripts/nose_tool_lib.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/pytest_temp_scan_lib.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_declared_gate_source.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/regenerable_facts_lib.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/runtime_budget_universe_lib.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/standing_gate_discovery_lib.py, skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/test_discovery_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/bump_version.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/claims_review_scope.py, skills/public/release/scripts/current_release.py, skills/public/release/scripts/plan_release_prepared_stop.py, skills/public/release/scripts/publish_release_adapter_preflight.py, skills/public/release/scripts/publish_release_commands.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/publish_release_scope.py, skills/public/release/scripts/release_delta.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/waste-sibling-scan.md, skills/public/retro/scripts/check_auto_trigger.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/setup/references/greenfield-flow.md, skills/public/setup/references/retro-memory-seam.md, skills/public/setup/scripts/seed_worktree_adapter_lib.py, skills/shared/references/binary-preflight.md, skills/shared/scripts/authoring_script_shim.py, skills/shared/scripts/reviewer_boundary_state.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/run_reviewer_worker.py, skills/shared/scripts/validate_skills.py, tools/validate_public_skill_dogfood.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- profiles-and-presets: Profile and preset bundles that define packaged defaults.
  source matches: profiles/README.md
  verify: python3 -m tools.validate_profiles --repo-root ., python3 scripts/validate_presets.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/quality-adapter.yaml, .agents/retro-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- cli-side-effect-probes: Repo-owned mutating CLI probe contract for no-side-effect help, option-looking positional rejection, dry-run or waiver, and watched side-effect seams.
  source matches: skills/public/quality/scripts/cli_side_effect_probe_lib.py
  verify: python3 skills/public/quality/scripts/inventory_cli_side_effect_probes.py --repo-root . --fail-on-findings
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 -m tools.validate_surfaces --repo-root .
- export-self-sufficiency: Whether the materialized plugin export can run on a machine that has only the export: shipped dependency contract, and repo-root paths exported modules read.
  source matches: scripts/packaging_lib.py, skills/public/gather/scripts/gather_public_url.py, tools/check_export_self_sufficiency.py, tools/export_self_sufficiency_lib.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m tools.check_export_self_sufficiency --repo-root ., python3 -m pytest -q tests/quality_gates/test_export_self_sufficiency.py
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: .agents/quality-adapter.yaml, scripts/check_mutation_suite_score.py, scripts/mutation_coverage_producer.py, scripts/mutation_sampling_lib.py, scripts/run_cosmic_ray_mutation.py, scripts/run_js_mutation.py, scripts/sample_mutation_files.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 -m pytest -q tests/quality_gates/test_coverage_builder_policy_parity.py, python3 scripts/check_github_actions.py --repo-root ., python3 scripts/validate_adapters.py --repo-root ., python3 scripts/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- quality-core-workflow: Repo-local light push/tag CI; expensive mutation coverage remains outside the push/PR workflow.
  source matches: .github/workflows/quality-core.yml
  verify: python3 scripts/check_github_actions.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-09-02-769-boundary-packet.json, charness-artifacts/critique/2026-09-02-769-boundary-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-09-02-session-retro.md, charness-artifacts/retro/recent-lessons.md, scripts/build_retro_lesson_selection_index.py, scripts/recent_lessons_lib.py, scripts/retro_persistence_lib.py
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-selection: Local cited lesson history and its pure selection projections.
  source matches: charness-artifacts/retro/lesson-ledger.json, scripts/check_lesson_ledger.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_selection_preview.py
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: integrations/tools/awiki.json, scripts/control_plane_lib.py, scripts/install_provenance_lib.py, scripts/upstream_release_lib.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/tools/awiki.json, scripts/control_plane_lib.py, scripts/install_provenance_lib.py, scripts/upstream_release_lib.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- maintainer-hooks: Repo-owned maintainer hook and hook bootstrap validation.
  source matches: .githooks/pre-commit, .githooks/pre-push, scripts/validate_maintainer_setup.py
  verify: python3 scripts/validate_maintainer_setup.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: charness, pyproject.toml, scripts/announcement_verification_lib.py, scripts/artifact_referents.py, scripts/artifact_run_scope.py, scripts/artifact_shape_source.py, scripts/bootstrap_runtime.py, scripts/boundary_bypass_ratchet_lib.py, scripts/build_retro_lesson_selection_index.py, scripts/changed_line_run_trust.py, scripts/check_artifact_referents.py, scripts/check_artifact_surface_preflight.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_cli_skill_surface.py, scripts/check_code_lengths.py, scripts/check_command_dominance.py, scripts/check_consumer_validator_catalog.py, scripts/check_coverage_lib.py, scripts/check_doc_links.py, scripts/check_docs_graph.py, scripts/check_documented_subcommands.py, scripts/check_git_identity.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_lesson_ledger.py, scripts/check_mutation_run_proof.py, scripts/check_mutation_suite_score.py, scripts/check_prose_pin.py, scripts/check_python_runtime_inheritance.py, scripts/check_skill_surface_preflight.py, scripts/check_spec_evidence_durability.py, scripts/check_staged_reversion.py, scripts/check_staged_router_change.py, scripts/check_staged_test_boundaries.py, scripts/check_staged_worktree_consistency.py, scripts/check_standalone_imports.py, scripts/check_subprocess_form.py, scripts/check_supply_chain_online.py, scripts/check_symbol_residue.py, scripts/check_test_production_ratio.py, scripts/check_upstream_support_drift.py, scripts/classify_push_diff_lib.py, scripts/classify_t_signal.py, scripts/command_carrier_discovery.py, scripts/command_plan_inputs.py, scripts/command_plan_preflight.py, scripts/control_plane_lib.py, scripts/critique_artifact_paths.py, scripts/critique_artifact_universe.py, scripts/critique_packet_lib.py, scripts/debug_persistence_lib.py, scripts/doc_file_population.py, scripts/dup_ratchet_edit_advisory.py, scripts/eval_support_sync_contracts.py, scripts/git_status_snapshot.py, scripts/install_provenance_lib.py, scripts/inventory_boundary_bypass_lib.py, scripts/inventory_cli_ergonomics_unavailable.py, scripts/inventory_current_pointer_layouts.py, scripts/inventory_gitignore_scan_hygiene_unavailable.py, scripts/inventory_nose_clones_unavailable.py, scripts/issue_source_capture_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_preview_bootstrap_lib.py, scripts/markdownlint_probe.py, scripts/mutate_and_restore.py, scripts/mutation_changed_files_lib.py, scripts/mutation_changed_line_diff.py, scripts/mutation_coverage_producer.py, scripts/mutation_recovery.py, scripts/mutation_sampling_lib.py, scripts/mutation_sampling_selection.py, scripts/mutation_sweep_report.py, scripts/native_gate_lib.py, scripts/packaging_lib.py, scripts/parity_harness.py, scripts/premise_git_snapshot.py, scripts/premise_tree_observation.py, scripts/prepush_close_keyword_scan.py, scripts/prepush_quality_receipt.py, scripts/probe_record_parse.py, scripts/probe_stimulus_replay.py, scripts/quality_adapter_lib.py, scripts/quality_artifact_skill_ergonomics.py, scripts/quality_gate_provenance_fallback.py, scripts/quality_label_universe.py, scripts/quality_universes_lib.py, scripts/recent_lesson_selection.py, scripts/recent_lessons_lib.py, scripts/release_changed_line_coverage.py, scripts/release_changed_line_coverage_unavailable.py, scripts/removed_name_consumers.py, scripts/render_cli_reference.py, scripts/render_lesson_selection_preview.py, scripts/render_validator_timing_layers.py, scripts/repo_file_listing.py, scripts/resolve_artifact_path.py, scripts/retro_output_dir_lib.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/reviewed_input_nonblob.py, scripts/run_cosmic_ray_mutation.py, scripts/run_js_mutation.py, scripts/run_quality_engine.py, scripts/run_quality_engine_model.py, scripts/run_quality_engine_output.py, scripts/run_quality_engine_phase.py, scripts/run_quality_engine_receipt.py, scripts/run_quality_engine_runtime.py, scripts/run_quality_engine_selection.py, scripts/run_specdown.py, scripts/run_standing_pytest.py, scripts/rust_changed_line_coverage.py, scripts/sample_mutation_files.py, scripts/setup_adapter_inspect_lib.py, scripts/setup_inspect_quality_lib.py, scripts/specdown_ephemeral_config.py, scripts/staged_commit_gate_plan.py, scripts/staged_commit_gate_plan_helpers.py, scripts/standing_pytest_basetemp.py, scripts/subprocess_guard.py, scripts/subprocess_only_coverage_advisory.py, scripts/surfaces_lib.py, scripts/task_run.py, scripts/task_run_execution.py, scripts/task_run_git.py, scripts/upstream_release_lib.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_maintainer_setup.py, scripts/validate_packaging_install_surface.py, scripts/validate_presets.py, scripts/validate_quality_artifact.py, scripts/waiver_file_lines.py, scripts/worktree_audit_lib.py, scripts/worktree_cleanup_lib.py, scripts/worktree_create_lib.py, scripts/worktree_doctor_checks.py, scripts/worktree_doctor_lib.py, scripts/worktree_doctor_manifest.py, scripts/worktree_exec_lib.py, tests/charness_cli/support.py, tests/charness_cli/test_bootstrap_runtime.py, tests/charness_cli/test_codex_cache_refresh.py, tests/charness_cli/test_codex_managed_install.py, tests/charness_cli/test_doctor_next_action.py, tests/charness_cli/test_managed_install.py, tests/charness_cli/test_managed_install_extended.py, tests/charness_cli/test_managed_install_release_checks.py, tests/charness_cli/test_task_run.py, tests/charness_cli/test_task_run_lib_root.py, tests/charness_cli/test_update_flow_unit.py, tests/charness_cli/test_update_output.py, tests/charness_cli/test_update_propagation.py, tests/charness_cli/test_version_surface.py, tests/charness_cli/test_worktree_audit.py, tests/charness_cli/test_worktree_cleanup.py, tests/charness_cli/test_worktree_create.py, tests/charness_cli/test_worktree_doctor.py, tests/charness_cli/test_worktree_exec.py, tests/conftest.py, tests/control_plane/support.py, tests/control_plane/test_integrations_validation.py, tests/control_plane/test_monorepo_layout.py, tests/control_plane/test_upstream_release.py, tests/control_plane/test_upstream_release_helpers.py, tests/coverage_debt/test_batch3.py, tests/coverage_debt/test_batch4.py, tests/coverage_debt/test_batch5.py, tests/coverage_debt/test_batch6.py, tests/coverage_debt/test_batch8.py, tests/quality_gates/fixtures/engine_gate.py, tests/quality_gates/fixtures/scripts/run-quality.sh, tests/quality_gates/inprocess_script_support.py, tests/quality_gates/quality_runner_seed.py, tests/quality_gates/release_publish_fixtures.py, tests/quality_gates/support.py, tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py, tests/quality_gates/test_absent_input_is_not_a_matching_input.py, tests/quality_gates/test_achieve_goal_run_pickup.py, tests/quality_gates/test_argparse_surface_lib.py, tests/quality_gates/test_artifact_naming.py, tests/quality_gates/test_artifact_referents.py, tests/quality_gates/test_attention_state_visibility.py, tests/quality_gates/test_boundary_bypass_payload_validator.py, tests/quality_gates/test_changed_line_run_trust.py, tests/quality_gates/test_check_artifact_surface_preflight.py, tests/quality_gates/test_check_bootstrap_shim_consistency.py, tests/quality_gates/test_check_coverage_inventory.py, tests/quality_gates/test_check_git_identity.py, tests/quality_gates/test_check_last_verified.py, tests/quality_gates/test_check_mutation_run_proof.py, tests/quality_gates/test_check_plugin_doc_links.py, tests/quality_gates/test_check_prose_pin.py, tests/quality_gates/test_check_public_doc_coupling.py, tests/quality_gates/test_check_skill_cut_safety.py, tests/quality_gates/test_check_staged_worktree_consistency.py, tests/quality_gates/test_check_test_completeness.py, tests/quality_gates/test_classify_push_diff.py, tests/quality_gates/test_cli_skill_surface.py, tests/quality_gates/test_closeout_authorization_ingress.py, tests/quality_gates/test_code_length_gates.py, tests/quality_gates/test_command_docs_gate.py, tests/quality_gates/test_command_dominance.py, tests/quality_gates/test_coverage_floor_inventory_reference.py, tests/quality_gates/test_critique_boundary_ownership_presence.py, tests/quality_gates/test_critique_delivery_state_floor.py, tests/quality_gates/test_current_pointer_freshness.py, tests/quality_gates/test_current_pointer_writers.py, tests/quality_gates/test_current_pointer_writes.py, tests/quality_gates/test_current_release_version_refusal.py, tests/quality_gates/test_docs_and_misc.py, tests/quality_gates/test_dup_ratchet_triage.py, tests/quality_gates/test_dup_ratchet_triage_draft.py, tests/quality_gates/test_dup_review_seed.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_every_resolver_answers_a_refused_document.py, tests/quality_gates/test_export_self_sufficiency.py, tests/quality_gates/test_gather_provider.py, tests/quality_gates/test_gather_symlink_safety.py, tests/quality_gates/test_goal_binding_v1.py, tests/quality_gates/test_hitl_chunk_contract.py, tests/quality_gates/test_inference_interpretation_meta_validator.py, tests/quality_gates/test_inventory_ci_local_gate_parity.py, tests/quality_gates/test_inventory_consumption.py, tests/quality_gates/test_issue_closeout_commit_msg_hook.py, tests/quality_gates/test_issue_read.py, tests/quality_gates/test_issue_worker_carrier.py, tests/quality_gates/test_js_mutation_tooling.py, tests/quality_gates/test_maintainer_hooks.py, tests/quality_gates/test_mutate_and_restore.py, tests/quality_gates/test_mutate_and_restore_call_sites.py, tests/quality_gates/test_mutation_baseline_abort.py, tests/quality_gates/test_mutation_changed_line_targets.py, tests/quality_gates/test_mutation_coverage_probe.py, tests/quality_gates/test_mutation_coverage_producer.py, tests/quality_gates/test_mutation_recovery.py, tests/quality_gates/test_mutation_sampling_line_coverage.py, tests/quality_gates/test_mutation_test_reporters.py, tests/quality_gates/test_native_gate_lib.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_parents_index_layout_invariant.py, tests/quality_gates/test_parity_harness.py, tests/quality_gates/test_plugin_asset_command_carriers.py, tests/quality_gates/test_premise_preflight.py, tests/quality_gates/test_prepush_close_keyword_guard.py, tests/quality_gates/test_prepush_runtime_regime.py, tests/quality_gates/test_prescribed_skill_executed.py, tests/quality_gates/test_profile_and_preset_validation.py, tests/quality_gates/test_public_skill_yaml_output_contract.py, tests/quality_gates/test_python_and_security_gates.py, tests/quality_gates/test_quality_bootstrap_absence.py, tests/quality_gates/test_quality_bootstrap_absence_paths.py, tests/quality_gates/test_quality_declaration_path_resolution.py, tests/quality_gates/test_quality_doc_duplicates.py, tests/quality_gates/test_quality_dual_implementation.py, tests/quality_gates/test_quality_gate_list_fixture_parity.py, tests/quality_gates/test_quality_gitignore_scan_hygiene.py, tests/quality_gates/test_quality_markdown_preview_bootstrap.py, tests/quality_gates/test_quality_mutation_coverage.py, tests/quality_gates/test_quality_mutation_sampling.py, tests/quality_gates/test_quality_mutation_testing.py, tests/quality_gates/test_quality_policy_merge_import.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_quality_run_planner_declared.py, tests/quality_gates/test_quality_runner.py, tests/quality_gates/test_quality_runner_coverage_selection.py, tests/quality_gates/test_quality_runner_exit_status.py, tests/quality_gates/test_quality_runner_label_universe.py, tests/quality_gates/test_quality_runner_progress.py, tests/quality_gates/test_quality_runner_release_order.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py, tests/quality_gates/test_quality_runner_unproven.py, tests/quality_gates/test_quality_runtime_recorder.py, tests/quality_gates/test_quality_skill_docs.py, tests/quality_gates/test_quality_standing_gate_verbosity.py, tests/quality_gates/test_quality_tool_fixtures.py, tests/quality_gates/test_quality_tool_recommendations.py, tests/quality_gates/test_quality_universes.py, tests/quality_gates/test_release_changed_line_coverage.py, tests/quality_gates/test_release_fresh_checkout_probes.py, tests/quality_gates/test_release_issue_closeout_preflight.py, tests/quality_gates/test_release_only_sentinel_inventory.py, tests/quality_gates/test_release_planner_version_refusal.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_release_publish_post_create.py, tests/quality_gates/test_release_publish_provenance.py, tests/quality_gates/test_release_publish_requested_review.py, tests/quality_gates/test_release_publish_rollback.py, tests/quality_gates/test_release_publish_tag_history.py, tests/quality_gates/test_release_quality_status_binding.py, tests/quality_gates/test_release_run_planner.py, tests/quality_gates/test_release_run_planner_prepared_stop.py, tests/quality_gates/test_repo_copy_invariants.py, tests/quality_gates/test_retro_artifact_validation.py, tests/quality_gates/test_retro_auto_trigger.py, tests/quality_gates/test_retro_installed_plan_path.py, tests/quality_gates/test_retro_lesson_selection_index.py, tests/quality_gates/test_retro_memory.py, tests/quality_gates/test_retro_persistence.py, tests/quality_gates/test_reviewer_runner.py, tests/quality_gates/test_reviewer_worker.py, tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py, tests/quality_gates/test_run_quality_engine.py, tests/quality_gates/test_runtime_budget_universe.py, tests/quality_gates/test_s6_changed_line_gaps.py, tests/quality_gates/test_s6b2_changed_line_gaps.py, tests/quality_gates/test_scaffold_claims_review.py, tests/quality_gates/test_scaffold_version_refusal.py, tests/quality_gates/test_script_inprocess_behaviors.py, tests/quality_gates/test_seed_worktree_adapter.py, tests/quality_gates/test_semantic_review_command.py, tests/quality_gates/test_setup_hook_failure_guidance.py, tests/quality_gates/test_setup_inspect_adapters.py, tests/quality_gates/test_setup_inspect_policy.py, tests/quality_gates/test_setup_retro_memory.py, tests/quality_gates/test_shared_script_gate_scope.py, tests/quality_gates/test_shell_gate_root_resolution.py, tests/quality_gates/test_skill_bootstrap_vars.py, tests/quality_gates/test_skill_contracts_validation.py, tests/quality_gates/test_skill_docs_contracts.py, tests/quality_gates/test_skill_ergonomics_gate.py, tests/quality_gates/test_skill_reference_index.py, tests/quality_gates/test_skill_surface_preflight.py, tests/quality_gates/test_skill_validation.py, tests/quality_gates/test_specdown_ephemeral_config.py, tests/quality_gates/test_staged_commit_gate_plan.py, tests/quality_gates/test_staged_test_boundaries.py, tests/quality_gates/test_standalone_imports.py, tests/quality_gates/test_standing_pytest_run_execution.py, tests/quality_gates/test_standing_pytest_runner.py, tests/quality_gates/test_subprocess_form_gate.py, tests/quality_gates/test_subprocess_only_coverage_advisory.py, tests/quality_gates/test_surface_obligations.py, tests/quality_gates/test_test_production_ratio.py, tests/quality_gates/test_timing_layer_completeness.py, tests/quality_gates/test_u2_doc_artifact_universes.py, tests/quality_gates/test_universe_consumers.py, tests/quality_gates/test_unreferenced_scripts.py, tests/test_achieve_lesson_citation.py, tests/test_adversarial_evidence.py, tests/test_agent_browser_runtime_guard.py, tests/test_announcement_delivery_verification.py, tests/test_authoring_preflight_reference.py, tests/test_boundary_bypass_ratchet.py, tests/test_changed_path_enumerator_agreement.py, tests/test_classify_t_signal.py, tests/test_closeout_classification_parity.py, tests/test_committed_packet_refusal.py, tests/test_consumer_validator_catalog.py, tests/test_critique_section_changed_surfaces.py, tests/test_critique_verify_packet.py, tests/test_debug_artifact.py, tests/test_debug_artifact_scope.py, tests/test_debug_persistence.py, tests/test_degradation_branch_coverage.py, tests/test_doc_duplicates_inprocess_coverage.py, tests/test_docs_graph_gate.py, tests/test_evidence_boundary_crosswalk.py, tests/test_gather_plan.py, tests/test_impl_survey_verification.py, tests/test_inventory_marker_rule_measurement.py, tests/test_issue_source_capture.py, tests/test_lesson_ledger.py, tests/test_lesson_ledger_refusals.py, tests/test_lesson_lifecycle.py, tests/test_lesson_selection_preview.py, tests/test_list_external_links.py, tests/test_markdown_preview_support.py, tests/test_public_skill_dogfood.py, tests/test_public_skill_validation.py, tests/test_quality_delegated_review.py, tests/test_retro_help.py, tests/test_reviewed_input_identity_binding.py, tests/test_reviewed_input_nonblob_binding.py, tests/test_scaffold_inprocess_coverage.py, tests/test_script_timeout.py, tests/test_seed_lesson_transitions.py, tests/test_shared_authoring_script_shims.py, tests/test_skill_anchor_guard_hook.py, tests/test_skill_script_references.py, tests/test_subprocess_guard.py, tests/test_supply_chain_online.py, tests/test_twitter_exact_source.py, tests/test_unhappy_path_branches.py, tests/test_validate_adapters_integration_schema.py, tests/test_validate_critique_artifacts_dates.py, tests/test_web_fetch_cleanup.py, tests/test_web_fetch_content_persistence.py, tests/test_web_fetch_route_and_classify.py, tests/test_web_fetch_support.py, tests/test_web_fetch_trace_quality.py, tests/test_write_artifact_path_single_owner.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: scripts/check_code_lengths.py, tools/validate_inference_interpretation.py
  verify: python3 -m tools.validate_inference_interpretation --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/announcement_verification_lib.py, scripts/artifact_referents.py, scripts/artifact_run_scope.py, scripts/artifact_shape_source.py, scripts/bootstrap_runtime.py, scripts/boundary_bypass_ratchet_lib.py, scripts/build_retro_lesson_selection_index.py, scripts/changed_line_run_trust.py, scripts/check_artifact_referents.py, scripts/check_artifact_surface_preflight.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_cli_skill_surface.py, scripts/check_code_lengths.py, scripts/check_command_dominance.py, scripts/check_consumer_validator_catalog.py, scripts/check_coverage_lib.py, scripts/check_doc_links.py, scripts/check_docs_graph.py, scripts/check_documented_subcommands.py, scripts/check_git_identity.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_lesson_ledger.py, scripts/check_mutation_run_proof.py, scripts/check_mutation_suite_score.py, scripts/check_prose_pin.py, scripts/check_python_runtime_inheritance.py, scripts/check_skill_surface_preflight.py, scripts/check_spec_evidence_durability.py, scripts/check_staged_reversion.py, scripts/check_staged_router_change.py, scripts/check_staged_test_boundaries.py, scripts/check_staged_worktree_consistency.py, scripts/check_standalone_imports.py, scripts/check_subprocess_form.py, scripts/check_supply_chain_online.py, scripts/check_symbol_residue.py, scripts/check_test_production_ratio.py, scripts/check_upstream_support_drift.py, scripts/classify_push_diff_lib.py, scripts/classify_t_signal.py, scripts/command_carrier_discovery.py, scripts/command_plan_inputs.py, scripts/command_plan_preflight.py, scripts/control_plane_lib.py, scripts/critique_artifact_paths.py, scripts/critique_artifact_universe.py, scripts/critique_packet_lib.py, scripts/debug_persistence_lib.py, scripts/doc_file_population.py, scripts/dup_ratchet_edit_advisory.py, scripts/eval_support_sync_contracts.py, scripts/git_status_snapshot.py, scripts/install_provenance_lib.py, scripts/inventory_boundary_bypass_lib.py, scripts/inventory_cli_ergonomics_unavailable.py, scripts/inventory_current_pointer_layouts.py, scripts/inventory_gitignore_scan_hygiene_unavailable.py, scripts/inventory_nose_clones_unavailable.py, scripts/issue_source_capture_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_preview_bootstrap_lib.py, scripts/markdownlint_probe.py, scripts/mutate_and_restore.py, scripts/mutation_changed_files_lib.py, scripts/mutation_changed_line_diff.py, scripts/mutation_coverage_producer.py, scripts/mutation_recovery.py, scripts/mutation_sampling_lib.py, scripts/mutation_sampling_selection.py, scripts/mutation_sweep_report.py, scripts/native_gate_lib.py, scripts/packaging_lib.py, scripts/parity_harness.py, scripts/premise_git_snapshot.py, scripts/premise_tree_observation.py, scripts/prepush_close_keyword_scan.py, scripts/prepush_quality_receipt.py, scripts/probe_record_parse.py, scripts/probe_stimulus_replay.py, scripts/quality_adapter_lib.py, scripts/quality_artifact_skill_ergonomics.py, scripts/quality_gate_provenance_fallback.py, scripts/quality_label_universe.py, scripts/quality_universes_lib.py, scripts/recent_lesson_selection.py, scripts/recent_lessons_lib.py, scripts/release_changed_line_coverage.py, scripts/release_changed_line_coverage_unavailable.py, scripts/removed_name_consumers.py, scripts/render_cli_reference.py, scripts/render_lesson_selection_preview.py, scripts/render_validator_timing_layers.py, scripts/repo_file_listing.py, scripts/resolve_artifact_path.py, scripts/retro_output_dir_lib.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/reviewed_input_nonblob.py, scripts/run_cosmic_ray_mutation.py, scripts/run_js_mutation.py, scripts/run_quality_engine.py, scripts/run_quality_engine_model.py, scripts/run_quality_engine_output.py, scripts/run_quality_engine_phase.py, scripts/run_quality_engine_receipt.py, scripts/run_quality_engine_runtime.py, scripts/run_quality_engine_selection.py, scripts/run_specdown.py, scripts/run_standing_pytest.py, scripts/rust_changed_line_coverage.py, scripts/sample_mutation_files.py, scripts/setup_adapter_inspect_lib.py, scripts/setup_inspect_quality_lib.py, scripts/specdown_ephemeral_config.py, scripts/staged_commit_gate_plan.py, scripts/staged_commit_gate_plan_helpers.py, scripts/standing_pytest_basetemp.py, scripts/subprocess_guard.py, scripts/subprocess_only_coverage_advisory.py, scripts/surfaces_lib.py, scripts/task_run.py, scripts/task_run_execution.py, scripts/task_run_git.py, scripts/upstream_release_lib.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_maintainer_setup.py, scripts/validate_packaging_install_surface.py, scripts/validate_presets.py, scripts/validate_quality_artifact.py, scripts/waiver_file_lines.py, scripts/worktree_audit_lib.py, scripts/worktree_cleanup_lib.py, scripts/worktree_create_lib.py, scripts/worktree_doctor_checks.py, scripts/worktree_doctor_lib.py, scripts/worktree_doctor_manifest.py, scripts/worktree_exec_lib.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_lessons.py, skills/public/announcement/scripts/collect_commits.py, skills/public/announcement/scripts/infer_audience_tags.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/gather/scripts/gather_public_execution.py, skills/public/gather/scripts/gather_public_url.py, skills/public/issue/scripts/issue_backend.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_runtime.py, skills/public/issue/scripts/issue_state_readback.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_authorization.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/narrative/scripts/map_sources.py, skills/public/quality/scripts/adapter_validators.py, skills/public/quality/scripts/changed_line_coverage_gate_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/cli_side_effect_probe_lib.py, skills/public/quality/scripts/discovery_filter_scan_lib.py, skills/public/quality/scripts/doc_duplicate_scan.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/dup_ratchet_git.py, skills/public/quality/scripts/dup_ratchet_lib.py, skills/public/quality/scripts/dup_ratchet_scan.py, skills/public/quality/scripts/inventory_ci_local_gate_parity.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py, skills/public/quality/scripts/inventory_sloc.py, skills/public/quality/scripts/measure_startup_probes.py, skills/public/quality/scripts/nose_tool_lib.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/pytest_temp_scan_lib.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_declared_gate_source.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/regenerable_facts_lib.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/runtime_budget_universe_lib.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/standing_gate_discovery_lib.py, skills/public/quality/scripts/standing_gate_verbosity_launcher_axes.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/test_discovery_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/bump_version.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/claims_review_scope.py, skills/public/release/scripts/current_release.py, skills/public/release/scripts/plan_release_prepared_stop.py, skills/public/release/scripts/publish_release_adapter_preflight.py, skills/public/release/scripts/publish_release_commands.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/publish_release_scope.py, skills/public/release/scripts/release_delta.py, skills/public/retro/scripts/check_auto_trigger.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/setup/scripts/seed_worktree_adapter_lib.py, skills/support/markdown-preview/scripts/markdown_preview_render.py, skills/support/web-fetch/scripts/acquire_public_url_io.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- goal-run-evidence: Durable Goal Run provider plans, operations, observations, graph snapshots, and evidence-lineage records.
  source matches: charness-artifacts/goal-runs/765/2026-09-02-session-record.md, charness-artifacts/goal-runs/765/bodies/ledger-only-lessons.md, charness-artifacts/goal-runs/765/bodies/parent-amended-774.md, charness-artifacts/goal-runs/765/bodies/parent-progress-768.md, charness-artifacts/goal-runs/765/bodies/parent-progress-769.md, charness-artifacts/goal-runs/765/briefs/brief-768-production.md, charness-artifacts/goal-runs/765/briefs/brief-768-ratchet.md, charness-artifacts/goal-runs/765/briefs/brief-768-repair.md, charness-artifacts/goal-runs/765/briefs/brief-768-tests.md, charness-artifacts/goal-runs/765/briefs/brief-769-r1-gate-list.md, charness-artifacts/goal-runs/765/briefs/brief-769-r2a-runner-lib.md, charness-artifacts/goal-runs/765/briefs/brief-769-r2b-wire-runner.md, charness-artifacts/goal-runs/765/briefs/brief-769-r3-native-reader.md, charness-artifacts/goal-runs/765/briefs/brief-769-s-consumer-scope.md, charness-artifacts/goal-runs/765/briefs/brief-769-t1-tools-tree.md, charness-artifacts/goal-runs/765/briefs/brief-769-t2-tools-batch-b.md, charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md, charness-artifacts/goal-runs/765/briefs/brief-769-u0-universes.md, charness-artifacts/goal-runs/765/briefs/brief-769-u1-sources.md, charness-artifacts/goal-runs/765/briefs/brief-769-u2-docs-artifacts.md, charness-artifacts/goal-runs/765/briefs/brief-769-u3-scanners-configs.md, charness-artifacts/goal-runs/765/briefs/brief-770-p-common.md, charness-artifacts/goal-runs/765/briefs/brief-770-p0-foundation.md, charness-artifacts/goal-runs/765/briefs/brief-770-p1-core-gates.md, charness-artifacts/goal-runs/765/briefs/brief-770-p2-mutation-worktree-hooks.md, charness-artifacts/goal-runs/765/briefs/brief-770-p3-review-lessons-adapters.md, charness-artifacts/goal-runs/765/briefs/brief-770-p4-remaining.md, charness-artifacts/goal-runs/765/briefs/design-critique-769.md, charness-artifacts/goal-runs/765/briefs/map-769-conditional.md, charness-artifacts/goal-runs/765/briefs/map-769-export.md, charness-artifacts/goal-runs/765/briefs/map-769-runner.md, charness-artifacts/goal-runs/765/briefs/map-770.md, charness-artifacts/goal-runs/765/briefs/map-772.md, charness-artifacts/goal-runs/765/briefs/repair-batch-r0.txt, charness-artifacts/goal-runs/765/briefs/repair-batch-r1.txt, charness-artifacts/goal-runs/765/briefs/repair-batch-r2.txt, charness-artifacts/goal-runs/765/briefs/reword-768-wip-subjects.sh, charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.started.json, charness-artifacts/goal-runs/765/observations/advance-cursor-768-1.terminal.json, charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.started.json, charness-artifacts/goal-runs/765/observations/advance-cursor-769-1.terminal.json, charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.started.json, charness-artifacts/goal-runs/765/observations/advance-cursor-769-2.terminal.json, charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.started.json, charness-artifacts/goal-runs/765/observations/amend-add-ledger-only-lessons-1.terminal.json, charness-artifacts/goal-runs/765/observations/amend-parent-774-1.started.json, charness-artifacts/goal-runs/765/observations/amend-parent-774-1.terminal.json, charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.json, charness-artifacts/goal-runs/765/operations/amend-add-ledger-only-lessons.out.yaml, charness-artifacts/goal-runs/765/operations/update-parent-amended-774.json, charness-artifacts/goal-runs/765/operations/update-parent-amended-774.out.yaml, charness-artifacts/goal-runs/765/operations/update-parent-progress-768.json, charness-artifacts/goal-runs/765/operations/update-parent-progress-768.out.yaml, charness-artifacts/goal-runs/765/operations/update-parent-progress-769.json
  verify: find charness-artifacts/goal-runs -type f -name '*.json' -exec python3 -m json.tool {} \;
- command-dominance-registry: The registry of commands this repo has measured as dominated by a cheaper one, and the gates that read it.
  source matches: .agents/command-dominance.yaml, scripts/check_command_dominance.py
  sync: python3 scripts/sync_root_plugin_manifests.py
  verify: python3 scripts/check_command_dominance.py --repo-root ., python3 -m pytest -q tests/quality_gates/test_command_dominance.py

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
- python3 scripts/sync_root_plugin_manifests.py
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section shape validation ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section shape validation ok**: True

```text
# Reviewer-Packet Semantic Question

Use this question when a slice changes a guard, reference, claim, or verdict
surface. It keeps a reviewer packet anchored to what a reader or control must
know, rather than to the observable form that happened to expose the problem.

## Ask Before Broad Sampling

The packet author and reviewer should use all four parts when they apply. If a
part is not applicable or cannot be established, record `not applicable` or
`insufficient evidence` with the reason; do not silently claim the control is
proven.

1. **Semantic fact or invariant:** what must be true, independently of the
   current representation or failure spelling?
2. **Owning boundary:** which source, helper, renderer, reference, or workflow
   boundary carries or derives that fact, and who reads it?
3. **Recorded instance:** which concrete observed instance must this slice catch,
   explain, or preserve?
4. **Axis-varying counterexample:** what changes the semantic axis while keeping
   the observed form similar enough to expose a proxy-based control?

The question is a review aid, not a packet-readiness predicate. A clean tree is
not evidence that the selected control catches a recorded instance.

## Compare the Proposed Control

After naming the four parts, state the proposed predicate, claim, or surface
change and compare it with the counterexample:

- If the observed form changes while the semantic fact does not, reject or
  repair a control that changes its verdict with that form.
- If the semantic fact changes while the observed form stays similar, reject or
  repair a control that cannot distinguish the changed outcome.
- If the comparison cannot be made, record `unproven — defer`; do not approve it
  as though a clean-tree result were proof.
- For a behavior-changing helper or command, first record the bounded candidate
  search and scope. When that change has a reader-facing or copy-paste reference
  in scope, identify the first reader and verify that its demonstrated invocation
  preserves the claimed behavior. Disposition each discovered reference as
  updated, not applicable, or insufficient evidence with a reason. If no such
  reference is in scope, record `not applicable` with the search scope; if the
  reader cannot be checked, record `insufficient evidence` or `unproven — defer`
  rather than treating the helper's own tests as proof of reference safety.

These are reviewer dispositions, not an automated semantic gate.

## Decision Boundary

- Prefer a surface fix when the owning surface can carry or derive the semantic
  fact and prove the recorded instance.
- Keep the control as a reviewer question when the fact is judgment-bound or
  cannot be mechanically observed without guessing.
- Add a gate only when the predicate is mechanically observable, its false-fire
  cost is understood, and a recorded escape supports the addition.

This is a reviewer question, not a semantic meta-gate. It does not claim that a
host renders the packet, that a reviewer reaches the right judgment, or that a
clean-tree run proves the control.
```
