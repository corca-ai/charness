# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-26T14:49:27Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `b6005caa722752eb3ef57e392e78459ee0d059d5835bd738d9abf3163b6b5834`
- **Reviewed paths**: 1
  - `scripts/goal_lineage.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/goal-run-729-dry-run-1-packet.json --packet-sha256 4b73678725cd04496e4187c6a2f54dad0d40bb75c91f2f67040edc3513d836b2 --identity-sha256 b6005caa722752eb3ef57e392e78459ee0d059d5835bd738d9abf3163b6b5834
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
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for working tree:
- .agents/achieve-adapter.yaml
- .agents/command-docs.yaml
- .agents/command-registry.json
- .agents/release-adapter.yaml
- charness
- charness-artifacts/gather/latest.md
- charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md
- charness-artifacts/retro/lesson-ledger.json
- docs/artifact-policy.md
- docs/cli-reference.md
- docs/development.md
- docs/goal-lifecycle.md
- docs/index.md
- docs/public-skill-dogfood.json
- docs/readme-proof.md
- docs/workflow-routes.md
- plugins/charness/scripts/check_docs_graph.py
- plugins/charness/scripts/check_premise_preflight.py
- plugins/charness/scripts/check_python_lengths.py
- plugins/charness/scripts/check_runtime_budget_universe.py
- plugins/charness/scripts/closeout_bundle.py
- plugins/charness/scripts/closeout_bundle_lib.py
- plugins/charness/scripts/dup_ratchet_edit_advisory.py
- plugins/charness/scripts/final_bundle_preflight.py
- plugins/charness/scripts/final_bundle_preflight_lib.py
- plugins/charness/scripts/host_log_probe_lib.py
- plugins/charness/scripts/plan_risk_interrupt.py
- plugins/charness/scripts/premise_preflight_lib.py
- plugins/charness/scripts/public_skill_dogfood_lib.py
- plugins/charness/scripts/retro_persistence_lib.py
- plugins/charness/scripts/setup_agent_docs_lib.py
- plugins/charness/scripts/setup_inspect_quality_lib.py
- plugins/charness/scripts/slice_manifest_lib.py
- plugins/charness/scripts/validate_slice_manifest.py
- plugins/charness/shared/references/active-goal-coordination.md
- plugins/charness/shared/scripts/reviewer_process.py
- plugins/charness/shared/scripts/run_reviewer_worker.py
- plugins/charness/skills/achieve/SKILL.md
- plugins/charness/skills/achieve/adapter.example.yaml
- plugins/charness/skills/achieve/references/adapter-contract.md
- plugins/charness/skills/achieve/references/coordination.md
- plugins/charness/skills/achieve/references/index.md
- plugins/charness/skills/achieve/references/lifecycle-after.md
- plugins/charness/skills/achieve/references/lifecycle-before.md
- plugins/charness/skills/achieve/references/lifecycle-during.md
- plugins/charness/skills/achieve/references/lifecycle.md
- plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py
- plugins/charness/skills/achieve/scripts/goal_cli_args.py
- plugins/charness/skills/achieve/scripts/init_adapter.py
- plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/references/adapter-contract.md
- plugins/charness/skills/critique/references/prepare-packet.md
- plugins/charness/skills/critique/scripts/record_round_findings.py
- plugins/charness/skills/impl/SKILL.md
- plugins/charness/skills/issue/SKILL.md
- plugins/charness/skills/issue/references/issue-backend.md
- plugins/charness/skills/issue/scripts/issue_close.py
- plugins/charness/skills/issue/scripts/issue_tracker_cli.py
- plugins/charness/skills/issue/scripts/issue_tracker_cli_parser.py
- plugins/charness/skills/prove/SKILL.md
- plugins/charness/skills/quality/scripts/check_dup_ratchet.py
- plugins/charness/skills/quality/scripts/plan_quality_run.py
- plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py
- plugins/charness/skills/retro/SKILL.md
- plugins/charness/skills/retro/scripts/persist_retro_artifact.py
- plugins/charness/skills/retro/scripts/probe_host_logs.py
- scripts/check_docs_graph.py
- scripts/check_premise_preflight.py
- scripts/check_python_lengths.py
- scripts/check_runtime_budget_universe.py
- scripts/closeout_bundle.py
- scripts/closeout_bundle_lib.py
- scripts/dup_ratchet_edit_advisory.py
- scripts/final_bundle_preflight.py
- scripts/final_bundle_preflight_lib.py
- scripts/host_log_probe_lib.py
- scripts/plan_risk_interrupt.py
- scripts/premise_preflight_lib.py
- scripts/public_skill_dogfood_lib.py
- scripts/retro_persistence_lib.py
- scripts/setup_agent_docs_lib.py
- scripts/setup_inspect_quality_lib.py
- scripts/slice_manifest_lib.py
- scripts/validate_slice_manifest.py
- skills/public/achieve/SKILL.md
- skills/public/achieve/adapter.example.yaml
- skills/public/achieve/references/adapter-contract.md
- skills/public/achieve/references/coordination.md
- skills/public/achieve/references/index.md
- skills/public/achieve/references/lifecycle-after.md
- skills/public/achieve/references/lifecycle-before.md
- skills/public/achieve/references/lifecycle-during.md
- skills/public/achieve/references/lifecycle.md
- skills/public/achieve/scripts/achieve_adapter_policy.py
- skills/public/achieve/scripts/goal_cli_args.py
- skills/public/achieve/scripts/init_adapter.py
- skills/public/achieve/scripts/normalize_goal_closeout.py
- skills/public/critique/SKILL.md
- skills/public/critique/references/adapter-contract.md
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/record_round_findings.py
- skills/public/impl/SKILL.md
- skills/public/issue/SKILL.md
- skills/public/issue/references/issue-backend.md
- skills/public/issue/scripts/issue_close.py
- skills/public/issue/scripts/issue_tracker_cli.py
- skills/public/issue/scripts/issue_tracker_cli_parser.py
- skills/public/prove/SKILL.md
- skills/public/quality/scripts/check_dup_ratchet.py
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/quality_declaration_lifecycle.py
- skills/public/retro/SKILL.md
- skills/public/retro/scripts/persist_retro_artifact.py
- skills/public/retro/scripts/probe_host_logs.py
- skills/shared/references/active-goal-coordination.md
- skills/shared/scripts/reviewer_process.py
- skills/shared/scripts/run_reviewer_worker.py
- tests/charness_cli/test_goal_helpers.py
- tests/charness_cli/test_yaml_output_branch_coverage.py
- tests/coverage_debt/test_batch6.py
- tests/quality_gates/test_achieve_adapter_policy.py
- tests/quality_gates/test_achieve_before_activation.py
- tests/quality_gates/test_dup_ratchet_edit_advisory.py
- tests/quality_gates/test_dup_ratchet_scope_coverage.py
- tests/quality_gates/test_goal_closeout_normalize.py
- tests/quality_gates/test_python_length_gates.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_retro_host_log_probe.py
- tests/quality_gates/test_retro_persistence.py
- tests/quality_gates/test_runtime_budget_universe.py
- tests/quality_gates/test_setup_inspect_policy.py
- tests/test_critique_round_findings.py
- tests/test_docs_graph_gate.py
- tests/test_risk_interrupt.py
- charness-artifacts/ideation/2026-08-26-friction-reset.md
- charness-artifacts/impl/2026-08-26-friction-reset-ownership-cutover.md
- docs/implementation-discipline.md
- docs/operating-contract.md
- plugins/charness/scripts/check_skill_contracts.py
- plugins/charness/skills/critique/references/cadence.md
- plugins/charness/skills/prove/references/review-gate.md
- scripts/check_skill_contracts.py
- skills/public/critique/references/cadence.md
- skills/public/prove/references/review-gate.md
- tests/quality_gates/test_critique_skill.py
- .charness/goal-consumer-census.json
- .charness/host-hooks/state.json
- .charness/issue-regroup-plan.json
- .charness/reviewer-output/r1-counterweight.md
- .charness/reviewer-output/r1-framing.md
- .charness/reviewer-output/r1-operability.md
- .charness/reviewer-output/r1-ownership.md
- .charness/reviewer-output/r2-architecture.json
- .charness/reviewer-output/r2-counterweight.json
- .charness/reviewer-output/r2-operator.json
- .charness/reviewer-output/r2-provider.json
- charness-artifacts/critique/2026-08-26-005458-packet.json
- charness-artifacts/critique/2026-08-26-005458-packet.md
- charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f1.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f2.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f3.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md
- charness-artifacts/critique/2026-08-26-goal-binding-v1-r1-packet.json
- charness-artifacts/critique/2026-08-26-goal-binding-v1-r1-packet.md
- charness-artifacts/critique/2026-08-26-goal-binding-v1-r2-packet.json
- charness-artifacts/critique/2026-08-26-goal-binding-v1-r2-packet.md
- charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.json
- charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.md
- charness-artifacts/critique/compact-hook-r10-packet.json
- charness-artifacts/critique/compact-hook-r10-packet.md
- charness-artifacts/critique/compact-hook-r3-packet.json
- charness-artifacts/critique/compact-hook-r3-packet.md
- charness-artifacts/critique/compact-hook-r4-packet.json
- charness-artifacts/critique/compact-hook-r4-packet.md
- charness-artifacts/critique/compact-hook-r5-packet.json
- charness-artifacts/critique/compact-hook-r5-packet.md
- charness-artifacts/critique/compact-hook-r6-packet.json
- charness-artifacts/critique/compact-hook-r6-packet.md
- charness-artifacts/critique/compact-hook-r7-packet.json
- charness-artifacts/critique/compact-hook-r7-packet.md
- charness-artifacts/critique/compact-hook-r8-packet.json
- charness-artifacts/critique/compact-hook-r8-packet.md
- charness-artifacts/critique/compact-hook-r9-packet.json
- charness-artifacts/critique/compact-hook-r9-packet.md
- charness-artifacts/critique/compact-hook-repaired-r2-packet.json
- charness-artifacts/critique/compact-hook-repaired-r2-packet.md
- charness-artifacts/critique/dry-run-plugin-packet.json
- charness-artifacts/critique/dry-run-plugin-packet.md
- charness-artifacts/critique/dry-run-source-2-packet.json
- charness-artifacts/critique/dry-run-source-2-packet.md
- charness-artifacts/critique/dry-run-source-packet.json
- charness-artifacts/critique/dry-run-source-packet.md
- charness-artifacts/critique/issue-726-bootstrap-closeout-r1-packet.json
- charness-artifacts/critique/issue-726-bootstrap-closeout-r1-packet.md
- charness-artifacts/critique/issue-726-bootstrap-closeout-r1-v2-packet.json
- charness-artifacts/critique/issue-726-bootstrap-closeout-r1-v2-packet.md
- charness-artifacts/critique/issue-native-achieve-planning-r1-packet.json
- charness-artifacts/critique/issue-native-achieve-planning-r1-packet.md
- charness-artifacts/critique/issue-native-achieve-planning-r2-packet.json
- charness-artifacts/critique/issue-native-achieve-planning-r2-packet.md
- charness-artifacts/critique/rounds/2026-08-26-r1-counterweight.md
- charness-artifacts/critique/rounds/2026-08-26-r1-framing.md
- charness-artifacts/critique/rounds/2026-08-26-r1-operability.md
- charness-artifacts/critique/rounds/2026-08-26-r1-ownership.md
- charness-artifacts/critique/rounds/2026-08-26-r2-architecture.md
- charness-artifacts/critique/rounds/2026-08-26-r2-counterweight.md
- charness-artifacts/critique/rounds/2026-08-26-r2-operator.md
- charness-artifacts/critique/rounds/2026-08-26-r2-provider.md
- charness-artifacts/gather/2026-08-26-charness-new-issues-728-732.md
- charness-artifacts/gather/2026-08-26-codex-goal-objective-contract.md
- charness-artifacts/gather/2026-08-26-cortex-702-achieve-tracker-reference.md
- charness-artifacts/goal-runs/724/approved-plan.json
- charness-artifacts/goal-runs/724/bodies/achieve-orchestration.md
- charness-artifacts/goal-runs/724/bodies/backlog-546.md
- charness-artifacts/goal-runs/724/bodies/backlog-634.md
- charness-artifacts/goal-runs/724/bodies/backlog-637.md
- charness-artifacts/goal-runs/724/bodies/backlog-667.md
- charness-artifacts/goal-runs/724/bodies/backlog-668.md
- charness-artifacts/goal-runs/724/bodies/backlog-669.md
- charness-artifacts/goal-runs/724/bodies/backlog-692.md
- charness-artifacts/goal-runs/724/bodies/backlog-693.md
- charness-artifacts/goal-runs/724/bodies/backlog-695.md
- charness-artifacts/goal-runs/724/bodies/backlog-697.md
- charness-artifacts/goal-runs/724/bodies/backlog-698.md
- charness-artifacts/goal-runs/724/bodies/backlog-699.md
- charness-artifacts/goal-runs/724/bodies/backlog-700.md
- charness-artifacts/goal-runs/724/bodies/backlog-701.md
- charness-artifacts/goal-runs/724/bodies/backlog-703.md
- charness-artifacts/goal-runs/724/bodies/backlog-704.md
- charness-artifacts/goal-runs/724/bodies/backlog-706.md
- charness-artifacts/goal-runs/724/bodies/backlog-708.md
- charness-artifacts/goal-runs/724/bodies/backlog-710.md
- charness-artifacts/goal-runs/724/bodies/backlog-715.md
- charness-artifacts/goal-runs/724/bodies/backlog-717.md
- charness-artifacts/goal-runs/724/bodies/backlog-722.md
- charness-artifacts/goal-runs/724/bodies/backlog-723.md
- charness-artifacts/goal-runs/724/bodies/dogfood-724-establishment.md
- charness-artifacts/goal-runs/724/bodies/goal-binding-v1.md
- charness-artifacts/goal-runs/724/bodies/goal-evidence-lineage.md
- charness-artifacts/goal-runs/724/bodies/goal-run-provider.md
- charness-artifacts/goal-runs/724/bodies/parent-724-cutover.md
- charness-artifacts/goal-runs/724/bootstrap-final-graph.json
- charness-artifacts/goal-runs/724/establishment-input-readback.md
- charness-artifacts/goal-runs/724/final-graph-readback.md
- charness-artifacts/goal-runs/724/observations/bootstrap-add-goal-binding-v1-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-add-goal-binding-v1-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-add-goal-evidence-lineage-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-add-goal-evidence-lineage-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-546-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-546-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-634-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-634-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-637-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-637-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-667-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-667-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-668-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-668-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-669-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-669-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-692-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-692-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-693-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-693-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-695-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-695-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-697-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-697-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-698-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-698-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-699-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-699-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-700-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-700-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-701-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-701-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-703-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-703-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-704-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-704-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-706-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-706-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-708-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-708-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-710-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-710-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-715-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-715-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-717-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-717-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-722-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-722-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-723-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-723-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-725-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-725-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-726-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-726-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-727-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-body-727-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-binding-v1-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-binding-v1-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-binding-v1-recovery-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-binding-v1-recovery-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-evidence-lineage-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-evidence-lineage-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-evidence-lineage-recovery-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-create-goal-evidence-lineage-recovery-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-cutover-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-cutover-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-identity-url-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-identity-url-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-membership-hash-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-parent-membership-hash-1.terminal.json
- charness-artifacts/goal-runs/724/observations/bootstrap-remove-legacy-unexpected-3-1.started.json
- charness-artifacts/goal-runs/724/observations/bootstrap-remove-legacy-unexpected-3-1.terminal.json
- charness-artifacts/goal-runs/724/observations/goal-run-546-verification-1.started.json
- charness-artifacts/goal-runs/724/observations/goal-run-546-verification-1.terminal.json
- charness-artifacts/goal-runs/724/observations/goal-run-725-roundtrip-1.started.json
- charness-artifacts/goal-runs/724/observations/goal-run-725-roundtrip-1.terminal.json
- charness-artifacts/goal-runs/724/observations/goal-run-727-roundtrip-1.started.json
- charness-artifacts/goal-runs/724/observations/goal-run-727-roundtrip-1.terminal.json
- charness-artifacts/goal-runs/724/observations/target-roundtrip-marker-1.started.json
- charness-artifacts/goal-runs/724/observations/target-roundtrip-marker-1.terminal.json
- charness-artifacts/goal-runs/724/operations/add-goal-binding-v1.json
- charness-artifacts/goal-runs/724/operations/add-goal-evidence-lineage.json
- charness-artifacts/goal-runs/724/operations/create-goal-binding-v1-recovery.json
- charness-artifacts/goal-runs/724/operations/create-goal-binding-v1.json
- charness-artifacts/goal-runs/724/operations/create-goal-evidence-lineage-recovery.json
- charness-artifacts/goal-runs/724/operations/create-goal-evidence-lineage.json
- charness-artifacts/goal-runs/724/operations/parent-cutover.json
- charness-artifacts/goal-runs/724/operations/parent-identity-url.json
- charness-artifacts/goal-runs/724/operations/parent-membership-hash.json
- charness-artifacts/goal-runs/724/operations/remove-legacy-unexpected-3.json
- charness-artifacts/goal-runs/724/operations/target-roundtrip-marker.json
- charness-artifacts/goal-runs/724/operations/update-body-546-verification.json
- charness-artifacts/goal-runs/724/operations/update-body-546.json
- charness-artifacts/goal-runs/724/operations/update-body-634.json
- charness-artifacts/goal-runs/724/operations/update-body-637.json
- charness-artifacts/goal-runs/724/operations/update-body-667.json
- charness-artifacts/goal-runs/724/operations/update-body-668.json
- charness-artifacts/goal-runs/724/operations/update-body-669.json
- charness-artifacts/goal-runs/724/operations/update-body-692.json
- charness-artifacts/goal-runs/724/operations/update-body-693.json
- charness-artifacts/goal-runs/724/operations/update-body-695.json
- charness-artifacts/goal-runs/724/operations/update-body-697.json
- charness-artifacts/goal-runs/724/operations/update-body-698.json
- charness-artifacts/goal-runs/724/operations/update-body-699.json
- charness-artifacts/goal-runs/724/operations/update-body-700.json
- charness-artifacts/goal-runs/724/operations/update-body-701.json
- charness-artifacts/goal-runs/724/operations/update-body-703.json
- charness-artifacts/goal-runs/724/operations/update-body-704.json
- charness-artifacts/goal-runs/724/operations/update-body-706.json
- charness-artifacts/goal-runs/724/operations/update-body-708.json
- charness-artifacts/goal-runs/724/operations/update-body-710.json
- charness-artifacts/goal-runs/724/operations/update-body-715.json
- charness-artifacts/goal-runs/724/operations/update-body-717.json
- charness-artifacts/goal-runs/724/operations/update-body-722.json
- charness-artifacts/goal-runs/724/operations/update-body-723.json
- charness-artifacts/goal-runs/724/operations/update-body-725-roundtrip.json
- charness-artifacts/goal-runs/724/operations/update-body-725.json
- charness-artifacts/goal-runs/724/operations/update-body-726.json
- charness-artifacts/goal-runs/724/operations/update-body-727-roundtrip.json
- charness-artifacts/goal-runs/724/operations/update-body-727.json
- charness-artifacts/goal-runs/724/target-roundtrip-readback.md
- charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json
- charness-artifacts/impl/2026-08-26-goal-run-provider-ownership-cutover.md
- charness-artifacts/impl/2026-08-26-reviewer-lifecycle-ownership-cutover.md
- charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-628.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-694.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-721.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-resume.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-resume.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/achieve-orchestration.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/goal-binding-v1.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/goal-consumer-cutover.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/index.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/consumer-cutover.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/final-alignment-audit.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/implementation-briefing.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md
- plugins/charness/scripts/classify_goal_consumers.py
- plugins/charness/scripts/goal_lineage.py
- plugins/charness/shared/scripts/reviewer_lifecycle.py
- plugins/charness/skills/achieve/scripts/goal_binding.py
- plugins/charness/skills/achieve/scripts/goal_binding_support.py
- plugins/charness/skills/achieve/scripts/goal_run_pickup.py
- plugins/charness/skills/achieve/scripts/goal_run_pickup_contract.py
- plugins/charness/skills/achieve/scripts/interview_contract.py
- plugins/charness/skills/critique/scripts/run_review.py
- plugins/charness/skills/critique/scripts/run_review_packet.py
- plugins/charness/skills/critique/scripts/run_review_support.py
- plugins/charness/skills/issue/scripts/issue_goal_run.py
- plugins/charness/skills/issue/scripts/issue_goal_run_close.py
- plugins/charness/skills/issue/scripts/issue_goal_run_contract.py
- plugins/charness/skills/issue/scripts/issue_goal_run_guard.py
- scripts/classify_goal_consumers.py
- scripts/goal_lineage.py
- skills/public/achieve/scripts/goal_binding.py
- skills/public/achieve/scripts/goal_binding_support.py
- skills/public/achieve/scripts/goal_run_pickup.py
- skills/public/achieve/scripts/goal_run_pickup_contract.py
- skills/public/achieve/scripts/interview_contract.py
- skills/public/critique/scripts/run_review.py
- skills/public/critique/scripts/run_review_packet.py
- skills/public/critique/scripts/run_review_support.py
- skills/public/issue/scripts/issue_goal_run.py
- skills/public/issue/scripts/issue_goal_run_close.py
- skills/public/issue/scripts/issue_goal_run_contract.py
- skills/public/issue/scripts/issue_goal_run_guard.py
- skills/shared/scripts/reviewer_lifecycle.py
- tests/quality_gates/test_achieve_goal_run_pickup.py
- tests/quality_gates/test_achieve_interview_contract.py
- tests/quality_gates/test_goal_binding_v1.py
- tests/quality_gates/test_goal_consumer_census.py
- tests/quality_gates/test_goal_evidence_lineage.py
- tests/quality_gates/test_goal_lineage_consumers.py
- tests/quality_gates/test_issue_goal_run.py
- tests/quality_gates/test_semantic_review_command.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check_docs_graph.py, scripts/check_premise_preflight.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/closeout_bundle.py, scripts/closeout_bundle_lib.py, scripts/dup_ratchet_edit_advisory.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_lib.py, scripts/host_log_probe_lib.py, scripts/plan_risk_interrupt.py, scripts/premise_preflight_lib.py, scripts/public_skill_dogfood_lib.py, scripts/retro_persistence_lib.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py, skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/goal_cli_args.py, skills/public/achieve/scripts/init_adapter.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_tracker_cli.py, skills/public/issue/scripts/issue_tracker_cli_parser.py, skills/public/prove/SKILL.md, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/retro/SKILL.md, skills/public/retro/scripts/persist_retro_artifact.py, skills/public/retro/scripts/probe_host_logs.py, skills/shared/references/active-goal-coordination.md, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/run_reviewer_worker.py, scripts/check_skill_contracts.py, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md, scripts/classify_goal_consumers.py, scripts/goal_lineage.py, skills/public/achieve/scripts/goal_binding.py, skills/public/achieve/scripts/goal_binding_support.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/achieve/scripts/interview_contract.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_support.py, skills/public/issue/scripts/issue_goal_run.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_contract.py, skills/public/issue/scripts/issue_goal_run_guard.py, skills/shared/scripts/reviewer_lifecycle.py
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/closeout_bundle.py, plugins/charness/scripts/closeout_bundle_lib.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/host_log_probe_lib.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py, plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/shared/scripts/reviewer_process.py, plugins/charness/shared/scripts/run_reviewer_worker.py, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/adapter.example.yaml, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/index.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py, plugins/charness/skills/achieve/scripts/goal_cli_args.py, plugins/charness/skills/achieve/scripts/init_adapter.py, plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/record_round_findings.py, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_tracker_cli.py, plugins/charness/skills/issue/scripts/issue_tracker_cli_parser.py, plugins/charness/skills/prove/SKILL.md, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/scripts/persist_retro_artifact.py, plugins/charness/skills/retro/scripts/probe_host_logs.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/prove/references/review-gate.md, plugins/charness/scripts/classify_goal_consumers.py, plugins/charness/scripts/goal_lineage.py, plugins/charness/shared/scripts/reviewer_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_binding.py, plugins/charness/skills/achieve/scripts/goal_binding_support.py, plugins/charness/skills/achieve/scripts/goal_run_pickup.py, plugins/charness/skills/achieve/scripts/goal_run_pickup_contract.py, plugins/charness/skills/achieve/scripts/interview_contract.py, plugins/charness/skills/critique/scripts/run_review.py, plugins/charness/skills/critique/scripts/run_review_packet.py, plugins/charness/skills/critique/scripts/run_review_support.py, plugins/charness/skills/issue/scripts/issue_goal_run.py, plugins/charness/skills/issue/scripts/issue_goal_run_close.py, plugins/charness/skills/issue/scripts/issue_goal_run_contract.py, plugins/charness/skills/issue/scripts/issue_goal_run_guard.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: .agents/command-docs.yaml, charness-artifacts/gather/latest.md, charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md, docs/artifact-policy.md, docs/cli-reference.md, docs/development.md, docs/goal-lifecycle.md, docs/index.md, docs/readme-proof.md, docs/workflow-routes.md, skills/public/achieve/SKILL.md, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/prove/SKILL.md, skills/public/retro/SKILL.md, skills/shared/references/active-goal-coordination.md, charness-artifacts/ideation/2026-08-26-friction-reset.md, charness-artifacts/impl/2026-08-26-friction-reset-ownership-cutover.md, docs/implementation-discipline.md, docs/operating-contract.md, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md, charness-artifacts/critique/2026-08-26-005458-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md, charness-artifacts/critique/2026-08-26-goal-binding-v1-r1-packet.md, charness-artifacts/critique/2026-08-26-goal-binding-v1-r2-packet.md, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.md, charness-artifacts/critique/compact-hook-r10-packet.md, charness-artifacts/critique/compact-hook-r3-packet.md, charness-artifacts/critique/compact-hook-r4-packet.md, charness-artifacts/critique/compact-hook-r5-packet.md, charness-artifacts/critique/compact-hook-r6-packet.md, charness-artifacts/critique/compact-hook-r7-packet.md, charness-artifacts/critique/compact-hook-r8-packet.md, charness-artifacts/critique/compact-hook-r9-packet.md, charness-artifacts/critique/compact-hook-repaired-r2-packet.md, charness-artifacts/critique/dry-run-plugin-packet.md, charness-artifacts/critique/dry-run-source-2-packet.md, charness-artifacts/critique/dry-run-source-packet.md, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-packet.md, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-v2-packet.md, charness-artifacts/critique/issue-native-achieve-planning-r1-packet.md, charness-artifacts/critique/issue-native-achieve-planning-r2-packet.md, charness-artifacts/critique/rounds/2026-08-26-r1-counterweight.md, charness-artifacts/critique/rounds/2026-08-26-r1-framing.md, charness-artifacts/critique/rounds/2026-08-26-r1-operability.md, charness-artifacts/critique/rounds/2026-08-26-r1-ownership.md, charness-artifacts/critique/rounds/2026-08-26-r2-architecture.md, charness-artifacts/critique/rounds/2026-08-26-r2-counterweight.md, charness-artifacts/critique/rounds/2026-08-26-r2-operator.md, charness-artifacts/critique/rounds/2026-08-26-r2-provider.md, charness-artifacts/gather/2026-08-26-charness-new-issues-728-732.md, charness-artifacts/gather/2026-08-26-codex-goal-objective-contract.md, charness-artifacts/gather/2026-08-26-cortex-702-achieve-tracker-reference.md, charness-artifacts/goal-runs/724/bodies/achieve-orchestration.md, charness-artifacts/goal-runs/724/bodies/backlog-546.md, charness-artifacts/goal-runs/724/bodies/backlog-634.md, charness-artifacts/goal-runs/724/bodies/backlog-637.md, charness-artifacts/goal-runs/724/bodies/backlog-667.md, charness-artifacts/goal-runs/724/bodies/backlog-668.md, charness-artifacts/goal-runs/724/bodies/backlog-669.md, charness-artifacts/goal-runs/724/bodies/backlog-692.md, charness-artifacts/goal-runs/724/bodies/backlog-693.md, charness-artifacts/goal-runs/724/bodies/backlog-695.md, charness-artifacts/goal-runs/724/bodies/backlog-697.md, charness-artifacts/goal-runs/724/bodies/backlog-698.md, charness-artifacts/goal-runs/724/bodies/backlog-699.md, charness-artifacts/goal-runs/724/bodies/backlog-700.md, charness-artifacts/goal-runs/724/bodies/backlog-701.md, charness-artifacts/goal-runs/724/bodies/backlog-703.md, charness-artifacts/goal-runs/724/bodies/backlog-704.md, charness-artifacts/goal-runs/724/bodies/backlog-706.md, charness-artifacts/goal-runs/724/bodies/backlog-708.md, charness-artifacts/goal-runs/724/bodies/backlog-710.md, charness-artifacts/goal-runs/724/bodies/backlog-715.md, charness-artifacts/goal-runs/724/bodies/backlog-717.md, charness-artifacts/goal-runs/724/bodies/backlog-722.md, charness-artifacts/goal-runs/724/bodies/backlog-723.md, charness-artifacts/goal-runs/724/bodies/dogfood-724-establishment.md, charness-artifacts/goal-runs/724/bodies/goal-binding-v1.md, charness-artifacts/goal-runs/724/bodies/goal-evidence-lineage.md, charness-artifacts/goal-runs/724/bodies/goal-run-provider.md, charness-artifacts/goal-runs/724/bodies/parent-724-cutover.md, charness-artifacts/goal-runs/724/establishment-input-readback.md, charness-artifacts/goal-runs/724/final-graph-readback.md, charness-artifacts/goal-runs/724/target-roundtrip-readback.md, charness-artifacts/impl/2026-08-26-goal-run-provider-ownership-cutover.md, charness-artifacts/impl/2026-08-26-reviewer-lifecycle-ownership-cutover.md, charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md, charness-artifacts/issues/closeouts/2026-08-26-issue-628.md, charness-artifacts/issues/closeouts/2026-08-26-issue-694.md, charness-artifacts/issues/closeouts/2026-08-26-issue-721.md, charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md, charness-artifacts/retro/lesson-session-receipts/2026-08-26-resume.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/achieve-orchestration.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/goal-binding-v1.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/goal-consumer-cutover.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/index.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/consumer-cutover.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/final-alignment-audit.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/implementation-briefing.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md
  derived matches: plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/index.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/prove/SKILL.md, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/prove/references/review-gate.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- goal-evidence-json: Machine-readable evidence captured beside achieve goal artifacts.
  source matches: charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.binding.json
  verify: for evidence_file in charness-artifacts/goals/*.json; do python3 -m json.tool "$evidence_file" >/dev/null || exit $?; done, python3 -c 'import json, pathlib; [json.loads(line) for path in pathlib.Path("charness-artifacts/goals").glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]', python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md, charness-artifacts/issues/closeouts/2026-08-26-issue-628.md, charness-artifacts/issues/closeouts/2026-08-26-issue-694.md, charness-artifacts/issues/closeouts/2026-08-26-issue-721.md
  verify: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/validate_quality_artifact.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/achieve-adapter.yaml, .agents/release-adapter.yaml, skills/public/achieve/SKILL.md, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/prove/SKILL.md, skills/public/retro/SKILL.md, skills/shared/references/active-goal-coordination.md, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/goal_cli_args.py, skills/public/achieve/scripts/init_adapter.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_tracker_cli.py, skills/public/issue/scripts/issue_tracker_cli_parser.py, skills/public/prove/SKILL.md, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/retro/SKILL.md, skills/public/retro/scripts/persist_retro_artifact.py, skills/public/retro/scripts/probe_host_logs.py, skills/shared/references/active-goal-coordination.md, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/run_reviewer_worker.py, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md, skills/public/achieve/scripts/goal_binding.py, skills/public/achieve/scripts/goal_binding_support.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/achieve/scripts/interview_contract.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_support.py, skills/public/issue/scripts/issue_goal_run.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_contract.py, skills/public/issue/scripts/issue_goal_run_guard.py, skills/shared/scripts/reviewer_lifecycle.py
  derived matches: plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/shared/scripts/reviewer_process.py, plugins/charness/shared/scripts/run_reviewer_worker.py, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/adapter.example.yaml, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/index.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py, plugins/charness/skills/achieve/scripts/goal_cli_args.py, plugins/charness/skills/achieve/scripts/init_adapter.py, plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/record_round_findings.py, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_tracker_cli.py, plugins/charness/skills/issue/scripts/issue_tracker_cli_parser.py, plugins/charness/skills/prove/SKILL.md, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/scripts/persist_retro_artifact.py, plugins/charness/skills/retro/scripts/probe_host_logs.py, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/prove/references/review-gate.md, plugins/charness/shared/scripts/reviewer_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_binding.py, plugins/charness/skills/achieve/scripts/goal_binding_support.py, plugins/charness/skills/achieve/scripts/goal_run_pickup.py, plugins/charness/skills/achieve/scripts/goal_run_pickup_contract.py, plugins/charness/skills/achieve/scripts/interview_contract.py, plugins/charness/skills/critique/scripts/run_review.py, plugins/charness/skills/critique/scripts/run_review_packet.py, plugins/charness/skills/critique/scripts/run_review_support.py, plugins/charness/skills/issue/scripts/issue_goal_run.py, plugins/charness/skills/issue/scripts/issue_goal_run_close.py, plugins/charness/skills/issue/scripts/issue_goal_run_contract.py, plugins/charness/skills/issue/scripts/issue_goal_run_guard.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 scripts/validate_current_pointer_freshness.py --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/goal_cli_args.py, skills/public/achieve/scripts/init_adapter.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_tracker_cli.py, skills/public/issue/scripts/issue_tracker_cli_parser.py, skills/public/prove/SKILL.md, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/retro/SKILL.md, skills/public/retro/scripts/persist_retro_artifact.py, skills/public/retro/scripts/probe_host_logs.py, skills/shared/references/active-goal-coordination.md, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/run_reviewer_worker.py, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md, skills/public/achieve/scripts/goal_binding.py, skills/public/achieve/scripts/goal_binding_support.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/achieve/scripts/interview_contract.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_support.py, skills/public/issue/scripts/issue_goal_run.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_contract.py, skills/public/issue/scripts/issue_goal_run_guard.py, skills/shared/scripts/reviewer_lifecycle.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, scripts/public_skill_dogfood_lib.py, skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/index.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/goal_cli_args.py, skills/public/achieve/scripts/init_adapter.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_tracker_cli.py, skills/public/issue/scripts/issue_tracker_cli_parser.py, skills/public/prove/SKILL.md, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/retro/SKILL.md, skills/public/retro/scripts/persist_retro_artifact.py, skills/public/retro/scripts/probe_host_logs.py, skills/shared/references/active-goal-coordination.md, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/run_reviewer_worker.py, skills/public/critique/references/cadence.md, skills/public/prove/references/review-gate.md, skills/public/achieve/scripts/goal_binding.py, skills/public/achieve/scripts/goal_binding_support.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/achieve/scripts/interview_contract.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_support.py, skills/public/issue/scripts/issue_goal_run.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_contract.py, skills/public/issue/scripts/issue_goal_run_guard.py, skills/shared/scripts/reviewer_lifecycle.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/achieve-adapter.yaml, .agents/release-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- cli-ergonomics-inventory: Advisory CLI ergonomics registry and archetype inputs for the charness command surface.
  source matches: .agents/command-registry.json
  verify: python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root . --detail
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-26-005458-packet.json, charness-artifacts/critique/2026-08-26-005458-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-f1.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-f2.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-f3.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md, charness-artifacts/critique/2026-08-26-goal-binding-v1-r1-packet.json, charness-artifacts/critique/2026-08-26-goal-binding-v1-r1-packet.md, charness-artifacts/critique/2026-08-26-goal-binding-v1-r2-packet.json, charness-artifacts/critique/2026-08-26-goal-binding-v1-r2-packet.md, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.json, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.md, charness-artifacts/critique/compact-hook-r10-packet.json, charness-artifacts/critique/compact-hook-r10-packet.md, charness-artifacts/critique/compact-hook-r3-packet.json, charness-artifacts/critique/compact-hook-r3-packet.md, charness-artifacts/critique/compact-hook-r4-packet.json, charness-artifacts/critique/compact-hook-r4-packet.md, charness-artifacts/critique/compact-hook-r5-packet.json, charness-artifacts/critique/compact-hook-r5-packet.md, charness-artifacts/critique/compact-hook-r6-packet.json, charness-artifacts/critique/compact-hook-r6-packet.md, charness-artifacts/critique/compact-hook-r7-packet.json, charness-artifacts/critique/compact-hook-r7-packet.md, charness-artifacts/critique/compact-hook-r8-packet.json, charness-artifacts/critique/compact-hook-r8-packet.md, charness-artifacts/critique/compact-hook-r9-packet.json, charness-artifacts/critique/compact-hook-r9-packet.md, charness-artifacts/critique/compact-hook-repaired-r2-packet.json, charness-artifacts/critique/compact-hook-repaired-r2-packet.md, charness-artifacts/critique/dry-run-plugin-packet.json, charness-artifacts/critique/dry-run-plugin-packet.md, charness-artifacts/critique/dry-run-source-2-packet.json, charness-artifacts/critique/dry-run-source-2-packet.md, charness-artifacts/critique/dry-run-source-packet.json, charness-artifacts/critique/dry-run-source-packet.md, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-packet.json, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-packet.md, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-v2-packet.json, charness-artifacts/critique/issue-726-bootstrap-closeout-r1-v2-packet.md, charness-artifacts/critique/issue-native-achieve-planning-r1-packet.json, charness-artifacts/critique/issue-native-achieve-planning-r1-packet.md, charness-artifacts/critique/issue-native-achieve-planning-r2-packet.json, charness-artifacts/critique/issue-native-achieve-planning-r2-packet.md, charness-artifacts/critique/rounds/2026-08-26-r1-counterweight.md, charness-artifacts/critique/rounds/2026-08-26-r1-framing.md, charness-artifacts/critique/rounds/2026-08-26-r1-operability.md, charness-artifacts/critique/rounds/2026-08-26-r1-ownership.md, charness-artifacts/critique/rounds/2026-08-26-r2-architecture.md, charness-artifacts/critique/rounds/2026-08-26-r2-counterweight.md, charness-artifacts/critique/rounds/2026-08-26-r2-operator.md, charness-artifacts/critique/rounds/2026-08-26-r2-provider.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: scripts/retro_persistence_lib.py, charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md, charness-artifacts/retro/lesson-session-receipts/2026-08-26-resume.md
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.json, charness-artifacts/retro/lesson-session-receipts/2026-08-26-resume.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/closeout_bundle.py, plugins/charness/scripts/closeout_bundle_lib.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/host_log_probe_lib.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py, plugins/charness/scripts/check_skill_contracts.py, .charness/goal-consumer-census.json, .charness/host-hooks/state.json, .charness/issue-regroup-plan.json, .charness/reviewer-output/r2-architecture.json, .charness/reviewer-output/r2-counterweight.json, .charness/reviewer-output/r2-operator.json, .charness/reviewer-output/r2-provider.json, plugins/charness/scripts/classify_goal_consumers.py, plugins/charness/scripts/goal_lineage.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/check_docs_graph.py, scripts/check_premise_preflight.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/closeout_bundle.py, scripts/closeout_bundle_lib.py, scripts/dup_ratchet_edit_advisory.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_lib.py, scripts/host_log_probe_lib.py, scripts/plan_risk_interrupt.py, scripts/premise_preflight_lib.py, scripts/public_skill_dogfood_lib.py, scripts/retro_persistence_lib.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py, tests/charness_cli/test_goal_helpers.py, tests/charness_cli/test_yaml_output_branch_coverage.py, tests/coverage_debt/test_batch6.py, tests/quality_gates/test_achieve_adapter_policy.py, tests/quality_gates/test_achieve_before_activation.py, tests/quality_gates/test_dup_ratchet_edit_advisory.py, tests/quality_gates/test_dup_ratchet_scope_coverage.py, tests/quality_gates/test_goal_closeout_normalize.py, tests/quality_gates/test_python_length_gates.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_retro_host_log_probe.py, tests/quality_gates/test_retro_persistence.py, tests/quality_gates/test_runtime_budget_universe.py, tests/quality_gates/test_setup_inspect_policy.py, tests/test_critique_round_findings.py, tests/test_docs_graph_gate.py, tests/test_risk_interrupt.py, scripts/check_skill_contracts.py, tests/quality_gates/test_critique_skill.py, scripts/classify_goal_consumers.py, scripts/goal_lineage.py, tests/quality_gates/test_achieve_goal_run_pickup.py, tests/quality_gates/test_achieve_interview_contract.py, tests/quality_gates/test_goal_binding_v1.py, tests/quality_gates/test_goal_consumer_census.py, tests/quality_gates/test_goal_evidence_lineage.py, tests/quality_gates/test_goal_lineage_consumers.py, tests/quality_gates/test_issue_goal_run.py, tests/quality_gates/test_semantic_review_command.py
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/closeout_bundle.py, plugins/charness/scripts/closeout_bundle_lib.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/host_log_probe_lib.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/classify_goal_consumers.py, plugins/charness/scripts/goal_lineage.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: scripts/check_python_lengths.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_docs_graph.py, scripts/check_premise_preflight.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/closeout_bundle.py, scripts/closeout_bundle_lib.py, scripts/dup_ratchet_edit_advisory.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_lib.py, scripts/host_log_probe_lib.py, scripts/plan_risk_interrupt.py, scripts/premise_preflight_lib.py, scripts/public_skill_dogfood_lib.py, scripts/retro_persistence_lib.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/goal_cli_args.py, skills/public/achieve/scripts/init_adapter.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/scripts/record_round_findings.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_tracker_cli.py, skills/public/issue/scripts/issue_tracker_cli_parser.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/retro/scripts/persist_retro_artifact.py, skills/public/retro/scripts/probe_host_logs.py, scripts/check_skill_contracts.py, scripts/classify_goal_consumers.py, scripts/goal_lineage.py, skills/public/achieve/scripts/goal_binding.py, skills/public/achieve/scripts/goal_binding_support.py, skills/public/achieve/scripts/goal_run_pickup.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/achieve/scripts/interview_contract.py, skills/public/critique/scripts/run_review.py, skills/public/critique/scripts/run_review_packet.py, skills/public/critique/scripts/run_review_support.py, skills/public/issue/scripts/issue_goal_run.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_contract.py, skills/public/issue/scripts/issue_goal_run_guard.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- closeout-floor-matrix: Declared floor x classification x carrier matrix for issue closeout, and the behavioral probe that re-derives it from the real carriers.
  source matches: skills/public/issue/scripts/issue_close.py
  verify: python3 scripts/check_closeout_floor_matrix.py --repo-root .

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
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
