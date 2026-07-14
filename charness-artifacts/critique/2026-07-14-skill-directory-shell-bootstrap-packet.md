# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-14T01:17:25Z
- **Prepared for**: SKILL_DIR bootstrap fix and locked-suite isolation repair
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
Changed paths for working tree:
- charness-artifacts/debug/latest.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/quality/2026-07-14-quality-review.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- docs/product-success-metrics.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/check_skill_bootstrap_vars.py
- plugins/charness/scripts/report_usage_episodes.py
- plugins/charness/scripts/usage_episode_feedback.py
- plugins/charness/scripts/usage_episode_product_evidence.py
- plugins/charness/shared/references/bootstrap-resolution.md
- plugins/charness/skills/issue/scripts/issue_close.py
- plugins/charness/skills/quality/references/attention-state-visibility.json
- plugins/charness/skills/release/scripts/publish_release_artifact.py
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- scripts/check_skill_bootstrap_vars.py
- scripts/report_usage_episodes.py
- scripts/usage_episode_feedback.py
- scripts/usage_episode_product_evidence.py
- skills/public/issue/scripts/issue_close.py
- skills/public/quality/references/attention-state-visibility.json
- skills/public/release/scripts/publish_release_artifact.py
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/shared/references/bootstrap-resolution.md
- tests/quality_gates/test_release_publish.py
- tests/test_usage_episodes_report.py
- tests/test_usage_feedback.py
- charness-artifacts/critique/2026-07-14-003710-packet.json
- charness-artifacts/critique/2026-07-14-003710-packet.md
- charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md
- charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.json
- charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md
- charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md
- charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md
- charness-artifacts/retro/2026-07-14-session-retro.md
- charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md
- charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md
- plugins/charness/scripts/lifecycle_usage_capture.py
- scripts/lifecycle_usage_capture.py
- tests/quality_gates/test_skill_bootstrap_vars.py
- tests/test_lifecycle_usage_capture.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check_skill_bootstrap_vars.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, skills/public/issue/scripts/issue_close.py, skills/public/quality/references/attention-state-visibility.json, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md, scripts/lifecycle_usage_capture.py
  derived matches: plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/shared/references/bootstrap-resolution.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/scripts/lifecycle_usage_capture.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/debug/latest.md, charness-artifacts/quality/2026-07-14-quality-review.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, docs/product-success-metrics.md, skills/shared/references/bootstrap-resolution.md, charness-artifacts/critique/2026-07-14-003710-packet.md, charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md, charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md, charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md, charness-artifacts/retro/2026-07-14-session-retro.md, charness-artifacts/spec/2026-07-14-lifecycle-feedback-and-quality-truthfulness.md, charness-artifacts/spec/2026-07-14-skill-directory-shell-bootstrap.md
  derived matches: plugins/charness/shared/references/bootstrap-resolution.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/issue/scripts/issue_close.py, skills/public/quality/references/attention-state-visibility.json, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  derived matches: plugins/charness/shared/references/bootstrap-resolution.md, plugins/charness/skills/issue/scripts/issue_close.py, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/issue/scripts/issue_close.py, skills/public/quality/references/attention-state-visibility.json, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/issue/scripts/issue_close.py, skills/public/quality/references/attention-state-visibility.json, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/shared/references/bootstrap-resolution.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-14-003710-packet.json, charness-artifacts/critique/2026-07-14-003710-packet.md, charness-artifacts/critique/2026-07-14-lifecycle-feedback-and-quality-truthfulness-critique.md, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.json, charness-artifacts/critique/2026-07-14-skill-directory-shell-bootstrap-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/latest.md, charness-artifacts/debug/2026-07-14-lifecycle-capture-quality-mode-test-isolation-debug.md, charness-artifacts/debug/2026-07-14-skill-directory-shell-expansion-debug.md
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/recent-lessons.md, charness-artifacts/retro/2026-07-14-session-retro.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/scripts/lifecycle_usage_capture.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/check_skill_bootstrap_vars.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, tests/quality_gates/test_release_publish.py, tests/test_usage_episodes_report.py, tests/test_usage_feedback.py, scripts/lifecycle_usage_capture.py, tests/quality_gates/test_skill_bootstrap_vars.py, tests/test_lifecycle_usage_capture.py
  derived matches: plugins/charness/scripts/check_skill_bootstrap_vars.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/scripts/lifecycle_usage_capture.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_skill_bootstrap_vars.py, scripts/report_usage_episodes.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, skills/public/issue/scripts/issue_close.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, scripts/lifecycle_usage_capture.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
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
