# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-09-06T07:21:22Z
- **Prepared for**: Goal 805 delegation net value and one integrated 8.5.0 release
- **Substrate mode**: `committed-ref`
- **Changed ref**: `af7c1b784cf9893aff10f6138c49c1bca2288059..bd3e677dd4cdbea0253d462e7ea42ae18d83c946`
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 2
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `af7c1b784cf9893aff10f6138c49c1bca2288059..bd3e677dd4cdbea0253d462e7ea42ae18d83c946`:
- .claude-plugin/marketplace.json
- .gitleaks.toml
- charness-artifacts/create-skill/2026-09-06-context-reuse-brief.md
- charness-artifacts/critique/2026-09-06-goal805-release-8-5-0.md
- charness-artifacts/critique/delegation-framing-integrity-1-packet.json
- charness-artifacts/critique/delegation-framing-integrity-1-packet.md
- charness-artifacts/critique/delegation-framing-product-1-packet.json
- charness-artifacts/critique/delegation-framing-product-1-packet.md
- charness-artifacts/critique/delegation-readiness-followup-3-packet.json
- charness-artifacts/critique/delegation-readiness-followup-3-packet.md
- charness-artifacts/critique/delegation-whole-product-2-packet.json
- charness-artifacts/critique/delegation-whole-product-2-packet.md
- charness-artifacts/critique/goal805-closeout-causal-packet.json
- charness-artifacts/critique/goal805-closeout-causal-packet.md
- charness-artifacts/critique/goal805-closeout-causal-quoted-packet.json
- charness-artifacts/critique/goal805-closeout-causal-quoted-packet.md
- charness-artifacts/critique/goal805-code-closeout-integrity-packet.json
- charness-artifacts/critique/goal805-code-closeout-integrity-packet.md
- charness-artifacts/critique/goal805-code-closeout-integrity-strict-packet.json
- charness-artifacts/critique/goal805-code-closeout-integrity-strict-packet.md
- charness-artifacts/critique/goal805-code-closeout-repair-packet.json
- charness-artifacts/critique/goal805-code-closeout-repair-packet.md
- charness-artifacts/critique/goal805-code-closeout-simplicity-packet.json
- charness-artifacts/critique/goal805-code-closeout-simplicity-packet.md
- charness-artifacts/critique/goal805-code-closeout-simplicity-strict-packet.json
- charness-artifacts/critique/goal805-code-closeout-simplicity-strict-packet.md
- charness-artifacts/critique/goal805-code-context-integrity-packet.json
- charness-artifacts/critique/goal805-code-context-integrity-packet.md
- charness-artifacts/critique/goal805-code-context-repair-packet.json
- charness-artifacts/critique/goal805-code-context-repair-packet.md
- charness-artifacts/critique/goal805-code-context-simplicity-packet.json
- charness-artifacts/critique/goal805-code-context-simplicity-packet.md
- charness-artifacts/critique/goal805-code-release-integrity-packet.json
- charness-artifacts/critique/goal805-code-release-integrity-packet.md
- charness-artifacts/critique/goal805-code-release-operability-packet.json
- charness-artifacts/critique/goal805-code-release-operability-packet.md
- charness-artifacts/critique/goal805-code-release-repair-packet.json
- charness-artifacts/critique/goal805-code-release-repair-packet.md
- charness-artifacts/critique/goal805-design-closeout-packet.json
- charness-artifacts/critique/goal805-design-closeout-packet.md
- charness-artifacts/critique/goal805-design-closeout-repair-packet.json
- charness-artifacts/critique/goal805-design-closeout-repair-packet.md
- charness-artifacts/critique/goal805-design-release-packet.json
- charness-artifacts/critique/goal805-design-release-packet.md
- charness-artifacts/critique/goal805-design-release-repair-packet.json
- charness-artifacts/critique/goal805-design-release-repair-packet.md
- charness-artifacts/critique/goal805-design-skill-cost-packet.json
- charness-artifacts/critique/goal805-design-skill-cost-packet.md
- charness-artifacts/critique/goal805-design-skill-customer-packet.json
- charness-artifacts/critique/goal805-design-skill-customer-packet.md
- charness-artifacts/critique/goal805-design-skill-repair-packet.json
- charness-artifacts/critique/goal805-design-skill-repair-packet.md
- charness-artifacts/critique/goal805-protocol-fairness-packet.json
- charness-artifacts/critique/goal805-protocol-fairness-packet.md
- charness-artifacts/critique/goal805-protocol-observer-packet.json
- charness-artifacts/critique/goal805-protocol-observer-packet.md
- charness-artifacts/critique/goal805-protocol-repair-packet.json
- charness-artifacts/critique/goal805-protocol-repair-packet.md
- charness-artifacts/critique/goal805-release-boundary-safety-packet.json
- charness-artifacts/critique/goal805-release-boundary-safety-packet.md
- charness-artifacts/critique/goal805-release-boundary-value-packet.json
- charness-artifacts/critique/goal805-release-boundary-value-packet.md
- charness-artifacts/critique/goal805-release-link-followup-packet.json
- charness-artifacts/critique/goal805-release-link-followup-packet.md
- charness-artifacts/critique/workers/delegation-framing-integrity-1/worker-report.yaml
- charness-artifacts/critique/workers/delegation-framing-product-1/worker-report.yaml
- charness-artifacts/critique/workers/delegation-readiness-followup-3/worker-report.yaml
- charness-artifacts/critique/workers/delegation-whole-product-2/worker-report.yaml
- charness-artifacts/critique/workers/goal805-closeout-causal-quoted/worker-report.yaml
- charness-artifacts/critique/workers/goal805-code-closeout-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-code-context-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-code-release-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-design-closeout-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-design-release-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-design-skill-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-protocol-repair/worker-report.yaml
- charness-artifacts/critique/workers/goal805-release-boundary-safety/worker-report.yaml
- charness-artifacts/critique/workers/goal805-release-boundary-value/worker-report.yaml
- charness-artifacts/critique/workers/goal805-release-link-followup/worker-report.yaml
- charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goal-runs/805/bodies/parent-bootstrap.md
- charness-artifacts/goal-runs/805/bodies/parent-progress-1.md
- charness-artifacts/goal-runs/805/bodies/parent-progress-2.md
- charness-artifacts/goal-runs/805/bodies/parent-progress-3.md
- charness-artifacts/goal-runs/805/bodies/parent-progress-4.md
- charness-artifacts/goal-runs/805/closeout-carrier-lineage.json
- charness-artifacts/goal-runs/805/comparison-contract-lineage.json
- charness-artifacts/goal-runs/805/consumer-comparison-lineage.json
- charness-artifacts/goal-runs/805/context-reuse-implementation-brief.md
- charness-artifacts/goal-runs/805/context-reuse-lineage.json
- charness-artifacts/goal-runs/805/expected-children.json
- charness-artifacts/goal-runs/805/observations/805-add-closeout-carrier.started.json
- charness-artifacts/goal-runs/805/observations/805-add-closeout-carrier.terminal.json
- charness-artifacts/goal-runs/805/observations/805-add-comparison-contract.started.json
- charness-artifacts/goal-runs/805/observations/805-add-comparison-contract.terminal.json
- charness-artifacts/goal-runs/805/observations/805-add-consumer-comparison.started.json
- charness-artifacts/goal-runs/805/observations/805-add-consumer-comparison.terminal.json
- charness-artifacts/goal-runs/805/observations/805-add-context-reuse.started.json
- charness-artifacts/goal-runs/805/observations/805-add-context-reuse.terminal.json
- charness-artifacts/goal-runs/805/observations/805-add-publish-closeout.started.json
- charness-artifacts/goal-runs/805/observations/805-add-publish-closeout.terminal.json
- charness-artifacts/goal-runs/805/observations/805-add-release-reuse.started.json
- charness-artifacts/goal-runs/805/observations/805-add-release-reuse.terminal.json
- charness-artifacts/goal-runs/805/observations/805-bootstrap-metadata.started.json
- charness-artifacts/goal-runs/805/observations/805-bootstrap-metadata.terminal.json
- charness-artifacts/goal-runs/805/observations/805-correct-progress-2-prose.started.json
- charness-artifacts/goal-runs/805/observations/805-correct-progress-2-prose.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-closeout-carrier.started.json
- charness-artifacts/goal-runs/805/observations/805-create-closeout-carrier.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-comparison-contract.started.json
- charness-artifacts/goal-runs/805/observations/805-create-comparison-contract.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-consumer-comparison.started.json
- charness-artifacts/goal-runs/805/observations/805-create-consumer-comparison.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-context-reuse.started.json
- charness-artifacts/goal-runs/805/observations/805-create-context-reuse.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-publish-closeout.started.json
- charness-artifacts/goal-runs/805/observations/805-create-publish-closeout.terminal.json
- charness-artifacts/goal-runs/805/observations/805-create-release-reuse.started.json
- charness-artifacts/goal-runs/805/observations/805-create-release-reuse.terminal.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-2.started.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-2.terminal.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-3.started.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-3.terminal.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-4.started.json
- charness-artifacts/goal-runs/805/observations/805-install-progress-4.terminal.json
- charness-artifacts/goal-runs/805/observations/805-install-progress.started.json
- charness-artifacts/goal-runs/805/observations/805-install-progress.terminal.json
- charness-artifacts/goal-runs/805/observations/805-verify-initial-graph.started.json
- charness-artifacts/goal-runs/805/observations/805-verify-initial-graph.terminal.json
- charness-artifacts/goal-runs/805/operations/add-closeout-carrier.json
- charness-artifacts/goal-runs/805/operations/add-comparison-contract.json
- charness-artifacts/goal-runs/805/operations/add-consumer-comparison.json
- charness-artifacts/goal-runs/805/operations/add-context-reuse.json
- charness-artifacts/goal-runs/805/operations/add-publish-closeout.json
- charness-artifacts/goal-runs/805/operations/add-release-reuse.json
- charness-artifacts/goal-runs/805/operations/bootstrap-metadata.json
- charness-artifacts/goal-runs/805/operations/correct-progress-2-prose.json
- charness-artifacts/goal-runs/805/operations/create-closeout-carrier.json
- charness-artifacts/goal-runs/805/operations/create-comparison-contract.json
- charness-artifacts/goal-runs/805/operations/create-consumer-comparison.json
- charness-artifacts/goal-runs/805/operations/create-context-reuse.json
- charness-artifacts/goal-runs/805/operations/create-publish-closeout.json
- charness-artifacts/goal-runs/805/operations/create-release-reuse.json
- charness-artifacts/goal-runs/805/operations/install-progress-2.json
- charness-artifacts/goal-runs/805/operations/install-progress-3.json
- charness-artifacts/goal-runs/805/operations/install-progress-4.json
- charness-artifacts/goal-runs/805/operations/install-progress.json
- charness-artifacts/goal-runs/805/operations/verify-initial-graph.json
- charness-artifacts/goal-runs/805/publish-closeout-lineage.json
- charness-artifacts/goal-runs/805/release-reuse-lineage.json
- charness-artifacts/goal-runs/805/reviews/closeout-code-observations.md
- charness-artifacts/goal-runs/805/reviews/closeout-code-paths.txt
- charness-artifacts/goal-runs/805/reviews/context-code-disposition.md
- charness-artifacts/goal-runs/805/reviews/context-code-observations.md
- charness-artifacts/goal-runs/805/reviews/design-disposition.md
- charness-artifacts/goal-runs/805/reviews/goal805-code-closeout-integrity-strict.json
- charness-artifacts/goal-runs/805/reviews/goal805-code-closeout-simplicity-strict.json
- charness-artifacts/goal-runs/805/reviews/goal805-code-context-integrity.json
- charness-artifacts/goal-runs/805/reviews/goal805-code-context-simplicity.json
- charness-artifacts/goal-runs/805/reviews/goal805-code-release-integrity.json
- charness-artifacts/goal-runs/805/reviews/goal805-code-release-operability.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-closeout-repair.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-closeout.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-release.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-skill-cost.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-skill-customer.json
- charness-artifacts/goal-runs/805/reviews/goal805-design-skill-repair.json
- charness-artifacts/goal-runs/805/reviews/integration-observations.md
- charness-artifacts/goal-runs/805/reviews/release-boundary-paths.txt
- charness-artifacts/goal-runs/805/reviews/release-boundary-safety.json
- charness-artifacts/goal-runs/805/reviews/release-boundary-value.json
- charness-artifacts/goal-runs/805/reviews/release-code-disposition.md
- charness-artifacts/goal-runs/805/reviews/release-link-followup.json
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/closeout-carrier.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/comparison-contract.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/consumer-comparison.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/context-reuse.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/publish-closeout.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/release-reuse.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-parent.md
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.binding.json
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.interview.json
- charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.md
- charness-artifacts/probe/2026-09-06-closeout-cardinality/classification-cardinality.receipt.json
- charness-artifacts/probe/2026-09-06-closeout-cardinality/replay.py
- charness-artifacts/probe/2026-09-06-closeout-cardinality/report.json
- charness-artifacts/probe/2026-09-06-closeout-cardinality/review-paths.txt
- charness-artifacts/probe/2026-09-06-closeout-cardinality/target-cardinality.receipt.json
- charness-artifacts/probe/2026-09-06-context-reuse/debug-changed-adapter-output.txt
- charness-artifacts/probe/2026-09-06-context-reuse/debug-changed-adapter-receipt.json
- charness-artifacts/probe/2026-09-06-context-reuse/debug-consumer-output.txt
- charness-artifacts/probe/2026-09-06-context-reuse/retro-consumer-output.txt
- charness-artifacts/probe/2026-09-06-context-reuse/spec-consumer-output.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/candidate-inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/phase1.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/phase2.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/workspaces.tar.gz
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/phase1.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/phase2.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/workspaces.tar.gz
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/phase1.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/phase2.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/workspaces.tar.gz
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/phase1.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/phase2.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/workspaces.tar.gz
- charness-artifacts/probe/2026-09-06-delegation-net-value/control-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/control_catalog.py
- charness-artifacts/probe/2026-09-06-delegation-net-value/controls.py
- charness-artifacts/probe/2026-09-06-delegation-net-value/evaluation-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/frozen-inputs.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/initial-task.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/launch.py
- charness-artifacts/probe/2026-09-06-delegation-net-value/launcher-control-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/launcher_controls.py
- charness-artifacts/probe/2026-09-06-delegation-net-value/oracle.py
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/candidate-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/candidate-transport.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/high-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/high-transport.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/low-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/low-transport.jsonl
- charness-artifacts/probe/2026-09-06-delegation-net-value/protocol.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/readiness.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/results.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/resume.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/review-paths.txt
- charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/disposition.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/fairness-initial.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/observer-initial.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/revised-task.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/start.md
- charness-artifacts/probe/2026-09-06-delegation-net-value/trace-observations.json
- charness-artifacts/probe/2026-09-06-delegation-net-value/treatment.md
- charness-artifacts/probe/2026-09-06-release-scheduling/observations.md
- charness-artifacts/probe/2026-09-06-v8.5.0-release-observer.json
- charness-artifacts/release-review/2026-09-06-v8.5.0-prepared-claims-review.json
- charness-artifacts/release-review/2026-09-06-v8.5.0-prepared-claims-review.md
- charness-artifacts/release/2026-09-06-v8.5.0-notes.md
- charness-artifacts/release/latest.md
- docs/development.md
- packaging/charness.json
- scripts/gates/check_issue_closeout_commit_msg.py
- scripts/gates/validate_debug_artifact.py
- scripts/prepush_close_keyword_guard.py
- scripts/prepush_quality_receipt.py
- scripts/review/critique_packet_lib.py
- scripts/run-quality.sh
- scripts/run_quality_engine.py
- scripts/run_quality_engine_receipt.py
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/prepare_packet.py
- skills/public/critique/scripts/run_review.py
- skills/public/critique/scripts/run_review_packet.py
- skills/public/debug/SKILL.md
- skills/public/debug/references/five-steps.md
- skills/public/debug/references/five-whys-causal-chain.md
- skills/public/debug/scripts/debug_artifact_state.py
- skills/public/debug/scripts/scaffold_debug_artifact.py
- skills/public/issue/references/closeout-discipline.md
- skills/public/issue/scripts/issue_closeout_classification_ledger.py
- skills/public/issue/scripts/issue_closeout_rung1_floors.py
- skills/public/issue/scripts/issue_critique_observer.py
- skills/public/issue/scripts/issue_critique_observer_support.py
- skills/public/issue/scripts/issue_resolution_critique.py
- skills/public/issue/scripts/issue_tool_parser.py
- skills/public/issue/scripts/issue_validate_closeout_draft.py
- skills/public/issue/scripts/issue_verify_closeout.py
- skills/public/issue/scripts/issue_verify_closeout_carrier.py
- skills/public/issue/scripts/issue_worker_targets.py
- skills/public/release/references/adapter-contract.md
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_execute.py
- skills/public/release/scripts/publish_release_resume_publish.py
- skills/public/retro/SKILL.md
- skills/public/retro/references/adapter-contract.md
- skills/public/retro/references/expert-lens.md
- skills/public/retro/references/section-guide.md
- skills/public/retro/references/trigger-and-persistence.md
- skills/public/retro/scripts/plan_retro_run.py
- skills/public/retro/scripts/retro_plan_gates.py
- skills/public/retro/scripts/retro_plan_reads.py
- skills/public/spec/SKILL.md
- skills/shared/references/bounded-review-result.schema.json
- skills/shared/scripts/reviewer_result_contract.py
- skills/shared/scripts/reviewer_worker_carrier.py
- skills/shared/scripts/reviewer_worker_carrier_support.py
- tests/coverage_debt/test_batch8.py
- tests/quality_gates/test_debug_rca_reference_cite_chain.py
- tests/quality_gates/test_issue_bundled_closeout.py
- tests/quality_gates/test_issue_closeout_authority.py
- tests/quality_gates/test_issue_closeout_invocation.py
- tests/quality_gates/test_issue_closeout_owner_contracts.py
- tests/quality_gates/test_prepush_runtime_regime.py
- tests/quality_gates/test_quality_runner_release_order.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_release_quality_gate_visibility.py
- tests/quality_gates/test_release_quality_status_binding.py
- tests/quality_gates/test_reviewer_capability.py
- tests/quality_gates/test_run_quality_engine.py
- tests/quality_gates/test_run_quality_engine_not_run.py
- tests/quality_gates/test_semantic_review_command.py
- tests/test_debug_artifact.py
- tests/test_debug_scaffold.py
- tests/test_release_lane_receipt.py
- tests/test_retro_plan.py
- tools/check_skill_contracts.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: packaging/charness.json, scripts/gates/check_issue_closeout_commit_msg.py, scripts/gates/validate_debug_artifact.py, scripts/prepush_close_keyword_guard.py, scripts/prepush_quality_receipt.py, scripts/review/critique_packet_lib.py, scripts/run-quality.sh, scripts/run_quality_engine.py, scripts/run_quality_engine_receipt.py, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/debug/SKILL.md, skills/public/debug/references/five-steps.md, skills/public/debug/references/five-whys-causal-chain.md, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/issue/scripts/issue_tool_parser.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/issue/scripts/issue_worker_targets.py, skills/public/release/references/adapter-contract.md, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/expert-lens.md, skills/public/retro/references/section-guide.md, skills/public/retro/references/trigger-and-persistence.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_gates.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/spec/SKILL.md, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker_carrier.py, skills/shared/scripts/reviewer_worker_carrier_support.py
  derived matches: .claude-plugin/marketplace.json
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: .gitleaks.toml, charness-artifacts/create-skill/2026-09-06-context-reuse-brief.md, charness-artifacts/critique/2026-09-06-goal805-release-8-5-0.md, charness-artifacts/critique/delegation-framing-integrity-1-packet.md, charness-artifacts/critique/delegation-framing-product-1-packet.md, charness-artifacts/critique/delegation-readiness-followup-3-packet.md, charness-artifacts/critique/delegation-whole-product-2-packet.md, charness-artifacts/critique/goal805-closeout-causal-packet.md, charness-artifacts/critique/goal805-closeout-causal-quoted-packet.md, charness-artifacts/critique/goal805-code-closeout-integrity-packet.md, charness-artifacts/critique/goal805-code-closeout-integrity-strict-packet.md, charness-artifacts/critique/goal805-code-closeout-repair-packet.md, charness-artifacts/critique/goal805-code-closeout-simplicity-packet.md, charness-artifacts/critique/goal805-code-closeout-simplicity-strict-packet.md, charness-artifacts/critique/goal805-code-context-integrity-packet.md, charness-artifacts/critique/goal805-code-context-repair-packet.md, charness-artifacts/critique/goal805-code-context-simplicity-packet.md, charness-artifacts/critique/goal805-code-release-integrity-packet.md, charness-artifacts/critique/goal805-code-release-operability-packet.md, charness-artifacts/critique/goal805-code-release-repair-packet.md, charness-artifacts/critique/goal805-design-closeout-packet.md, charness-artifacts/critique/goal805-design-closeout-repair-packet.md, charness-artifacts/critique/goal805-design-release-packet.md, charness-artifacts/critique/goal805-design-release-repair-packet.md, charness-artifacts/critique/goal805-design-skill-cost-packet.md, charness-artifacts/critique/goal805-design-skill-customer-packet.md, charness-artifacts/critique/goal805-design-skill-repair-packet.md, charness-artifacts/critique/goal805-protocol-fairness-packet.md, charness-artifacts/critique/goal805-protocol-observer-packet.md, charness-artifacts/critique/goal805-protocol-repair-packet.md, charness-artifacts/critique/goal805-release-boundary-safety-packet.md, charness-artifacts/critique/goal805-release-boundary-value-packet.md, charness-artifacts/critique/goal805-release-link-followup-packet.md, charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md, charness-artifacts/debug/latest.md, charness-artifacts/goal-runs/805/bodies/parent-bootstrap.md, charness-artifacts/goal-runs/805/bodies/parent-progress-1.md, charness-artifacts/goal-runs/805/bodies/parent-progress-2.md, charness-artifacts/goal-runs/805/bodies/parent-progress-3.md, charness-artifacts/goal-runs/805/bodies/parent-progress-4.md, charness-artifacts/goal-runs/805/context-reuse-implementation-brief.md, charness-artifacts/goal-runs/805/reviews/closeout-code-observations.md, charness-artifacts/goal-runs/805/reviews/context-code-disposition.md, charness-artifacts/goal-runs/805/reviews/context-code-observations.md, charness-artifacts/goal-runs/805/reviews/design-disposition.md, charness-artifacts/goal-runs/805/reviews/integration-observations.md, charness-artifacts/goal-runs/805/reviews/release-code-disposition.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/closeout-carrier.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/comparison-contract.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/consumer-comparison.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/context-reuse.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/publish-closeout.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-items/release-reuse.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value-parent.md, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.md, charness-artifacts/probe/2026-09-06-context-reuse/spec-consumer-output.md, charness-artifacts/probe/2026-09-06-delegation-net-value/initial-task.md, charness-artifacts/probe/2026-09-06-delegation-net-value/protocol.md, charness-artifacts/probe/2026-09-06-delegation-net-value/readiness.md, charness-artifacts/probe/2026-09-06-delegation-net-value/results.md, charness-artifacts/probe/2026-09-06-delegation-net-value/resume.md, charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/disposition.md, charness-artifacts/probe/2026-09-06-delegation-net-value/revised-task.md, charness-artifacts/probe/2026-09-06-delegation-net-value/start.md, charness-artifacts/probe/2026-09-06-delegation-net-value/treatment.md, charness-artifacts/probe/2026-09-06-release-scheduling/observations.md, charness-artifacts/release-review/2026-09-06-v8.5.0-prepared-claims-review.md, charness-artifacts/release/2026-09-06-v8.5.0-notes.md, charness-artifacts/release/latest.md, docs/development.md, skills/public/critique/references/prepare-packet.md, skills/public/debug/SKILL.md, skills/public/debug/references/five-steps.md, skills/public/debug/references/five-whys-causal-chain.md, skills/public/issue/references/closeout-discipline.md, skills/public/release/references/adapter-contract.md, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/expert-lens.md, skills/public/retro/references/section-guide.md, skills/public/retro/references/trigger-and-persistence.md, skills/public/spec/SKILL.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- goal-evidence-json: Machine-readable evidence captured beside achieve goal artifacts.
  source matches: charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.binding.json, charness-artifacts/goals/2026-09-06-long-term-delegation-net-value.interview.json
  verify: for evidence_file in charness-artifacts/goals/*.json; do python3 -m json.tool "$evidence_file" >/dev/null || exit $?; done, python3 -c 'import json, pathlib; [json.loads(line) for path in pathlib.Path("charness-artifacts/goals").glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]'
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-09-06-v8.5.0-notes.md, charness-artifacts/release/latest.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/debug/SKILL.md, skills/public/debug/references/five-steps.md, skills/public/debug/references/five-whys-causal-chain.md, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/issue/scripts/issue_tool_parser.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/issue/scripts/issue_worker_targets.py, skills/public/release/references/adapter-contract.md, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/expert-lens.md, skills/public/retro/references/section-guide.md, skills/public/retro/references/trigger-and-persistence.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_gates.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/spec/SKILL.md, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker_carrier.py, skills/shared/scripts/reviewer_worker_carrier_support.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- consumer-validator-catalog: Explicit packaged consumer-validator inventory, adoption decisions, and the installed/source-layout checker that enforces the contract.
  source matches: scripts/run-quality.sh
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/gates/check_consumer_validator_catalog.py --repo-root . --adoption-path .agents/consumer-validator-adoption.yaml --require-adoption, python3 -m pytest -q tests/test_consumer_validator_catalog.py tests/test_capability_catalog.py
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/debug/SKILL.md, skills/public/debug/references/five-steps.md, skills/public/debug/references/five-whys-causal-chain.md, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/issue/scripts/issue_tool_parser.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/issue/scripts/issue_worker_targets.py, skills/public/release/references/adapter-contract.md, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/expert-lens.md, skills/public/retro/references/section-guide.md, skills/public/retro/references/trigger-and-persistence.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_gates.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/spec/SKILL.md, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker_carrier.py, skills/shared/scripts/reviewer_worker_carrier_support.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/debug/SKILL.md, skills/public/debug/references/five-steps.md, skills/public/debug/references/five-whys-causal-chain.md, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/issue/scripts/issue_tool_parser.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/issue/scripts/issue_worker_targets.py, skills/public/release/references/adapter-contract.md, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/expert-lens.md, skills/public/retro/references/section-guide.md, skills/public/retro/references/trigger-and-persistence.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_gates.py, skills/public/retro/scripts/retro_plan_reads.py, skills/public/spec/SKILL.md, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_worker_carrier.py, skills/shared/scripts/reviewer_worker_carrier_support.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- release-claims-review-evidence: Committed, machine-readable claims-review evidence that binds a prepared local release record before publication may resume.
  source matches: charness-artifacts/release-review/2026-09-06-v8.5.0-prepared-claims-review.json, charness-artifacts/release-review/2026-09-06-v8.5.0-prepared-claims-review.md
  verify: for review_record in charness-artifacts/release-review/*.json; do [ -e "$review_record" ] && python3 -m json.tool "$review_record" >/dev/null || exit $?; done
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-09-06-goal805-release-8-5-0.md, charness-artifacts/critique/delegation-framing-integrity-1-packet.json, charness-artifacts/critique/delegation-framing-integrity-1-packet.md, charness-artifacts/critique/delegation-framing-product-1-packet.json, charness-artifacts/critique/delegation-framing-product-1-packet.md, charness-artifacts/critique/delegation-readiness-followup-3-packet.json, charness-artifacts/critique/delegation-readiness-followup-3-packet.md, charness-artifacts/critique/delegation-whole-product-2-packet.json, charness-artifacts/critique/delegation-whole-product-2-packet.md, charness-artifacts/critique/goal805-closeout-causal-packet.json, charness-artifacts/critique/goal805-closeout-causal-packet.md, charness-artifacts/critique/goal805-closeout-causal-quoted-packet.json, charness-artifacts/critique/goal805-closeout-causal-quoted-packet.md, charness-artifacts/critique/goal805-code-closeout-integrity-packet.json, charness-artifacts/critique/goal805-code-closeout-integrity-packet.md, charness-artifacts/critique/goal805-code-closeout-integrity-strict-packet.json, charness-artifacts/critique/goal805-code-closeout-integrity-strict-packet.md, charness-artifacts/critique/goal805-code-closeout-repair-packet.json, charness-artifacts/critique/goal805-code-closeout-repair-packet.md, charness-artifacts/critique/goal805-code-closeout-simplicity-packet.json, charness-artifacts/critique/goal805-code-closeout-simplicity-packet.md, charness-artifacts/critique/goal805-code-closeout-simplicity-strict-packet.json, charness-artifacts/critique/goal805-code-closeout-simplicity-strict-packet.md, charness-artifacts/critique/goal805-code-context-integrity-packet.json, charness-artifacts/critique/goal805-code-context-integrity-packet.md, charness-artifacts/critique/goal805-code-context-repair-packet.json, charness-artifacts/critique/goal805-code-context-repair-packet.md, charness-artifacts/critique/goal805-code-context-simplicity-packet.json, charness-artifacts/critique/goal805-code-context-simplicity-packet.md, charness-artifacts/critique/goal805-code-release-integrity-packet.json, charness-artifacts/critique/goal805-code-release-integrity-packet.md, charness-artifacts/critique/goal805-code-release-operability-packet.json, charness-artifacts/critique/goal805-code-release-operability-packet.md, charness-artifacts/critique/goal805-code-release-repair-packet.json, charness-artifacts/critique/goal805-code-release-repair-packet.md, charness-artifacts/critique/goal805-design-closeout-packet.json, charness-artifacts/critique/goal805-design-closeout-packet.md, charness-artifacts/critique/goal805-design-closeout-repair-packet.json, charness-artifacts/critique/goal805-design-closeout-repair-packet.md, charness-artifacts/critique/goal805-design-release-packet.json, charness-artifacts/critique/goal805-design-release-packet.md, charness-artifacts/critique/goal805-design-release-repair-packet.json, charness-artifacts/critique/goal805-design-release-repair-packet.md, charness-artifacts/critique/goal805-design-skill-cost-packet.json, charness-artifacts/critique/goal805-design-skill-cost-packet.md, charness-artifacts/critique/goal805-design-skill-customer-packet.json, charness-artifacts/critique/goal805-design-skill-customer-packet.md, charness-artifacts/critique/goal805-design-skill-repair-packet.json, charness-artifacts/critique/goal805-design-skill-repair-packet.md, charness-artifacts/critique/goal805-protocol-fairness-packet.json, charness-artifacts/critique/goal805-protocol-fairness-packet.md, charness-artifacts/critique/goal805-protocol-observer-packet.json, charness-artifacts/critique/goal805-protocol-observer-packet.md, charness-artifacts/critique/goal805-protocol-repair-packet.json, charness-artifacts/critique/goal805-protocol-repair-packet.md, charness-artifacts/critique/goal805-release-boundary-safety-packet.json, charness-artifacts/critique/goal805-release-boundary-safety-packet.md, charness-artifacts/critique/goal805-release-boundary-value-packet.json, charness-artifacts/critique/goal805-release-boundary-value-packet.md, charness-artifacts/critique/goal805-release-link-followup-packet.json, charness-artifacts/critique/goal805-release-link-followup-packet.md, charness-artifacts/critique/workers/delegation-framing-integrity-1/worker-report.yaml, charness-artifacts/critique/workers/delegation-framing-product-1/worker-report.yaml, charness-artifacts/critique/workers/delegation-readiness-followup-3/worker-report.yaml, charness-artifacts/critique/workers/delegation-whole-product-2/worker-report.yaml, charness-artifacts/critique/workers/goal805-closeout-causal-quoted/worker-report.yaml, charness-artifacts/critique/workers/goal805-code-closeout-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-code-context-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-code-release-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-design-closeout-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-design-release-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-design-skill-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-protocol-repair/worker-report.yaml, charness-artifacts/critique/workers/goal805-release-boundary-safety/worker-report.yaml, charness-artifacts/critique/workers/goal805-release-boundary-value/worker-report.yaml, charness-artifacts/critique/workers/goal805-release-link-followup/worker-report.yaml
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-09-06-closeout-cardinality/classification-cardinality.receipt.json, charness-artifacts/probe/2026-09-06-closeout-cardinality/report.json, charness-artifacts/probe/2026-09-06-closeout-cardinality/target-cardinality.receipt.json, charness-artifacts/probe/2026-09-06-context-reuse/debug-changed-adapter-receipt.json, charness-artifacts/probe/2026-09-06-delegation-net-value/candidate-inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-baseline/observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/high-candidate/observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-baseline/observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/cells/low-candidate/observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/control-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/evaluation-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/frozen-inputs.json, charness-artifacts/probe/2026-09-06-delegation-net-value/launcher-control-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/candidate-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/high-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/preflight/low-observations.json, charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/fairness-initial.json, charness-artifacts/probe/2026-09-06-delegation-net-value/reviews/observer-initial.json, charness-artifacts/probe/2026-09-06-delegation-net-value/trace-observations.json, charness-artifacts/probe/2026-09-06-v8.5.0-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --check
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/gates/check_issue_closeout_commit_msg.py, scripts/gates/validate_debug_artifact.py, scripts/prepush_close_keyword_guard.py, scripts/prepush_quality_receipt.py, scripts/review/critique_packet_lib.py, scripts/run_quality_engine.py, scripts/run_quality_engine_receipt.py, tests/coverage_debt/test_batch8.py, tests/quality_gates/test_debug_rca_reference_cite_chain.py, tests/quality_gates/test_issue_bundled_closeout.py, tests/quality_gates/test_issue_closeout_authority.py, tests/quality_gates/test_issue_closeout_invocation.py, tests/quality_gates/test_issue_closeout_owner_contracts.py, tests/quality_gates/test_prepush_runtime_regime.py, tests/quality_gates/test_quality_runner_release_order.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_release_quality_gate_visibility.py, tests/quality_gates/test_release_quality_status_binding.py, tests/quality_gates/test_reviewer_capability.py, tests/quality_gates/test_run_quality_engine.py, tests/quality_gates/test_run_quality_engine_not_run.py, tests/quality_gates/test_semantic_review_command.py, tests/test_debug_artifact.py, tests/test_debug_scaffold.py, tests/test_release_lane_receipt.py, tests/test_retro_plan.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/gates/check_issue_closeout_commit_msg.py, scripts/gates/validate_debug_artifact.py, scripts/prepush_close_keyword_guard.py, scripts/prepush_quality_receipt.py, scripts/review/critique_packet_lib.py, scripts/run_quality_engine.py, scripts/run_quality_engine_receipt.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/scaffold_debug_artifact.py, skills/public/issue/scripts/issue_closeout_classification_ledger.py, skills/public/issue/scripts/issue_closeout_rung1_floors.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_critique_observer_support.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/issue/scripts/issue_tool_parser.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/issue/scripts/issue_verify_closeout.py, skills/public/issue/scripts/issue_verify_closeout_carrier.py, skills/public/issue/scripts/issue_worker_targets.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/retro_plan_gates.py, skills/public/retro/scripts/retro_plan_reads.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- goal-run-evidence: Durable Goal Run provider plans, operations, observations, graph snapshots, and evidence-lineage records.
  source matches: charness-artifacts/goal-runs/805/bodies/parent-bootstrap.md, charness-artifacts/goal-runs/805/bodies/parent-progress-1.md, charness-artifacts/goal-runs/805/bodies/parent-progress-2.md, charness-artifacts/goal-runs/805/bodies/parent-progress-3.md, charness-artifacts/goal-runs/805/bodies/parent-progress-4.md, charness-artifacts/goal-runs/805/closeout-carrier-lineage.json, charness-artifacts/goal-runs/805/comparison-contract-lineage.json, charness-artifacts/goal-runs/805/consumer-comparison-lineage.json, charness-artifacts/goal-runs/805/context-reuse-implementation-brief.md, charness-artifacts/goal-runs/805/context-reuse-lineage.json, charness-artifacts/goal-runs/805/expected-children.json, charness-artifacts/goal-runs/805/observations/805-add-closeout-carrier.started.json, charness-artifacts/goal-runs/805/observations/805-add-closeout-carrier.terminal.json, charness-artifacts/goal-runs/805/observations/805-add-comparison-contract.started.json, charness-artifacts/goal-runs/805/observations/805-add-comparison-contract.terminal.json, charness-artifacts/goal-runs/805/observations/805-add-consumer-comparison.started.json, charness-artifacts/goal-runs/805/observations/805-add-consumer-comparison.terminal.json, charness-artifacts/goal-runs/805/observations/805-add-context-reuse.started.json, charness-artifacts/goal-runs/805/observations/805-add-context-reuse.terminal.json, charness-artifacts/goal-runs/805/observations/805-add-publish-closeout.started.json, charness-artifacts/goal-runs/805/observations/805-add-publish-closeout.terminal.json, charness-artifacts/goal-runs/805/observations/805-add-release-reuse.started.json, charness-artifacts/goal-runs/805/observations/805-add-release-reuse.terminal.json, charness-artifacts/goal-runs/805/observations/805-bootstrap-metadata.started.json, charness-artifacts/goal-runs/805/observations/805-bootstrap-metadata.terminal.json, charness-artifacts/goal-runs/805/observations/805-correct-progress-2-prose.started.json, charness-artifacts/goal-runs/805/observations/805-correct-progress-2-prose.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-closeout-carrier.started.json, charness-artifacts/goal-runs/805/observations/805-create-closeout-carrier.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-comparison-contract.started.json, charness-artifacts/goal-runs/805/observations/805-create-comparison-contract.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-consumer-comparison.started.json, charness-artifacts/goal-runs/805/observations/805-create-consumer-comparison.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-context-reuse.started.json, charness-artifacts/goal-runs/805/observations/805-create-context-reuse.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-publish-closeout.started.json, charness-artifacts/goal-runs/805/observations/805-create-publish-closeout.terminal.json, charness-artifacts/goal-runs/805/observations/805-create-release-reuse.started.json, charness-artifacts/goal-runs/805/observations/805-create-release-reuse.terminal.json, charness-artifacts/goal-runs/805/observations/805-install-progress-2.started.json, charness-artifacts/goal-runs/805/observations/805-install-progress-2.terminal.json, charness-artifacts/goal-runs/805/observations/805-install-progress-3.started.json, charness-artifacts/goal-runs/805/observations/805-install-progress-3.terminal.json, charness-artifacts/goal-runs/805/observations/805-install-progress-4.started.json, charness-artifacts/goal-runs/805/observations/805-install-progress-4.terminal.json, charness-artifacts/goal-runs/805/observations/805-install-progress.started.json, charness-artifacts/goal-runs/805/observations/805-install-progress.terminal.json, charness-artifacts/goal-runs/805/observations/805-verify-initial-graph.started.json, charness-artifacts/goal-runs/805/observations/805-verify-initial-graph.terminal.json, charness-artifacts/goal-runs/805/operations/add-closeout-carrier.json, charness-artifacts/goal-runs/805/operations/add-comparison-contract.json, charness-artifacts/goal-runs/805/operations/add-consumer-comparison.json, charness-artifacts/goal-runs/805/operations/add-context-reuse.json, charness-artifacts/goal-runs/805/operations/add-publish-closeout.json, charness-artifacts/goal-runs/805/operations/add-release-reuse.json, charness-artifacts/goal-runs/805/operations/bootstrap-metadata.json, charness-artifacts/goal-runs/805/operations/correct-progress-2-prose.json, charness-artifacts/goal-runs/805/operations/create-closeout-carrier.json, charness-artifacts/goal-runs/805/operations/create-comparison-contract.json, charness-artifacts/goal-runs/805/operations/create-consumer-comparison.json, charness-artifacts/goal-runs/805/operations/create-context-reuse.json, charness-artifacts/goal-runs/805/operations/create-publish-closeout.json, charness-artifacts/goal-runs/805/operations/create-release-reuse.json, charness-artifacts/goal-runs/805/operations/install-progress-2.json, charness-artifacts/goal-runs/805/operations/install-progress-3.json, charness-artifacts/goal-runs/805/operations/install-progress-4.json, charness-artifacts/goal-runs/805/operations/install-progress.json, charness-artifacts/goal-runs/805/operations/verify-initial-graph.json, charness-artifacts/goal-runs/805/publish-closeout-lineage.json, charness-artifacts/goal-runs/805/release-reuse-lineage.json, charness-artifacts/goal-runs/805/reviews/closeout-code-observations.md, charness-artifacts/goal-runs/805/reviews/closeout-code-paths.txt, charness-artifacts/goal-runs/805/reviews/context-code-disposition.md, charness-artifacts/goal-runs/805/reviews/context-code-observations.md, charness-artifacts/goal-runs/805/reviews/design-disposition.md, charness-artifacts/goal-runs/805/reviews/goal805-code-closeout-integrity-strict.json, charness-artifacts/goal-runs/805/reviews/goal805-code-closeout-simplicity-strict.json, charness-artifacts/goal-runs/805/reviews/goal805-code-context-integrity.json, charness-artifacts/goal-runs/805/reviews/goal805-code-context-simplicity.json, charness-artifacts/goal-runs/805/reviews/goal805-code-release-integrity.json, charness-artifacts/goal-runs/805/reviews/goal805-code-release-operability.json, charness-artifacts/goal-runs/805/reviews/goal805-design-closeout-repair.json, charness-artifacts/goal-runs/805/reviews/goal805-design-closeout.json, charness-artifacts/goal-runs/805/reviews/goal805-design-release.json, charness-artifacts/goal-runs/805/reviews/goal805-design-skill-cost.json, charness-artifacts/goal-runs/805/reviews/goal805-design-skill-customer.json, charness-artifacts/goal-runs/805/reviews/goal805-design-skill-repair.json, charness-artifacts/goal-runs/805/reviews/integration-observations.md, charness-artifacts/goal-runs/805/reviews/release-boundary-paths.txt, charness-artifacts/goal-runs/805/reviews/release-boundary-safety.json, charness-artifacts/goal-runs/805/reviews/release-boundary-value.json, charness-artifacts/goal-runs/805/reviews/release-code-disposition.md, charness-artifacts/goal-runs/805/reviews/release-link-followup.json
  verify: find charness-artifacts/goal-runs -type f -name '*.json' -exec python3 -m json.tool {} \;

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
```

## Rework Issues By Causing Skill

- **Section id**: `rework-issues-by-causing-skill`
- **Content kind**: `script`
- **Producer**: `python3 scripts/retro_debug/render_retro_section_rework_issues.py --repo corca-ai/charness`
- **Section shape validation ok**: True

```text
Rework issues labelled `rework` created since 2026-08-07 (3 issue(s)):

| Causing skill | Issues |
| --- | --- |
| achieve | 2 |
| issue | 2 |
| critique | 1 |
| retro | 1 |

Counts are per attribution; one issue naming multiple skills is counted once under each skill.

- #810 Multi-issue closeout forces repeated reviews and classification partitions (OPEN, 2026-09-06; issue, critique) https://github.com/corca-ai/charness/issues/810
- #774 Charness still projects recent-lessons.md although the operator chose the ledger as the only lesson surface (CLOSED, 2026-09-02; retro, achieve) https://github.com/corca-ai/charness/issues/774
- #773 Goal Run binding hashes content, not identity: one-line child edits and new Work Items force a full re-bootstrap (CLOSED, 2026-09-02; achieve, issue) https://github.com/corca-ai/charness/issues/773
```
