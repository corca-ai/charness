# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-18T20:52:35Z
- **Prepared for**: v2.1.6 release candidate after duplicate-gate repair
- **Changed ref**: `dcc4595f..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `2cbf148b01a7960d5d4f8d24baed0d8fcad485841b4b95ce18a0870b5fabe2b6`
- **Reviewed paths**: 69
- **Sections**: 2
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
Changed paths for ref `dcc4595f..HEAD`:
- .agents/surfaces.json
- charness-artifacts/critique/2026-07-18-185648-packet.json
- charness-artifacts/critique/2026-07-18-185648-packet.md
- charness-artifacts/critique/2026-07-19-critique-review.md
- charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md
- charness-artifacts/critique/v2-1-6-release-candidate-packet.json
- charness-artifacts/critique/v2-1-6-release-candidate-packet.md
- charness-artifacts/debug/2026-07-19-release-issue-close-evidence-ordering.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/quality/2026-07-19-quality-review.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/release/2026-07-19-v2.1.6-notes.md
- charness-artifacts/retro/2026-07-19-session-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-07-19-release-close-evidence-ordering.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/boundary-bypass-exemptions.txt
- plugins/charness/skills/release/references/publication-boundary.md
- plugins/charness/skills/release/references/real-host-proof.md
- plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py
- plugins/charness/skills/release/scripts/check_real_host_proof.py
- plugins/charness/skills/release/scripts/check_requested_review_gate.py
- plugins/charness/skills/release/scripts/plan_release_run.py
- plugins/charness/skills/release/scripts/plan_release_run_packets.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- plugins/charness/skills/release/scripts/publish_release_execute.py
- plugins/charness/skills/release/scripts/publish_release_helpers.py
- plugins/charness/skills/release/scripts/publish_release_resume.py
- plugins/charness/skills/release/scripts/publish_release_resume_closeout.py
- plugins/charness/skills/release/scripts/publish_release_runtime.py
- plugins/charness/skills/release/scripts/release_delta.py
- plugins/charness/skills/release/scripts/release_issue_closeout.py
- plugins/charness/skills/release/scripts/release_issue_closeout_artifact.py
- plugins/charness/skills/release/scripts/release_issue_closeout_message.py
- scripts/boundary-bypass-exemptions.txt
- skills/public/release/references/publication-boundary.md
- skills/public/release/references/real-host-proof.md
- skills/public/release/scripts/check_fresh_checkout_probes.py
- skills/public/release/scripts/check_real_host_proof.py
- skills/public/release/scripts/check_requested_review_gate.py
- skills/public/release/scripts/plan_release_run.py
- skills/public/release/scripts/plan_release_run_packets.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_execute.py
- skills/public/release/scripts/publish_release_helpers.py
- skills/public/release/scripts/publish_release_resume.py
- skills/public/release/scripts/publish_release_resume_closeout.py
- skills/public/release/scripts/publish_release_runtime.py
- skills/public/release/scripts/release_delta.py
- skills/public/release/scripts/release_issue_closeout.py
- skills/public/release/scripts/release_issue_closeout_artifact.py
- skills/public/release/scripts/release_issue_closeout_message.py
- tests/quality_gates/fixtures/release_publish_fake_gh.py
- tests/quality_gates/fixtures/release_publish_fake_git.py
- tests/quality_gates/test_public_skill_yaml_output_contract.py
- tests/quality_gates/test_release_distinct_channel.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_release_publish_real_host_delta.py
- tests/quality_gates/test_release_publish_resilience.py
- tests/quality_gates/test_release_real_host.py
- tests/quality_gates/test_release_resume_edge_coverage.py
- tests/quality_gates/test_release_resume_state_validation.py
- tests/quality_gates/test_release_run_planner.py
- tests/quality_gates/test_staged_commit_gate_plan.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/boundary-bypass-exemptions.txt, skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_real_host_proof.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/plan_release_run.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/release_delta.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_issue_closeout_artifact.py, skills/public/release/scripts/release_issue_closeout_message.py
  derived matches: plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/skills/release/references/publication-boundary.md, plugins/charness/skills/release/references/real-host-proof.md, plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py, plugins/charness/skills/release/scripts/check_real_host_proof.py, plugins/charness/skills/release/scripts/check_requested_review_gate.py, plugins/charness/skills/release/scripts/plan_release_run.py, plugins/charness/skills/release/scripts/plan_release_run_packets.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_execute.py, plugins/charness/skills/release/scripts/publish_release_helpers.py, plugins/charness/skills/release/scripts/publish_release_resume.py, plugins/charness/skills/release/scripts/publish_release_resume_closeout.py, plugins/charness/skills/release/scripts/publish_release_runtime.py, plugins/charness/skills/release/scripts/release_delta.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/release/scripts/release_issue_closeout_artifact.py, plugins/charness/skills/release/scripts/release_issue_closeout_message.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-18-185648-packet.md, charness-artifacts/critique/2026-07-19-critique-review.md, charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md, charness-artifacts/critique/v2-1-6-release-candidate-packet.md, charness-artifacts/debug/2026-07-19-release-issue-close-evidence-ordering.md, charness-artifacts/debug/latest.md, charness-artifacts/quality/2026-07-19-quality-review.md, charness-artifacts/quality/latest.md, charness-artifacts/release/2026-07-19-v2.1.6-notes.md, charness-artifacts/retro/2026-07-19-session-retro.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-07-19-release-close-evidence-ordering.md, docs/handoff.md, skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md
  derived matches: plugins/charness/skills/release/references/publication-boundary.md, plugins/charness/skills/release/references/real-host-proof.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json >/dev/null
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_real_host_proof.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/plan_release_run.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/release_delta.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_issue_closeout_artifact.py, skills/public/release/scripts/release_issue_closeout_message.py
  derived matches: plugins/charness/skills/release/references/publication-boundary.md, plugins/charness/skills/release/references/real-host-proof.md, plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py, plugins/charness/skills/release/scripts/check_real_host_proof.py, plugins/charness/skills/release/scripts/check_requested_review_gate.py, plugins/charness/skills/release/scripts/plan_release_run.py, plugins/charness/skills/release/scripts/plan_release_run_packets.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_execute.py, plugins/charness/skills/release/scripts/publish_release_helpers.py, plugins/charness/skills/release/scripts/publish_release_resume.py, plugins/charness/skills/release/scripts/publish_release_resume_closeout.py, plugins/charness/skills/release/scripts/publish_release_runtime.py, plugins/charness/skills/release/scripts/release_delta.py, plugins/charness/skills/release/scripts/release_issue_closeout.py, plugins/charness/skills/release/scripts/release_issue_closeout_artifact.py, plugins/charness/skills/release/scripts/release_issue_closeout_message.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_real_host_proof.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/plan_release_run.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/release_delta.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_issue_closeout_artifact.py, skills/public/release/scripts/release_issue_closeout_message.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/release/references/publication-boundary.md, skills/public/release/references/real-host-proof.md, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_real_host_proof.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/plan_release_run.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/release_delta.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_issue_closeout_artifact.py, skills/public/release/scripts/release_issue_closeout_message.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-18-185648-packet.json, charness-artifacts/critique/2026-07-18-185648-packet.md, charness-artifacts/critique/2026-07-19-critique-review.md, charness-artifacts/critique/2026-07-19-v2-1-6-release-critique.md, charness-artifacts/critique/v2-1-6-release-candidate-packet.json, charness-artifacts/critique/v2-1-6-release-candidate-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-19-release-issue-close-evidence-ordering.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-19-session-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/boundary-bypass-exemptions.txt
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/fixtures/release_publish_fake_gh.py, tests/quality_gates/fixtures/release_publish_fake_git.py, tests/quality_gates/test_public_skill_yaml_output_contract.py, tests/quality_gates/test_release_distinct_channel.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_release_publish_real_host_delta.py, tests/quality_gates/test_release_publish_resilience.py, tests/quality_gates/test_release_real_host.py, tests/quality_gates/test_release_resume_edge_coverage.py, tests/quality_gates/test_release_resume_state_validation.py, tests/quality_gates/test_release_run_planner.py, tests/quality_gates/test_staged_commit_gate_plan.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/check_real_host_proof.py, skills/public/release/scripts/check_requested_review_gate.py, skills/public/release/scripts/plan_release_run.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_execute.py, skills/public/release/scripts/publish_release_helpers.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_runtime.py, skills/public/release/scripts/release_delta.py, skills/public/release/scripts/release_issue_closeout.py, skills/public/release/scripts/release_issue_closeout_artifact.py, skills/public/release/scripts/release_issue_closeout_message.py
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
