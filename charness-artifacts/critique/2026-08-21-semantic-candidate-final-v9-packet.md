# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-20T18:40:43Z
- **Prepared for**: semantic candidate final v9 fixed candidate endpoint
- **Changed ref**: `38775dfeb8d1e5574663d7ef461d19a63e252841..19e62aea829e4d40b1ede2d1e2273ea067963dd1`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `06d40fe77d56d483fb73ad1caadb156a769d2807fc2fb5d3048530fc697291bb`
- **Reviewed paths**: 218
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
Changed paths for ref `38775dfeb8d1e5574663d7ef461d19a63e252841..19e62aea829e4d40b1ede2d1e2273ea067963dd1`:
- .agents/surfaces.json
- charness-artifacts/critique/2026-08-20-142117-packet.json
- charness-artifacts/critique/2026-08-20-142117-packet.md
- charness-artifacts/critique/2026-08-20-broad-release-goal-packet.json
- charness-artifacts/critique/2026-08-20-broad-release-goal-packet.md
- charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-packet.json
- charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-packet.md
- charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-r2-packet.json
- charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-r2-packet.md
- charness-artifacts/critique/2026-08-20-release-handoff-packet.json
- charness-artifacts/critique/2026-08-20-release-handoff-packet.md
- charness-artifacts/critique/2026-08-21-semantic-candidate-packet.json
- charness-artifacts/critique/2026-08-21-semantic-candidate-packet.md
- charness-artifacts/critique/2026-08-21-semantic-candidate-release-critique.md
- charness-artifacts/critique/command-plans/2026-08-21-goal-fanout.json
- charness-artifacts/critique/findings/2026-08-20-s3-r2-code.txt
- charness-artifacts/critique/findings/2026-08-20-s3-r2-consumer.txt
- charness-artifacts/critique/findings/2026-08-20-s3-r2-goal.txt
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-code-logic.md
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-consumer-export.md
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-goal-claims.md
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-code.md
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-consumer.md
- charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-goal.md
- charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan-repair.md
- charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan.md
- charness-artifacts/critique/rounds/2026-08-21-2026-08-21-goal-codex-review.md
- charness-artifacts/critique/snapshots/2026-08-20-s3-code-logic.json
- charness-artifacts/critique/snapshots/2026-08-20-s3-consumer-export.json
- charness-artifacts/critique/snapshots/2026-08-20-s3-goal-claims.json
- charness-artifacts/critique/snapshots/2026-08-20-s3-r2-code.json
- charness-artifacts/critique/snapshots/2026-08-20-s3-r2-consumer.json
- charness-artifacts/critique/snapshots/2026-08-20-s3-r2-goal.json
- charness-artifacts/critique/snapshots/2026-08-21-command-plan-repair.json
- charness-artifacts/critique/snapshots/2026-08-21-command-plan.json
- charness-artifacts/critique/snapshots/2026-08-21-goal-codex-review.json
- charness-artifacts/debug/2026-08-20-debug-review.md
- charness-artifacts/debug/2026-08-20-fresh-checkout-probe-timeout.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md
- charness-artifacts/issues/2026-08-20-612-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-612-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-634-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-634-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-635-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-635-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-637-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-637-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-638-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-638-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-639-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-639-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-668-reproduction.meta.yaml
- charness-artifacts/issues/2026-08-20-668-reproduction.raw.yaml
- charness-artifacts/issues/2026-08-20-669a-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-669a-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-669b-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-669b-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-670-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-670-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-671-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-671-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-672-fallback-split.txt
- charness-artifacts/issues/2026-08-20-672-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-672-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-676-repair-parity-split.txt
- charness-artifacts/issues/2026-08-20-676-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-676-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-677-consumer-gap.txt
- charness-artifacts/issues/2026-08-20-677-consumer-proof.txt
- charness-artifacts/issues/2026-08-20-677-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-677-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-678-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-678-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-678-usage-classifier-split.txt
- charness-artifacts/issues/2026-08-20-679-reproduction.txt
- charness-artifacts/issues/2026-08-20-681-reproduction.meta.txt
- charness-artifacts/issues/2026-08-20-681-reproduction.raw.txt
- charness-artifacts/issues/2026-08-20-issue-plan.meta.txt
- charness-artifacts/issues/2026-08-20-issue-plan.raw.txt
- charness-artifacts/issues/2026-08-20-next-release-ledger.json
- charness-artifacts/issues/2026-08-20-open-issues.meta.txt
- charness-artifacts/issues/2026-08-20-open-issues.raw.json
- charness-artifacts/issues/reads/527.meta.txt
- charness-artifacts/issues/reads/527.raw.yaml
- charness-artifacts/issues/reads/546.meta.txt
- charness-artifacts/issues/reads/546.raw.yaml
- charness-artifacts/issues/reads/550.meta.txt
- charness-artifacts/issues/reads/550.raw.yaml
- charness-artifacts/issues/reads/582.meta.txt
- charness-artifacts/issues/reads/582.raw.yaml
- charness-artifacts/issues/reads/583.meta.txt
- charness-artifacts/issues/reads/583.raw.yaml
- charness-artifacts/issues/reads/584.meta.txt
- charness-artifacts/issues/reads/584.raw.yaml
- charness-artifacts/issues/reads/586.meta.txt
- charness-artifacts/issues/reads/586.raw.yaml
- charness-artifacts/issues/reads/587.meta.txt
- charness-artifacts/issues/reads/587.raw.yaml
- charness-artifacts/issues/reads/599.meta.txt
- charness-artifacts/issues/reads/599.raw.yaml
- charness-artifacts/issues/reads/601.meta.txt
- charness-artifacts/issues/reads/601.raw.yaml
- charness-artifacts/issues/reads/605.meta.txt
- charness-artifacts/issues/reads/605.raw.yaml
- charness-artifacts/issues/reads/612.meta.txt
- charness-artifacts/issues/reads/612.raw.yaml
- charness-artifacts/issues/reads/628.meta.txt
- charness-artifacts/issues/reads/628.raw.yaml
- charness-artifacts/issues/reads/634.meta.txt
- charness-artifacts/issues/reads/634.raw.yaml
- charness-artifacts/issues/reads/635.meta.txt
- charness-artifacts/issues/reads/635.raw.yaml
- charness-artifacts/issues/reads/637.meta.txt
- charness-artifacts/issues/reads/637.raw.yaml
- charness-artifacts/issues/reads/638.meta.txt
- charness-artifacts/issues/reads/638.raw.yaml
- charness-artifacts/issues/reads/639.meta.txt
- charness-artifacts/issues/reads/639.raw.yaml
- charness-artifacts/issues/reads/667.meta.txt
- charness-artifacts/issues/reads/667.raw.yaml
- charness-artifacts/issues/reads/668.meta.txt
- charness-artifacts/issues/reads/668.raw.yaml
- charness-artifacts/issues/reads/669.meta.txt
- charness-artifacts/issues/reads/669.raw.yaml
- charness-artifacts/issues/reads/670.meta.txt
- charness-artifacts/issues/reads/670.raw.yaml
- charness-artifacts/issues/reads/671.meta.txt
- charness-artifacts/issues/reads/671.raw.yaml
- charness-artifacts/issues/reads/672.meta.txt
- charness-artifacts/issues/reads/672.raw.yaml
- charness-artifacts/issues/reads/676.meta.txt
- charness-artifacts/issues/reads/676.raw.yaml
- charness-artifacts/issues/reads/677.meta.txt
- charness-artifacts/issues/reads/677.raw.yaml
- charness-artifacts/issues/reads/678.meta.txt
- charness-artifacts/issues/reads/678.raw.yaml
- charness-artifacts/issues/reads/679.meta.txt
- charness-artifacts/issues/reads/679.raw.yaml
- charness-artifacts/issues/reads/680.meta.txt
- charness-artifacts/issues/reads/680.raw.yaml
- charness-artifacts/issues/reads/681.meta.txt
- charness-artifacts/issues/reads/681.raw.yaml
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/quality/2026-08-20-slice-0-quality-planner.meta.txt
- charness-artifacts/quality/2026-08-20-slice-0-quality-planner.raw.yaml
- charness-artifacts/quality/2026-08-21-command-plan-broad-quality-proof.md
- charness-artifacts/quality/2026-08-21-command-plan-changed-line-proof.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/release/2026-08-20-slice-0-release-planner.meta.txt
- charness-artifacts/release/2026-08-20-slice-0-release-planner.raw.yaml
- charness-artifacts/retro/2026-08-20-093708-packet.json
- charness-artifacts/retro/2026-08-20-093708-packet.md
- charness-artifacts/retro/2026-08-20-152747-packet.json
- charness-artifacts/retro/2026-08-20-152747-packet.md
- charness-artifacts/retro/2026-08-20-release-goal-shaping.md
- charness-artifacts/retro/2026-08-21-command-plan-preflight-retro.md
- charness-artifacts/retro/2026-08-21-goal-continuation-retro.md
- charness-artifacts/retro/2026-08-21-session-retro.md
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.md
- charness-artifacts/retro/lesson-session-receipts/2026-08-21-goal-codex-review.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-21-goal-codex-review.md
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md
- charness-artifacts/spec/2026-08-20-fresh-checkout-probe-timeout.md
- charness-artifacts/spec/2026-08-20-issue-679-impl-bootstrap-idempotence.md
- docs/conventions/parallel-execution.md
- docs/handoff.md
- plugins/charness/scripts/adapter-consumer-classification.json
- plugins/charness/scripts/adapter_init_lib.py
- plugins/charness/scripts/adapter_key_registry.py
- plugins/charness/scripts/adapter_key_usage.py
- plugins/charness/scripts/check_artifact_citations.py
- plugins/charness/scripts/check_consumer_validator_catalog.py
- plugins/charness/scripts/check_release_issue_ledger.py
- plugins/charness/scripts/command_plan_preflight.py
- plugins/charness/scripts/manage_mutation_reports.py
- plugins/charness/scripts/mutation_sampling_lib.py
- plugins/charness/scripts/release_issue_ledger_contract.py
- plugins/charness/scripts/release_issue_ledger_evidence.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/session_start_lesson_context.py
- plugins/charness/scripts/slice_closeout_advisories.py
- plugins/charness/scripts/slice_closeout_repair_parity.py
- plugins/charness/scripts/what_reads_this.py
- plugins/charness/scripts/what_reads_this_fallback.py
- plugins/charness/skills/achieve/references/lifecycle-during.md
- plugins/charness/skills/achieve/scripts/goal_artifact_lib.py
- plugins/charness/skills/achieve/scripts/goal_artifact_portability_gate.py
- plugins/charness/skills/achieve/scripts/goal_path_portability.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/scripts/record_round_findings.py
- plugins/charness/skills/impl/scripts/init_adapter.py
- plugins/charness/skills/quality/references/consumer-validator-catalog.yaml
- plugins/charness/skills/quality/references/index.md
- plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py
- scripts/adapter-consumer-classification.json
- scripts/adapter_init_lib.py
- scripts/adapter_key_registry.py
- scripts/adapter_key_usage.py
- scripts/check_artifact_citations.py
- scripts/check_consumer_validator_catalog.py
- scripts/check_release_issue_ledger.py
- scripts/command_plan_preflight.py
- scripts/manage_mutation_reports.py
- scripts/mutation_sampling_lib.py
- scripts/release_issue_ledger_contract.py
- scripts/release_issue_ledger_evidence.py
- scripts/run_slice_closeout.py
- scripts/session_start_lesson_context.py
- scripts/slice_closeout_advisories.py
- scripts/slice_closeout_repair_parity.py
- scripts/what_reads_this.py
- scripts/what_reads_this_fallback.py
- skills/public/achieve/references/lifecycle-during.md
- skills/public/achieve/scripts/goal_artifact_lib.py
- skills/public/achieve/scripts/goal_artifact_portability_gate.py
- skills/public/achieve/scripts/goal_path_portability.py
- skills/public/critique/SKILL.md
- skills/public/critique/scripts/record_round_findings.py
- skills/public/impl/scripts/init_adapter.py
- skills/public/quality/references/consumer-validator-catalog.yaml
- skills/public/quality/references/index.md
- skills/public/release/scripts/check_fresh_checkout_probes.py
- tests/coverage_debt/test_batch2.py
- tests/quality_gates/test_adapter_key_registry.py
- tests/quality_gates/test_command_plan_preflight.py
- tests/quality_gates/test_goal_artifact_portability.py
- tests/quality_gates/test_public_skill_yaml_output_contract.py
- tests/quality_gates/test_quality_mutation_coverage.py
- tests/quality_gates/test_release_issue_ledger.py
- tests/quality_gates/test_removed_name_consumers.py
- tests/quality_gates/test_script_inprocess_behaviors.py
- tests/quality_gates/test_slice_closeout_artifact_citations.py
- tests/quality_gates/test_slice_closeout_new_pool_advisory.py
- tests/test_achieve_lesson_citation.py
- tests/test_adapter_key_registry.py
- tests/test_artifact_citations.py
- tests/test_consumer_validator_catalog.py
- tests/test_critique_round_findings.py
- tests/test_goal_path_portability.py
- tests/test_impl_bootstrap.py
- tests/test_session_start_lesson_context.py
- tests/test_slice_closeout_advisories.py
- tests/test_what_reads_this.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/adapter-consumer-classification.json, scripts/adapter_init_lib.py, scripts/adapter_key_registry.py, scripts/adapter_key_usage.py, scripts/check_artifact_citations.py, scripts/check_consumer_validator_catalog.py, scripts/check_release_issue_ledger.py, scripts/command_plan_preflight.py, scripts/manage_mutation_reports.py, scripts/mutation_sampling_lib.py, scripts/release_issue_ledger_contract.py, scripts/release_issue_ledger_evidence.py, scripts/run_slice_closeout.py, scripts/session_start_lesson_context.py, scripts/slice_closeout_advisories.py, scripts/slice_closeout_repair_parity.py, scripts/what_reads_this.py, scripts/what_reads_this_fallback.py, skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_portability_gate.py, skills/public/achieve/scripts/goal_path_portability.py, skills/public/critique/SKILL.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/scripts/init_adapter.py, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/index.md, skills/public/release/scripts/check_fresh_checkout_probes.py
  derived matches: plugins/charness/scripts/adapter-consumer-classification.json, plugins/charness/scripts/adapter_init_lib.py, plugins/charness/scripts/adapter_key_registry.py, plugins/charness/scripts/adapter_key_usage.py, plugins/charness/scripts/check_artifact_citations.py, plugins/charness/scripts/check_consumer_validator_catalog.py, plugins/charness/scripts/check_release_issue_ledger.py, plugins/charness/scripts/command_plan_preflight.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/mutation_sampling_lib.py, plugins/charness/scripts/release_issue_ledger_contract.py, plugins/charness/scripts/release_issue_ledger_evidence.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/session_start_lesson_context.py, plugins/charness/scripts/slice_closeout_advisories.py, plugins/charness/scripts/slice_closeout_repair_parity.py, plugins/charness/scripts/what_reads_this.py, plugins/charness/scripts/what_reads_this_fallback.py, plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/goal_artifact_portability_gate.py, plugins/charness/skills/achieve/scripts/goal_path_portability.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/scripts/record_round_findings.py, plugins/charness/skills/impl/scripts/init_adapter.py, plugins/charness/skills/quality/references/consumer-validator-catalog.yaml, plugins/charness/skills/quality/references/index.md, plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-20-142117-packet.md, charness-artifacts/critique/2026-08-20-broad-release-goal-packet.md, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-packet.md, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-r2-packet.md, charness-artifacts/critique/2026-08-20-release-handoff-packet.md, charness-artifacts/critique/2026-08-21-semantic-candidate-packet.md, charness-artifacts/critique/2026-08-21-semantic-candidate-release-critique.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-code-logic.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-consumer-export.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-goal-claims.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-code.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-consumer.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-goal.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan-repair.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-goal-codex-review.md, charness-artifacts/debug/2026-08-20-debug-review.md, charness-artifacts/debug/2026-08-20-fresh-checkout-probe-timeout.md, charness-artifacts/debug/latest.md, charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md, charness-artifacts/quality/2026-08-21-command-plan-broad-quality-proof.md, charness-artifacts/quality/2026-08-21-command-plan-changed-line-proof.md, charness-artifacts/retro/2026-08-20-093708-packet.md, charness-artifacts/retro/2026-08-20-152747-packet.md, charness-artifacts/retro/2026-08-20-release-goal-shaping.md, charness-artifacts/retro/2026-08-21-command-plan-preflight-retro.md, charness-artifacts/retro/2026-08-21-goal-continuation-retro.md, charness-artifacts/retro/2026-08-21-session-retro.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.md, charness-artifacts/retro/lesson-session-receipts/2026-08-21-goal-codex-review.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md, charness-artifacts/spec/2026-08-20-fresh-checkout-probe-timeout.md, charness-artifacts/spec/2026-08-20-issue-679-impl-bootstrap-idempotence.md, docs/conventions/parallel-execution.md, docs/handoff.md, skills/public/achieve/references/lifecycle-during.md, skills/public/critique/SKILL.md, skills/public/quality/references/index.md
  derived matches: plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/quality/references/index.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, python3 scripts/check_docs_graph.py --repo-root . || { [ "$?" -eq 3 ] && ! command -v awiki >/dev/null; }, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- handoff-machine-readers: docs/handoff.md is a rotating human document that is ALSO a machine-read source: the retro-memory gate requires its recent-lessons reference, and the artifact-surface preflight requires its H2 sections and a References link.
  source matches: docs/handoff.md
  verify: python3 scripts/validate_handoff_artifact.py --repo-root ., python3 -m pytest -q tests/quality_gates/test_retro_memory.py
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --detail >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --detail >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/issues/2026-08-20-612-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-612-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-634-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-634-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-635-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-635-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-637-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-637-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-638-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-638-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-639-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-639-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-668-reproduction.meta.yaml, charness-artifacts/issues/2026-08-20-668-reproduction.raw.yaml, charness-artifacts/issues/2026-08-20-669a-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-669a-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-669b-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-669b-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-670-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-670-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-671-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-671-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-672-fallback-split.txt, charness-artifacts/issues/2026-08-20-672-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-672-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-676-repair-parity-split.txt, charness-artifacts/issues/2026-08-20-676-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-676-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-677-consumer-gap.txt, charness-artifacts/issues/2026-08-20-677-consumer-proof.txt, charness-artifacts/issues/2026-08-20-677-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-677-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-678-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-678-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-678-usage-classifier-split.txt, charness-artifacts/issues/2026-08-20-679-reproduction.txt, charness-artifacts/issues/2026-08-20-681-reproduction.meta.txt, charness-artifacts/issues/2026-08-20-681-reproduction.raw.txt, charness-artifacts/issues/2026-08-20-issue-plan.meta.txt, charness-artifacts/issues/2026-08-20-issue-plan.raw.txt, charness-artifacts/issues/2026-08-20-next-release-ledger.json, charness-artifacts/issues/2026-08-20-open-issues.meta.txt, charness-artifacts/issues/2026-08-20-open-issues.raw.json, charness-artifacts/issues/reads/527.meta.txt, charness-artifacts/issues/reads/527.raw.yaml, charness-artifacts/issues/reads/546.meta.txt, charness-artifacts/issues/reads/546.raw.yaml, charness-artifacts/issues/reads/550.meta.txt, charness-artifacts/issues/reads/550.raw.yaml, charness-artifacts/issues/reads/582.meta.txt, charness-artifacts/issues/reads/582.raw.yaml, charness-artifacts/issues/reads/583.meta.txt, charness-artifacts/issues/reads/583.raw.yaml, charness-artifacts/issues/reads/584.meta.txt, charness-artifacts/issues/reads/584.raw.yaml, charness-artifacts/issues/reads/586.meta.txt, charness-artifacts/issues/reads/586.raw.yaml, charness-artifacts/issues/reads/587.meta.txt, charness-artifacts/issues/reads/587.raw.yaml, charness-artifacts/issues/reads/599.meta.txt, charness-artifacts/issues/reads/599.raw.yaml, charness-artifacts/issues/reads/601.meta.txt, charness-artifacts/issues/reads/601.raw.yaml, charness-artifacts/issues/reads/605.meta.txt, charness-artifacts/issues/reads/605.raw.yaml, charness-artifacts/issues/reads/612.meta.txt, charness-artifacts/issues/reads/612.raw.yaml, charness-artifacts/issues/reads/628.meta.txt, charness-artifacts/issues/reads/628.raw.yaml, charness-artifacts/issues/reads/634.meta.txt, charness-artifacts/issues/reads/634.raw.yaml, charness-artifacts/issues/reads/635.meta.txt, charness-artifacts/issues/reads/635.raw.yaml, charness-artifacts/issues/reads/637.meta.txt, charness-artifacts/issues/reads/637.raw.yaml, charness-artifacts/issues/reads/638.meta.txt, charness-artifacts/issues/reads/638.raw.yaml, charness-artifacts/issues/reads/639.meta.txt, charness-artifacts/issues/reads/639.raw.yaml, charness-artifacts/issues/reads/667.meta.txt, charness-artifacts/issues/reads/667.raw.yaml, charness-artifacts/issues/reads/668.meta.txt, charness-artifacts/issues/reads/668.raw.yaml, charness-artifacts/issues/reads/669.meta.txt, charness-artifacts/issues/reads/669.raw.yaml, charness-artifacts/issues/reads/670.meta.txt, charness-artifacts/issues/reads/670.raw.yaml, charness-artifacts/issues/reads/671.meta.txt, charness-artifacts/issues/reads/671.raw.yaml, charness-artifacts/issues/reads/672.meta.txt, charness-artifacts/issues/reads/672.raw.yaml, charness-artifacts/issues/reads/676.meta.txt, charness-artifacts/issues/reads/676.raw.yaml, charness-artifacts/issues/reads/677.meta.txt, charness-artifacts/issues/reads/677.raw.yaml, charness-artifacts/issues/reads/678.meta.txt, charness-artifacts/issues/reads/678.raw.yaml, charness-artifacts/issues/reads/679.meta.txt, charness-artifacts/issues/reads/679.raw.yaml, charness-artifacts/issues/reads/680.meta.txt, charness-artifacts/issues/reads/680.raw.yaml, charness-artifacts/issues/reads/681.meta.txt, charness-artifacts/issues/reads/681.raw.yaml, charness-artifacts/quality/2026-08-20-slice-0-quality-planner.meta.txt, charness-artifacts/quality/2026-08-20-slice-0-quality-planner.raw.yaml, charness-artifacts/quality/2026-08-21-command-plan-broad-quality-proof.md, charness-artifacts/quality/2026-08-21-command-plan-changed-line-proof.md, charness-artifacts/quality/dup-review.json, charness-artifacts/release/2026-08-20-slice-0-release-planner.meta.txt, charness-artifacts/release/2026-08-20-slice-0-release-planner.raw.yaml
  verify: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/validate_quality_artifact.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/achieve/references/lifecycle-during.md, skills/public/critique/SKILL.md, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/index.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_portability_gate.py, skills/public/achieve/scripts/goal_path_portability.py, skills/public/critique/SKILL.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/scripts/init_adapter.py, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/index.md, skills/public/release/scripts/check_fresh_checkout_probes.py
  derived matches: plugins/charness/skills/achieve/references/lifecycle-during.md, plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/goal_artifact_portability_gate.py, plugins/charness/skills/achieve/scripts/goal_path_portability.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/scripts/record_round_findings.py, plugins/charness/skills/impl/scripts/init_adapter.py, plugins/charness/skills/quality/references/consumer-validator-catalog.yaml, plugins/charness/skills/quality/references/index.md, plugins/charness/skills/release/scripts/check_fresh_checkout_probes.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_portability_gate.py, skills/public/achieve/scripts/goal_path_portability.py, skills/public/critique/SKILL.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/scripts/init_adapter.py, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/index.md, skills/public/release/scripts/check_fresh_checkout_probes.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/achieve/references/lifecycle-during.md, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_portability_gate.py, skills/public/achieve/scripts/goal_path_portability.py, skills/public/critique/SKILL.md, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/scripts/init_adapter.py, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/index.md, skills/public/release/scripts/check_fresh_checkout_probes.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: scripts/adapter_init_lib.py
  verify: python3 scripts/validate_adapters.py --repo-root .
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: scripts/mutation_sampling_lib.py
  derived matches: plugins/charness/scripts/mutation_sampling_lib.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 -m pytest -q tests/quality_gates/test_coverage_builder_policy_parity.py, python3 scripts/check_github_actions.py --repo-root ., python3 scripts/validate_adapters.py --repo-root ., python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-20-142117-packet.json, charness-artifacts/critique/2026-08-20-142117-packet.md, charness-artifacts/critique/2026-08-20-broad-release-goal-packet.json, charness-artifacts/critique/2026-08-20-broad-release-goal-packet.md, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-packet.json, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-packet.md, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-r2-packet.json, charness-artifacts/critique/2026-08-20-release-goal-execution-readiness-r2-packet.md, charness-artifacts/critique/2026-08-20-release-handoff-packet.json, charness-artifacts/critique/2026-08-20-release-handoff-packet.md, charness-artifacts/critique/2026-08-21-semantic-candidate-packet.json, charness-artifacts/critique/2026-08-21-semantic-candidate-packet.md, charness-artifacts/critique/2026-08-21-semantic-candidate-release-critique.md, charness-artifacts/critique/command-plans/2026-08-21-goal-fanout.json, charness-artifacts/critique/findings/2026-08-20-s3-r2-code.txt, charness-artifacts/critique/findings/2026-08-20-s3-r2-consumer.txt, charness-artifacts/critique/findings/2026-08-20-s3-r2-goal.txt, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-code-logic.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-consumer-export.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-goal-claims.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-code.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-consumer.md, charness-artifacts/critique/rounds/2026-08-20-w-20260820-s3-r2-goal.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan-repair.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-command-plan.md, charness-artifacts/critique/rounds/2026-08-21-2026-08-21-goal-codex-review.md, charness-artifacts/critique/snapshots/2026-08-20-s3-code-logic.json, charness-artifacts/critique/snapshots/2026-08-20-s3-consumer-export.json, charness-artifacts/critique/snapshots/2026-08-20-s3-goal-claims.json, charness-artifacts/critique/snapshots/2026-08-20-s3-r2-code.json, charness-artifacts/critique/snapshots/2026-08-20-s3-r2-consumer.json, charness-artifacts/critique/snapshots/2026-08-20-s3-r2-goal.json, charness-artifacts/critique/snapshots/2026-08-21-command-plan-repair.json, charness-artifacts/critique/snapshots/2026-08-21-command-plan.json, charness-artifacts/critique/snapshots/2026-08-21-goal-codex-review.json
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-20-debug-review.md, charness-artifacts/debug/2026-08-20-fresh-checkout-probe-timeout.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-20-093708-packet.json, charness-artifacts/retro/2026-08-20-093708-packet.md, charness-artifacts/retro/2026-08-20-152747-packet.json, charness-artifacts/retro/2026-08-20-152747-packet.md, charness-artifacts/retro/2026-08-20-release-goal-shaping.md, charness-artifacts/retro/2026-08-21-command-plan-preflight-retro.md, charness-artifacts/retro/2026-08-21-goal-continuation-retro.md, charness-artifacts/retro/2026-08-21-session-retro.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234.md, charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.md, charness-artifacts/retro/lesson-session-receipts/2026-08-21-goal-codex-review.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e68-fafb-7fc1-b27c-51a1bc88014b.json, charness-artifacts/retro/lesson-session-receipts/2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234.json, charness-artifacts/retro/lesson-session-receipts/2026-08-20-goal-continuation.json, charness-artifacts/retro/lesson-session-receipts/2026-08-21-goal-codex-review.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/adapter-consumer-classification.json, plugins/charness/scripts/adapter_init_lib.py, plugins/charness/scripts/adapter_key_registry.py, plugins/charness/scripts/adapter_key_usage.py, plugins/charness/scripts/check_artifact_citations.py, plugins/charness/scripts/check_consumer_validator_catalog.py, plugins/charness/scripts/check_release_issue_ledger.py, plugins/charness/scripts/command_plan_preflight.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/mutation_sampling_lib.py, plugins/charness/scripts/release_issue_ledger_contract.py, plugins/charness/scripts/release_issue_ledger_evidence.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/session_start_lesson_context.py, plugins/charness/scripts/slice_closeout_advisories.py, plugins/charness/scripts/slice_closeout_repair_parity.py, plugins/charness/scripts/what_reads_this.py, plugins/charness/scripts/what_reads_this_fallback.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/adapter_init_lib.py, scripts/adapter_key_registry.py, scripts/adapter_key_usage.py, scripts/check_artifact_citations.py, scripts/check_consumer_validator_catalog.py, scripts/check_release_issue_ledger.py, scripts/command_plan_preflight.py, scripts/manage_mutation_reports.py, scripts/mutation_sampling_lib.py, scripts/release_issue_ledger_contract.py, scripts/release_issue_ledger_evidence.py, scripts/run_slice_closeout.py, scripts/session_start_lesson_context.py, scripts/slice_closeout_advisories.py, scripts/slice_closeout_repair_parity.py, scripts/what_reads_this.py, scripts/what_reads_this_fallback.py, tests/coverage_debt/test_batch2.py, tests/quality_gates/test_adapter_key_registry.py, tests/quality_gates/test_command_plan_preflight.py, tests/quality_gates/test_goal_artifact_portability.py, tests/quality_gates/test_public_skill_yaml_output_contract.py, tests/quality_gates/test_quality_mutation_coverage.py, tests/quality_gates/test_release_issue_ledger.py, tests/quality_gates/test_removed_name_consumers.py, tests/quality_gates/test_script_inprocess_behaviors.py, tests/quality_gates/test_slice_closeout_artifact_citations.py, tests/quality_gates/test_slice_closeout_new_pool_advisory.py, tests/test_achieve_lesson_citation.py, tests/test_adapter_key_registry.py, tests/test_artifact_citations.py, tests/test_consumer_validator_catalog.py, tests/test_critique_round_findings.py, tests/test_goal_path_portability.py, tests/test_impl_bootstrap.py, tests/test_session_start_lesson_context.py, tests/test_slice_closeout_advisories.py, tests/test_what_reads_this.py
  derived matches: plugins/charness/scripts/adapter_init_lib.py, plugins/charness/scripts/adapter_key_registry.py, plugins/charness/scripts/adapter_key_usage.py, plugins/charness/scripts/check_artifact_citations.py, plugins/charness/scripts/check_consumer_validator_catalog.py, plugins/charness/scripts/check_release_issue_ledger.py, plugins/charness/scripts/command_plan_preflight.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/mutation_sampling_lib.py, plugins/charness/scripts/release_issue_ledger_contract.py, plugins/charness/scripts/release_issue_ledger_evidence.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/session_start_lesson_context.py, plugins/charness/scripts/slice_closeout_advisories.py, plugins/charness/scripts/slice_closeout_repair_parity.py, plugins/charness/scripts/what_reads_this.py, plugins/charness/scripts/what_reads_this_fallback.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/adapter_init_lib.py, scripts/adapter_key_registry.py, scripts/adapter_key_usage.py, scripts/check_artifact_citations.py, scripts/check_consumer_validator_catalog.py, scripts/check_release_issue_ledger.py, scripts/command_plan_preflight.py, scripts/manage_mutation_reports.py, scripts/mutation_sampling_lib.py, scripts/release_issue_ledger_contract.py, scripts/release_issue_ledger_evidence.py, scripts/run_slice_closeout.py, scripts/session_start_lesson_context.py, scripts/slice_closeout_advisories.py, scripts/slice_closeout_repair_parity.py, scripts/what_reads_this.py, scripts/what_reads_this_fallback.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_portability_gate.py, skills/public/achieve/scripts/goal_path_portability.py, skills/public/critique/scripts/record_round_findings.py, skills/public/impl/scripts/init_adapter.py, skills/public/release/scripts/check_fresh_checkout_probes.py
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
