# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-11T12:22:03Z
- **Prepared for**: v0.66.2 full origin-main carrier release decision
- **Changed ref**: `origin/main..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
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
Changed paths for ref `origin/main..HEAD`:
- AGENTS.md
- charness-artifacts/critique/2026-07-11-080522-packet.json
- charness-artifacts/critique/2026-07-11-080522-packet.md
- charness-artifacts/critique/2026-07-11-082541-packet.json
- charness-artifacts/critique/2026-07-11-082541-packet.md
- charness-artifacts/critique/2026-07-11-083446-packet.json
- charness-artifacts/critique/2026-07-11-083446-packet.md
- charness-artifacts/critique/2026-07-11-085201-packet.json
- charness-artifacts/critique/2026-07-11-085201-packet.md
- charness-artifacts/critique/2026-07-11-091356-packet.json
- charness-artifacts/critique/2026-07-11-091356-packet.md
- charness-artifacts/critique/2026-07-11-093306-packet.json
- charness-artifacts/critique/2026-07-11-093306-packet.md
- charness-artifacts/critique/2026-07-11-094504-packet.json
- charness-artifacts/critique/2026-07-11-094504-packet.md
- charness-artifacts/critique/2026-07-11-101842-packet.json
- charness-artifacts/critique/2026-07-11-101842-packet.md
- charness-artifacts/critique/2026-07-11-103004-packet.json
- charness-artifacts/critique/2026-07-11-103004-packet.md
- charness-artifacts/critique/2026-07-11-110741-packet.json
- charness-artifacts/critique/2026-07-11-110741-packet.md
- charness-artifacts/critique/2026-07-11-closeout-parser-extraction-packet.json
- charness-artifacts/critique/2026-07-11-closeout-parser-extraction-packet.md
- charness-artifacts/critique/2026-07-11-closeout-parser-extraction.md
- charness-artifacts/critique/2026-07-11-coverage-anchor-postreview-packet.json
- charness-artifacts/critique/2026-07-11-coverage-anchor-postreview-packet.md
- charness-artifacts/critique/2026-07-11-coverage-anchor-worktree-packet.json
- charness-artifacts/critique/2026-07-11-coverage-anchor-worktree-packet.md
- charness-artifacts/critique/2026-07-11-coverage-anchor.md
- charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification-packet.json
- charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification-packet.md
- charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification.md
- charness-artifacts/critique/2026-07-11-final-quality-argparse-help-critique.md
- charness-artifacts/critique/2026-07-11-five-package-argparse-help-critique.md
- charness-artifacts/critique/2026-07-11-host-reference-north-star-critique.md
- charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.json
- charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.md
- charness-artifacts/critique/2026-07-11-quality-scaffold-h1.md
- charness-artifacts/critique/2026-07-11-release-argparse-help-critique.md
- charness-artifacts/critique/2026-07-11-retro-argparse-help-critique.md
- charness-artifacts/critique/2026-07-11-superseded-release-regex-packet.json
- charness-artifacts/critique/2026-07-11-superseded-release-regex-packet.md
- charness-artifacts/critique/2026-07-11-superseded-release-regex.md
- charness-artifacts/critique/2026-07-11-truthful-standing-delegation.md
- charness-artifacts/critique/2026-07-11-web-fetch-argparse-help-critique.md
- charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md
- charness-artifacts/quality/2026-07-11-final-quality-argparse-help.md
- charness-artifacts/quality/2026-07-11-five-package-argparse-help.md
- charness-artifacts/quality/2026-07-11-host-reference-north-star.md
- charness-artifacts/quality/2026-07-11-release-argparse-help.md
- charness-artifacts/quality/2026-07-11-retro-argparse-help.md
- charness-artifacts/quality/2026-07-11-truthful-standing-delegation.md
- charness-artifacts/quality/2026-07-11-web-fetch-argparse-help.md
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-07-11-105806-packet.json
- charness-artifacts/retro/2026-07-11-105806-packet.md
- charness-artifacts/retro/2026-07-11-truthful-standing-delegation-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- docs/operator-progressive-path.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/mutation_coverage_producer.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/setup_agent_docs_fresh_eye_lib.py
- plugins/charness/scripts/slice_closeout_parser.py
- plugins/charness/scripts/surfaces_lib.py
- plugins/charness/skills/achieve/references/coordination.md
- plugins/charness/skills/achieve/references/goal-artifact.md
- plugins/charness/skills/achieve/scripts/audit_disposition_corpus.py
- plugins/charness/skills/achieve/scripts/describe_goal_closeout_shape.py
- plugins/charness/skills/achieve/scripts/goal_artifact_early_close_report.py
- plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py
- plugins/charness/skills/critique/references/adapter-contract.md
- plugins/charness/skills/gather/scripts/gather_plan.py
- plugins/charness/skills/handoff/scripts/plan_handoff_run.py
- plugins/charness/skills/impl/scripts/check_boundary_escalation.py
- plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py
- plugins/charness/skills/issue/scripts/issue_validate_closeout_draft.py
- plugins/charness/skills/quality/references/skill-ergonomics.md
- plugins/charness/skills/quality/scripts/check_changed_line_coverage.py
- plugins/charness/skills/quality/scripts/check_dup_ratchet.py
- plugins/charness/skills/quality/scripts/check_standing_doc_provenance.py
- plugins/charness/skills/quality/scripts/draft_dup_ratchet_triage.py
- plugins/charness/skills/quality/scripts/inventory_doc_duplicates.py
- plugins/charness/skills/quality/scripts/inventory_nose_clones.py
- plugins/charness/skills/quality/scripts/inventory_release_only_sentinels.py
- plugins/charness/skills/quality/scripts/migrate_dup_fingerprints.py
- plugins/charness/skills/quality/scripts/plan_quality_run.py
- plugins/charness/skills/quality/scripts/run_dead_code_advisory.py
- plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py
- plugins/charness/skills/quality/scripts/seed_dup_review.py
- plugins/charness/skills/quality/scripts/skill_text_quality_lib.py
- plugins/charness/skills/quality/scripts/surface_marker_lib.py
- plugins/charness/skills/release/scripts/plan_release_run.py
- plugins/charness/skills/retro/SKILL.md
- plugins/charness/skills/retro/references/phase-aware-efficiency.md
- plugins/charness/skills/retro/scripts/mine_closeout_telemetry.py
- plugins/charness/skills/retro/scripts/plan_retro_run.py
- plugins/charness/skills/retro/scripts/prepare_packet.py
- plugins/charness/skills/setup/references/agent-docs-policy.md
- plugins/charness/support/web-fetch/scripts/acquire_public_url.py
- plugins/charness/support/web-fetch/scripts/classify_fetch_response.py
- plugins/charness/support/web-fetch/scripts/route_public_fetch.py
- scripts/mutation_coverage_producer.py
- scripts/run_slice_closeout.py
- scripts/setup_agent_docs_fresh_eye_lib.py
- scripts/slice_closeout_parser.py
- scripts/surfaces_lib.py
- skills/public/achieve/references/coordination.md
- skills/public/achieve/references/goal-artifact.md
- skills/public/achieve/scripts/audit_disposition_corpus.py
- skills/public/achieve/scripts/describe_goal_closeout_shape.py
- skills/public/achieve/scripts/goal_artifact_early_close_report.py
- skills/public/achieve/scripts/normalize_goal_closeout.py
- skills/public/critique/references/adapter-contract.md
- skills/public/gather/scripts/gather_plan.py
- skills/public/handoff/scripts/plan_handoff_run.py
- skills/public/impl/scripts/check_boundary_escalation.py
- skills/public/issue/scripts/describe_closeout_draft_shape.py
- skills/public/issue/scripts/issue_validate_closeout_draft.py
- skills/public/quality/references/skill-ergonomics.md
- skills/public/quality/scripts/check_changed_line_coverage.py
- skills/public/quality/scripts/check_dup_ratchet.py
- skills/public/quality/scripts/check_standing_doc_provenance.py
- skills/public/quality/scripts/draft_dup_ratchet_triage.py
- skills/public/quality/scripts/inventory_doc_duplicates.py
- skills/public/quality/scripts/inventory_nose_clones.py
- skills/public/quality/scripts/inventory_release_only_sentinels.py
- skills/public/quality/scripts/migrate_dup_fingerprints.py
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/run_dead_code_advisory.py
- skills/public/quality/scripts/scaffold_quality_artifact.py
- skills/public/quality/scripts/seed_dup_review.py
- skills/public/quality/scripts/skill_text_quality_lib.py
- skills/public/quality/scripts/surface_marker_lib.py
- skills/public/release/scripts/plan_release_run.py
- skills/public/retro/SKILL.md
- skills/public/retro/references/phase-aware-efficiency.md
- skills/public/retro/scripts/mine_closeout_telemetry.py
- skills/public/retro/scripts/plan_retro_run.py
- skills/public/retro/scripts/prepare_packet.py
- skills/public/setup/references/agent-docs-policy.md
- skills/support/web-fetch/scripts/acquire_public_url.py
- skills/support/web-fetch/scripts/classify_fetch_response.py
- skills/support/web-fetch/scripts/route_public_fetch.py
- tests/quality_gates/test_changed_line_coverage_gate.py
- tests/quality_gates/test_check_artifact_surface_preflight.py
- tests/quality_gates/test_critique_boundary_ownership_presence.py
- tests/quality_gates/test_describe_goal_closeout_shape.py
- tests/quality_gates/test_dup_ratchet.py
- tests/quality_gates/test_dup_ratchet_triage_draft.py
- tests/quality_gates/test_dup_review_seed.py
- tests/quality_gates/test_goal_closeout_normalize.py
- tests/quality_gates/test_goal_disposition_gate.py
- tests/quality_gates/test_goal_early_close_report.py
- tests/quality_gates/test_issue_closeout_draft_validation.py
- tests/quality_gates/test_migrate_dup_fingerprints.py
- tests/quality_gates/test_mutation_coverage_producer.py
- tests/quality_gates/test_quality_dead_code_advisory.py
- tests/quality_gates/test_quality_doc_duplicates.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_release_only_sentinel_inventory.py
- tests/quality_gates/test_release_run_planner.py
- tests/quality_gates/test_reviewer_tier_policy.py
- tests/quality_gates/test_run_slice_closeout_surface_obligations.py
- tests/quality_gates/test_setup_inspect_policy.py
- tests/quality_gates/test_slice_closeout_base_range.py
- tests/quality_gates/test_standing_doc_provenance.py
- tests/test_gather_plan.py
- tests/test_handoff_plan.py
- tests/test_nose_inprocess_coverage.py
- tests/test_quality_scaffold.py
- tests/test_retro_help.py
- tests/test_skill_text_quality_lib.py
- tests/test_web_fetch_help.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/mutation_coverage_producer.py, scripts/run_slice_closeout.py, scripts/setup_agent_docs_fresh_eye_lib.py, scripts/slice_closeout_parser.py, scripts/surfaces_lib.py, skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/scripts/audit_disposition_corpus.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, skills/public/achieve/scripts/goal_artifact_early_close_report.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/references/adapter-contract.md, skills/public/gather/scripts/gather_plan.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/impl/scripts/check_boundary_escalation.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/quality/references/skill-ergonomics.md, skills/public/quality/scripts/check_changed_line_coverage.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/check_standing_doc_provenance.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_nose_clones.py, skills/public/quality/scripts/inventory_release_only_sentinels.py, skills/public/quality/scripts/migrate_dup_fingerprints.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/skill_text_quality_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/plan_release_run.py, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/retro/scripts/mine_closeout_telemetry.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/prepare_packet.py, skills/public/setup/references/agent-docs-policy.md, skills/support/web-fetch/scripts/acquire_public_url.py, skills/support/web-fetch/scripts/classify_fetch_response.py, skills/support/web-fetch/scripts/route_public_fetch.py
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/setup_agent_docs_fresh_eye_lib.py, plugins/charness/scripts/slice_closeout_parser.py, plugins/charness/scripts/surfaces_lib.py, plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/scripts/audit_disposition_corpus.py, plugins/charness/skills/achieve/scripts/describe_goal_closeout_shape.py, plugins/charness/skills/achieve/scripts/goal_artifact_early_close_report.py, plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/gather/scripts/gather_plan.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/impl/scripts/check_boundary_escalation.py, plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py, plugins/charness/skills/issue/scripts/issue_validate_closeout_draft.py, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/quality/scripts/check_changed_line_coverage.py, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/check_standing_doc_provenance.py, plugins/charness/skills/quality/scripts/draft_dup_ratchet_triage.py, plugins/charness/skills/quality/scripts/inventory_doc_duplicates.py, plugins/charness/skills/quality/scripts/inventory_nose_clones.py, plugins/charness/skills/quality/scripts/inventory_release_only_sentinels.py, plugins/charness/skills/quality/scripts/migrate_dup_fingerprints.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/quality/scripts/seed_dup_review.py, plugins/charness/skills/quality/scripts/skill_text_quality_lib.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/skills/release/scripts/plan_release_run.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/references/phase-aware-efficiency.md, plugins/charness/skills/retro/scripts/mine_closeout_telemetry.py, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/skills/retro/scripts/prepare_packet.py, plugins/charness/skills/setup/references/agent-docs-policy.md, plugins/charness/support/web-fetch/scripts/acquire_public_url.py, plugins/charness/support/web-fetch/scripts/classify_fetch_response.py, plugins/charness/support/web-fetch/scripts/route_public_fetch.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: AGENTS.md, charness-artifacts/critique/2026-07-11-080522-packet.md, charness-artifacts/critique/2026-07-11-082541-packet.md, charness-artifacts/critique/2026-07-11-083446-packet.md, charness-artifacts/critique/2026-07-11-085201-packet.md, charness-artifacts/critique/2026-07-11-091356-packet.md, charness-artifacts/critique/2026-07-11-093306-packet.md, charness-artifacts/critique/2026-07-11-094504-packet.md, charness-artifacts/critique/2026-07-11-101842-packet.md, charness-artifacts/critique/2026-07-11-103004-packet.md, charness-artifacts/critique/2026-07-11-110741-packet.md, charness-artifacts/critique/2026-07-11-closeout-parser-extraction-packet.md, charness-artifacts/critique/2026-07-11-closeout-parser-extraction.md, charness-artifacts/critique/2026-07-11-coverage-anchor-postreview-packet.md, charness-artifacts/critique/2026-07-11-coverage-anchor-worktree-packet.md, charness-artifacts/critique/2026-07-11-coverage-anchor.md, charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification-packet.md, charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification.md, charness-artifacts/critique/2026-07-11-final-quality-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-five-package-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-host-reference-north-star-critique.md, charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.md, charness-artifacts/critique/2026-07-11-quality-scaffold-h1.md, charness-artifacts/critique/2026-07-11-release-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-retro-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-superseded-release-regex-packet.md, charness-artifacts/critique/2026-07-11-superseded-release-regex.md, charness-artifacts/critique/2026-07-11-truthful-standing-delegation.md, charness-artifacts/critique/2026-07-11-web-fetch-argparse-help-critique.md, charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md, charness-artifacts/quality/2026-07-11-final-quality-argparse-help.md, charness-artifacts/quality/2026-07-11-five-package-argparse-help.md, charness-artifacts/quality/2026-07-11-host-reference-north-star.md, charness-artifacts/quality/2026-07-11-release-argparse-help.md, charness-artifacts/quality/2026-07-11-retro-argparse-help.md, charness-artifacts/quality/2026-07-11-truthful-standing-delegation.md, charness-artifacts/quality/2026-07-11-web-fetch-argparse-help.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-07-11-105806-packet.md, charness-artifacts/retro/2026-07-11-truthful-standing-delegation-retro.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, docs/operator-progressive-path.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/critique/references/adapter-contract.md, skills/public/quality/references/skill-ergonomics.md, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/setup/references/agent-docs-policy.md
  derived matches: plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/references/phase-aware-efficiency.md, plugins/charness/skills/setup/references/agent-docs-policy.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: AGENTS.md, skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/critique/references/adapter-contract.md, skills/public/quality/references/skill-ergonomics.md, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/setup/references/agent-docs-policy.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/scripts/audit_disposition_corpus.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, skills/public/achieve/scripts/goal_artifact_early_close_report.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/references/adapter-contract.md, skills/public/gather/scripts/gather_plan.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/impl/scripts/check_boundary_escalation.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/quality/references/skill-ergonomics.md, skills/public/quality/scripts/check_changed_line_coverage.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/check_standing_doc_provenance.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_nose_clones.py, skills/public/quality/scripts/inventory_release_only_sentinels.py, skills/public/quality/scripts/migrate_dup_fingerprints.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/skill_text_quality_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/plan_release_run.py, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/retro/scripts/mine_closeout_telemetry.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/prepare_packet.py, skills/public/setup/references/agent-docs-policy.md, skills/support/web-fetch/scripts/acquire_public_url.py, skills/support/web-fetch/scripts/classify_fetch_response.py, skills/support/web-fetch/scripts/route_public_fetch.py
  derived matches: plugins/charness/skills/achieve/references/coordination.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/scripts/audit_disposition_corpus.py, plugins/charness/skills/achieve/scripts/describe_goal_closeout_shape.py, plugins/charness/skills/achieve/scripts/goal_artifact_early_close_report.py, plugins/charness/skills/achieve/scripts/normalize_goal_closeout.py, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/gather/scripts/gather_plan.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/impl/scripts/check_boundary_escalation.py, plugins/charness/skills/issue/scripts/describe_closeout_draft_shape.py, plugins/charness/skills/issue/scripts/issue_validate_closeout_draft.py, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/quality/scripts/check_changed_line_coverage.py, plugins/charness/skills/quality/scripts/check_dup_ratchet.py, plugins/charness/skills/quality/scripts/check_standing_doc_provenance.py, plugins/charness/skills/quality/scripts/draft_dup_ratchet_triage.py, plugins/charness/skills/quality/scripts/inventory_doc_duplicates.py, plugins/charness/skills/quality/scripts/inventory_nose_clones.py, plugins/charness/skills/quality/scripts/inventory_release_only_sentinels.py, plugins/charness/skills/quality/scripts/migrate_dup_fingerprints.py, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/quality/scripts/seed_dup_review.py, plugins/charness/skills/quality/scripts/skill_text_quality_lib.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/skills/release/scripts/plan_release_run.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/references/phase-aware-efficiency.md, plugins/charness/skills/retro/scripts/mine_closeout_telemetry.py, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/skills/retro/scripts/prepare_packet.py, plugins/charness/skills/setup/references/agent-docs-policy.md, plugins/charness/support/web-fetch/scripts/acquire_public_url.py, plugins/charness/support/web-fetch/scripts/classify_fetch_response.py, plugins/charness/support/web-fetch/scripts/route_public_fetch.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/scripts/audit_disposition_corpus.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, skills/public/achieve/scripts/goal_artifact_early_close_report.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/references/adapter-contract.md, skills/public/gather/scripts/gather_plan.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/impl/scripts/check_boundary_escalation.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/quality/references/skill-ergonomics.md, skills/public/quality/scripts/check_changed_line_coverage.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/check_standing_doc_provenance.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_nose_clones.py, skills/public/quality/scripts/inventory_release_only_sentinels.py, skills/public/quality/scripts/migrate_dup_fingerprints.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/skill_text_quality_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/plan_release_run.py, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/retro/scripts/mine_closeout_telemetry.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/prepare_packet.py, skills/public/setup/references/agent-docs-policy.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/achieve/references/coordination.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/scripts/audit_disposition_corpus.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, skills/public/achieve/scripts/goal_artifact_early_close_report.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/critique/references/adapter-contract.md, skills/public/gather/scripts/gather_plan.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/impl/scripts/check_boundary_escalation.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/quality/references/skill-ergonomics.md, skills/public/quality/scripts/check_changed_line_coverage.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/check_standing_doc_provenance.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_nose_clones.py, skills/public/quality/scripts/inventory_release_only_sentinels.py, skills/public/quality/scripts/migrate_dup_fingerprints.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/skill_text_quality_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/plan_release_run.py, skills/public/retro/SKILL.md, skills/public/retro/references/phase-aware-efficiency.md, skills/public/retro/scripts/mine_closeout_telemetry.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/prepare_packet.py, skills/public/setup/references/agent-docs-policy.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-11-080522-packet.json, charness-artifacts/critique/2026-07-11-080522-packet.md, charness-artifacts/critique/2026-07-11-082541-packet.json, charness-artifacts/critique/2026-07-11-082541-packet.md, charness-artifacts/critique/2026-07-11-083446-packet.json, charness-artifacts/critique/2026-07-11-083446-packet.md, charness-artifacts/critique/2026-07-11-085201-packet.json, charness-artifacts/critique/2026-07-11-085201-packet.md, charness-artifacts/critique/2026-07-11-091356-packet.json, charness-artifacts/critique/2026-07-11-091356-packet.md, charness-artifacts/critique/2026-07-11-093306-packet.json, charness-artifacts/critique/2026-07-11-093306-packet.md, charness-artifacts/critique/2026-07-11-094504-packet.json, charness-artifacts/critique/2026-07-11-094504-packet.md, charness-artifacts/critique/2026-07-11-101842-packet.json, charness-artifacts/critique/2026-07-11-101842-packet.md, charness-artifacts/critique/2026-07-11-103004-packet.json, charness-artifacts/critique/2026-07-11-103004-packet.md, charness-artifacts/critique/2026-07-11-110741-packet.json, charness-artifacts/critique/2026-07-11-110741-packet.md, charness-artifacts/critique/2026-07-11-closeout-parser-extraction-packet.json, charness-artifacts/critique/2026-07-11-closeout-parser-extraction-packet.md, charness-artifacts/critique/2026-07-11-closeout-parser-extraction.md, charness-artifacts/critique/2026-07-11-coverage-anchor-postreview-packet.json, charness-artifacts/critique/2026-07-11-coverage-anchor-postreview-packet.md, charness-artifacts/critique/2026-07-11-coverage-anchor-worktree-packet.json, charness-artifacts/critique/2026-07-11-coverage-anchor-worktree-packet.md, charness-artifacts/critique/2026-07-11-coverage-anchor.md, charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification-packet.json, charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification-packet.md, charness-artifacts/critique/2026-07-11-dataclass-dead-code-classification.md, charness-artifacts/critique/2026-07-11-final-quality-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-five-package-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-host-reference-north-star-critique.md, charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.json, charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.md, charness-artifacts/critique/2026-07-11-quality-scaffold-h1.md, charness-artifacts/critique/2026-07-11-release-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-retro-argparse-help-critique.md, charness-artifacts/critique/2026-07-11-superseded-release-regex-packet.json, charness-artifacts/critique/2026-07-11-superseded-release-regex-packet.md, charness-artifacts/critique/2026-07-11-superseded-release-regex.md, charness-artifacts/critique/2026-07-11-truthful-standing-delegation.md, charness-artifacts/critique/2026-07-11-web-fetch-argparse-help-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-11-105806-packet.json, charness-artifacts/retro/2026-07-11-105806-packet.md, charness-artifacts/retro/2026-07-11-truthful-standing-delegation-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/setup_agent_docs_fresh_eye_lib.py, plugins/charness/scripts/slice_closeout_parser.py, plugins/charness/scripts/surfaces_lib.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/mutation_coverage_producer.py, scripts/run_slice_closeout.py, scripts/setup_agent_docs_fresh_eye_lib.py, scripts/slice_closeout_parser.py, scripts/surfaces_lib.py, tests/quality_gates/test_changed_line_coverage_gate.py, tests/quality_gates/test_check_artifact_surface_preflight.py, tests/quality_gates/test_critique_boundary_ownership_presence.py, tests/quality_gates/test_describe_goal_closeout_shape.py, tests/quality_gates/test_dup_ratchet.py, tests/quality_gates/test_dup_ratchet_triage_draft.py, tests/quality_gates/test_dup_review_seed.py, tests/quality_gates/test_goal_closeout_normalize.py, tests/quality_gates/test_goal_disposition_gate.py, tests/quality_gates/test_goal_early_close_report.py, tests/quality_gates/test_issue_closeout_draft_validation.py, tests/quality_gates/test_migrate_dup_fingerprints.py, tests/quality_gates/test_mutation_coverage_producer.py, tests/quality_gates/test_quality_dead_code_advisory.py, tests/quality_gates/test_quality_doc_duplicates.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_release_only_sentinel_inventory.py, tests/quality_gates/test_release_run_planner.py, tests/quality_gates/test_reviewer_tier_policy.py, tests/quality_gates/test_run_slice_closeout_surface_obligations.py, tests/quality_gates/test_setup_inspect_policy.py, tests/quality_gates/test_slice_closeout_base_range.py, tests/quality_gates/test_standing_doc_provenance.py, tests/test_gather_plan.py, tests/test_handoff_plan.py, tests/test_nose_inprocess_coverage.py, tests/test_quality_scaffold.py, tests/test_retro_help.py, tests/test_skill_text_quality_lib.py, tests/test_web_fetch_help.py
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/setup_agent_docs_fresh_eye_lib.py, plugins/charness/scripts/slice_closeout_parser.py, plugins/charness/scripts/surfaces_lib.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: skills/public/quality/scripts/inventory_nose_clones.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/mutation_coverage_producer.py, scripts/run_slice_closeout.py, scripts/setup_agent_docs_fresh_eye_lib.py, scripts/slice_closeout_parser.py, scripts/surfaces_lib.py, skills/public/achieve/scripts/audit_disposition_corpus.py, skills/public/achieve/scripts/describe_goal_closeout_shape.py, skills/public/achieve/scripts/goal_artifact_early_close_report.py, skills/public/achieve/scripts/normalize_goal_closeout.py, skills/public/gather/scripts/gather_plan.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/impl/scripts/check_boundary_escalation.py, skills/public/issue/scripts/describe_closeout_draft_shape.py, skills/public/issue/scripts/issue_validate_closeout_draft.py, skills/public/quality/scripts/check_changed_line_coverage.py, skills/public/quality/scripts/check_dup_ratchet.py, skills/public/quality/scripts/check_standing_doc_provenance.py, skills/public/quality/scripts/draft_dup_ratchet_triage.py, skills/public/quality/scripts/inventory_doc_duplicates.py, skills/public/quality/scripts/inventory_nose_clones.py, skills/public/quality/scripts/inventory_release_only_sentinels.py, skills/public/quality/scripts/migrate_dup_fingerprints.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/quality/scripts/seed_dup_review.py, skills/public/quality/scripts/skill_text_quality_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/public/release/scripts/plan_release_run.py, skills/public/retro/scripts/mine_closeout_telemetry.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/prepare_packet.py, skills/support/web-fetch/scripts/acquire_public_url.py, skills/support/web-fetch/scripts/classify_fetch_response.py, skills/support/web-fetch/scripts/route_public_fetch.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
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
