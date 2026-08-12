# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-12T08:22:19Z
- **Prepared for**: release 5.0.0 current committed scope
- **Changed ref**: `v4.2.0..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `e3116788bfc37811591afa3a298fc71010625351056d575b55fa24b3a43b6a1a`
- **Reviewed paths**: 294
- **Sections**: 3
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for ref `v4.2.0..HEAD`:
- .agents/closeout-floor-matrix.json
- .agents/command-docs.yaml
- .agents/quality-adapter.yaml
- .agents/surfaces.json
- .github/workflows/mutation-tests.yml
- .github/workflows/quality-core.yml
- charness-artifacts/audit/2026-08-10-umbrella-class-survival-review.md
- charness-artifacts/audit/2026-08-11-pickup-deletion-experiment.patch
- charness-artifacts/audit/2026-08-12-shown-set-session-records-host-log-probe.md
- charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/finding.md
- charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/justification.md
- charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/observed.v1.json
- charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/summary.json
- charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/trace-digest.jsonl
- charness-artifacts/cautilus/latest.md
- charness-artifacts/critique/2026-08-10-203927-packet.json
- charness-artifacts/critique/2026-08-10-203927-packet.md
- charness-artifacts/critique/2026-08-10-issue-515-518-resolution-critique.md
- charness-artifacts/critique/2026-08-10-issue-546-declared-universe-pre-design-critique.md
- charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md
- charness-artifacts/critique/2026-08-10-issue-546-unenforceable-budget-critique.md
- charness-artifacts/critique/2026-08-10-issue-554-571-resolution-critique.md
- charness-artifacts/critique/2026-08-10-issue-591-floor-widening-closeout-critique.md
- charness-artifacts/critique/2026-08-11-deletable-surfaces-sweep.md
- charness-artifacts/critique/2026-08-11-umbrella-class-disposition-plan.md
- charness-artifacts/critique/2026-08-12-001253-packet.json
- charness-artifacts/critique/2026-08-12-001253-packet.md
- charness-artifacts/critique/2026-08-12-011040-packet.json
- charness-artifacts/critique/2026-08-12-011040-packet.md
- charness-artifacts/critique/2026-08-12-011526-packet.json
- charness-artifacts/critique/2026-08-12-011526-packet.md
- charness-artifacts/critique/2026-08-12-012152-packet.json
- charness-artifacts/critique/2026-08-12-012152-packet.md
- charness-artifacts/critique/2026-08-12-012525-packet.json
- charness-artifacts/critique/2026-08-12-012525-packet.md
- charness-artifacts/critique/2026-08-12-014829-packet.json
- charness-artifacts/critique/2026-08-12-014829-packet.md
- charness-artifacts/critique/2026-08-12-021730-packet.json
- charness-artifacts/critique/2026-08-12-021730-packet.md
- charness-artifacts/critique/2026-08-12-023240-packet.json
- charness-artifacts/critique/2026-08-12-023240-packet.md
- charness-artifacts/critique/2026-08-12-023722-packet.json
- charness-artifacts/critique/2026-08-12-023722-packet.md
- charness-artifacts/critique/2026-08-12-025103-packet.json
- charness-artifacts/critique/2026-08-12-025103-packet.md
- charness-artifacts/critique/2026-08-12-033958-packet.json
- charness-artifacts/critique/2026-08-12-033958-packet.md
- charness-artifacts/critique/2026-08-12-035924-packet.json
- charness-artifacts/critique/2026-08-12-035924-packet.md
- charness-artifacts/critique/2026-08-12-040146-packet.json
- charness-artifacts/critique/2026-08-12-040146-packet.md
- charness-artifacts/critique/2026-08-12-060853-packet.json
- charness-artifacts/critique/2026-08-12-060853-packet.md
- charness-artifacts/critique/2026-08-12-complete-local-lesson-ledger-capability-disposition-review.md
- charness-artifacts/critique/2026-08-12-contract-register-proof-critique.md
- charness-artifacts/critique/2026-08-12-critique-review.md
- charness-artifacts/critique/2026-08-12-first-score-cohort-policy-defer.md
- charness-artifacts/critique/2026-08-12-handoff-bullet-ownership-critique.md
- charness-artifacts/critique/2026-08-12-handoff-operator-decisions-critique.md
- charness-artifacts/critique/2026-08-12-lesson-score-authoring-proof-critique.md
- charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-packet.json
- charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-packet.md
- charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-repair-packet.json
- charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-repair-packet.md
- charness-artifacts/critique/2026-08-12-operator-rulings-goal-activation-critique.md
- charness-artifacts/critique/2026-08-12-operator-rulings-midpoint-claims-critique.md
- charness-artifacts/critique/2026-08-12-prepare-session-score-observation-disposition-review.md
- charness-artifacts/critique/2026-08-12-r3-timing-layer-ci-critique.md
- charness-artifacts/critique/2026-08-12-r5-judge-intent-scenario-critique.md
- charness-artifacts/critique/2026-08-12-r596-d47-snapshot-critique.md
- charness-artifacts/critique/2026-08-12-r6-boundary-bypass-content-identity-critique.md
- charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.json
- charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.md
- charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.json
- charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.md
- charness-artifacts/critique/2026-08-12-release-5-0-0-critique.md
- charness-artifacts/critique/2026-08-12-shown-set-session-records-disposition-review.md
- charness-artifacts/critique/operator-rulings-goal-activation-active-packet.json
- charness-artifacts/critique/operator-rulings-goal-activation-active-packet.md
- charness-artifacts/debug/2026-08-12-release-quality-record-contract-drift.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/gather/2026-08-10-wiki-g15e-com-pages-tasteful-software-md-536ebc23.md
- charness-artifacts/gather/latest.md
- charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md
- charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md
- charness-artifacts/goals/2026-08-12-complete-local-lesson-ledger-capability.md
- charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6-disposition-review.md
- charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md
- charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md
- charness-artifacts/goals/2026-08-12-shown-set-session-records.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
- charness-artifacts/probe/2026-08-01-inventory-marker-rule.json
- charness-artifacts/probe/2026-08-09-v4.2.0-release-observer.json
- charness-artifacts/probe/2026-08-12-inventory-marker-rule-snapshot.json
- charness-artifacts/quality/2026-08-12-quality-review.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/2026-08-12-v5.0.0-notes.md
- charness-artifacts/release/latest.md
- charness-artifacts/retro/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md
- charness-artifacts/retro/2026-08-11-120136-packet.json
- charness-artifacts/retro/2026-08-11-120136-packet.md
- charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md
- charness-artifacts/retro/2026-08-11-session-retro.md
- charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md
- charness-artifacts/retro/2026-08-12-001027-packet.json
- charness-artifacts/retro/2026-08-12-001027-packet.md
- charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md
- charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md
- charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md
- charness-artifacts/retro/2026-08-12-operator-rulings-2-3-5-6-closeout-retro.md
- charness-artifacts/retro/2026-08-12-session-retro.md
- charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md
- charness-artifacts/retro/contract-register.json
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json
- charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md
- charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md
- charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md
- charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md
- charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md
- charness-artifacts/spec/2026-08-11-six-operator-rulings.md
- charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md
- docs/conventions/implementation-discipline.md
- docs/conventions/validator-timing-layers.md
- docs/deferred-decisions.md
- docs/design-north-star.md
- docs/development.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- evals/cautilus/claim-fidelity-registry.json
- evals/cautilus/handoff-claim-fidelity/judge-intent.spec.json
- evals/cautilus/handoff-claim-fidelity/outcome-assertions.json
- evals/cautilus/handoff-claim-fidelity/pickup-ambiguous.spec.json
- evals/cautilus/handoff-claim-fidelity/pickup.spec.json
- evals/cautilus/handoff-claim-fidelity/refresh.spec.json
- evals/cautilus/handoff-claim-fidelity/spec.json
- plugins/charness/scripts/agent-runtime/build-skill-execution-observation.mjs
- plugins/charness/scripts/argparse_help_probe.py
- plugins/charness/scripts/argparse_surface_lib.py
- plugins/charness/scripts/boundary-bypass-baseline.json
- plugins/charness/scripts/boundary-bypass-exemptions.txt
- plugins/charness/scripts/boundary_bypass_ratchet_lib.py
- plugins/charness/scripts/check-markdown.sh
- plugins/charness/scripts/check_closeout_floor_matrix.py
- plugins/charness/scripts/check_contract_register.py
- plugins/charness/scripts/check_documented_command_flags.py
- plugins/charness/scripts/check_documented_subcommands.py
- plugins/charness/scripts/check_issue_closeout_commit_msg.py
- plugins/charness/scripts/check_js_mutation_score.py
- plugins/charness/scripts/check_lesson_ledger.py
- plugins/charness/scripts/check_mutation_score.py
- plugins/charness/scripts/check_runtime_budget_universe.py
- plugins/charness/scripts/check_timing_layer_completeness.py
- plugins/charness/scripts/check_title_slug_drift.py
- plugins/charness/scripts/check_upstream_support_drift.py
- plugins/charness/scripts/claim_fidelity_lib.py
- plugins/charness/scripts/closeout_floor_matrix_lib.py
- plugins/charness/scripts/closeout_floor_matrix_world.py
- plugins/charness/scripts/contract_register_lib.py
- plugins/charness/scripts/gate_report_emit.py
- plugins/charness/scripts/inventory_boundary_bypass_lib.py
- plugins/charness/scripts/lesson_ledger_lib.py
- plugins/charness/scripts/lesson_ledger_writer_lib.py
- plugins/charness/scripts/lesson_selection_preview_lib.py
- plugins/charness/scripts/markdown_doc_scan.py
- plugins/charness/scripts/mutation_baseline_abort_lib.py
- plugins/charness/scripts/quality_adapter_lib.py
- plugins/charness/scripts/quality_bootstrap_lib.py
- plugins/charness/scripts/quality_bootstrap_render.py
- plugins/charness/scripts/quality_label_universe.py
- plugins/charness/scripts/record_lesson_score.py
- plugins/charness/scripts/record_lesson_session.py
- plugins/charness/scripts/render_lesson_selection_preview.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/scripts/run_cosmic_ray_mutation.py
- plugins/charness/scripts/sample_mutation_files.py
- plugins/charness/scripts/slice_closeout_commit_advisories.py
- plugins/charness/scripts/staged_commit_gate_plan.py
- plugins/charness/scripts/subprocess_only_coverage_advisory.py
- plugins/charness/scripts/validate_handoff_artifact.py
- plugins/charness/scripts/validate_inventory_consumption.py
- plugins/charness/scripts/validate_scenario_conditional_reads.allowlist.txt
- plugins/charness/shared/scripts/check_title_slug_drift.py
- plugins/charness/skills/handoff/SKILL.md
- plugins/charness/skills/handoff/references/spill-targets.md
- plugins/charness/skills/handoff/references/state-selection.md
- plugins/charness/skills/handoff/scripts/handoff_bullet_ownership.py
- plugins/charness/skills/handoff/scripts/handoff_content_budget.py
- plugins/charness/skills/handoff/scripts/plan_handoff_run.py
- plugins/charness/skills/handoff/scripts/scaffold_handoff_artifact.py
- plugins/charness/skills/issue/references/closeout-discipline.md
- plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py
- plugins/charness/skills/issue/scripts/issue_close.py
- plugins/charness/skills/issue/scripts/issue_close_comment_floor.py
- plugins/charness/skills/issue/scripts/issue_closeout_rung1_floors.py
- plugins/charness/skills/issue/scripts/issue_tool.py
- plugins/charness/skills/issue/scripts/issue_verify_closeout.py
- plugins/charness/skills/issue/scripts/issue_verify_closeout_body.py
- plugins/charness/skills/quality/references/adapter-contract.md
- plugins/charness/skills/quality/references/attention-state-visibility.json
- plugins/charness/skills/quality/references/boundary-bypass-payload.example.json
- plugins/charness/skills/quality/references/boundary-bypass-ratchet.md
- plugins/charness/skills/quality/references/catalog.yaml
- plugins/charness/skills/quality/references/inventory-consumer-fields.json
- plugins/charness/skills/quality/references/inventory-dispatch.md
- plugins/charness/skills/quality/references/maintainer-local-enforcement.md
- plugins/charness/skills/quality/scripts/ci_local_gate_parity_lib.py
- plugins/charness/skills/quality/scripts/inventory_ubiquitous_language.py
- plugins/charness/skills/quality/scripts/run_dead_code_advisory.py
- plugins/charness/skills/quality/scripts/source_role_evidence.py
- plugins/charness/skills/quality/scripts/structural_waste_lib.py
- plugins/charness/skills/quality/scripts/validate_boundary_bypass_payload.py
- plugins/charness/skills/release/scripts/release_issue_closeout.py
- plugins/charness/skills/setup/scripts/render_skill_routing.py
- scripts/agent-runtime/build-skill-execution-observation.mjs
- scripts/argparse_help_probe.py
- scripts/argparse_surface_lib.py
- scripts/boundary-bypass-baseline.json
- scripts/boundary-bypass-exemptions.txt
- scripts/boundary_bypass_ratchet_lib.py
- scripts/check-markdown.sh
- scripts/check_closeout_floor_matrix.py
- scripts/check_contract_register.py
- scripts/check_documented_command_flags.py
- scripts/check_documented_subcommands.py
- scripts/check_issue_closeout_commit_msg.py
- scripts/check_js_mutation_score.py
- scripts/check_lesson_ledger.py
- scripts/check_mutation_score.py
- scripts/check_runtime_budget_universe.py
- scripts/check_timing_layer_completeness.py
- scripts/check_title_slug_drift.py
- scripts/check_upstream_support_drift.py
- scripts/claim_fidelity_lib.py
- scripts/closeout_floor_matrix_lib.py
- scripts/closeout_floor_matrix_world.py
- scripts/contract_register_lib.py
- scripts/gate_report_emit.py
- scripts/inventory_boundary_bypass_lib.py
- scripts/lesson_ledger_lib.py
- scripts/lesson_ledger_writer_lib.py
- scripts/lesson_selection_preview_lib.py
- scripts/markdown_doc_scan.py
- scripts/mutation_baseline_abort_lib.py
- scripts/quality_adapter_lib.py
- scripts/quality_bootstrap_lib.py
- scripts/quality_bootstrap_render.py
- scripts/quality_label_universe.py
- scripts/record_lesson_score.py
- scripts/record_lesson_session.py
- scripts/render_lesson_selection_preview.py
- scripts/run-quality.sh
- scripts/run_cosmic_ray_mutation.py
- scripts/sample_mutation_files.py
- scripts/slice_closeout_commit_advisories.py
- scripts/staged_commit_gate_plan.py
- scripts/subprocess_only_coverage_advisory.py
- scripts/validate_handoff_artifact.py
- scripts/validate_inventory_consumption.py
- scripts/validate_scenario_conditional_reads.allowlist.txt
- skills/public/handoff/SKILL.md
- skills/public/handoff/references/spill-targets.md
- skills/public/handoff/references/state-selection.md
- skills/public/handoff/scripts/handoff_bullet_ownership.py
- skills/public/handoff/scripts/handoff_content_budget.py
- skills/public/handoff/scripts/plan_handoff_run.py
- skills/public/handoff/scripts/scaffold_handoff_artifact.py
- skills/public/issue/references/closeout-discipline.md
- skills/public/issue/scripts/describe_closeout_draft_shape.py
- skills/public/issue/scripts/issue_close.py
- skills/public/issue/scripts/issue_close_comment_floor.py
- skills/public/issue/scripts/issue_closeout_rung1_floors.py
- skills/public/issue/scripts/issue_tool.py
- skills/public/issue/scripts/issue_verify_closeout.py
- skills/public/issue/scripts/issue_verify_closeout_body.py
- skills/public/quality/references/adapter-contract.md
- skills/public/quality/references/attention-state-visibility.json
- skills/public/quality/references/boundary-bypass-payload.example.json
- skills/public/quality/references/boundary-bypass-ratchet.md
- skills/public/quality/references/catalog.yaml
- skills/public/quality/references/inventory-consumer-fields.json
- skills/public/quality/references/inventory-dispatch.md
- skills/public/quality/references/maintainer-local-enforcement.md
- skills/public/quality/scripts/ci_local_gate_parity_lib.py
- skills/public/quality/scripts/inventory_ubiquitous_language.py
- skills/public/quality/scripts/run_dead_code_advisory.py
- skills/public/quality/scripts/source_role_evidence.py
- skills/public/quality/scripts/structural_waste_lib.py
- skills/public/quality/scripts/validate_boundary_bypass_payload.py
- skills/public/release/scripts/release_issue_closeout.py
- skills/public/setup/scripts/render_skill_routing.py
- skills/shared/scripts/check_title_slug_drift.py
- tests/agent-runtime/build-skill-execution-observation.test.mjs
- tests/handoff_artifact_fixtures.py
- tests/quality_gates/quality_bootstrap_support.py
- tests/quality_gates/support.py
- tests/quality_gates/test_adapter_version_reconciliation.py
- tests/quality_gates/test_argparse_surface_lib.py
- tests/quality_gates/test_boundary_bypass_payload_validator.py
- tests/quality_gates/test_claim_fidelity_specs.py
- tests/quality_gates/test_documented_command_flags.py
- tests/quality_gates/test_documented_subcommands.py
- tests/quality_gates/test_empty_scope_refusals.py
- tests/quality_gates/test_handoff_skill.py
- tests/quality_gates/test_inventory_ci_local_gate_parity.py
- tests/quality_gates/test_issue_close_comment_floor.py
- tests/quality_gates/test_issue_closeout_commit_msg_hook.py
- tests/quality_gates/test_issue_closeout_rung1_floors.py
- tests/quality_gates/test_issue_closeout_verifier_critique.py
- tests/quality_gates/test_issue_consolidated_closeout.py
- tests/quality_gates/test_issue_skill.py
- tests/quality_gates/test_issue_source_preservation.py
- tests/quality_gates/test_markdown_doc_scan.py
- tests/quality_gates/test_mutate_and_restore.py
- tests/quality_gates/test_mutation_baseline_abort.py
- tests/quality_gates/test_quality_bootstrap.py
- tests/quality_gates/test_quality_dead_code_advisory.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_quality_runner_label_universe.py
- tests/quality_gates/test_quality_ubiquitous_language.py
- tests/quality_gates/test_release_issue_closeout_behavioral_floor.py
- tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py
- tests/quality_gates/test_runtime_budget_universe.py
- tests/quality_gates/test_scenario_conditional_reads.py
- tests/quality_gates/test_setup_render_skill_routing.py
- tests/quality_gates/test_setup_routing_charness_managed.py
- tests/quality_gates/test_staged_commit_gate_plan.py
- tests/quality_gates/test_structural_waste_inventory.py
- tests/quality_gates/test_subagent_delegation_ladder.py
- tests/quality_gates/test_subprocess_only_coverage_advisory.py
- tests/quality_gates/test_timing_layer_completeness.py
- tests/quality_gates/test_title_slug_retirement_compatibility.py
- tests/test_boundary_bypass_inventory.py
- tests/test_boundary_bypass_ratchet.py
- tests/test_closeout_floor_matrix.py
- tests/test_contract_register.py
- tests/test_degradation_branch_coverage.py
- tests/test_doc_authoring_preflight.py
- tests/test_docs_graph_gate.py
- tests/test_evidence_boundary_crosswalk.py
- tests/test_handoff_artifact.py
- tests/test_handoff_bullet_ownership.py
- tests/test_handoff_plan.py
- tests/test_handoff_scaffold.py
- tests/test_inventory_marker_rule_measurement.py
- tests/test_issue_close_exemption_advisory.py
- tests/test_lesson_ledger.py
- tests/test_lesson_ledger_refusals.py
- tests/test_lesson_selection_preview.py
- tests/test_lifecycle_usage_capture.py
- tests/test_retro_scaffold.py
- tests/test_unhappy_path_branches.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/agent-runtime/build-skill-execution-observation.mjs, scripts/argparse_help_probe.py, scripts/argparse_surface_lib.py, scripts/boundary-bypass-baseline.json, scripts/boundary-bypass-exemptions.txt, scripts/boundary_bypass_ratchet_lib.py, scripts/check-markdown.sh, scripts/check_closeout_floor_matrix.py, scripts/check_contract_register.py, scripts/check_documented_command_flags.py, scripts/check_documented_subcommands.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_js_mutation_score.py, scripts/check_lesson_ledger.py, scripts/check_mutation_score.py, scripts/check_runtime_budget_universe.py, scripts/check_timing_layer_completeness.py, scripts/check_title_slug_drift.py, scripts/check_upstream_support_drift.py, scripts/claim_fidelity_lib.py, scripts/closeout_floor_matrix_lib.py, scripts/closeout_floor_matrix_world.py, scripts/contract_register_lib.py, scripts/gate_report_emit.py, scripts/inventory_boundary_bypass_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_ledger_writer_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_doc_scan.py, scripts/mutation_baseline_abort_lib.py, scripts/quality_adapter_lib.py, scripts/quality_bootstrap_lib.py, scripts/quality_bootstrap_render.py, scripts/quality_label_universe.py, scripts/record_lesson_score.py, scripts/record_lesson_session.py, scripts/render_lesson_selection_preview.py, scripts/run-quality.sh, scripts/run_cosmic_ray_mutation.py, scripts/sample_mutation_files.py, scripts/slice_closeout_commit_advisories.py, scripts/staged_commit_gate_plan.py, scripts/subprocess_only_coverage_advisory.py, scripts/validate_handoff_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_scenario_conditional_reads.allowlist.txt, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/handoff/scripts/handoff_bullet_ownership.py, skills/public/handoff/scripts/handoff_content_budget.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/handoff/scripts/scaffold_handoff_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_tool.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/inventory_ubiquitous_language.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/source_role_evidence.py, skills/public/quality/scripts/structural_waste_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/setup/scripts/render_skill_routing.py, skills/shared/scripts/check_title_slug_drift.py
  derived matches: plugins/charness/scripts/agent-runtime/build-skill-execution-observation.mjs, plugins/charness/scripts/argparse_help_probe.py, plugins/charness/scripts/argparse_surface_lib.py, plugins/charness/scripts/boundary-bypass-baseline.json, plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check-markdown.sh, plugins/charness/scripts/check_closeout_floor_matrix.py, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_documented_command_flags.py, plugins/charness/scripts/check_documented_subcommands.py, plugins/charness/scripts/check_issue_closeout_commit_msg.py, plugins/charness/scripts/check_js_mutation_score.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/check_mutation_score.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/check_timing_layer_completeness.py, plugins/charness/scripts/check_title_slug_drift.py, plugins/charness/scripts/check_upstream_support_drift.py, plugins/charness/scripts/claim_fidelity_lib.py, plugins/charness/scripts/closeout_floor_matrix_lib.py, plugins/charness/scripts/closeout_floor_matrix_world.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/gate_report_emit.py, plugins/charness/scripts/inventory_boundary_bypass_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_ledger_writer_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/markdown_doc_scan.py, plugins/charness/scripts/mutation_baseline_abort_lib.py, plugins/charness/scripts/quality_adapter_lib.py, plugins/charness/scripts/quality_bootstrap_lib.py, plugins/charness/scripts/quality_bootstrap_render.py, plugins/charness/scripts/quality_label_universe.py, plugins/charness/scripts/record_lesson_score.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_cosmic_ray_mutation.py, plugins/charness/scripts/sample_mutation_files.py, plugins/charness/scripts/slice_closeout_commit_advisories.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/subprocess_only_coverage_advisory.py, plugins/charness/scripts/validate_handoff_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_scenario_conditional_reads.allowlist.txt, plugins/charness/shared/scripts/check_title_slug_drift.py, plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/handoff/references/state-selection.md, plugins/charness/skills/handoff/scripts/handoff_bullet_ownership.py, plugins/charness/skills/handoff/scripts/handoff_content_budget.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/handoff/scripts/scaffold_handoff_artifact.py, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_close_comment_floor.py, plugins/charness/skills/issue/scripts/issue_closeout_rung1_floors.py, plugins/charness/skills/issue/scripts/issue_tool.py, plugins/charness/skills/issue/scripts/issue_verify_closeout.py, plugins/charness/skills/issue/scripts/issue_verify_closeout_body.py, plugins/charness/skills/quality/references/adapter-contract.md, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/quality/references/boundary-bypass-payload.example.json, plugins/charness/skills/quality/references/boundary-bypass-ratchet.md, plugins/charness/skills/quality/references/catalog.yaml, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/references/inventory-dispatch.md, plugins/charness/skills/quality/references/maintainer-local-enforcement.md, plugins/charness/skills/quality/scripts/ci_local_gate_parity_lib.py, plugins/charness/skills/quality/scripts/inventory_ubiquitous_language.py, plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/source_role_evidence.py, plugins/charness/skills/quality/scripts/structural_waste_lib.py, plugins/charness/skills/quality/scripts/validate_boundary_bypass_payload.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/setup/scripts/render_skill_routing.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: .agents/command-docs.yaml, charness-artifacts/audit/2026-08-10-umbrella-class-survival-review.md, charness-artifacts/audit/2026-08-12-shown-set-session-records-host-log-probe.md, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/finding.md, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/justification.md, charness-artifacts/cautilus/latest.md, charness-artifacts/critique/2026-08-10-203927-packet.md, charness-artifacts/critique/2026-08-10-issue-515-518-resolution-critique.md, charness-artifacts/critique/2026-08-10-issue-546-declared-universe-pre-design-critique.md, charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md, charness-artifacts/critique/2026-08-10-issue-546-unenforceable-budget-critique.md, charness-artifacts/critique/2026-08-10-issue-554-571-resolution-critique.md, charness-artifacts/critique/2026-08-10-issue-591-floor-widening-closeout-critique.md, charness-artifacts/critique/2026-08-11-deletable-surfaces-sweep.md, charness-artifacts/critique/2026-08-11-umbrella-class-disposition-plan.md, charness-artifacts/critique/2026-08-12-001253-packet.md, charness-artifacts/critique/2026-08-12-011040-packet.md, charness-artifacts/critique/2026-08-12-011526-packet.md, charness-artifacts/critique/2026-08-12-012152-packet.md, charness-artifacts/critique/2026-08-12-012525-packet.md, charness-artifacts/critique/2026-08-12-014829-packet.md, charness-artifacts/critique/2026-08-12-021730-packet.md, charness-artifacts/critique/2026-08-12-023240-packet.md, charness-artifacts/critique/2026-08-12-023722-packet.md, charness-artifacts/critique/2026-08-12-025103-packet.md, charness-artifacts/critique/2026-08-12-033958-packet.md, charness-artifacts/critique/2026-08-12-035924-packet.md, charness-artifacts/critique/2026-08-12-040146-packet.md, charness-artifacts/critique/2026-08-12-060853-packet.md, charness-artifacts/critique/2026-08-12-complete-local-lesson-ledger-capability-disposition-review.md, charness-artifacts/critique/2026-08-12-contract-register-proof-critique.md, charness-artifacts/critique/2026-08-12-critique-review.md, charness-artifacts/critique/2026-08-12-first-score-cohort-policy-defer.md, charness-artifacts/critique/2026-08-12-handoff-bullet-ownership-critique.md, charness-artifacts/critique/2026-08-12-handoff-operator-decisions-critique.md, charness-artifacts/critique/2026-08-12-lesson-score-authoring-proof-critique.md, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-packet.md, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-repair-packet.md, charness-artifacts/critique/2026-08-12-operator-rulings-goal-activation-critique.md, charness-artifacts/critique/2026-08-12-operator-rulings-midpoint-claims-critique.md, charness-artifacts/critique/2026-08-12-prepare-session-score-observation-disposition-review.md, charness-artifacts/critique/2026-08-12-r3-timing-layer-ci-critique.md, charness-artifacts/critique/2026-08-12-r5-judge-intent-scenario-critique.md, charness-artifacts/critique/2026-08-12-r596-d47-snapshot-critique.md, charness-artifacts/critique/2026-08-12-r6-boundary-bypass-content-identity-critique.md, charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.md, charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.md, charness-artifacts/critique/2026-08-12-release-5-0-0-critique.md, charness-artifacts/critique/2026-08-12-shown-set-session-records-disposition-review.md, charness-artifacts/critique/operator-rulings-goal-activation-active-packet.md, charness-artifacts/debug/2026-08-12-release-quality-record-contract-drift.md, charness-artifacts/debug/latest.md, charness-artifacts/gather/2026-08-10-wiki-g15e-com-pages-tasteful-software-md-536ebc23.md, charness-artifacts/gather/latest.md, charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md, charness-artifacts/goals/2026-08-12-compare-score-policy-evidence.md, charness-artifacts/goals/2026-08-12-complete-local-lesson-ledger-capability.md, charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6-disposition-review.md, charness-artifacts/goals/2026-08-12-execute-operator-rulings-2-3-5-6.md, charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md, charness-artifacts/goals/2026-08-12-shown-set-session-records.md, charness-artifacts/quality/2026-08-12-quality-review.md, charness-artifacts/quality/latest.md, charness-artifacts/release/2026-08-12-v5.0.0-notes.md, charness-artifacts/release/latest.md, charness-artifacts/retro/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md, charness-artifacts/retro/2026-08-11-120136-packet.md, charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md, charness-artifacts/retro/2026-08-11-session-retro.md, charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md, charness-artifacts/retro/2026-08-12-001027-packet.md, charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md, charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md, charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md, charness-artifacts/retro/2026-08-12-operator-rulings-2-3-5-6-closeout-retro.md, charness-artifacts/retro/2026-08-12-session-retro.md, charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md, charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md, charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md, charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md, charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md, charness-artifacts/spec/2026-08-11-six-operator-rulings.md, charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md, docs/conventions/implementation-discipline.md, docs/conventions/validator-timing-layers.md, docs/deferred-decisions.md, docs/design-north-star.md, docs/development.md, docs/handoff.md, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/issue/references/closeout-discipline.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md
  derived matches: plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/handoff/references/state-selection.md, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/quality/references/adapter-contract.md, plugins/charness/skills/quality/references/boundary-bypass-ratchet.md, plugins/charness/skills/quality/references/inventory-dispatch.md, plugins/charness/skills/quality/references/maintainer-local-enforcement.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- handoff-machine-readers: docs/handoff.md is a rotating human document that is ALSO a machine-read source: the publish-state ledger declares it as a source locator, and the retro-memory gate requires its recent-lessons reference.
  source matches: docs/handoff.md
  verify: python3 scripts/publish_state_ledger.py --repo-root ., python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/quality-adapter.yaml, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/issue/references/closeout-discipline.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md
  derived matches: charness-artifacts/cautilus/latest.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- claim-fidelity-capture-bundles: Ask-before-run claim-fidelity capture bundles under charness-artifacts/cautilus/: per-run observed packets, trace digests, transcripts, probes, and findings that prove a floor move or keep.
  source matches: charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/finding.md, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/justification.md, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/observed.v1.json, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/summary.json, charness-artifacts/cautilus/handoff-judge-intent-2026-08-12/trace-digest.jsonl
  verify: for path in charness-artifacts/cautilus/*/*.json; do [ -e "$path" ] && { python3 -m json.tool "$path" >/dev/null || exit $?; }; done
- claim-fidelity-specs: Per-skill Cautilus claim-fidelity specs and registry: each public skill's reference-engagement classification proving a real /charness:<skill> run honors its own reference routing.
  source matches: evals/cautilus/claim-fidelity-registry.json, evals/cautilus/handoff-claim-fidelity/judge-intent.spec.json, evals/cautilus/handoff-claim-fidelity/outcome-assertions.json, evals/cautilus/handoff-claim-fidelity/pickup-ambiguous.spec.json, evals/cautilus/handoff-claim-fidelity/pickup.spec.json, evals/cautilus/handoff-claim-fidelity/refresh.spec.json, evals/cautilus/handoff-claim-fidelity/spec.json
  verify: python3 scripts/validate_claim_fidelity_specs.py --repo-root ., python3 scripts/validate_outcome_assertions.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/handoff/scripts/handoff_bullet_ownership.py, skills/public/handoff/scripts/handoff_content_budget.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/handoff/scripts/scaffold_handoff_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_tool.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/inventory_ubiquitous_language.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/source_role_evidence.py, skills/public/quality/scripts/structural_waste_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/setup/scripts/render_skill_routing.py, skills/shared/scripts/check_title_slug_drift.py
  derived matches: plugins/charness/shared/scripts/check_title_slug_drift.py, plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/handoff/references/state-selection.md, plugins/charness/skills/handoff/scripts/handoff_bullet_ownership.py, plugins/charness/skills/handoff/scripts/handoff_content_budget.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/handoff/scripts/scaffold_handoff_artifact.py, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_close_comment_floor.py, plugins/charness/skills/issue/scripts/issue_closeout_rung1_floors.py, plugins/charness/skills/issue/scripts/issue_tool.py, plugins/charness/skills/issue/scripts/issue_verify_closeout.py, plugins/charness/skills/issue/scripts/issue_verify_closeout_body.py, plugins/charness/skills/quality/references/adapter-contract.md, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/quality/references/boundary-bypass-payload.example.json, plugins/charness/skills/quality/references/boundary-bypass-ratchet.md, plugins/charness/skills/quality/references/catalog.yaml, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/references/inventory-dispatch.md, plugins/charness/skills/quality/references/maintainer-local-enforcement.md, plugins/charness/skills/quality/scripts/ci_local_gate_parity_lib.py, plugins/charness/skills/quality/scripts/inventory_ubiquitous_language.py, plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/source_role_evidence.py, plugins/charness/skills/quality/scripts/structural_waste_lib.py, plugins/charness/skills/quality/scripts/validate_boundary_bypass_payload.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/setup/scripts/render_skill_routing.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/handoff/scripts/handoff_bullet_ownership.py, skills/public/handoff/scripts/handoff_content_budget.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/handoff/scripts/scaffold_handoff_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_tool.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/inventory_ubiquitous_language.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/source_role_evidence.py, skills/public/quality/scripts/structural_waste_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/setup/scripts/render_skill_routing.py, skills/shared/scripts/check_title_slug_drift.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/references/state-selection.md, skills/public/handoff/scripts/handoff_bullet_ownership.py, skills/public/handoff/scripts/handoff_content_budget.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/handoff/scripts/scaffold_handoff_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_tool.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/references/boundary-bypass-payload.example.json, skills/public/quality/references/boundary-bypass-ratchet.md, skills/public/quality/references/catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/references/inventory-dispatch.md, skills/public/quality/references/maintainer-local-enforcement.md, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/inventory_ubiquitous_language.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/source_role_evidence.py, skills/public/quality/scripts/structural_waste_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/setup/scripts/render_skill_routing.py, skills/shared/scripts/check_title_slug_drift.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/quality-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- agent-runtime-js: Repo-owned JavaScript agent-runtime modules and their native test command.
  source matches: scripts/agent-runtime/build-skill-execution-observation.mjs, tests/agent-runtime/build-skill-execution-observation.test.mjs
  verify: npm run test:agent-runtime, npm run test:mutation:js:dry-run
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: .agents/quality-adapter.yaml, .github/workflows/mutation-tests.yml, scripts/check_js_mutation_score.py, scripts/check_mutation_score.py, scripts/run_cosmic_ray_mutation.py, scripts/sample_mutation_files.py
  derived matches: plugins/charness/scripts/check_js_mutation_score.py, plugins/charness/scripts/check_mutation_score.py, plugins/charness/scripts/run_cosmic_ray_mutation.py, plugins/charness/scripts/sample_mutation_files.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 scripts/check_github_actions.py --repo-root ., python3 scripts/validate_adapters.py --repo-root ., python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- quality-core-workflow: Repo-local light push/tag CI plus the CI-PR changed-line mutation mirror (consumer-inert; every step invokes a repo-owned validator).
  source matches: .github/workflows/quality-core.yml
  verify: python3 scripts/check_github_actions.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-10-203927-packet.json, charness-artifacts/critique/2026-08-10-203927-packet.md, charness-artifacts/critique/2026-08-10-issue-515-518-resolution-critique.md, charness-artifacts/critique/2026-08-10-issue-546-declared-universe-pre-design-critique.md, charness-artifacts/critique/2026-08-10-issue-546-label-universe-implementation-critique.md, charness-artifacts/critique/2026-08-10-issue-546-unenforceable-budget-critique.md, charness-artifacts/critique/2026-08-10-issue-554-571-resolution-critique.md, charness-artifacts/critique/2026-08-10-issue-591-floor-widening-closeout-critique.md, charness-artifacts/critique/2026-08-11-deletable-surfaces-sweep.md, charness-artifacts/critique/2026-08-11-umbrella-class-disposition-plan.md, charness-artifacts/critique/2026-08-12-001253-packet.json, charness-artifacts/critique/2026-08-12-001253-packet.md, charness-artifacts/critique/2026-08-12-011040-packet.json, charness-artifacts/critique/2026-08-12-011040-packet.md, charness-artifacts/critique/2026-08-12-011526-packet.json, charness-artifacts/critique/2026-08-12-011526-packet.md, charness-artifacts/critique/2026-08-12-012152-packet.json, charness-artifacts/critique/2026-08-12-012152-packet.md, charness-artifacts/critique/2026-08-12-012525-packet.json, charness-artifacts/critique/2026-08-12-012525-packet.md, charness-artifacts/critique/2026-08-12-014829-packet.json, charness-artifacts/critique/2026-08-12-014829-packet.md, charness-artifacts/critique/2026-08-12-021730-packet.json, charness-artifacts/critique/2026-08-12-021730-packet.md, charness-artifacts/critique/2026-08-12-023240-packet.json, charness-artifacts/critique/2026-08-12-023240-packet.md, charness-artifacts/critique/2026-08-12-023722-packet.json, charness-artifacts/critique/2026-08-12-023722-packet.md, charness-artifacts/critique/2026-08-12-025103-packet.json, charness-artifacts/critique/2026-08-12-025103-packet.md, charness-artifacts/critique/2026-08-12-033958-packet.json, charness-artifacts/critique/2026-08-12-033958-packet.md, charness-artifacts/critique/2026-08-12-035924-packet.json, charness-artifacts/critique/2026-08-12-035924-packet.md, charness-artifacts/critique/2026-08-12-040146-packet.json, charness-artifacts/critique/2026-08-12-040146-packet.md, charness-artifacts/critique/2026-08-12-060853-packet.json, charness-artifacts/critique/2026-08-12-060853-packet.md, charness-artifacts/critique/2026-08-12-complete-local-lesson-ledger-capability-disposition-review.md, charness-artifacts/critique/2026-08-12-contract-register-proof-critique.md, charness-artifacts/critique/2026-08-12-critique-review.md, charness-artifacts/critique/2026-08-12-first-score-cohort-policy-defer.md, charness-artifacts/critique/2026-08-12-handoff-bullet-ownership-critique.md, charness-artifacts/critique/2026-08-12-handoff-operator-decisions-critique.md, charness-artifacts/critique/2026-08-12-lesson-score-authoring-proof-critique.md, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-packet.json, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-packet.md, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-repair-packet.json, charness-artifacts/critique/2026-08-12-operator-rulings-final-claims-repair-packet.md, charness-artifacts/critique/2026-08-12-operator-rulings-goal-activation-critique.md, charness-artifacts/critique/2026-08-12-operator-rulings-midpoint-claims-critique.md, charness-artifacts/critique/2026-08-12-prepare-session-score-observation-disposition-review.md, charness-artifacts/critique/2026-08-12-r3-timing-layer-ci-critique.md, charness-artifacts/critique/2026-08-12-r5-judge-intent-scenario-critique.md, charness-artifacts/critique/2026-08-12-r596-d47-snapshot-critique.md, charness-artifacts/critique/2026-08-12-r6-boundary-bypass-content-identity-critique.md, charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.json, charness-artifacts/critique/2026-08-12-r6-repair-round2-packet.md, charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.json, charness-artifacts/critique/2026-08-12-release-5-0-0-critique-packet.md, charness-artifacts/critique/2026-08-12-release-5-0-0-critique.md, charness-artifacts/critique/2026-08-12-shown-set-session-records-disposition-review.md, charness-artifacts/critique/operator-rulings-goal-activation-active-packet.json, charness-artifacts/critique/operator-rulings-goal-activation-active-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json, charness-artifacts/probe/2026-08-01-inventory-marker-rule.json, charness-artifacts/probe/2026-08-09-v4.2.0-release-observer.json, charness-artifacts/probe/2026-08-12-inventory-marker-rule-snapshot.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- audit-evidence-attachments: Preserved diffs (*.patch) committed under charness-artifacts/audit/ alongside the audit or spec artifact that cites them. The audit's own *.md prose is covered by repo-markdown; this surface owns only the .patch extension repo-markdown cannot match. Scoped to .patch on purpose: another attachment extension under the same directory should get its own content check rather than inherit a diff parser, so it still trips unmatched_surface_path until someone decides what verifies it.
  source matches: charness-artifacts/audit/2026-08-11-pickup-deletion-experiment.patch
  verify: for path in charness-artifacts/audit/*.patch; do [ -e "$path" ] || continue; git apply --stat "$path" >/dev/null || exit $?; done, ./scripts/check-secrets.sh
- retired-closeout-authorization-instance: The retired #514/#515/#518 evidence-boundary crosswalk instance and the record that retired it. The crosswalk path is declared here while ABSENT on purpose: the deletion of a proof-surface instance is itself a change that needs an owning surface, and this one's verify command asserts the absence rather than the file.
  source matches: charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json, charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md
  verify: python3 -m pytest -q tests/test_evidence_boundary_crosswalk.py::test_this_repo_checks_in_no_crosswalk_instance tests/test_evidence_boundary_crosswalk.py::test_absent_instance_is_reported_as_inapplicable_not_as_a_pass tests/test_evidence_boundary_crosswalk.py::test_the_installed_plugin_projection_exposes_the_same_authorization_entrypoint
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-12-release-quality-record-contract-drift.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md, charness-artifacts/retro/2026-08-11-120136-packet.json, charness-artifacts/retro/2026-08-11-120136-packet.md, charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md, charness-artifacts/retro/2026-08-11-session-retro.md, charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md, charness-artifacts/retro/2026-08-12-001027-packet.json, charness-artifacts/retro/2026-08-12-001027-packet.md, charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md, charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md, charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md, charness-artifacts/retro/2026-08-12-operator-rulings-2-3-5-6-closeout-retro.md, charness-artifacts/retro/2026-08-12-session-retro.md, charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/contract-register.json, charness-artifacts/retro/lesson-ledger.json, scripts/check_contract_register.py, scripts/check_lesson_ledger.py, scripts/contract_register_lib.py, scripts/lesson_ledger_lib.py, scripts/record_lesson_score.py
  derived matches: plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/record_lesson_score.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/agent-runtime/build-skill-execution-observation.mjs, plugins/charness/scripts/argparse_help_probe.py, plugins/charness/scripts/argparse_surface_lib.py, plugins/charness/scripts/boundary-bypass-baseline.json, plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check-markdown.sh, plugins/charness/scripts/check_closeout_floor_matrix.py, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_documented_command_flags.py, plugins/charness/scripts/check_documented_subcommands.py, plugins/charness/scripts/check_issue_closeout_commit_msg.py, plugins/charness/scripts/check_js_mutation_score.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/check_mutation_score.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/check_timing_layer_completeness.py, plugins/charness/scripts/check_title_slug_drift.py, plugins/charness/scripts/check_upstream_support_drift.py, plugins/charness/scripts/claim_fidelity_lib.py, plugins/charness/scripts/closeout_floor_matrix_lib.py, plugins/charness/scripts/closeout_floor_matrix_world.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/gate_report_emit.py, plugins/charness/scripts/inventory_boundary_bypass_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_ledger_writer_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/markdown_doc_scan.py, plugins/charness/scripts/mutation_baseline_abort_lib.py, plugins/charness/scripts/quality_adapter_lib.py, plugins/charness/scripts/quality_bootstrap_lib.py, plugins/charness/scripts/quality_bootstrap_render.py, plugins/charness/scripts/quality_label_universe.py, plugins/charness/scripts/record_lesson_score.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_cosmic_ray_mutation.py, plugins/charness/scripts/sample_mutation_files.py, plugins/charness/scripts/slice_closeout_commit_advisories.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/subprocess_only_coverage_advisory.py, plugins/charness/scripts/validate_handoff_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_scenario_conditional_reads.allowlist.txt
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/argparse_help_probe.py, scripts/argparse_surface_lib.py, scripts/boundary_bypass_ratchet_lib.py, scripts/check_closeout_floor_matrix.py, scripts/check_contract_register.py, scripts/check_documented_command_flags.py, scripts/check_documented_subcommands.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_js_mutation_score.py, scripts/check_lesson_ledger.py, scripts/check_mutation_score.py, scripts/check_runtime_budget_universe.py, scripts/check_timing_layer_completeness.py, scripts/check_title_slug_drift.py, scripts/check_upstream_support_drift.py, scripts/claim_fidelity_lib.py, scripts/closeout_floor_matrix_lib.py, scripts/closeout_floor_matrix_world.py, scripts/contract_register_lib.py, scripts/gate_report_emit.py, scripts/inventory_boundary_bypass_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_ledger_writer_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_doc_scan.py, scripts/mutation_baseline_abort_lib.py, scripts/quality_adapter_lib.py, scripts/quality_bootstrap_lib.py, scripts/quality_bootstrap_render.py, scripts/quality_label_universe.py, scripts/record_lesson_score.py, scripts/record_lesson_session.py, scripts/render_lesson_selection_preview.py, scripts/run_cosmic_ray_mutation.py, scripts/sample_mutation_files.py, scripts/slice_closeout_commit_advisories.py, scripts/staged_commit_gate_plan.py, scripts/subprocess_only_coverage_advisory.py, scripts/validate_handoff_artifact.py, scripts/validate_inventory_consumption.py, tests/handoff_artifact_fixtures.py, tests/quality_gates/quality_bootstrap_support.py, tests/quality_gates/support.py, tests/quality_gates/test_adapter_version_reconciliation.py, tests/quality_gates/test_argparse_surface_lib.py, tests/quality_gates/test_boundary_bypass_payload_validator.py, tests/quality_gates/test_claim_fidelity_specs.py, tests/quality_gates/test_documented_command_flags.py, tests/quality_gates/test_documented_subcommands.py, tests/quality_gates/test_empty_scope_refusals.py, tests/quality_gates/test_handoff_skill.py, tests/quality_gates/test_inventory_ci_local_gate_parity.py, tests/quality_gates/test_issue_close_comment_floor.py, tests/quality_gates/test_issue_closeout_commit_msg_hook.py, tests/quality_gates/test_issue_closeout_rung1_floors.py, tests/quality_gates/test_issue_closeout_verifier_critique.py, tests/quality_gates/test_issue_consolidated_closeout.py, tests/quality_gates/test_issue_skill.py, tests/quality_gates/test_issue_source_preservation.py, tests/quality_gates/test_markdown_doc_scan.py, tests/quality_gates/test_mutate_and_restore.py, tests/quality_gates/test_mutation_baseline_abort.py, tests/quality_gates/test_quality_bootstrap.py, tests/quality_gates/test_quality_dead_code_advisory.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_quality_runner_label_universe.py, tests/quality_gates/test_quality_ubiquitous_language.py, tests/quality_gates/test_release_issue_closeout_behavioral_floor.py, tests/quality_gates/test_run_cosmic_ray_mutation_resilience.py, tests/quality_gates/test_runtime_budget_universe.py, tests/quality_gates/test_scenario_conditional_reads.py, tests/quality_gates/test_setup_render_skill_routing.py, tests/quality_gates/test_setup_routing_charness_managed.py, tests/quality_gates/test_staged_commit_gate_plan.py, tests/quality_gates/test_structural_waste_inventory.py, tests/quality_gates/test_subagent_delegation_ladder.py, tests/quality_gates/test_subprocess_only_coverage_advisory.py, tests/quality_gates/test_timing_layer_completeness.py, tests/quality_gates/test_title_slug_retirement_compatibility.py, tests/test_boundary_bypass_inventory.py, tests/test_boundary_bypass_ratchet.py, tests/test_closeout_floor_matrix.py, tests/test_contract_register.py, tests/test_degradation_branch_coverage.py, tests/test_doc_authoring_preflight.py, tests/test_docs_graph_gate.py, tests/test_evidence_boundary_crosswalk.py, tests/test_handoff_artifact.py, tests/test_handoff_bullet_ownership.py, tests/test_handoff_plan.py, tests/test_handoff_scaffold.py, tests/test_inventory_marker_rule_measurement.py, tests/test_issue_close_exemption_advisory.py, tests/test_lesson_ledger.py, tests/test_lesson_ledger_refusals.py, tests/test_lesson_selection_preview.py, tests/test_lifecycle_usage_capture.py, tests/test_retro_scaffold.py, tests/test_unhappy_path_branches.py
  derived matches: plugins/charness/scripts/argparse_help_probe.py, plugins/charness/scripts/argparse_surface_lib.py, plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check_closeout_floor_matrix.py, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_documented_command_flags.py, plugins/charness/scripts/check_documented_subcommands.py, plugins/charness/scripts/check_issue_closeout_commit_msg.py, plugins/charness/scripts/check_js_mutation_score.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/check_mutation_score.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/check_timing_layer_completeness.py, plugins/charness/scripts/check_title_slug_drift.py, plugins/charness/scripts/check_upstream_support_drift.py, plugins/charness/scripts/claim_fidelity_lib.py, plugins/charness/scripts/closeout_floor_matrix_lib.py, plugins/charness/scripts/closeout_floor_matrix_world.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/gate_report_emit.py, plugins/charness/scripts/inventory_boundary_bypass_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_ledger_writer_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/markdown_doc_scan.py, plugins/charness/scripts/mutation_baseline_abort_lib.py, plugins/charness/scripts/quality_adapter_lib.py, plugins/charness/scripts/quality_bootstrap_lib.py, plugins/charness/scripts/quality_bootstrap_render.py, plugins/charness/scripts/quality_label_universe.py, plugins/charness/scripts/record_lesson_score.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run_cosmic_ray_mutation.py, plugins/charness/scripts/sample_mutation_files.py, plugins/charness/scripts/slice_closeout_commit_advisories.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/subprocess_only_coverage_advisory.py, plugins/charness/scripts/validate_handoff_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/argparse_help_probe.py, scripts/argparse_surface_lib.py, scripts/boundary_bypass_ratchet_lib.py, scripts/check_closeout_floor_matrix.py, scripts/check_contract_register.py, scripts/check_documented_command_flags.py, scripts/check_documented_subcommands.py, scripts/check_issue_closeout_commit_msg.py, scripts/check_js_mutation_score.py, scripts/check_lesson_ledger.py, scripts/check_mutation_score.py, scripts/check_runtime_budget_universe.py, scripts/check_timing_layer_completeness.py, scripts/check_title_slug_drift.py, scripts/check_upstream_support_drift.py, scripts/claim_fidelity_lib.py, scripts/closeout_floor_matrix_lib.py, scripts/closeout_floor_matrix_world.py, scripts/contract_register_lib.py, scripts/gate_report_emit.py, scripts/inventory_boundary_bypass_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_ledger_writer_lib.py, scripts/lesson_selection_preview_lib.py, scripts/markdown_doc_scan.py, scripts/mutation_baseline_abort_lib.py, scripts/quality_adapter_lib.py, scripts/quality_bootstrap_lib.py, scripts/quality_bootstrap_render.py, scripts/quality_label_universe.py, scripts/record_lesson_score.py, scripts/record_lesson_session.py, scripts/render_lesson_selection_preview.py, scripts/run_cosmic_ray_mutation.py, scripts/sample_mutation_files.py, scripts/slice_closeout_commit_advisories.py, scripts/staged_commit_gate_plan.py, scripts/subprocess_only_coverage_advisory.py, scripts/validate_handoff_artifact.py, scripts/validate_inventory_consumption.py, skills/public/handoff/scripts/handoff_bullet_ownership.py, skills/public/handoff/scripts/handoff_content_budget.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/handoff/scripts/scaffold_handoff_artifact.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_tool.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/quality/scripts/ci_local_gate_parity_lib.py, skills/public/quality/scripts/inventory_ubiquitous_language.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/source_role_evidence.py, skills/public/quality/scripts/structural_waste_lib.py, skills/public/quality/scripts/validate_boundary_bypass_payload.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/setup/scripts/render_skill_routing.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- closeout-floor-matrix: Declared floor x classification x carrier matrix for issue closeout, and the behavioral probe that re-derives it from the real carriers.
  source matches: .agents/closeout-floor-matrix.json, scripts/check_closeout_floor_matrix.py, scripts/check_issue_closeout_commit_msg.py, scripts/closeout_floor_matrix_lib.py, scripts/closeout_floor_matrix_world.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_close_comment_floor.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_body.py, skills/public/release/scripts/release_issue_closeout.py
  verify: python3 scripts/check_closeout_floor_matrix.py --repo-root .

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section ok**: True

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
