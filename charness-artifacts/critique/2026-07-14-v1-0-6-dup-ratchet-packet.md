# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-14T02:43:35Z
- **Prepared for**: v1.0.6 dup-ratchet disposition after structural reduction
- **Changed ref**: `4ccbdf757bfe2867501a447742f07eb871848f8e..HEAD`
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
Changed paths for ref `4ccbdf757bfe2867501a447742f07eb871848f8e..HEAD`:
- .claude-plugin/marketplace.json
- charness
- charness-artifacts/critique/2026-07-13-075725-packet.json
- charness-artifacts/critique/2026-07-13-075725-packet.md
- charness-artifacts/critique/2026-07-13-081550-packet.json
- charness-artifacts/critique/2026-07-13-081550-packet.md
- charness-artifacts/critique/2026-07-13-082943-packet.json
- charness-artifacts/critique/2026-07-13-082943-packet.md
- charness-artifacts/critique/2026-07-13-084328-packet.json
- charness-artifacts/critique/2026-07-13-084328-packet.md
- charness-artifacts/critique/2026-07-13-225535-packet.json
- charness-artifacts/critique/2026-07-13-225535-packet.md
- charness-artifacts/critique/2026-07-13-231102-packet.json
- charness-artifacts/critique/2026-07-13-231102-packet.md
- charness-artifacts/critique/2026-07-13-catalog-refresh-invalid-root-code-critique.md
- charness-artifacts/critique/2026-07-13-custom-home-claude-subprocess-code-critique.md
- charness-artifacts/critique/2026-07-13-issue-resolve-preflight-ordering-code-critique.md
- charness-artifacts/critique/2026-07-13-north-star-autonomous-two-hour-release-round-4-disposition-review.md
- charness-artifacts/critique/2026-07-13-north-star-round-5-disposition-review.md
- charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.json
- charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.md
- charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.json
- charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.md
- charness-artifacts/critique/2026-07-13-v1-0-1-retired-hook-ledger-cleanup.md
- charness-artifacts/critique/2026-07-13-v1-0-2-release-critique.md
- charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.json
- charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.md
- charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-critique.md
- charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.json
- charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.md
- charness-artifacts/critique/2026-07-13-v1-0-4-release-critique.md
- charness-artifacts/critique/2026-07-14-003710-packet.json
- charness-artifacts/critique/2026-07-14-003710-packet.md
- charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md
- charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.json
- charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.md
- charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md
- charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-critique.md
- charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.json
- charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md
- charness-artifacts/critique/2026-07-14-v1-0-5-handoff-refresh-critique.md
- charness-artifacts/critique/2026-07-14-v1-0-5-release-critique.md
- charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-critique.md
- charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.json
- charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.md
- charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.json
- charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md
- charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md
- charness-artifacts/debug/2026-07-13-debug-review-followup-2.md
- charness-artifacts/debug/2026-07-13-debug-review-followup-3.md
- charness-artifacts/debug/2026-07-13-debug-review-followup.md
- charness-artifacts/debug/2026-07-13-debug-review.md
- charness-artifacts/debug/2026-07-13-quality-scaffold-reproduction-source-omission.md
- charness-artifacts/debug/2026-07-14-debug-review.md
- charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md
- charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md
- charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5-early-close-report.md
- charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-07-13-north-star-autonomous-two-hour-release-round-4-host-log.json
- charness-artifacts/probe/2026-07-13-v1.0.4-independent-release-observer.json
- charness-artifacts/quality/2026-07-13-quality-review.md
- charness-artifacts/quality/2026-07-13-round4-v1-0-2-release-readiness.md
- charness-artifacts/quality/2026-07-13-round5-v1-0-4-release-readiness.md
- charness-artifacts/quality/2026-07-14-quality-review.md
- charness-artifacts/quality/history/2026-07-14-open-issue-resolution-proof.md
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/2026-07-13-v1.0.1-notes.md
- charness-artifacts/release/2026-07-13-v1.0.2-notes.md
- charness-artifacts/release/2026-07-13-v1.0.3-notes.md
- charness-artifacts/release/2026-07-13-v1.0.4-notes.md
- charness-artifacts/release/2026-07-14-v1.0.5-notes.md
- charness-artifacts/release/2026-07-14-v1.0.6-notes.md
- charness-artifacts/release/latest.md
- charness-artifacts/retro/2026-07-13-071142-packet.json
- charness-artifacts/retro/2026-07-13-071142-packet.md
- charness-artifacts/retro/2026-07-13-085819-packet.json
- charness-artifacts/retro/2026-07-13-085819-packet.md
- charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md
- charness-artifacts/retro/2026-07-13-north-star-autonomous-two-hour-release-round-4-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-1-release-auto-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-4-release-auto-retro.md
- charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md
- charness-artifacts/retro/2026-07-14-session-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-07-13-retired-hook-ledger-cleanup.md
- charness-artifacts/spec/2026-07-14-cautilus-structured-output-compatibility.md
- charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md
- charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md
- docs/handoff.md
- docs/product-success-metrics.md
- docs/public-skill-dogfood.json
- evals/cautilus/chatbot-scenario-proposal-inputs.json
- packaging/charness.json
- plugins/charness/.claude-plugin/plugin.json
- plugins/charness/.codex-plugin/plugin.json
- plugins/charness/scripts/boundary-bypass-exemptions.txt
- plugins/charness/scripts/capability_catalog.py
- plugins/charness/scripts/check_skill_bootstrap_vars.py
- plugins/charness/scripts/eval_cautilus_chatbot_compare.py
- plugins/charness/scripts/eval_cautilus_chatbot_proposals.py
- plugins/charness/scripts/host_hook_session_routing.py
- plugins/charness/scripts/lifecycle_usage_capture.py
- plugins/charness/scripts/report_usage_episodes.py
- plugins/charness/scripts/usage_episode_feedback.py
- plugins/charness/scripts/usage_episode_product_evidence.py
- plugins/charness/shared/references/bootstrap-resolution.md
- plugins/charness/skills/issue/scripts/issue_close.py
- plugins/charness/skills/issue/scripts/issue_plan.py
- plugins/charness/skills/quality/references/attention-state-visibility.json
- plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py
- plugins/charness/skills/release/scripts/publish_release_artifact.py
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- scripts/boundary-bypass-exemptions.txt
- scripts/capability_catalog.py
- scripts/check_skill_bootstrap_vars.py
- scripts/eval_cautilus_chatbot_compare.py
- scripts/eval_cautilus_chatbot_proposals.py
- scripts/host_hook_session_routing.py
- scripts/lifecycle_usage_capture.py
- scripts/report_usage_episodes.py
- scripts/usage_episode_feedback.py
- scripts/usage_episode_product_evidence.py
- skills/public/issue/scripts/issue_close.py
- skills/public/issue/scripts/issue_plan.py
- skills/public/quality/references/attention-state-visibility.json
- skills/public/quality/scripts/scaffold_quality_artifact.py
- skills/public/release/scripts/publish_release_artifact.py
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/shared/references/bootstrap-resolution.md
- tests/charness_cli/test_claude_home_unit.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/charness_cli/test_managed_install.py
- tests/charness_cli/test_managed_install_extended.py
- tests/quality_gates/test_dup_ratchet.py
- tests/quality_gates/test_dup_ratchet_scoped_rebaseline.py
- tests/quality_gates/test_issue_skill.py
- tests/quality_gates/test_issue_tool_runners.py
- tests/quality_gates/test_python_and_security_gates.py
- tests/quality_gates/test_python_length_gates.py
- tests/quality_gates/test_quality_runner_runtime_aggregate.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_run_slice_closeout_review_obligations.py
- tests/quality_gates/test_run_slice_closeout_surface_obligations.py
- tests/quality_gates/test_skill_bootstrap_vars.py
- tests/test_capability_catalog.py
- tests/test_cautilus_chatbot_compare.py
- tests/test_cautilus_eval_commands.py
- tests/test_lifecycle_usage_capture.py
- tests/test_quality_scaffold.py
- tests/test_session_routing_host_hook_reconcile.py
- tests/test_usage_episodes_report.py
- tests/test_usage_feedback.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: packaging/charness.json, scripts/boundary-bypass-exemptions.txt, scripts/capability_catalog.py, scripts/check_skill_bootstrap_vars.py, scripts/eval_cautilus_chatbot_compare.py, scripts/eval_cautilus_chatbot_proposals.py, scripts/host_hook_session_routing.py, scripts/lifecycle_usage_capture.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_plan.py, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  derived matches: .claude-plugin/marketplace.json, plugins/charness/.claude-plugin/plugin.json, plugins/charness/.codex-plugin/plugin.json, plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/capability_catalog.py, plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/eval_cautilus_chatbot_compare.py, plugins/charness/scripts/eval_cautilus_chatbot_proposals.py, plugins/charness/scripts/host_hook_session_routing.py, plugins/charness/scripts/lifecycle_usage_capture.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/shared/references/bootstrap-resolution.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_plan.py, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-13-075725-packet.md, charness-artifacts/critique/2026-07-13-081550-packet.md, charness-artifacts/critique/2026-07-13-082943-packet.md, charness-artifacts/critique/2026-07-13-084328-packet.md, charness-artifacts/critique/2026-07-13-225535-packet.md, charness-artifacts/critique/2026-07-13-231102-packet.md, charness-artifacts/critique/2026-07-13-catalog-refresh-invalid-root-code-critique.md, charness-artifacts/critique/2026-07-13-custom-home-claude-subprocess-code-critique.md, charness-artifacts/critique/2026-07-13-issue-resolve-preflight-ordering-code-critique.md, charness-artifacts/critique/2026-07-13-north-star-autonomous-two-hour-release-round-4-disposition-review.md, charness-artifacts/critique/2026-07-13-north-star-round-5-disposition-review.md, charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.md, charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.md, charness-artifacts/critique/2026-07-13-v1-0-1-retired-hook-ledger-cleanup.md, charness-artifacts/critique/2026-07-13-v1-0-2-release-critique.md, charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.md, charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-critique.md, charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.md, charness-artifacts/critique/2026-07-13-v1-0-4-release-critique.md, charness-artifacts/critique/2026-07-14-003710-packet.md, charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md, charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.md, charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md, charness-artifacts/critique/2026-07-14-v1-0-5-handoff-refresh-critique.md, charness-artifacts/critique/2026-07-14-v1-0-5-release-critique.md, charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-critique.md, charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.md, charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md, charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md, charness-artifacts/debug/2026-07-13-debug-review-followup-2.md, charness-artifacts/debug/2026-07-13-debug-review-followup-3.md, charness-artifacts/debug/2026-07-13-debug-review-followup.md, charness-artifacts/debug/2026-07-13-debug-review.md, charness-artifacts/debug/2026-07-13-quality-scaffold-reproduction-source-omission.md, charness-artifacts/debug/2026-07-14-debug-review.md, charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md, charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md, charness-artifacts/debug/latest.md, charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md, charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5-early-close-report.md, charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md, charness-artifacts/quality/2026-07-13-quality-review.md, charness-artifacts/quality/2026-07-13-round4-v1-0-2-release-readiness.md, charness-artifacts/quality/2026-07-13-round5-v1-0-4-release-readiness.md, charness-artifacts/quality/2026-07-14-quality-review.md, charness-artifacts/quality/history/2026-07-14-open-issue-resolution-proof.md, charness-artifacts/quality/latest.md, charness-artifacts/release/2026-07-13-v1.0.1-notes.md, charness-artifacts/release/2026-07-13-v1.0.2-notes.md, charness-artifacts/release/2026-07-13-v1.0.3-notes.md, charness-artifacts/release/2026-07-13-v1.0.4-notes.md, charness-artifacts/release/2026-07-14-v1.0.5-notes.md, charness-artifacts/release/2026-07-14-v1.0.6-notes.md, charness-artifacts/release/latest.md, charness-artifacts/retro/2026-07-13-071142-packet.md, charness-artifacts/retro/2026-07-13-085819-packet.md, charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md, charness-artifacts/retro/2026-07-13-north-star-autonomous-two-hour-release-round-4-retro.md, charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-1-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-4-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md, charness-artifacts/retro/2026-07-14-session-retro.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-07-13-retired-hook-ledger-cleanup.md, charness-artifacts/spec/2026-07-14-cautilus-structured-output-compatibility.md, charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md, charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md, docs/handoff.md, docs/product-success-metrics.md, skills/shared/references/bootstrap-resolution.md
  derived matches: plugins/charness/shared/references/bootstrap-resolution.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_plan.py, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  derived matches: plugins/charness/shared/references/bootstrap-resolution.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/issue/scripts/issue_plan.py, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness, scripts/capability_catalog.py
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 scripts/validate_current_pointer_freshness.py --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_plan.py, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_plan.py, skills/public/quality/references/attention-state-visibility.json, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-13-075725-packet.json, charness-artifacts/critique/2026-07-13-075725-packet.md, charness-artifacts/critique/2026-07-13-081550-packet.json, charness-artifacts/critique/2026-07-13-081550-packet.md, charness-artifacts/critique/2026-07-13-082943-packet.json, charness-artifacts/critique/2026-07-13-082943-packet.md, charness-artifacts/critique/2026-07-13-084328-packet.json, charness-artifacts/critique/2026-07-13-084328-packet.md, charness-artifacts/critique/2026-07-13-225535-packet.json, charness-artifacts/critique/2026-07-13-225535-packet.md, charness-artifacts/critique/2026-07-13-231102-packet.json, charness-artifacts/critique/2026-07-13-231102-packet.md, charness-artifacts/critique/2026-07-13-catalog-refresh-invalid-root-code-critique.md, charness-artifacts/critique/2026-07-13-custom-home-claude-subprocess-code-critique.md, charness-artifacts/critique/2026-07-13-issue-resolve-preflight-ordering-code-critique.md, charness-artifacts/critique/2026-07-13-north-star-autonomous-two-hour-release-round-4-disposition-review.md, charness-artifacts/critique/2026-07-13-north-star-round-5-disposition-review.md, charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.json, charness-artifacts/critique/2026-07-13-round4-goal-plan-packet.md, charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.json, charness-artifacts/critique/2026-07-13-round4-issue-preflight-packet.md, charness-artifacts/critique/2026-07-13-v1-0-1-retired-hook-ledger-cleanup.md, charness-artifacts/critique/2026-07-13-v1-0-2-release-critique.md, charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.json, charness-artifacts/critique/2026-07-13-v1-0-2-release-packet.md, charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-critique.md, charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.json, charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.md, charness-artifacts/critique/2026-07-13-v1-0-4-release-critique.md, charness-artifacts/critique/2026-07-14-003710-packet.json, charness-artifacts/critique/2026-07-14-003710-packet.md, charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-critique.md, charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.json, charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.md, charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.json, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md, charness-artifacts/critique/2026-07-14-v1-0-5-handoff-refresh-critique.md, charness-artifacts/critique/2026-07-14-v1-0-5-release-critique.md, charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-critique.md, charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.json, charness-artifacts/critique/2026-07-14-v1-0-6-pre-release-packet.md, charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.json, charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-13-north-star-autonomous-two-hour-release-round-4-host-log.json, charness-artifacts/probe/2026-07-13-v1.0.4-independent-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- cautilus-chatbot-proposals: Checked-in long-context chatbot proposal packets and their current-pointer artifacts.
  source matches: evals/cautilus/chatbot-scenario-proposal-inputs.json, scripts/eval_cautilus_chatbot_proposals.py
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- cautilus-chatbot-benchmark: A/B comparison runner and current-pointer artifacts for long-context chatbot proposal benchmarking.
  source matches: scripts/eval_cautilus_chatbot_compare.py, scripts/eval_cautilus_chatbot_proposals.py
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md, charness-artifacts/debug/2026-07-13-debug-review-followup-2.md, charness-artifacts/debug/2026-07-13-debug-review-followup-3.md, charness-artifacts/debug/2026-07-13-debug-review-followup.md, charness-artifacts/debug/2026-07-13-debug-review.md, charness-artifacts/debug/2026-07-13-quality-scaffold-reproduction-source-omission.md, charness-artifacts/debug/2026-07-14-debug-review.md, charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md, charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-13-071142-packet.json, charness-artifacts/retro/2026-07-13-071142-packet.md, charness-artifacts/retro/2026-07-13-085819-packet.json, charness-artifacts/retro/2026-07-13-085819-packet.md, charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md, charness-artifacts/retro/2026-07-13-north-star-autonomous-two-hour-release-round-4-retro.md, charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-1-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-4-release-auto-retro.md, charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md, charness-artifacts/retro/2026-07-14-session-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/capability_catalog.py, plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/eval_cautilus_chatbot_compare.py, plugins/charness/scripts/eval_cautilus_chatbot_proposals.py, plugins/charness/scripts/host_hook_session_routing.py, plugins/charness/scripts/lifecycle_usage_capture.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/capability_catalog.py, scripts/check_skill_bootstrap_vars.py, scripts/eval_cautilus_chatbot_compare.py, scripts/eval_cautilus_chatbot_proposals.py, scripts/host_hook_session_routing.py, scripts/lifecycle_usage_capture.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, tests/charness_cli/test_claude_home_unit.py, tests/charness_cli/test_codex_cache_refresh.py, tests/charness_cli/test_managed_install.py, tests/charness_cli/test_managed_install_extended.py, tests/quality_gates/test_dup_ratchet.py, tests/quality_gates/test_dup_ratchet_scoped_rebaseline.py, tests/quality_gates/test_issue_skill.py, tests/quality_gates/test_issue_tool_runners.py, tests/quality_gates/test_python_and_security_gates.py, tests/quality_gates/test_python_length_gates.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_run_slice_closeout_review_obligations.py, tests/quality_gates/test_run_slice_closeout_surface_obligations.py, tests/quality_gates/test_skill_bootstrap_vars.py, tests/test_capability_catalog.py, tests/test_cautilus_chatbot_compare.py, tests/test_cautilus_eval_commands.py, tests/test_lifecycle_usage_capture.py, tests/test_quality_scaffold.py, tests/test_session_routing_host_hook_reconcile.py, tests/test_usage_episodes_report.py, tests/test_usage_feedback.py
  derived matches: plugins/charness/scripts/capability_catalog.py, plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/eval_cautilus_chatbot_compare.py, plugins/charness/scripts/eval_cautilus_chatbot_proposals.py, plugins/charness/scripts/host_hook_session_routing.py, plugins/charness/scripts/lifecycle_usage_capture.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/capability_catalog.py, scripts/check_skill_bootstrap_vars.py, scripts/eval_cautilus_chatbot_compare.py, scripts/eval_cautilus_chatbot_proposals.py, scripts/host_hook_session_routing.py, scripts/lifecycle_usage_capture.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, skills/public/issue/scripts/issue_close.py, skills/public/issue/scripts/issue_plan.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

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
