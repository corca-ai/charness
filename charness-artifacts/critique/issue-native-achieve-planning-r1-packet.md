# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-26T06:56:01Z
- **Prepared for**: issue-native achieve planning critique round 1
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `284146b7316146be3b1adfc6b4117903658f4f1372a75a5506c77cda9ea0a53b`
- **Reviewed paths**: 3
  - `charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md`
  - `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md`
  - `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/issue-native-achieve-planning-r1-packet.json --packet-sha256 59425e174344798ed0ed1d3bcfd90e05f2040e3808ba9103a6f2a97de769a06a --identity-sha256 284146b7316146be3b1adfc6b4117903658f4f1372a75a5506c77cda9ea0a53b
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
- charness-artifacts/gather/latest.md
- charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md
- charness-artifacts/retro/lesson-ledger.json
- docs/public-skill-dogfood.json
- plugins/charness/scripts/check_docs_graph.py
- plugins/charness/scripts/check_python_lengths.py
- plugins/charness/scripts/check_runtime_budget_universe.py
- plugins/charness/scripts/dup_ratchet_edit_advisory.py
- plugins/charness/scripts/plan_risk_interrupt.py
- plugins/charness/scripts/setup_agent_docs_lib.py
- plugins/charness/scripts/setup_inspect_quality_lib.py
- plugins/charness/shared/references/active-goal-coordination.md
- plugins/charness/skills/achieve/SKILL.md
- plugins/charness/skills/achieve/adapter.example.yaml
- plugins/charness/skills/achieve/references/adapter-contract.md
- plugins/charness/skills/achieve/references/lifecycle-after.md
- plugins/charness/skills/achieve/references/lifecycle-before.md
- plugins/charness/skills/achieve/references/lifecycle-during.md
- plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py
- plugins/charness/skills/achieve/scripts/append_slice_log.py
- plugins/charness/skills/achieve/scripts/check_goal_artifact.py
- plugins/charness/skills/achieve/scripts/init_adapter.py
- plugins/charness/skills/issue/SKILL.md
- plugins/charness/skills/issue/adapter.example.yaml
- plugins/charness/skills/issue/references/issue-backend.md
- plugins/charness/skills/issue/scripts/issue_tool.py
- plugins/charness/skills/quality/scripts/check_dup_ratchet.py
- plugins/charness/skills/quality/scripts/plan_quality_run.py
- plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py
- scripts/check_docs_graph.py
- scripts/check_python_lengths.py
- scripts/check_runtime_budget_universe.py
- scripts/dup_ratchet_edit_advisory.py
- scripts/plan_risk_interrupt.py
- scripts/setup_agent_docs_lib.py
- scripts/setup_inspect_quality_lib.py
- skills/public/achieve/SKILL.md
- skills/public/achieve/adapter.example.yaml
- skills/public/achieve/references/adapter-contract.md
- skills/public/achieve/references/lifecycle-after.md
- skills/public/achieve/references/lifecycle-before.md
- skills/public/achieve/references/lifecycle-during.md
- skills/public/achieve/scripts/achieve_adapter_policy.py
- skills/public/achieve/scripts/append_slice_log.py
- skills/public/achieve/scripts/check_goal_artifact.py
- skills/public/achieve/scripts/init_adapter.py
- skills/public/issue/SKILL.md
- skills/public/issue/adapter.example.yaml
- skills/public/issue/references/issue-backend.md
- skills/public/issue/scripts/issue_tool.py
- skills/public/quality/scripts/check_dup_ratchet.py
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/quality_declaration_lifecycle.py
- skills/shared/references/active-goal-coordination.md
- tests/quality_gates/test_achieve_adapter_policy.py
- tests/quality_gates/test_dup_ratchet_edit_advisory.py
- tests/quality_gates/test_dup_ratchet_scope_coverage.py
- tests/quality_gates/test_issue_skill.py
- tests/quality_gates/test_python_length_gates.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_runtime_budget_universe.py
- tests/quality_gates/test_setup_inspect_policy.py
- tests/test_docs_graph_gate.py
- tests/test_risk_interrupt.py
- .charness/host-hooks/state.json
- .charness/issue-regroup-plan.json
- charness-artifacts/critique/2026-08-26-005458-packet.json
- charness-artifacts/critique/2026-08-26-005458-packet.md
- charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f1.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f2.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-f3.json
- charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md
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
- charness-artifacts/gather/2026-08-26-cortex-702-achieve-tracker-reference.md
- charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-628.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-694.md
- charness-artifacts/issues/closeouts/2026-08-26-issue-721.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md
- charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md
- plugins/charness/skills/achieve/scripts/goal_tracker_receipt.py
- plugins/charness/skills/achieve/scripts/interview_contract.py
- plugins/charness/skills/achieve/scripts/write_goal_receipt.py
- plugins/charness/skills/issue/scripts/issue_tracker.py
- skills/public/achieve/scripts/goal_tracker_receipt.py
- skills/public/achieve/scripts/interview_contract.py
- skills/public/achieve/scripts/write_goal_receipt.py
- skills/public/issue/scripts/issue_tracker.py
- tests/quality_gates/test_achieve_interview_contract.py
- tests/quality_gates/test_goal_tracker_receipt.py
- tests/quality_gates/test_issue_tracker.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check_docs_graph.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/dup_ratchet_edit_advisory.py, scripts/plan_risk_interrupt.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/append_slice_log.py, skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/init_adapter.py, skills/public/issue/SKILL.md, skills/public/issue/adapter.example.yaml, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_tool.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/shared/references/active-goal-coordination.md, skills/public/achieve/scripts/goal_tracker_receipt.py, skills/public/achieve/scripts/interview_contract.py, skills/public/achieve/scripts/write_goal_receipt.py, skills/public/issue/scripts/issue_tracker.py
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py, plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/adapter.example.yaml, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py, plugins/charness/skills/achieve/scripts/append_slice_log.py, plugins/charness/skills/achieve/scripts/check_goal_artifact.py, plugins/charness/skills/achieve/scripts/init_adapter.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/adapter.example.yaml, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_tool.py, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_tracker_receipt.py, plugins/charness/skills/achieve/scripts/interview_contract.py, plugins/charness/skills/achieve/scripts/write_goal_receipt.py, plugins/charness/skills/issue/scripts/issue_tracker.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/gather/latest.md, charness-artifacts/goals/2026-08-26-adversarial-priority-backlog-closeout.md, skills/public/achieve/SKILL.md, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/shared/references/active-goal-coordination.md, charness-artifacts/critique/2026-08-26-005458-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.md, charness-artifacts/critique/compact-hook-r10-packet.md, charness-artifacts/critique/compact-hook-r3-packet.md, charness-artifacts/critique/compact-hook-r4-packet.md, charness-artifacts/critique/compact-hook-r5-packet.md, charness-artifacts/critique/compact-hook-r6-packet.md, charness-artifacts/critique/compact-hook-r7-packet.md, charness-artifacts/critique/compact-hook-r8-packet.md, charness-artifacts/critique/compact-hook-r9-packet.md, charness-artifacts/critique/compact-hook-repaired-r2-packet.md, charness-artifacts/gather/2026-08-26-cortex-702-achieve-tracker-reference.md, charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md, charness-artifacts/issues/closeouts/2026-08-26-issue-628.md, charness-artifacts/issues/closeouts/2026-08-26-issue-694.md, charness-artifacts/issues/closeouts/2026-08-26-issue-721.md, charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/planning-contract.md, charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/spec.md
  derived matches: plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/issues/2026-08-26-adversarial-priority-backlog-requalification.md, charness-artifacts/issues/closeouts/2026-08-26-issue-628.md, charness-artifacts/issues/closeouts/2026-08-26-issue-694.md, charness-artifacts/issues/closeouts/2026-08-26-issue-721.md
  verify: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/validate_quality_artifact.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/achieve-adapter.yaml, skills/public/achieve/SKILL.md, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/shared/references/active-goal-coordination.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/append_slice_log.py, skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/init_adapter.py, skills/public/issue/SKILL.md, skills/public/issue/adapter.example.yaml, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_tool.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/shared/references/active-goal-coordination.md, skills/public/achieve/scripts/goal_tracker_receipt.py, skills/public/achieve/scripts/interview_contract.py, skills/public/achieve/scripts/write_goal_receipt.py, skills/public/issue/scripts/issue_tracker.py
  derived matches: plugins/charness/shared/references/active-goal-coordination.md, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/adapter.example.yaml, plugins/charness/skills/achieve/references/adapter-contract.md, plugins/charness/skills/achieve/references/lifecycle-after.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/scripts/achieve_adapter_policy.py, plugins/charness/skills/achieve/scripts/append_slice_log.py, plugins/charness/skills/achieve/scripts/check_goal_artifact.py, plugins/charness/skills/achieve/scripts/init_adapter.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/adapter.example.yaml, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_tool.py, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_tracker_receipt.py, plugins/charness/skills/achieve/scripts/interview_contract.py, plugins/charness/skills/achieve/scripts/write_goal_receipt.py, plugins/charness/skills/issue/scripts/issue_tracker.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/append_slice_log.py, skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/init_adapter.py, skills/public/issue/SKILL.md, skills/public/issue/adapter.example.yaml, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_tool.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/shared/references/active-goal-coordination.md, skills/public/achieve/scripts/goal_tracker_receipt.py, skills/public/achieve/scripts/interview_contract.py, skills/public/achieve/scripts/write_goal_receipt.py, skills/public/issue/scripts/issue_tracker.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/achieve/SKILL.md, skills/public/achieve/adapter.example.yaml, skills/public/achieve/references/adapter-contract.md, skills/public/achieve/references/lifecycle-after.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/append_slice_log.py, skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/init_adapter.py, skills/public/issue/SKILL.md, skills/public/issue/adapter.example.yaml, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_tool.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/shared/references/active-goal-coordination.md, skills/public/achieve/scripts/goal_tracker_receipt.py, skills/public/achieve/scripts/interview_contract.py, skills/public/achieve/scripts/write_goal_receipt.py, skills/public/issue/scripts/issue_tracker.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/achieve-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-26-005458-packet.json, charness-artifacts/critique/2026-08-26-005458-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-closeout-packet.md, charness-artifacts/critique/2026-08-26-adversarial-no-change-f1.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-f2.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-f3.json, charness-artifacts/critique/2026-08-26-adversarial-no-change-issue-closeout.md, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.json, charness-artifacts/critique/2026-08-26-phase0-issue-native-achieve-r1-packet.md, charness-artifacts/critique/compact-hook-r10-packet.json, charness-artifacts/critique/compact-hook-r10-packet.md, charness-artifacts/critique/compact-hook-r3-packet.json, charness-artifacts/critique/compact-hook-r3-packet.md, charness-artifacts/critique/compact-hook-r4-packet.json, charness-artifacts/critique/compact-hook-r4-packet.md, charness-artifacts/critique/compact-hook-r5-packet.json, charness-artifacts/critique/compact-hook-r5-packet.md, charness-artifacts/critique/compact-hook-r6-packet.json, charness-artifacts/critique/compact-hook-r6-packet.md, charness-artifacts/critique/compact-hook-r7-packet.json, charness-artifacts/critique/compact-hook-r7-packet.md, charness-artifacts/critique/compact-hook-r8-packet.json, charness-artifacts/critique/compact-hook-r8-packet.md, charness-artifacts/critique/compact-hook-r9-packet.json, charness-artifacts/critique/compact-hook-r9-packet.md, charness-artifacts/critique/compact-hook-repaired-r2-packet.json, charness-artifacts/critique/compact-hook-repaired-r2-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.md
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-26-01a03c37-b39b-7541-9dc2-95459b1d7479.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py, .charness/host-hooks/state.json, .charness/issue-regroup-plan.json
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/check_docs_graph.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/dup_ratchet_edit_advisory.py, scripts/plan_risk_interrupt.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, tests/quality_gates/test_achieve_adapter_policy.py, tests/quality_gates/test_dup_ratchet_edit_advisory.py, tests/quality_gates/test_dup_ratchet_scope_coverage.py, tests/quality_gates/test_issue_skill.py, tests/quality_gates/test_python_length_gates.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_runtime_budget_universe.py, tests/quality_gates/test_setup_inspect_policy.py, tests/test_docs_graph_gate.py, tests/test_risk_interrupt.py, tests/quality_gates/test_achieve_interview_contract.py, tests/quality_gates/test_goal_tracker_receipt.py, tests/quality_gates/test_issue_tracker.py
  derived matches: plugins/charness/scripts/check_docs_graph.py, plugins/charness/scripts/check_python_lengths.py, plugins/charness/scripts/check_runtime_budget_universe.py, plugins/charness/scripts/dup_ratchet_edit_advisory.py, plugins/charness/scripts/plan_risk_interrupt.py, plugins/charness/scripts/setup_agent_docs_lib.py, plugins/charness/scripts/setup_inspect_quality_lib.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: scripts/check_python_lengths.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_docs_graph.py, scripts/check_python_lengths.py, scripts/check_runtime_budget_universe.py, scripts/dup_ratchet_edit_advisory.py, scripts/plan_risk_interrupt.py, scripts/setup_agent_docs_lib.py, scripts/setup_inspect_quality_lib.py, skills/public/achieve/scripts/achieve_adapter_policy.py, skills/public/achieve/scripts/append_slice_log.py, skills/public/achieve/scripts/check_goal_artifact.py, skills/public/achieve/scripts/init_adapter.py, skills/public/issue/scripts/issue_tool.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/achieve/scripts/goal_tracker_receipt.py, skills/public/achieve/scripts/interview_contract.py, skills/public/achieve/scripts/write_goal_receipt.py, skills/public/issue/scripts/issue_tracker.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

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
