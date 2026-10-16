# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-16T22:38:07Z
- **Prepared for**: v8.14.7 integrated candidate 862a8300b
- **Prepared targets**: 1
  - `release-v8.14.7`
- **Substrate mode**: `committed-ref`
- **Changed ref**: `feba132624fa7f63cdd6be785409cb53acc150c8..862a8300b1b496dfb205e8a23ea44002a0101cd3`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `bb796ef1d00e54baa720913f7debcdb3f85f6626f99c445e74d84381465fa444`
- **Reviewed paths**: 130
  - `.agents/temp-producers.yaml`
  - `charness`
  - `charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.md`
  - `charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.receipt.json`
  - `charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.md`
  - `charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.receipt.json`
  - `charness-artifacts/debug/latest.md`
  - `charness-artifacts/debug/seam-risk-index.json`
  - `charness-artifacts/probe/2026-10-01-v8.14.6-release-observer.json`
  - `charness-artifacts/release-review/2026-10-01-v8.14.6-claims-review.md`
  - `charness-artifacts/release-review/2026-10-01-v8.14.6-prepared-claims-review.json`
  - `charness-artifacts/release/.8.14.6-prepush-quality.json.charness-receipt.json`
  - `charness-artifacts/release/8.14.6-prepush-quality.json`
  - `charness-artifacts/release/latest.md`
  - `docs/agent-task-runs.md`
  - `docs/cli-reference.md`
  - `scripts/cli/cmd_task.py`
  - `scripts/mutation/release_changed_line_coverage.py`
  - `scripts/plugin_export/validate_packaging_install_surface.py`
  - `scripts/review/critique_packet_lib.py`
  - `scripts/runtime_scratch.py`
  - `scripts/runtime_scratch_cli.py`
  - `scripts/runtime_scratch_registry.py`
  - `scripts/task_run/task_run.py`
  - `scripts/task_run/task_run_attempts.py`
  - `scripts/task_run/task_run_completion.py`
  - `scripts/task_run/task_run_completion_proof.py`
  - `scripts/task_run/task_run_detach.py`
  - `scripts/task_run/task_run_evidence.py`
  - `scripts/task_run/task_run_execution.py`
  - `scripts/task_run/task_run_inventory.py`
  - `scripts/task_run/task_run_lane_runner.py`
  - `scripts/task_run/task_run_muse_events.py`
  - `scripts/task_run/task_run_prelaunch.py`
  - `scripts/task_run/task_run_progress.py`
  - `scripts/task_run/task_run_runtime.py`
  - `scripts/task_run/task_run_self_review.py`
  - `scripts/task_run/task_run_state.py`
  - `scripts/templates/plugin_import_smoke.py.txt`
  - `skills/public/critique/adapter.example.yaml`
  - `skills/public/critique/references/adapter-contract.md`
  - `skills/public/critique/scripts/prepare_packet.py`
  - `skills/public/critique/scripts/review_followup_provenance.py`
  - `skills/public/critique/scripts/run_review.py`
  - `skills/public/critique/scripts/run_review_carrier.py`
  - `skills/public/critique/scripts/run_review_execution.py`
  - `skills/public/critique/scripts/run_review_invocation.py`
  - `skills/public/critique/scripts/run_review_packet.py`
  - `skills/public/critique/scripts/run_review_promotion.py`
  - `skills/public/critique/scripts/run_review_promotion_storage.py`
  - `skills/public/critique/scripts/run_review_recovery.py`
  - `skills/public/critique/scripts/run_review_recovery_inputs.py`
  - `skills/public/critique/scripts/run_review_support.py`
  - `skills/public/critique/scripts/semantic_review_input.py`
  - `skills/public/critique/scripts/templates/critique_adapter.yaml`
  - `skills/public/quality/references/attention-state-visibility.json`
  - `skills/shared/references/fresh-eye-subagent-review.md`
  - `skills/shared/scripts/reviewer_delivery_fields.py`
  - `skills/shared/scripts/reviewer_partial_output.py`
  - `skills/shared/scripts/reviewer_result_contract.py`
  - `skills/shared/scripts/reviewer_worker.py`
  - `skills/shared/scripts/reviewer_worker_backend.py`
  - `skills/shared/scripts/reviewer_worker_carrier_support.py`
  - `skills/shared/scripts/reviewer_worker_report.py`
  - `skills/shared/scripts/reviewer_worker_runner_support.py`
  - `skills/shared/scripts/reviewer_worker_runtime.py`
  - `skills/shared/scripts/run_reviewer_worker.py`
  - `tests/charness_cli/task_run_completion_support.py`
  - `tests/charness_cli/test_claude_home_unit.py`
  - `tests/charness_cli/test_codex_cache_refresh.py`
  - `tests/charness_cli/test_codex_managed_install.py`
  - `tests/charness_cli/test_doctor_cache_selection.py`
  - `tests/charness_cli/test_entry_cov_e5_874.py`
  - `tests/charness_cli/test_repo_script_payload_parsing.py`
  - `tests/charness_cli/test_task_run.py`
  - `tests/charness_cli/test_task_run_completion.py`
  - `tests/charness_cli/test_task_run_completion_deletions.py`
  - `tests/charness_cli/test_task_run_detach_wait_866.py`
  - `tests/charness_cli/test_task_run_executor_probe.py`
  - `tests/charness_cli/test_task_run_exit_codes.py`
  - `tests/charness_cli/test_task_run_fixtures.py`
  - `tests/charness_cli/test_task_run_friction.py`
  - `tests/charness_cli/test_task_run_implementation_lane.py`
  - `tests/charness_cli/test_task_run_launch_hygiene.py`
  - `tests/charness_cli/test_task_run_muse_stream_886.py`
  - `tests/charness_cli/test_task_run_parent_progress.py`
  - `tests/charness_cli/test_task_run_report_ledger.py`
  - `tests/charness_cli/test_task_run_result.py`
  - `tests/charness_cli/test_task_run_scope.py`
  - `tests/charness_cli/test_task_run_scope_deletions.py`
  - `tests/charness_cli/test_task_run_scope_mismatch_834.py`
  - `tests/charness_cli/test_task_run_self_review.py`
  - `tests/charness_cli/test_task_run_status_inventory.py`
  - `tests/charness_cli/test_task_run_steer.py`
  - `tests/charness_cli/test_tool_lifecycle.py`
  - `tests/charness_cli/test_uninstall_native_residue.py`
  - `tests/charness_cli/test_update_flow_unit.py`
  - `tests/charness_cli/test_update_output.py`
  - `tests/charness_cli/test_yaml_output_branch_coverage.py`
  - `tests/coverage_debt/test_batch10.py`
  - `tests/coverage_debt/test_batch5.py`
  - `tests/quality_gates/test_critique_enforcement_scope.py`
  - `tests/quality_gates/test_issue_bundled_closeout.py`
  - `tests/quality_gates/test_issue_worker_carrier.py`
  - `tests/quality_gates/test_packaging_validation.py`
  - `tests/quality_gates/test_provider_boundary.py`
  - `tests/quality_gates/test_release_changed_line_coverage.py`
  - `tests/quality_gates/test_release_changed_line_staged_preflight.py`
  - `tests/quality_gates/test_review_invocation_command.py`
  - `tests/quality_gates/test_reviewer_delivery_state_machine.py`
  - `tests/quality_gates/test_reviewer_runner.py`
  - `tests/quality_gates/test_reviewer_tier_policy.py`
  - `tests/quality_gates/test_reviewer_worker.py`
  - `tests/quality_gates/test_reviewer_worker_backend.py`
  - `tests/quality_gates/test_reviewer_worker_report.py`
  - `tests/quality_gates/test_semantic_review_command.py`
  - `tests/test_command_guards.py`
  - `tests/test_common_runner_failure_coverage.py`
  - `tests/test_critique_prepare_packet.py`
  - `tests/test_grok_host_install.py`
  - `tests/test_review_followup.py`
  - `tests/test_review_followup_failures.py`
  - `tests/test_review_promotion_failures.py`
  - `tests/test_review_recovery_failures.py`
  - `tests/test_review_runner_terminal_paths.py`
  - `tests/test_reviewer_result_coverage.py`
  - `tests/test_run_review_declared_path_resolution.py`
  - `tests/test_runtime_scratch.py`
  - `tests/test_runtime_scratch_failures.py`
  - `tests/test_temp_producer_inventory.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8147-integrated-candidate-20261017-packet.json --packet-sha256 3ac48ddc4d4fc42de34f21b1240cf107a0f78ead509950413bc18a746ff626b9 --identity-sha256 bb796ef1d00e54baa720913f7debcdb3f85f6626f99c445e74d84381465fa444
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-6-luna, reasoning_effort=xhigh, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Execution mode**: `file-backed-worker`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `feba132624fa7f63cdd6be785409cb53acc150c8..862a8300b1b496dfb205e8a23ea44002a0101cd3`:
Exact reviewed-path manifest:
- .agents/temp-producers.yaml
- charness
- charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.md
- charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.receipt.json
- charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.md
- charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.receipt.json
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/probe/2026-10-01-v8.14.6-release-observer.json
- charness-artifacts/release-review/2026-10-01-v8.14.6-claims-review.md
- charness-artifacts/release-review/2026-10-01-v8.14.6-prepared-claims-review.json
- charness-artifacts/release/.8.14.6-prepush-quality.json.charness-receipt.json
- charness-artifacts/release/8.14.6-prepush-quality.json
- charness-artifacts/release/latest.md
- docs/agent-task-runs.md
- docs/cli-reference.md
- scripts/cli/cmd_task.py
- scripts/mutation/release_changed_line_coverage.py
- scripts/plugin_export/validate_packaging_install_surface.py
- scripts/review/critique_packet_lib.py
- scripts/runtime_scratch.py
- scripts/runtime_scratch_cli.py
- scripts/runtime_scratch_registry.py
- scripts/task_run/task_run.py
- scripts/task_run/task_run_attempts.py
- scripts/task_run/task_run_completion.py
- scripts/task_run/task_run_completion_proof.py
- scripts/task_run/task_run_detach.py
- scripts/task_run/task_run_evidence.py
- scripts/task_run/task_run_execution.py
- scripts/task_run/task_run_inventory.py
- scripts/task_run/task_run_lane_runner.py
- scripts/task_run/task_run_muse_events.py
- scripts/task_run/task_run_prelaunch.py
- scripts/task_run/task_run_progress.py
- scripts/task_run/task_run_runtime.py
- scripts/task_run/task_run_self_review.py
- scripts/task_run/task_run_state.py
- scripts/templates/plugin_import_smoke.py.txt
- skills/public/critique/adapter.example.yaml
- skills/public/critique/references/adapter-contract.md
- skills/public/critique/scripts/prepare_packet.py
- skills/public/critique/scripts/review_followup_provenance.py
- skills/public/critique/scripts/run_review.py
- skills/public/critique/scripts/run_review_carrier.py
- skills/public/critique/scripts/run_review_execution.py
- skills/public/critique/scripts/run_review_invocation.py
- skills/public/critique/scripts/run_review_packet.py
- skills/public/critique/scripts/run_review_promotion.py
- skills/public/critique/scripts/run_review_promotion_storage.py
- skills/public/critique/scripts/run_review_recovery.py
- skills/public/critique/scripts/run_review_recovery_inputs.py
- skills/public/critique/scripts/run_review_support.py
- skills/public/critique/scripts/semantic_review_input.py
- skills/public/critique/scripts/templates/critique_adapter.yaml
- skills/public/quality/references/attention-state-visibility.json
- skills/shared/references/fresh-eye-subagent-review.md
- skills/shared/scripts/reviewer_delivery_fields.py
- skills/shared/scripts/reviewer_partial_output.py
- skills/shared/scripts/reviewer_result_contract.py
- skills/shared/scripts/reviewer_worker.py
- skills/shared/scripts/reviewer_worker_backend.py
- skills/shared/scripts/reviewer_worker_carrier_support.py
- skills/shared/scripts/reviewer_worker_report.py
- skills/shared/scripts/reviewer_worker_runner_support.py
- skills/shared/scripts/reviewer_worker_runtime.py
- skills/shared/scripts/run_reviewer_worker.py
- tests/charness_cli/task_run_completion_support.py
- tests/charness_cli/test_claude_home_unit.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/charness_cli/test_codex_managed_install.py
- tests/charness_cli/test_doctor_cache_selection.py
- tests/charness_cli/test_entry_cov_e5_874.py
- tests/charness_cli/test_repo_script_payload_parsing.py
- tests/charness_cli/test_task_run.py
- tests/charness_cli/test_task_run_completion.py
- tests/charness_cli/test_task_run_completion_deletions.py
- tests/charness_cli/test_task_run_detach_wait_866.py
- tests/charness_cli/test_task_run_executor_probe.py
- tests/charness_cli/test_task_run_exit_codes.py
- tests/charness_cli/test_task_run_fixtures.py
- tests/charness_cli/test_task_run_friction.py
- tests/charness_cli/test_task_run_implementation_lane.py
- tests/charness_cli/test_task_run_launch_hygiene.py
- tests/charness_cli/test_task_run_muse_stream_886.py
- tests/charness_cli/test_task_run_parent_progress.py
- tests/charness_cli/test_task_run_report_ledger.py
- tests/charness_cli/test_task_run_result.py
- tests/charness_cli/test_task_run_scope.py
- tests/charness_cli/test_task_run_scope_deletions.py
- tests/charness_cli/test_task_run_scope_mismatch_834.py
- tests/charness_cli/test_task_run_self_review.py
- tests/charness_cli/test_task_run_status_inventory.py
- tests/charness_cli/test_task_run_steer.py
- tests/charness_cli/test_tool_lifecycle.py
- tests/charness_cli/test_uninstall_native_residue.py
- tests/charness_cli/test_update_flow_unit.py
- tests/charness_cli/test_update_output.py
- tests/charness_cli/test_yaml_output_branch_coverage.py
- tests/coverage_debt/test_batch10.py
- tests/coverage_debt/test_batch5.py
- tests/quality_gates/test_critique_enforcement_scope.py
- tests/quality_gates/test_issue_bundled_closeout.py
- tests/quality_gates/test_issue_worker_carrier.py
- tests/quality_gates/test_packaging_validation.py
- tests/quality_gates/test_provider_boundary.py
- tests/quality_gates/test_release_changed_line_coverage.py
- tests/quality_gates/test_release_changed_line_staged_preflight.py
- tests/quality_gates/test_review_invocation_command.py
- tests/quality_gates/test_reviewer_delivery_state_machine.py
- tests/quality_gates/test_reviewer_runner.py
- tests/quality_gates/test_reviewer_tier_policy.py
- tests/quality_gates/test_reviewer_worker.py
- tests/quality_gates/test_reviewer_worker_backend.py
- tests/quality_gates/test_reviewer_worker_report.py
- tests/quality_gates/test_semantic_review_command.py
- tests/test_command_guards.py
- tests/test_common_runner_failure_coverage.py
- tests/test_critique_prepare_packet.py
- tests/test_grok_host_install.py
- tests/test_review_followup.py
- tests/test_review_followup_failures.py
- tests/test_review_promotion_failures.py
- tests/test_review_recovery_failures.py
- tests/test_review_runner_terminal_paths.py
- tests/test_reviewer_result_coverage.py
- tests/test_run_review_declared_path_resolution.py
- tests/test_runtime_scratch.py
- tests/test_runtime_scratch_failures.py
- tests/test_temp_producer_inventory.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/cli/cmd_task.py, scripts/mutation/release_changed_line_coverage.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/review/critique_packet_lib.py, scripts/runtime_scratch.py, scripts/runtime_scratch_cli.py, scripts/runtime_scratch_registry.py, scripts/task_run/task_run.py, scripts/task_run/task_run_attempts.py, scripts/task_run/task_run_completion.py, scripts/task_run/task_run_completion_proof.py, scripts/task_run/task_run_detach.py, scripts/task_run/task_run_evidence.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_inventory.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_muse_events.py, scripts/task_run/task_run_prelaunch.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, scripts/task_run/task_run_state.py, scripts/templates/plugin_import_smoke.py.txt, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/review_followup_provenance.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_invocation.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/critique/scripts/templates/critique_adapter.yaml, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_partial_output.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_backend.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.md, charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.md, charness-artifacts/debug/latest.md, charness-artifacts/release-review/2026-10-01-v8.14.6-claims-review.md, charness-artifacts/release/latest.md, docs/agent-task-runs.md, docs/cli-reference.md, skills/public/critique/references/adapter-contract.md, skills/shared/references/fresh-eye-subagent-review.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/.8.14.6-prepush-quality.json.charness-receipt.json, charness-artifacts/release/8.14.6-prepush-quality.json, charness-artifacts/release/latest.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/review_followup_provenance.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_invocation.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/critique/scripts/templates/critique_adapter.yaml, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_partial_output.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_backend.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 -m tools.validate_current_pointer_freshness --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/review_followup_provenance.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_invocation.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/critique/scripts/templates/critique_adapter.yaml, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_partial_output.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_backend.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/review_followup_provenance.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_invocation.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py, skills/public/critique/scripts/templates/critique_adapter.yaml, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_partial_output.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_backend.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runner_support.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- release-claims-review-evidence: Committed, machine-readable claims-review evidence that binds a prepared local release record before publication may resume.
  source matches: charness-artifacts/release-review/2026-10-01-v8.14.6-claims-review.md, charness-artifacts/release-review/2026-10-01-v8.14.6-prepared-claims-review.json
  verify: for review_record in charness-artifacts/release-review/*.json; do [ -e "$review_record" ] && python3 -m json.tool "$review_record" >/dev/null || exit $?; done
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-10-01-v8.14.6-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.md, charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --check
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/cli/cmd_task.py, scripts/mutation/release_changed_line_coverage.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/review/critique_packet_lib.py, scripts/runtime_scratch.py, scripts/runtime_scratch_cli.py, scripts/runtime_scratch_registry.py, scripts/task_run/task_run.py, scripts/task_run/task_run_attempts.py, scripts/task_run/task_run_completion.py, scripts/task_run/task_run_completion_proof.py, scripts/task_run/task_run_detach.py, scripts/task_run/task_run_evidence.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_inventory.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_muse_events.py, scripts/task_run/task_run_prelaunch.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, scripts/task_run/task_run_state.py, tests/charness_cli/task_run_completion_support.py, tests/charness_cli/test_claude_home_unit.py, tests/charness_cli/test_codex_cache_refresh.py, tests/charness_cli/test_codex_managed_install.py, tests/charness_cli/test_doctor_cache_selection.py, tests/charness_cli/test_entry_cov_e5_874.py, tests/charness_cli/test_repo_script_payload_parsing.py, tests/charness_cli/test_task_run.py, tests/charness_cli/test_task_run_completion.py, tests/charness_cli/test_task_run_completion_deletions.py, tests/charness_cli/test_task_run_detach_wait_866.py, tests/charness_cli/test_task_run_executor_probe.py, tests/charness_cli/test_task_run_exit_codes.py, tests/charness_cli/test_task_run_fixtures.py, tests/charness_cli/test_task_run_friction.py, tests/charness_cli/test_task_run_implementation_lane.py, tests/charness_cli/test_task_run_launch_hygiene.py, tests/charness_cli/test_task_run_muse_stream_886.py, tests/charness_cli/test_task_run_parent_progress.py, tests/charness_cli/test_task_run_report_ledger.py, tests/charness_cli/test_task_run_result.py, tests/charness_cli/test_task_run_scope.py, tests/charness_cli/test_task_run_scope_deletions.py, tests/charness_cli/test_task_run_scope_mismatch_834.py, tests/charness_cli/test_task_run_self_review.py, tests/charness_cli/test_task_run_status_inventory.py, tests/charness_cli/test_task_run_steer.py, tests/charness_cli/test_tool_lifecycle.py, tests/charness_cli/test_uninstall_native_residue.py, tests/charness_cli/test_update_flow_unit.py, tests/charness_cli/test_update_output.py, tests/charness_cli/test_yaml_output_branch_coverage.py, tests/coverage_debt/test_batch10.py, tests/coverage_debt/test_batch5.py, tests/quality_gates/test_critique_enforcement_scope.py, tests/quality_gates/test_issue_bundled_closeout.py, tests/quality_gates/test_issue_worker_carrier.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_provider_boundary.py, tests/quality_gates/test_release_changed_line_coverage.py, tests/quality_gates/test_release_changed_line_staged_preflight.py, tests/quality_gates/test_review_invocation_command.py, tests/quality_gates/test_reviewer_delivery_state_machine.py, tests/quality_gates/test_reviewer_runner.py, tests/quality_gates/test_reviewer_tier_policy.py, tests/quality_gates/test_reviewer_worker.py, tests/quality_gates/test_reviewer_worker_backend.py, tests/quality_gates/test_reviewer_worker_report.py, tests/quality_gates/test_semantic_review_command.py, tests/test_command_guards.py, tests/test_common_runner_failure_coverage.py, tests/test_critique_prepare_packet.py, tests/test_grok_host_install.py, tests/test_review_followup.py, tests/test_review_followup_failures.py, tests/test_review_promotion_failures.py, tests/test_review_recovery_failures.py, tests/test_review_runner_terminal_paths.py, tests/test_reviewer_result_coverage.py, tests/test_run_review_declared_path_resolution.py, tests/test_runtime_scratch.py, tests/test_runtime_scratch_failures.py, tests/test_temp_producer_inventory.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/cli/cmd_task.py, scripts/mutation/release_changed_line_coverage.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/review/critique_packet_lib.py, scripts/runtime_scratch.py, scripts/runtime_scratch_cli.py, scripts/runtime_scratch_registry.py, scripts/task_run/task_run.py, scripts/task_run/task_run_attempts.py, scripts/task_run/task_run_completion.py, scripts/task_run/task_run_completion_proof.py, scripts/task_run/task_run_detach.py, scripts/task_run/task_run_evidence.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_inventory.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_muse_events.py, scripts/task_run/task_run_prelaunch.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, scripts/task_run/task_run_state.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/review_followup_provenance.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_invocation.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py, skills/public/critique/scripts/run_review_support.py, skills/public/critique/scripts/semantic_review_input.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
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
