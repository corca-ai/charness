# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-07-18T18:04:51Z
- **Prepared for**: gajae pattern adoption v2.1.5 release closeout
- **Changed ref**: `v2.1.4..eae81f48`
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
Changed paths for ref `v2.1.4..eae81f48`:
- .agents/release-adapter.yaml
- charness
- charness-artifacts/critique/2026-07-18-152736-packet.json
- charness-artifacts/critique/2026-07-18-152736-packet.md
- charness-artifacts/critique/2026-07-19-changed-line-coverage-branch-proof.md
- charness-artifacts/critique/2026-07-19-critique-scaffold-binding-opt-in.md
- charness-artifacts/critique/2026-07-19-cumulative-closeout-structural-sweep-decoupling.md
- charness-artifacts/critique/2026-07-19-gajae-code-adoption-plan.md
- charness-artifacts/critique/2026-07-19-gajae-slice2-packet.json
- charness-artifacts/critique/2026-07-19-gajae-slice2-packet.md
- charness-artifacts/critique/2026-07-19-gajae-slice2-reviewed-input-binding.md
- charness-artifacts/critique/2026-07-19-gajae-slice3-release-observer.md
- charness-artifacts/critique/2026-07-19-gajae-slice4-efficiency-comparability.md
- charness-artifacts/critique/2026-07-19-gajae-slice5-governed-probes.md
- charness-artifacts/critique/2026-07-19-release-observer-fail-closed.md
- charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.json
- charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.md
- charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.json
- charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.md
- charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-final-packet.json
- charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-final-packet.md
- charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-packet.json
- charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-packet.md
- charness-artifacts/critique/gajae-slice3-release-observer-packet.json
- charness-artifacts/critique/gajae-slice3-release-observer-packet.md
- charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.json
- charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.md
- charness-artifacts/critique/gajae-slice5-governed-probes-final-packet.json
- charness-artifacts/critique/gajae-slice5-governed-probes-final-packet.md
- charness-artifacts/critique/gajae-slice5-governed-probes-packet.json
- charness-artifacts/critique/gajae-slice5-governed-probes-packet.md
- charness-artifacts/critique/gajae-slice5-governed-probes-staged-final-packet.json
- charness-artifacts/critique/gajae-slice5-governed-probes-staged-final-packet.md
- charness-artifacts/critique/release-observer-fail-closed-final-packet.json
- charness-artifacts/critique/release-observer-fail-closed-final-packet.md
- charness-artifacts/debug/2026-07-19-codex-app-server-deadline.md
- charness-artifacts/debug/2026-07-19-critique-content-digest-interpretation-hold.md
- charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md
- charness-artifacts/debug/2026-07-19-cumulative-closeout-staged-scope-coupling.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/gather/2026-07-19-gajae-code-pattern-review.md
- charness-artifacts/gather/latest.md
- charness-artifacts/goals/2026-07-19-gajae-pattern-adoption.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-07-19-v2.1.4-release-observer.json
- charness-artifacts/release/latest.md
- charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/codex_session_audit_lib.py
- plugins/charness/scripts/critique_packet_lib.py
- plugins/charness/scripts/critique_reviewed_input_binding.py
- plugins/charness/scripts/public_skill_dogfood_lib.py
- plugins/charness/scripts/reviewed_input_identity.py
- plugins/charness/scripts/run_skill_efficiency_ab.py
- plugins/charness/scripts/run_skill_efficiency_ab_validation.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/skill_efficiency_report.py
- plugins/charness/scripts/staged_commit_gate_plan.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/references/prepare-packet.md
- plugins/charness/skills/critique/scripts/prepare_packet.py
- plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py
- plugins/charness/skills/release/references/adapter-contract.md
- plugins/charness/skills/release/references/install-refresh.md
- plugins/charness/skills/release/scripts/publish_release_artifact.py
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- plugins/charness/skills/release/scripts/publish_release_helpers.py
- plugins/charness/skills/release/scripts/publish_release_post_create.py
- plugins/charness/skills/release/scripts/release_issue_closeout.py
- plugins/charness/skills/release/scripts/release_observer.py
- plugins/charness/skills/release/scripts/resolve_adapter.py
- plugins/charness/skills/retro/scripts/prepare_packet.py
- scripts/codex_session_audit_lib.py
- scripts/critique_packet_lib.py
- scripts/critique_reviewed_input_binding.py
- scripts/public_skill_dogfood_lib.py
- scripts/reviewed_input_identity.py
- scripts/run_skill_efficiency_ab.py
- scripts/run_skill_efficiency_ab_validation.py
- scripts/run_slice_closeout.py
- scripts/skill_efficiency_report.py
- scripts/staged_commit_gate_plan.py
- scripts/validate_critique_artifacts.py
- skills/public/critique/SKILL.md
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/prepare_packet.py
- skills/public/critique/scripts/scaffold_critique_artifact.py
- skills/public/release/references/adapter-contract.md
- skills/public/release/references/install-refresh.md
- skills/public/release/scripts/publish_release_artifact.py
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_helpers.py
- skills/public/release/scripts/publish_release_post_create.py
- skills/public/release/scripts/release_issue_closeout.py
- skills/public/release/scripts/release_observer.py
- skills/public/release/scripts/resolve_adapter.py
- skills/public/retro/scripts/prepare_packet.py
- tests/charness_cli/fixtures/fake_codex.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/quality_gates/test_release_distinct_channel.py
- tests/quality_gates/test_release_observer.py
- tests/quality_gates/test_retro_codex_session_audit.py
- tests/quality_gates/test_run_slice_closeout_surface_obligations.py
- tests/test_critique_prepare_packet.py
- tests/test_critique_scaffold.py
- tests/test_reviewed_input_identity_failures.py
- tests/test_skill_efficiency_ab.py
- tests/test_skill_efficiency_comparability.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/codex_session_audit_lib.py, scripts/critique_packet_lib.py, scripts/critique_reviewed_input_binding.py, scripts/public_skill_dogfood_lib.py, scripts/reviewed_input_identity.py, scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/run_slice_closeout.py, scripts/skill_efficiency_report.py, scripts/staged_commit_gate_plan.py, scripts/validate_critique_artifacts.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_observer.py, skills/public/release/scripts/resolve_adapter.py, skills/public/retro/scripts/prepare_packet.py
  derived matches: plugins/charness/scripts/codex_session_audit_lib.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/skill_efficiency_report.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/install-refresh.md, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_helpers.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/release/scripts/release_observer.py, plugins/charness/skills/release/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/prepare_packet.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-18-152736-packet.md, charness-artifacts/critique/2026-07-19-changed-line-coverage-branch-proof.md, charness-artifacts/critique/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/critique/2026-07-19-cumulative-closeout-structural-sweep-decoupling.md, charness-artifacts/critique/2026-07-19-gajae-code-adoption-plan.md, charness-artifacts/critique/2026-07-19-gajae-slice2-packet.md, charness-artifacts/critique/2026-07-19-gajae-slice2-reviewed-input-binding.md, charness-artifacts/critique/2026-07-19-gajae-slice3-release-observer.md, charness-artifacts/critique/2026-07-19-gajae-slice4-efficiency-comparability.md, charness-artifacts/critique/2026-07-19-gajae-slice5-governed-probes.md, charness-artifacts/critique/2026-07-19-release-observer-fail-closed.md, charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.md, charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.md, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-final-packet.md, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-packet.md, charness-artifacts/critique/gajae-slice3-release-observer-packet.md, charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-final-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-staged-final-packet.md, charness-artifacts/critique/release-observer-fail-closed-final-packet.md, charness-artifacts/debug/2026-07-19-codex-app-server-deadline.md, charness-artifacts/debug/2026-07-19-critique-content-digest-interpretation-hold.md, charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/debug/2026-07-19-cumulative-closeout-staged-scope-coupling.md, charness-artifacts/debug/latest.md, charness-artifacts/gather/2026-07-19-gajae-code-pattern-review.md, charness-artifacts/gather/latest.md, charness-artifacts/goals/2026-07-19-gajae-pattern-adoption.md, charness-artifacts/release/latest.md, charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md, docs/handoff.md, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/install-refresh.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/release-adapter.yaml, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_observer.py, skills/public/release/scripts/resolve_adapter.py, skills/public/retro/scripts/prepare_packet.py
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/install-refresh.md, plugins/charness/skills/release/scripts/publish_release_artifact.py, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_helpers.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/release/scripts/release_observer.py, plugins/charness/skills/release/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/prepare_packet.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 scripts/validate_current_pointer_freshness.py --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_observer.py, skills/public/release/scripts/resolve_adapter.py, skills/public/retro/scripts/prepare_packet.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, scripts/public_skill_dogfood_lib.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/release/references/adapter-contract.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_observer.py, skills/public/release/scripts/resolve_adapter.py, skills/public/retro/scripts/prepare_packet.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/release-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-18-152736-packet.json, charness-artifacts/critique/2026-07-18-152736-packet.md, charness-artifacts/critique/2026-07-19-changed-line-coverage-branch-proof.md, charness-artifacts/critique/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/critique/2026-07-19-cumulative-closeout-structural-sweep-decoupling.md, charness-artifacts/critique/2026-07-19-gajae-code-adoption-plan.md, charness-artifacts/critique/2026-07-19-gajae-slice2-packet.json, charness-artifacts/critique/2026-07-19-gajae-slice2-packet.md, charness-artifacts/critique/2026-07-19-gajae-slice2-reviewed-input-binding.md, charness-artifacts/critique/2026-07-19-gajae-slice3-release-observer.md, charness-artifacts/critique/2026-07-19-gajae-slice4-efficiency-comparability.md, charness-artifacts/critique/2026-07-19-gajae-slice5-governed-probes.md, charness-artifacts/critique/2026-07-19-release-observer-fail-closed.md, charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.json, charness-artifacts/critique/changed-line-coverage-branch-proof-final-packet.md, charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.json, charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.md, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-final-packet.json, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-final-packet.md, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-packet.json, charness-artifacts/critique/cumulative-closeout-structural-sweep-decoupling-packet.md, charness-artifacts/critique/gajae-slice3-release-observer-packet.json, charness-artifacts/critique/gajae-slice3-release-observer-packet.md, charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.json, charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-final-packet.json, charness-artifacts/critique/gajae-slice5-governed-probes-final-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-packet.json, charness-artifacts/critique/gajae-slice5-governed-probes-packet.md, charness-artifacts/critique/gajae-slice5-governed-probes-staged-final-packet.json, charness-artifacts/critique/gajae-slice5-governed-probes-staged-final-packet.md, charness-artifacts/critique/release-observer-fail-closed-final-packet.json, charness-artifacts/critique/release-observer-fail-closed-final-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-19-v2.1.4-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-19-codex-app-server-deadline.md, charness-artifacts/debug/2026-07-19-critique-content-digest-interpretation-hold.md, charness-artifacts/debug/2026-07-19-critique-scaffold-binding-opt-in.md, charness-artifacts/debug/2026-07-19-cumulative-closeout-staged-scope-coupling.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/codex_session_audit_lib.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/skill_efficiency_report.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/codex_session_audit_lib.py, scripts/critique_packet_lib.py, scripts/critique_reviewed_input_binding.py, scripts/public_skill_dogfood_lib.py, scripts/reviewed_input_identity.py, scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/run_slice_closeout.py, scripts/skill_efficiency_report.py, scripts/staged_commit_gate_plan.py, scripts/validate_critique_artifacts.py, tests/charness_cli/fixtures/fake_codex.py, tests/charness_cli/test_codex_cache_refresh.py, tests/quality_gates/test_release_distinct_channel.py, tests/quality_gates/test_release_observer.py, tests/quality_gates/test_retro_codex_session_audit.py, tests/quality_gates/test_run_slice_closeout_surface_obligations.py, tests/test_critique_prepare_packet.py, tests/test_critique_scaffold.py, tests/test_reviewed_input_identity_failures.py, tests/test_skill_efficiency_ab.py, tests/test_skill_efficiency_comparability.py
  derived matches: plugins/charness/scripts/codex_session_audit_lib.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/skill_efficiency_report.py, plugins/charness/scripts/staged_commit_gate_plan.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/codex_session_audit_lib.py, scripts/critique_packet_lib.py, scripts/critique_reviewed_input_binding.py, scripts/public_skill_dogfood_lib.py, scripts/reviewed_input_identity.py, scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/run_slice_closeout.py, scripts/skill_efficiency_report.py, scripts/staged_commit_gate_plan.py, scripts/validate_critique_artifacts.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_observer.py, skills/public/release/scripts/resolve_adapter.py, skills/public/retro/scripts/prepare_packet.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
```
