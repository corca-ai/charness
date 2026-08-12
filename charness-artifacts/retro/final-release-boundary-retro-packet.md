# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-08-12T21:48:30Z
- **Prepared for**: final release-boundary retro
- **Changed ref**: `ef07aca4af2339872708f4141ec7d96dec8e9f5c..0ac9260d51bd0890d1fec6fb3c5ca411698623da`
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 1
- **Overall ok**: True


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for ref `ef07aca4af2339872708f4141ec7d96dec8e9f5c..0ac9260d51bd0890d1fec6fb3c5ca411698623da`:
- charness-artifacts/critique/2026-08-12-140743-packet.json
- charness-artifacts/critique/2026-08-12-140743-packet.md
- charness-artifacts/critique/2026-08-12-141010-packet.json
- charness-artifacts/critique/2026-08-12-141010-packet.md
- charness-artifacts/critique/2026-08-12-142919-packet.json
- charness-artifacts/critique/2026-08-12-142919-packet.md
- charness-artifacts/critique/2026-08-12-143920-packet.json
- charness-artifacts/critique/2026-08-12-143920-packet.md
- charness-artifacts/critique/2026-08-12-144548-packet.json
- charness-artifacts/critique/2026-08-12-144548-packet.md
- charness-artifacts/critique/2026-08-12-145810-packet.json
- charness-artifacts/critique/2026-08-12-145810-packet.md
- charness-artifacts/critique/2026-08-12-151434-packet.json
- charness-artifacts/critique/2026-08-12-151434-packet.md
- charness-artifacts/critique/2026-08-12-152909-packet.json
- charness-artifacts/critique/2026-08-12-152909-packet.md
- charness-artifacts/critique/2026-08-12-154616-packet.json
- charness-artifacts/critique/2026-08-12-154616-packet.md
- charness-artifacts/critique/2026-08-12-154946-packet.json
- charness-artifacts/critique/2026-08-12-154946-packet.md
- charness-artifacts/critique/2026-08-12-155204-packet.json
- charness-artifacts/critique/2026-08-12-155204-packet.md
- charness-artifacts/critique/2026-08-12-160206-packet.json
- charness-artifacts/critique/2026-08-12-160206-packet.md
- charness-artifacts/critique/2026-08-12-160548-packet.json
- charness-artifacts/critique/2026-08-12-160548-packet.md
- charness-artifacts/critique/2026-08-12-160812-packet.json
- charness-artifacts/critique/2026-08-12-160812-packet.md
- charness-artifacts/critique/2026-08-12-160936-packet.json
- charness-artifacts/critique/2026-08-12-160936-packet.md
- charness-artifacts/critique/2026-08-12-161938-packet.json
- charness-artifacts/critique/2026-08-12-161938-packet.md
- charness-artifacts/critique/2026-08-12-162230-packet.json
- charness-artifacts/critique/2026-08-12-162230-packet.md
- charness-artifacts/critique/2026-08-12-162942-packet.json
- charness-artifacts/critique/2026-08-12-162942-packet.md
- charness-artifacts/critique/2026-08-12-163119-packet.json
- charness-artifacts/critique/2026-08-12-163119-packet.md
- charness-artifacts/critique/2026-08-12-163518-packet.json
- charness-artifacts/critique/2026-08-12-163518-packet.md
- charness-artifacts/critique/2026-08-12-163704-packet.json
- charness-artifacts/critique/2026-08-12-163704-packet.md
- charness-artifacts/critique/2026-08-12-163923-packet.json
- charness-artifacts/critique/2026-08-12-163923-packet.md
- charness-artifacts/critique/2026-08-12-163952-packet.json
- charness-artifacts/critique/2026-08-12-163952-packet.md
- charness-artifacts/critique/2026-08-12-164727-packet.json
- charness-artifacts/critique/2026-08-12-164727-packet.md
- charness-artifacts/critique/2026-08-12-164956-packet.json
- charness-artifacts/critique/2026-08-12-164956-packet.md
- charness-artifacts/critique/2026-08-12-165549-packet.json
- charness-artifacts/critique/2026-08-12-165549-packet.md
- charness-artifacts/critique/2026-08-12-165836-packet.json
- charness-artifacts/critique/2026-08-12-165836-packet.md
- charness-artifacts/critique/2026-08-12-170112-packet.json
- charness-artifacts/critique/2026-08-12-170112-packet.md
- charness-artifacts/critique/2026-08-12-170646-packet.json
- charness-artifacts/critique/2026-08-12-170646-packet.md
- charness-artifacts/critique/2026-08-12-171322-packet.json
- charness-artifacts/critique/2026-08-12-171322-packet.md
- charness-artifacts/critique/2026-08-12-171855-packet.json
- charness-artifacts/critique/2026-08-12-171855-packet.md
- charness-artifacts/critique/2026-08-12-172306-packet.json
- charness-artifacts/critique/2026-08-12-172306-packet.md
- charness-artifacts/critique/2026-08-12-173729-packet.json
- charness-artifacts/critique/2026-08-12-173729-packet.md
- charness-artifacts/critique/2026-08-12-173751-packet.json
- charness-artifacts/critique/2026-08-12-173751-packet.md
- charness-artifacts/critique/2026-08-12-173947-packet.json
- charness-artifacts/critique/2026-08-12-173947-packet.md
- charness-artifacts/critique/2026-08-12-174749-packet.json
- charness-artifacts/critique/2026-08-12-174749-packet.md
- charness-artifacts/critique/2026-08-12-175129-packet.json
- charness-artifacts/critique/2026-08-12-175129-packet.md
- charness-artifacts/critique/2026-08-12-175516-packet.json
- charness-artifacts/critique/2026-08-12-175516-packet.md
- charness-artifacts/critique/2026-08-12-175707-packet.json
- charness-artifacts/critique/2026-08-12-175707-packet.md
- charness-artifacts/critique/2026-08-12-181550-packet.json
- charness-artifacts/critique/2026-08-12-181550-packet.md
- charness-artifacts/critique/2026-08-12-181857-packet.json
- charness-artifacts/critique/2026-08-12-181857-packet.md
- charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md
- charness-artifacts/critique/2026-08-12-handoff-post-release-refresh-packet.json
- charness-artifacts/critique/2026-08-12-handoff-post-release-refresh-packet.md
- charness-artifacts/critique/2026-08-12-issue-584-sessionstart-routing-repair-critique.md
- charness-artifacts/critique/2026-08-12-issue-595-runtime-advisory-contract-critique.md
- charness-artifacts/critique/2026-08-12-issue-597-quality-fixture-gate-repair-critique.md
- charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.json
- charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.md
- charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-packet.json
- charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-packet.md
- charness-artifacts/critique/2026-08-12-open-backlog-goal-final-activation.md
- charness-artifacts/critique/2026-08-12-post-publication-issue-closeout-carriers.md
- charness-artifacts/critique/2026-08-13-issue-539-create-url-shape-resolution.md
- charness-artifacts/critique/2026-08-13-issue-542-closeout-target-disagreement-resolution.md
- charness-artifacts/critique/2026-08-13-issue-582-readme-proof-evidence-binding-resolution.md
- charness-artifacts/critique/2026-08-13-issue-584-planner-read-cost-resolution.md
- charness-artifacts/critique/2026-08-13-issue-588-policy-absent-dogfood-resolution.md
- charness-artifacts/critique/2026-08-13-issue-589-preset-reconciliation-resolution.md
- charness-artifacts/critique/2026-08-13-issue-602-create-verification-grammar-resolution.md
- charness-artifacts/critique/2026-08-13-issue-606-boundary-baseline-resolution.md
- charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md
- charness-artifacts/critique/2026-08-13-issue-608-claims-review-release-stage.md
- charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.json
- charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.md
- charness-artifacts/critique/2026-08-13-open-backlog-handoff-528-542-refresh.md
- charness-artifacts/critique/2026-08-13-release-5-1-0-critique.md
- charness-artifacts/debug/2026-08-12-issue-584-planner-read-cost-debug.md
- charness-artifacts/debug/2026-08-12-issue-584-sessionstart-routing-debug.md
- charness-artifacts/debug/2026-08-12-issue-595-runtime-advisory-contract-debug.md
- charness-artifacts/debug/2026-08-12-issue-597-quality-fixture-gate-debug.md
- charness-artifacts/debug/2026-08-13-debug-review-followup.md
- charness-artifacts/debug/2026-08-13-debug-review.md
- charness-artifacts/debug/2026-08-13-issue-539-create-url-shape.md
- charness-artifacts/debug/2026-08-13-issue-542-closeout-target-disagreement.md
- charness-artifacts/debug/2026-08-13-issue-584-planner-read-cost-implementation-debug.md
- charness-artifacts/debug/2026-08-13-issue-588-policy-absent-dogfood.md
- charness-artifacts/debug/2026-08-13-issue-589-preset-reconciliation-debug.md
- charness-artifacts/debug/2026-08-13-issue-602-create-verification-grammar.md
- charness-artifacts/debug/2026-08-13-readme-proof-evidence-binding-debug.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md
- charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md
- charness-artifacts/issue/2026-08-13-issue-527-brief.md
- charness-artifacts/issue/2026-08-13-issue-608-resolution-brief.md
- charness-artifacts/issue/2026-08-13-release-claims-review-pause-body.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
- charness-artifacts/quality/2026-08-13-dup-ratchet-backlog-triage.md
- charness-artifacts/quality/dup-ratchet-baseline.json
- charness-artifacts/quality/dup-review.json
- charness-artifacts/release/2026-08-13-v5.1.0-notes.md
- charness-artifacts/retro/2026-08-12-180732-packet.json
- charness-artifacts/retro/2026-08-12-180732-packet.md
- charness-artifacts/retro/2026-08-12-195646-packet.json
- charness-artifacts/retro/2026-08-12-195646-packet.md
- charness-artifacts/retro/2026-08-12-session-release-closeout-packet.json
- charness-artifacts/retro/2026-08-12-session-release-closeout-packet.md
- charness-artifacts/retro/2026-08-12-session-retro.md
- charness-artifacts/retro/2026-08-13-release-preflight-retro.md
- charness-artifacts/retro/2026-08-13-session-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-08-13-preset-lineage-reconciliation-contract.md
- charness-artifacts/spec/planner-required-read-cost-contract.md
- docs/conventions/validator-timing-layers.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- docs/readme-proof.md
- docs/testability-dsl-initiative.md
- plugins/charness/scripts/boundary-bypass-baseline.json
- plugins/charness/scripts/boundary_bypass_ratchet_lib.py
- plugins/charness/scripts/check_boundary_bypass_ratchet.py
- plugins/charness/scripts/check_quality_tool_fixtures.py
- plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt
- plugins/charness/scripts/evidence_boundary_crosswalk.py
- plugins/charness/scripts/public_skill_dogfood_lib.py
- plugins/charness/scripts/readme_proof_ledger_lib.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/scripts/session_start_routing.py
- plugins/charness/scripts/suggest_public_skill_dogfood.py
- plugins/charness/scripts/validate_presets.py
- plugins/charness/shared/references/run-plan-envelope.md
- plugins/charness/shared/scripts/run_plan_envelope.py
- plugins/charness/skills/handoff/scripts/plan_handoff_run.py
- plugins/charness/skills/issue/SKILL.md
- plugins/charness/skills/issue/references/issue-backend.md
- plugins/charness/skills/issue/scripts/issue_create.py
- plugins/charness/skills/issue/scripts/issue_create_verify.py
- plugins/charness/skills/quality/references/bootstrap-posture.md
- plugins/charness/skills/quality/references/inventory-consumer-fields.json
- plugins/charness/skills/quality/scripts/check_runtime_budget.py
- plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py
- plugins/charness/skills/quality/scripts/plan_quality_run.py
- plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py
- plugins/charness/skills/quality/scripts/quality_preset_reconciliation.py
- plugins/charness/skills/quality/scripts/quality_run_plan_render.py
- plugins/charness/skills/quality/scripts/runtime_budget_lib.py
- plugins/charness/skills/quality/scripts/runtime_visibility_lib.py
- plugins/charness/skills/quality/scripts/standing_test_economics_lib.py
- plugins/charness/skills/quality/scripts/suggest_public_skill_dogfood.py
- plugins/charness/skills/quality/scripts/surface_marker_lib.py
- plugins/charness/skills/release/scripts/publish_release_artifact.py
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_claims_review.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_execute.py
- plugins/charness/skills/release/scripts/publish_release_resume.py
- plugins/charness/skills/release/scripts/publish_release_resume_closeout.py
- plugins/charness/skills/release/scripts/publish_release_resume_publish.py
- scripts/boundary-bypass-baseline.json
- scripts/boundary_bypass_ratchet_lib.py
- scripts/check_boundary_bypass_ratchet.py
- scripts/check_quality_tool_fixtures.py
- scripts/check_skill_ownership_overlap.allowlist.txt
- scripts/evidence_boundary_crosswalk.py
- scripts/public_skill_dogfood_lib.py
- scripts/readme_proof_ledger_lib.py
- scripts/run-quality.sh
- scripts/session_start_routing.py
- scripts/suggest_public_skill_dogfood.py
- scripts/validate_presets.py
- skills/public/handoff/scripts/plan_handoff_run.py
- skills/public/issue/SKILL.md
- skills/public/issue/references/issue-backend.md
- skills/public/issue/scripts/issue_create.py
- skills/public/issue/scripts/issue_create_verify.py
- skills/public/quality/references/bootstrap-posture.md
- skills/public/quality/references/inventory-consumer-fields.json
- skills/public/quality/scripts/check_runtime_budget.py
- skills/public/quality/scripts/inventory_standing_test_economics.py
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/quality_declaration_lifecycle.py
- skills/public/quality/scripts/quality_preset_reconciliation.py
- skills/public/quality/scripts/quality_run_plan_render.py
- skills/public/quality/scripts/runtime_budget_lib.py
- skills/public/quality/scripts/runtime_visibility_lib.py
- skills/public/quality/scripts/standing_test_economics_lib.py
- skills/public/quality/scripts/suggest_public_skill_dogfood.py
- skills/public/quality/scripts/surface_marker_lib.py
- skills/public/release/scripts/publish_release_artifact.py
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_claims_review.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_execute.py
- skills/public/release/scripts/publish_release_resume.py
- skills/public/release/scripts/publish_release_resume_closeout.py
- skills/public/release/scripts/publish_release_resume_publish.py
- skills/shared/references/run-plan-envelope.md
- skills/shared/scripts/run_plan_envelope.py
- specs/readme-proof.spec.md
- tests/quality_gates/release_publish_fixtures.py
- tests/quality_gates/support.py
- tests/quality_gates/test_closeout_authorization_ingress.py
- tests/quality_gates/test_issue_closeout_discipline.py
- tests/quality_gates/test_issue_create.py
- tests/quality_gates/test_issue_create_failure_branches.py
- tests/quality_gates/test_profile_and_preset_validation.py
- tests/quality_gates/test_public_skill_dogfood.py
- tests/quality_gates/test_quality_declaration_path_resolution.py
- tests/quality_gates/test_quality_run_gate_packets.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_quality_run_read_measurement.py
- tests/quality_gates/test_quality_tool_fixtures.py
- tests/quality_gates/test_release_claims_review.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_release_publish_resilience.py
- tests/quality_gates/test_release_resume_state_validation.py
- tests/quality_gates/test_runtime_budget_gate.py
- tests/quality_gates/test_subprocess_settlement_inventory.py
- tests/test_boundary_bypass_ratchet.py
- tests/test_evidence_boundary_crosswalk.py
- tests/test_handoff_plan.py
- tests/test_public_skill_dogfood.py
- tests/test_readme_proof_ledger.py
- tests/test_run_plan_envelope.py
- tests/test_session_start_routing.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/boundary-bypass-baseline.json, scripts/boundary_bypass_ratchet_lib.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_quality_tool_fixtures.py, scripts/check_skill_ownership_overlap.allowlist.txt, scripts/evidence_boundary_crosswalk.py, scripts/public_skill_dogfood_lib.py, scripts/readme_proof_ledger_lib.py, scripts/run-quality.sh, scripts/session_start_routing.py, scripts/suggest_public_skill_dogfood.py, scripts/validate_presets.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_create.py, skills/public/issue/scripts/issue_create_verify.py, skills/public/quality/references/bootstrap-posture.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/check_runtime_budget.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/quality_run_plan_render.py, skills/public/quality/scripts/runtime_budget_lib.py, skills/public/quality/scripts/runtime_visibility_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/suggest_public_skill_dogfood.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_claims_review.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/shared/references/run-plan-envelope.md, skills/shared/scripts/run_plan_envelope.py
  derived matches: plugins/charness/scripts/boundary-bypass-baseline.json, plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check_boundary_bypass_ratchet.py, plugins/charness/scripts/check_quality_tool_fixtures.py, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/evidence_boundary_crosswalk.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/readme_proof_ledger_lib.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/suggest_public_skill_dogfood.py, plugins/charness/scripts/validate_presets.py, plugins/charness/shared/references/run-plan-envelope.md, plugins/charness/shared/scripts/run_plan_envelope.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_create.py, plugins/charness/skills/issue/scripts/issue_create_verify.py, plugins/charness/skills/quality/references/bootstrap-posture.md, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/scripts/check_runtime_budget.py, plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/quality/scripts/quality_preset_reconciliation.py, plugins/charness/skills/quality/scripts/quality_run_plan_render.py, plugins/charness/skills/quality/scripts/runtime_budget_lib.py, plugins/charness/skills/quality/scripts/runtime_visibility_lib.py, plugins/charness/skills/quality/scripts/standing_test_economics_lib.py, plugins/charness/skills/quality/scripts/suggest_public_skill_dogfood.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_claims_review.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_execute.py, plugins/charness/skills/release/scripts/publish_release_resume.py, plugins/charness/skills/release/scripts/publish_release_resume_closeout.py, plugins/charness/skills/release/scripts/publish_release_resume_publish.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-12-140743-packet.md, charness-artifacts/critique/2026-08-12-141010-packet.md, charness-artifacts/critique/2026-08-12-142919-packet.md, charness-artifacts/critique/2026-08-12-143920-packet.md, charness-artifacts/critique/2026-08-12-144548-packet.md, charness-artifacts/critique/2026-08-12-145810-packet.md, charness-artifacts/critique/2026-08-12-151434-packet.md, charness-artifacts/critique/2026-08-12-152909-packet.md, charness-artifacts/critique/2026-08-12-154616-packet.md, charness-artifacts/critique/2026-08-12-154946-packet.md, charness-artifacts/critique/2026-08-12-155204-packet.md, charness-artifacts/critique/2026-08-12-160206-packet.md, charness-artifacts/critique/2026-08-12-160548-packet.md, charness-artifacts/critique/2026-08-12-160812-packet.md, charness-artifacts/critique/2026-08-12-160936-packet.md, charness-artifacts/critique/2026-08-12-161938-packet.md, charness-artifacts/critique/2026-08-12-162230-packet.md, charness-artifacts/critique/2026-08-12-162942-packet.md, charness-artifacts/critique/2026-08-12-163119-packet.md, charness-artifacts/critique/2026-08-12-163518-packet.md, charness-artifacts/critique/2026-08-12-163704-packet.md, charness-artifacts/critique/2026-08-12-163923-packet.md, charness-artifacts/critique/2026-08-12-163952-packet.md, charness-artifacts/critique/2026-08-12-164727-packet.md, charness-artifacts/critique/2026-08-12-164956-packet.md, charness-artifacts/critique/2026-08-12-165549-packet.md, charness-artifacts/critique/2026-08-12-165836-packet.md, charness-artifacts/critique/2026-08-12-170112-packet.md, charness-artifacts/critique/2026-08-12-170646-packet.md, charness-artifacts/critique/2026-08-12-171322-packet.md, charness-artifacts/critique/2026-08-12-171855-packet.md, charness-artifacts/critique/2026-08-12-172306-packet.md, charness-artifacts/critique/2026-08-12-173729-packet.md, charness-artifacts/critique/2026-08-12-173751-packet.md, charness-artifacts/critique/2026-08-12-173947-packet.md, charness-artifacts/critique/2026-08-12-174749-packet.md, charness-artifacts/critique/2026-08-12-175129-packet.md, charness-artifacts/critique/2026-08-12-175516-packet.md, charness-artifacts/critique/2026-08-12-175707-packet.md, charness-artifacts/critique/2026-08-12-181550-packet.md, charness-artifacts/critique/2026-08-12-181857-packet.md, charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md, charness-artifacts/critique/2026-08-12-handoff-post-release-refresh-packet.md, charness-artifacts/critique/2026-08-12-issue-584-sessionstart-routing-repair-critique.md, charness-artifacts/critique/2026-08-12-issue-595-runtime-advisory-contract-critique.md, charness-artifacts/critique/2026-08-12-issue-597-quality-fixture-gate-repair-critique.md, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.md, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-packet.md, charness-artifacts/critique/2026-08-12-open-backlog-goal-final-activation.md, charness-artifacts/critique/2026-08-12-post-publication-issue-closeout-carriers.md, charness-artifacts/critique/2026-08-13-issue-539-create-url-shape-resolution.md, charness-artifacts/critique/2026-08-13-issue-542-closeout-target-disagreement-resolution.md, charness-artifacts/critique/2026-08-13-issue-582-readme-proof-evidence-binding-resolution.md, charness-artifacts/critique/2026-08-13-issue-584-planner-read-cost-resolution.md, charness-artifacts/critique/2026-08-13-issue-588-policy-absent-dogfood-resolution.md, charness-artifacts/critique/2026-08-13-issue-589-preset-reconciliation-resolution.md, charness-artifacts/critique/2026-08-13-issue-602-create-verification-grammar-resolution.md, charness-artifacts/critique/2026-08-13-issue-606-boundary-baseline-resolution.md, charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md, charness-artifacts/critique/2026-08-13-issue-608-claims-review-release-stage.md, charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.md, charness-artifacts/critique/2026-08-13-open-backlog-handoff-528-542-refresh.md, charness-artifacts/critique/2026-08-13-release-5-1-0-critique.md, charness-artifacts/debug/2026-08-12-issue-584-planner-read-cost-debug.md, charness-artifacts/debug/2026-08-12-issue-584-sessionstart-routing-debug.md, charness-artifacts/debug/2026-08-12-issue-595-runtime-advisory-contract-debug.md, charness-artifacts/debug/2026-08-12-issue-597-quality-fixture-gate-debug.md, charness-artifacts/debug/2026-08-13-debug-review-followup.md, charness-artifacts/debug/2026-08-13-debug-review.md, charness-artifacts/debug/2026-08-13-issue-539-create-url-shape.md, charness-artifacts/debug/2026-08-13-issue-542-closeout-target-disagreement.md, charness-artifacts/debug/2026-08-13-issue-584-planner-read-cost-implementation-debug.md, charness-artifacts/debug/2026-08-13-issue-588-policy-absent-dogfood.md, charness-artifacts/debug/2026-08-13-issue-589-preset-reconciliation-debug.md, charness-artifacts/debug/2026-08-13-issue-602-create-verification-grammar.md, charness-artifacts/debug/2026-08-13-readme-proof-evidence-binding-debug.md, charness-artifacts/debug/latest.md, charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md, charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md, charness-artifacts/issue/2026-08-13-issue-527-brief.md, charness-artifacts/issue/2026-08-13-issue-608-resolution-brief.md, charness-artifacts/issue/2026-08-13-release-claims-review-pause-body.md, charness-artifacts/quality/2026-08-13-dup-ratchet-backlog-triage.md, charness-artifacts/release/2026-08-13-v5.1.0-notes.md, charness-artifacts/retro/2026-08-12-180732-packet.md, charness-artifacts/retro/2026-08-12-195646-packet.md, charness-artifacts/retro/2026-08-12-session-release-closeout-packet.md, charness-artifacts/retro/2026-08-12-session-retro.md, charness-artifacts/retro/2026-08-13-release-preflight-retro.md, charness-artifacts/retro/2026-08-13-session-retro.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-08-13-preset-lineage-reconciliation-contract.md, charness-artifacts/spec/planner-required-read-cost-contract.md, docs/conventions/validator-timing-layers.md, docs/handoff.md, docs/readme-proof.md, docs/testability-dsl-initiative.md, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/quality/references/bootstrap-posture.md, skills/shared/references/run-plan-envelope.md
  derived matches: plugins/charness/shared/references/run-plan-envelope.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/quality/references/bootstrap-posture.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- handoff-machine-readers: docs/handoff.md is a rotating human document that is ALSO a machine-read source: the publish-state ledger declares it as a source locator, and the retro-memory gate requires its recent-lessons reference.
  source matches: docs/handoff.md
  verify: python3 scripts/publish_state_ledger.py --repo-root ., python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-ratchet-baseline.json, charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/quality/references/bootstrap-posture.md, skills/public/quality/references/inventory-consumer-fields.json, skills/shared/references/run-plan-envelope.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/handoff/scripts/plan_handoff_run.py, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_create.py, skills/public/issue/scripts/issue_create_verify.py, skills/public/quality/references/bootstrap-posture.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/check_runtime_budget.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/quality_run_plan_render.py, skills/public/quality/scripts/runtime_budget_lib.py, skills/public/quality/scripts/runtime_visibility_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/suggest_public_skill_dogfood.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_claims_review.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/shared/references/run-plan-envelope.md, skills/shared/scripts/run_plan_envelope.py
  derived matches: plugins/charness/shared/references/run-plan-envelope.md, plugins/charness/shared/scripts/run_plan_envelope.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/issue-backend.md, plugins/charness/skills/issue/scripts/issue_create.py, plugins/charness/skills/issue/scripts/issue_create_verify.py, plugins/charness/skills/quality/references/bootstrap-posture.md, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/scripts/check_runtime_budget.py, plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py, plugins/charness/skills/quality/scripts/quality_preset_reconciliation.py, plugins/charness/skills/quality/scripts/quality_run_plan_render.py, plugins/charness/skills/quality/scripts/runtime_budget_lib.py, plugins/charness/skills/quality/scripts/runtime_visibility_lib.py, plugins/charness/skills/quality/scripts/standing_test_economics_lib.py, plugins/charness/skills/quality/scripts/suggest_public_skill_dogfood.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_claims_review.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_execute.py, plugins/charness/skills/release/scripts/publish_release_resume.py, plugins/charness/skills/release/scripts/publish_release_resume_closeout.py, plugins/charness/skills/release/scripts/publish_release_resume_publish.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/handoff/scripts/plan_handoff_run.py, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_create.py, skills/public/issue/scripts/issue_create_verify.py, skills/public/quality/references/bootstrap-posture.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/check_runtime_budget.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/quality_run_plan_render.py, skills/public/quality/scripts/runtime_budget_lib.py, skills/public/quality/scripts/runtime_visibility_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/suggest_public_skill_dogfood.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_claims_review.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/shared/references/run-plan-envelope.md, skills/shared/scripts/run_plan_envelope.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, scripts/public_skill_dogfood_lib.py, scripts/suggest_public_skill_dogfood.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/issue/SKILL.md, skills/public/issue/references/issue-backend.md, skills/public/issue/scripts/issue_create.py, skills/public/issue/scripts/issue_create_verify.py, skills/public/quality/references/bootstrap-posture.md, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/check_runtime_budget.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/quality_run_plan_render.py, skills/public/quality/scripts/runtime_budget_lib.py, skills/public/quality/scripts/runtime_visibility_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/suggest_public_skill_dogfood.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_claims_review.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/shared/references/run-plan-envelope.md, skills/shared/scripts/run_plan_envelope.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-12-140743-packet.json, charness-artifacts/critique/2026-08-12-140743-packet.md, charness-artifacts/critique/2026-08-12-141010-packet.json, charness-artifacts/critique/2026-08-12-141010-packet.md, charness-artifacts/critique/2026-08-12-142919-packet.json, charness-artifacts/critique/2026-08-12-142919-packet.md, charness-artifacts/critique/2026-08-12-143920-packet.json, charness-artifacts/critique/2026-08-12-143920-packet.md, charness-artifacts/critique/2026-08-12-144548-packet.json, charness-artifacts/critique/2026-08-12-144548-packet.md, charness-artifacts/critique/2026-08-12-145810-packet.json, charness-artifacts/critique/2026-08-12-145810-packet.md, charness-artifacts/critique/2026-08-12-151434-packet.json, charness-artifacts/critique/2026-08-12-151434-packet.md, charness-artifacts/critique/2026-08-12-152909-packet.json, charness-artifacts/critique/2026-08-12-152909-packet.md, charness-artifacts/critique/2026-08-12-154616-packet.json, charness-artifacts/critique/2026-08-12-154616-packet.md, charness-artifacts/critique/2026-08-12-154946-packet.json, charness-artifacts/critique/2026-08-12-154946-packet.md, charness-artifacts/critique/2026-08-12-155204-packet.json, charness-artifacts/critique/2026-08-12-155204-packet.md, charness-artifacts/critique/2026-08-12-160206-packet.json, charness-artifacts/critique/2026-08-12-160206-packet.md, charness-artifacts/critique/2026-08-12-160548-packet.json, charness-artifacts/critique/2026-08-12-160548-packet.md, charness-artifacts/critique/2026-08-12-160812-packet.json, charness-artifacts/critique/2026-08-12-160812-packet.md, charness-artifacts/critique/2026-08-12-160936-packet.json, charness-artifacts/critique/2026-08-12-160936-packet.md, charness-artifacts/critique/2026-08-12-161938-packet.json, charness-artifacts/critique/2026-08-12-161938-packet.md, charness-artifacts/critique/2026-08-12-162230-packet.json, charness-artifacts/critique/2026-08-12-162230-packet.md, charness-artifacts/critique/2026-08-12-162942-packet.json, charness-artifacts/critique/2026-08-12-162942-packet.md, charness-artifacts/critique/2026-08-12-163119-packet.json, charness-artifacts/critique/2026-08-12-163119-packet.md, charness-artifacts/critique/2026-08-12-163518-packet.json, charness-artifacts/critique/2026-08-12-163518-packet.md, charness-artifacts/critique/2026-08-12-163704-packet.json, charness-artifacts/critique/2026-08-12-163704-packet.md, charness-artifacts/critique/2026-08-12-163923-packet.json, charness-artifacts/critique/2026-08-12-163923-packet.md, charness-artifacts/critique/2026-08-12-163952-packet.json, charness-artifacts/critique/2026-08-12-163952-packet.md, charness-artifacts/critique/2026-08-12-164727-packet.json, charness-artifacts/critique/2026-08-12-164727-packet.md, charness-artifacts/critique/2026-08-12-164956-packet.json, charness-artifacts/critique/2026-08-12-164956-packet.md, charness-artifacts/critique/2026-08-12-165549-packet.json, charness-artifacts/critique/2026-08-12-165549-packet.md, charness-artifacts/critique/2026-08-12-165836-packet.json, charness-artifacts/critique/2026-08-12-165836-packet.md, charness-artifacts/critique/2026-08-12-170112-packet.json, charness-artifacts/critique/2026-08-12-170112-packet.md, charness-artifacts/critique/2026-08-12-170646-packet.json, charness-artifacts/critique/2026-08-12-170646-packet.md, charness-artifacts/critique/2026-08-12-171322-packet.json, charness-artifacts/critique/2026-08-12-171322-packet.md, charness-artifacts/critique/2026-08-12-171855-packet.json, charness-artifacts/critique/2026-08-12-171855-packet.md, charness-artifacts/critique/2026-08-12-172306-packet.json, charness-artifacts/critique/2026-08-12-172306-packet.md, charness-artifacts/critique/2026-08-12-173729-packet.json, charness-artifacts/critique/2026-08-12-173729-packet.md, charness-artifacts/critique/2026-08-12-173751-packet.json, charness-artifacts/critique/2026-08-12-173751-packet.md, charness-artifacts/critique/2026-08-12-173947-packet.json, charness-artifacts/critique/2026-08-12-173947-packet.md, charness-artifacts/critique/2026-08-12-174749-packet.json, charness-artifacts/critique/2026-08-12-174749-packet.md, charness-artifacts/critique/2026-08-12-175129-packet.json, charness-artifacts/critique/2026-08-12-175129-packet.md, charness-artifacts/critique/2026-08-12-175516-packet.json, charness-artifacts/critique/2026-08-12-175516-packet.md, charness-artifacts/critique/2026-08-12-175707-packet.json, charness-artifacts/critique/2026-08-12-175707-packet.md, charness-artifacts/critique/2026-08-12-181550-packet.json, charness-artifacts/critique/2026-08-12-181550-packet.md, charness-artifacts/critique/2026-08-12-181857-packet.json, charness-artifacts/critique/2026-08-12-181857-packet.md, charness-artifacts/critique/2026-08-12-goal-progress-frame-and-ledger-critique.md, charness-artifacts/critique/2026-08-12-handoff-post-release-refresh-packet.json, charness-artifacts/critique/2026-08-12-handoff-post-release-refresh-packet.md, charness-artifacts/critique/2026-08-12-issue-584-sessionstart-routing-repair-critique.md, charness-artifacts/critique/2026-08-12-issue-595-runtime-advisory-contract-critique.md, charness-artifacts/critique/2026-08-12-issue-597-quality-fixture-gate-repair-critique.md, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.json, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-final-packet.md, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-packet.json, charness-artifacts/critique/2026-08-12-issue-post-publication-closeout-packet.md, charness-artifacts/critique/2026-08-12-open-backlog-goal-final-activation.md, charness-artifacts/critique/2026-08-12-post-publication-issue-closeout-carriers.md, charness-artifacts/critique/2026-08-13-issue-539-create-url-shape-resolution.md, charness-artifacts/critique/2026-08-13-issue-542-closeout-target-disagreement-resolution.md, charness-artifacts/critique/2026-08-13-issue-582-readme-proof-evidence-binding-resolution.md, charness-artifacts/critique/2026-08-13-issue-584-planner-read-cost-resolution.md, charness-artifacts/critique/2026-08-13-issue-588-policy-absent-dogfood-resolution.md, charness-artifacts/critique/2026-08-13-issue-589-preset-reconciliation-resolution.md, charness-artifacts/critique/2026-08-13-issue-602-create-verification-grammar-resolution.md, charness-artifacts/critique/2026-08-13-issue-606-boundary-baseline-resolution.md, charness-artifacts/critique/2026-08-13-issue-607-subprocess-settlement-inventory-resolution.md, charness-artifacts/critique/2026-08-13-issue-608-claims-review-release-stage.md, charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.json, charness-artifacts/critique/2026-08-13-issue-608-resolution-final-packet.md, charness-artifacts/critique/2026-08-13-open-backlog-handoff-528-542-refresh.md, charness-artifacts/critique/2026-08-13-release-5-1-0-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-12-issue-584-planner-read-cost-debug.md, charness-artifacts/debug/2026-08-12-issue-584-sessionstart-routing-debug.md, charness-artifacts/debug/2026-08-12-issue-595-runtime-advisory-contract-debug.md, charness-artifacts/debug/2026-08-12-issue-597-quality-fixture-gate-debug.md, charness-artifacts/debug/2026-08-13-debug-review-followup.md, charness-artifacts/debug/2026-08-13-debug-review.md, charness-artifacts/debug/2026-08-13-issue-539-create-url-shape.md, charness-artifacts/debug/2026-08-13-issue-542-closeout-target-disagreement.md, charness-artifacts/debug/2026-08-13-issue-584-planner-read-cost-implementation-debug.md, charness-artifacts/debug/2026-08-13-issue-588-policy-absent-dogfood.md, charness-artifacts/debug/2026-08-13-issue-589-preset-reconciliation-debug.md, charness-artifacts/debug/2026-08-13-issue-602-create-verification-grammar.md, charness-artifacts/debug/2026-08-13-readme-proof-evidence-binding-debug.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-12-180732-packet.json, charness-artifacts/retro/2026-08-12-180732-packet.md, charness-artifacts/retro/2026-08-12-195646-packet.json, charness-artifacts/retro/2026-08-12-195646-packet.md, charness-artifacts/retro/2026-08-12-session-release-closeout-packet.json, charness-artifacts/retro/2026-08-12-session-release-closeout-packet.md, charness-artifacts/retro/2026-08-12-session-retro.md, charness-artifacts/retro/2026-08-13-release-preflight-retro.md, charness-artifacts/retro/2026-08-13-session-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- executable-specs: Repo-owned specdown executable acceptance specs and their config.
  source matches: specs/readme-proof.spec.md
  verify: specdown_report_dir=$(mktemp -d); specdown_config=$(python3 scripts/specdown_ephemeral_config.py --repo-root . --out-dir "$specdown_report_dir") || exit 1; trap 'rm -rf "$specdown_report_dir" "$specdown_config"' EXIT; specdown run -config "$specdown_config" -jobs 4 -out "$specdown_report_dir"
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/boundary-bypass-baseline.json, plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check_boundary_bypass_ratchet.py, plugins/charness/scripts/check_quality_tool_fixtures.py, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/evidence_boundary_crosswalk.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/readme_proof_ledger_lib.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/suggest_public_skill_dogfood.py, plugins/charness/scripts/validate_presets.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/boundary_bypass_ratchet_lib.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_quality_tool_fixtures.py, scripts/evidence_boundary_crosswalk.py, scripts/public_skill_dogfood_lib.py, scripts/readme_proof_ledger_lib.py, scripts/session_start_routing.py, scripts/suggest_public_skill_dogfood.py, scripts/validate_presets.py, tests/quality_gates/release_publish_fixtures.py, tests/quality_gates/support.py, tests/quality_gates/test_closeout_authorization_ingress.py, tests/quality_gates/test_issue_closeout_discipline.py, tests/quality_gates/test_issue_create.py, tests/quality_gates/test_issue_create_failure_branches.py, tests/quality_gates/test_profile_and_preset_validation.py, tests/quality_gates/test_public_skill_dogfood.py, tests/quality_gates/test_quality_declaration_path_resolution.py, tests/quality_gates/test_quality_run_gate_packets.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_quality_run_read_measurement.py, tests/quality_gates/test_quality_tool_fixtures.py, tests/quality_gates/test_release_claims_review.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_release_publish_resilience.py, tests/quality_gates/test_release_resume_state_validation.py, tests/quality_gates/test_runtime_budget_gate.py, tests/quality_gates/test_subprocess_settlement_inventory.py, tests/test_boundary_bypass_ratchet.py, tests/test_evidence_boundary_crosswalk.py, tests/test_handoff_plan.py, tests/test_public_skill_dogfood.py, tests/test_readme_proof_ledger.py, tests/test_run_plan_envelope.py, tests/test_session_start_routing.py
  derived matches: plugins/charness/scripts/boundary_bypass_ratchet_lib.py, plugins/charness/scripts/check_boundary_bypass_ratchet.py, plugins/charness/scripts/check_quality_tool_fixtures.py, plugins/charness/scripts/evidence_boundary_crosswalk.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/readme_proof_ledger_lib.py, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/suggest_public_skill_dogfood.py, plugins/charness/scripts/validate_presets.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: skills/public/quality/scripts/inventory_standing_test_economics.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/boundary_bypass_ratchet_lib.py, scripts/check_boundary_bypass_ratchet.py, scripts/check_quality_tool_fixtures.py, scripts/evidence_boundary_crosswalk.py, scripts/public_skill_dogfood_lib.py, scripts/readme_proof_ledger_lib.py, scripts/session_start_routing.py, scripts/suggest_public_skill_dogfood.py, scripts/validate_presets.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/issue/scripts/issue_create.py, skills/public/issue/scripts/issue_create_verify.py, skills/public/quality/scripts/check_runtime_budget.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/quality_declaration_lifecycle.py, skills/public/quality/scripts/quality_preset_reconciliation.py, skills/public/quality/scripts/quality_run_plan_render.py, skills/public/quality/scripts/runtime_budget_lib.py, skills/public/quality/scripts/runtime_visibility_lib.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/suggest_public_skill_dogfood.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_claims_review.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```
