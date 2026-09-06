# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-09-06T01:13:36Z
- **Prepared for**: Goal 798 consumer improvement session
- **Substrate mode**: `committed-ref`
- **Changed ref**: `be60aba4b62bfbb9a8bc385227b9db9fa0581c23..44cd33060026fe4fe603632df1ef24677913fcda`
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
Changed paths for ref `be60aba4b62bfbb9a8bc385227b9db9fa0581c23..44cd33060026fe4fe603632df1ef24677913fcda`:
- charness
- charness-artifacts/create-skill/2026-09-06-impl-evidence-reuse.md
- charness-artifacts/critique/consumer-plan-framing-packet.json
- charness-artifacts/critique/consumer-plan-framing-packet.md
- charness-artifacts/critique/consumer-plan-proof-packet.json
- charness-artifacts/critique/consumer-plan-proof-packet.md
- charness-artifacts/critique/consumer-plan-whole-packet.json
- charness-artifacts/critique/consumer-plan-whole-packet.md
- charness-artifacts/critique/goal798-code-contracts-packet.json
- charness-artifacts/critique/goal798-code-contracts-packet.md
- charness-artifacts/critique/goal798-consumer-oracle-packet.json
- charness-artifacts/critique/goal798-consumer-oracle-packet.md
- charness-artifacts/critique/goal798-consumer-oracle-r2-packet.json
- charness-artifacts/critique/goal798-consumer-oracle-r2-packet.md
- charness-artifacts/critique/goal798-consumer-oracle-r3-packet.json
- charness-artifacts/critique/goal798-consumer-oracle-r3-packet.md
- charness-artifacts/critique/goal798-final-owner-review-packet.json
- charness-artifacts/critique/goal798-final-owner-review-packet.md
- charness-artifacts/critique/workers/consumer-plan-framing-live/worker-report.yaml
- charness-artifacts/critique/workers/consumer-plan-whole/worker-report.yaml
- charness-artifacts/critique/workers/goal798-code-contracts/worker-report.yaml
- charness-artifacts/critique/workers/goal798-consumer-oracle-r3/worker-report.yaml
- charness-artifacts/critique/workers/goal798-final-owner-review/worker-report.yaml
- charness-artifacts/debug/2026-09-06-critique-preview-live-collision.md
- charness-artifacts/debug/2026-09-06-release-advisory-meaning.md
- charness-artifacts/debug/2026-09-06-staged-owner-universe.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goal-runs/798/bodies/parent-bootstrap.md
- charness-artifacts/goal-runs/798/bodies/parent-progress-1.md
- charness-artifacts/goal-runs/798/bodies/parent-progress-2.md
- charness-artifacts/goal-runs/798/consumer-lineage.json
- charness-artifacts/goal-runs/798/expected-children.json
- charness-artifacts/goal-runs/798/observations/798-add-cli-journey.started.json
- charness-artifacts/goal-runs/798/observations/798-add-cli-journey.terminal.json
- charness-artifacts/goal-runs/798/observations/798-add-contract-ownership.started.json
- charness-artifacts/goal-runs/798/observations/798-add-contract-ownership.terminal.json
- charness-artifacts/goal-runs/798/observations/798-add-evidence-meaning.started.json
- charness-artifacts/goal-runs/798/observations/798-add-evidence-meaning.terminal.json
- charness-artifacts/goal-runs/798/observations/798-add-friction-reduction.started.json
- charness-artifacts/goal-runs/798/observations/798-add-friction-reduction.terminal.json
- charness-artifacts/goal-runs/798/observations/798-add-publish-closeout.started.json
- charness-artifacts/goal-runs/798/observations/798-add-publish-closeout.terminal.json
- charness-artifacts/goal-runs/798/observations/798-add-spec-impl-journey.started.json
- charness-artifacts/goal-runs/798/observations/798-add-spec-impl-journey.terminal.json
- charness-artifacts/goal-runs/798/observations/798-bootstrap-metadata.started.json
- charness-artifacts/goal-runs/798/observations/798-bootstrap-metadata.terminal.json
- charness-artifacts/goal-runs/798/observations/798-consumer-frontier.started.json
- charness-artifacts/goal-runs/798/observations/798-consumer-frontier.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-cli-journey.started.json
- charness-artifacts/goal-runs/798/observations/798-create-cli-journey.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-contract-ownership.started.json
- charness-artifacts/goal-runs/798/observations/798-create-contract-ownership.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-evidence-meaning.started.json
- charness-artifacts/goal-runs/798/observations/798-create-evidence-meaning.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-friction-reduction.started.json
- charness-artifacts/goal-runs/798/observations/798-create-friction-reduction.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-publish-closeout.started.json
- charness-artifacts/goal-runs/798/observations/798-create-publish-closeout.terminal.json
- charness-artifacts/goal-runs/798/observations/798-create-spec-impl-journey.started.json
- charness-artifacts/goal-runs/798/observations/798-create-spec-impl-journey.terminal.json
- charness-artifacts/goal-runs/798/observations/798-install-progress.started.json
- charness-artifacts/goal-runs/798/observations/798-install-progress.terminal.json
- charness-artifacts/goal-runs/798/observations/798-verify-initial-graph.started.json
- charness-artifacts/goal-runs/798/observations/798-verify-initial-graph.terminal.json
- charness-artifacts/goal-runs/798/operations/add-cli-journey.json
- charness-artifacts/goal-runs/798/operations/add-contract-ownership.json
- charness-artifacts/goal-runs/798/operations/add-evidence-meaning.json
- charness-artifacts/goal-runs/798/operations/add-friction-reduction.json
- charness-artifacts/goal-runs/798/operations/add-publish-closeout.json
- charness-artifacts/goal-runs/798/operations/add-spec-impl-journey.json
- charness-artifacts/goal-runs/798/operations/bootstrap-metadata.json
- charness-artifacts/goal-runs/798/operations/consumer-frontier.json
- charness-artifacts/goal-runs/798/operations/create-cli-journey.json
- charness-artifacts/goal-runs/798/operations/create-contract-ownership.json
- charness-artifacts/goal-runs/798/operations/create-evidence-meaning.json
- charness-artifacts/goal-runs/798/operations/create-friction-reduction.json
- charness-artifacts/goal-runs/798/operations/create-publish-closeout.json
- charness-artifacts/goal-runs/798/operations/create-spec-impl-journey.json
- charness-artifacts/goal-runs/798/operations/install-progress.json
- charness-artifacts/goal-runs/798/operations/verify-initial-graph.json
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/cli-journey.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/contract-ownership.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/evidence-meaning.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/friction-reduction.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/publish-closeout.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/spec-impl-journey.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-parent.md
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.binding.json
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.interview.json
- charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-09-06-advisory-render-comparison.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/alias-baseline-acceptance.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/alias-baseline-spec-task-receipt.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/baseline-cli-trace-audit.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/check_alias.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/check_cli.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/cli-baseline-acceptance.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/cli-baseline-task-receipt.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/cli-candidate-acceptance.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/freeze.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/integration-filename-refusal.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/oracle-review-1.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/oracle-review-2.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-baseline-spec.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-candidate-spec.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_baseline_catalog.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias_baseline_tests.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-baseline-readme.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-candidate-readme.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_baseline_repoctl.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_baseline_tests.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_candidate_repoctl.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli_candidate_tests.py
- charness-artifacts/probe/2026-09-06-consumer-journeys/package-identities.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/protocol.md
- charness-artifacts/probe/2026-09-06-consumer-journeys/reviewed-paths.txt
- charness-artifacts/probe/2026-09-06-consumer-journeys/seed-disconfirmation-r3.json
- charness-artifacts/probe/2026-09-06-consumer-journeys/seed-disconfirmation.json
- charness-artifacts/probe/2026-09-06-consumer-plan-proof-findings.json
- charness-artifacts/probe/2026-09-06-goal798-code-review-paths.txt
- charness-artifacts/probe/2026-09-06-integration-seam-findings.json
- charness-artifacts/probe/2026-09-06-preview-recovery-comparison.json
- docs/cli-reference.md
- docs/development.md
- docs/operating-contract.md
- docs/parallel-execution.md
- docs/validator-timing-layers.md
- evals/fixtures/consumer-journeys/create-cli-refresh/README.md
- evals/fixtures/consumer-journeys/create-cli-refresh/prompts/create-cli.md
- evals/fixtures/consumer-journeys/create-cli-refresh/prompts/impl.md
- evals/fixtures/consumer-journeys/create-cli-refresh/seed/AGENTS.md
- evals/fixtures/consumer-journeys/create-cli-refresh/seed/README.md
- evals/fixtures/consumer-journeys/create-cli-refresh/seed/scripts/check_cache.py
- evals/fixtures/consumer-journeys/create-cli-refresh/seed/scripts/refresh_cache.py
- evals/fixtures/consumer-journeys/create-cli-refresh/seed/tests/test_current_scripts.py
- evals/fixtures/consumer-journeys/spec-impl-alias/README.md
- evals/fixtures/consumer-journeys/spec-impl-alias/prompts/impl.md
- evals/fixtures/consumer-journeys/spec-impl-alias/prompts/spec.md
- evals/fixtures/consumer-journeys/spec-impl-alias/seed/AGENTS.md
- evals/fixtures/consumer-journeys/spec-impl-alias/seed/README.md
- evals/fixtures/consumer-journeys/spec-impl-alias/seed/src/__init__.py
- evals/fixtures/consumer-journeys/spec-impl-alias/seed/src/catalog.py
- evals/fixtures/consumer-journeys/spec-impl-alias/seed/tests/test_catalog.py
- scripts/hooks/check_staged_cheap_owners.py
- scripts/review/reviewed_input_identity.py
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/run_review.py
- skills/public/impl/SKILL.md
- skills/public/quality/SKILL.md
- skills/public/quality/references/proposal-flow.md
- skills/public/release/scripts/publish_release_artifact_sections.py
- tests/quality_gates/test_claims_review_publication_boundary.py
- tests/quality_gates/test_claims_review_scope.py
- tests/quality_gates/test_semantic_review_command.py
- tests/quality_gates/test_staged_cheap_owners.py
- tests/quality_gates/test_standalone_imports.py
- tests/test_consumer_journey_fixtures.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/hooks/check_staged_cheap_owners.py, scripts/review/reviewed_input_identity.py, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/run_review.py, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/proposal-flow.md, skills/public/release/scripts/publish_release_artifact_sections.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/issue/validate_rca_ledger.py --repo-root ., python3 scripts/issue/aggregate_rca_ledger.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/create-skill/2026-09-06-impl-evidence-reuse.md, charness-artifacts/critique/consumer-plan-framing-packet.md, charness-artifacts/critique/consumer-plan-proof-packet.md, charness-artifacts/critique/consumer-plan-whole-packet.md, charness-artifacts/critique/goal798-code-contracts-packet.md, charness-artifacts/critique/goal798-consumer-oracle-packet.md, charness-artifacts/critique/goal798-consumer-oracle-r2-packet.md, charness-artifacts/critique/goal798-consumer-oracle-r3-packet.md, charness-artifacts/critique/goal798-final-owner-review-packet.md, charness-artifacts/debug/2026-09-06-critique-preview-live-collision.md, charness-artifacts/debug/2026-09-06-release-advisory-meaning.md, charness-artifacts/debug/2026-09-06-staged-owner-universe.md, charness-artifacts/debug/latest.md, charness-artifacts/goal-runs/798/bodies/parent-bootstrap.md, charness-artifacts/goal-runs/798/bodies/parent-progress-1.md, charness-artifacts/goal-runs/798/bodies/parent-progress-2.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/cli-journey.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/contract-ownership.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/evidence-meaning.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/friction-reduction.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/publish-closeout.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/spec-impl-journey.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-parent.md, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.md, charness-artifacts/probe/2026-09-06-consumer-journeys/baseline-cli-trace-audit.md, charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-baseline-spec.md, charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/alias-candidate-spec.md, charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-baseline-readme.md, charness-artifacts/probe/2026-09-06-consumer-journeys/outputs/cli-candidate-readme.md, charness-artifacts/probe/2026-09-06-consumer-journeys/protocol.md, docs/cli-reference.md, docs/development.md, docs/operating-contract.md, docs/parallel-execution.md, docs/validator-timing-layers.md, evals/fixtures/consumer-journeys/create-cli-refresh/README.md, evals/fixtures/consumer-journeys/create-cli-refresh/prompts/create-cli.md, evals/fixtures/consumer-journeys/create-cli-refresh/prompts/impl.md, evals/fixtures/consumer-journeys/create-cli-refresh/seed/AGENTS.md, evals/fixtures/consumer-journeys/create-cli-refresh/seed/README.md, evals/fixtures/consumer-journeys/spec-impl-alias/README.md, evals/fixtures/consumer-journeys/spec-impl-alias/prompts/impl.md, evals/fixtures/consumer-journeys/spec-impl-alias/prompts/spec.md, evals/fixtures/consumer-journeys/spec-impl-alias/seed/AGENTS.md, evals/fixtures/consumer-journeys/spec-impl-alias/seed/README.md, skills/public/critique/references/prepare-packet.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/proposal-flow.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- goal-evidence-json: Machine-readable evidence captured beside achieve goal artifacts.
  source matches: charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.binding.json, charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.interview.json
  verify: for evidence_file in charness-artifacts/goals/*.json; do python3 -m json.tool "$evidence_file" >/dev/null || exit $?; done, python3 -c 'import json, pathlib; [json.loads(line) for path in pathlib.Path("charness-artifacts/goals").glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]'
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/run_review.py, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/proposal-flow.md, skills/public/release/scripts/publish_release_artifact_sections.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 -m tools.validate_current_pointer_freshness --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/run_review.py, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/proposal-flow.md, skills/public/release/scripts/publish_release_artifact_sections.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/run_review.py, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/proposal-flow.md, skills/public/release/scripts/publish_release_artifact_sections.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/consumer-plan-framing-packet.json, charness-artifacts/critique/consumer-plan-framing-packet.md, charness-artifacts/critique/consumer-plan-proof-packet.json, charness-artifacts/critique/consumer-plan-proof-packet.md, charness-artifacts/critique/consumer-plan-whole-packet.json, charness-artifacts/critique/consumer-plan-whole-packet.md, charness-artifacts/critique/goal798-code-contracts-packet.json, charness-artifacts/critique/goal798-code-contracts-packet.md, charness-artifacts/critique/goal798-consumer-oracle-packet.json, charness-artifacts/critique/goal798-consumer-oracle-packet.md, charness-artifacts/critique/goal798-consumer-oracle-r2-packet.json, charness-artifacts/critique/goal798-consumer-oracle-r2-packet.md, charness-artifacts/critique/goal798-consumer-oracle-r3-packet.json, charness-artifacts/critique/goal798-consumer-oracle-r3-packet.md, charness-artifacts/critique/goal798-final-owner-review-packet.json, charness-artifacts/critique/goal798-final-owner-review-packet.md, charness-artifacts/critique/workers/consumer-plan-framing-live/worker-report.yaml, charness-artifacts/critique/workers/consumer-plan-whole/worker-report.yaml, charness-artifacts/critique/workers/goal798-code-contracts/worker-report.yaml, charness-artifacts/critique/workers/goal798-consumer-oracle-r3/worker-report.yaml, charness-artifacts/critique/workers/goal798-final-owner-review/worker-report.yaml
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-09-06-advisory-render-comparison.json, charness-artifacts/probe/2026-09-06-consumer-journeys/alias-baseline-acceptance.json, charness-artifacts/probe/2026-09-06-consumer-journeys/alias-baseline-spec-task-receipt.json, charness-artifacts/probe/2026-09-06-consumer-journeys/cli-baseline-acceptance.json, charness-artifacts/probe/2026-09-06-consumer-journeys/cli-baseline-task-receipt.json, charness-artifacts/probe/2026-09-06-consumer-journeys/cli-candidate-acceptance.json, charness-artifacts/probe/2026-09-06-consumer-journeys/freeze.json, charness-artifacts/probe/2026-09-06-consumer-journeys/integration-filename-refusal.json, charness-artifacts/probe/2026-09-06-consumer-journeys/oracle-review-1.json, charness-artifacts/probe/2026-09-06-consumer-journeys/oracle-review-2.json, charness-artifacts/probe/2026-09-06-consumer-journeys/package-identities.json, charness-artifacts/probe/2026-09-06-consumer-journeys/seed-disconfirmation-r3.json, charness-artifacts/probe/2026-09-06-consumer-journeys/seed-disconfirmation.json, charness-artifacts/probe/2026-09-06-consumer-plan-proof-findings.json, charness-artifacts/probe/2026-09-06-integration-seam-findings.json, charness-artifacts/probe/2026-09-06-preview-recovery-comparison.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-09-06-critique-preview-live-collision.md, charness-artifacts/debug/2026-09-06-release-advisory-meaning.md, charness-artifacts/debug/2026-09-06-staged-owner-universe.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --check
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/hooks/check_staged_cheap_owners.py, scripts/review/reviewed_input_identity.py, tests/quality_gates/test_claims_review_publication_boundary.py, tests/quality_gates/test_claims_review_scope.py, tests/quality_gates/test_semantic_review_command.py, tests/quality_gates/test_staged_cheap_owners.py, tests/quality_gates/test_standalone_imports.py, tests/test_consumer_journey_fixtures.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/hooks/check_staged_cheap_owners.py, scripts/review/reviewed_input_identity.py, skills/public/critique/scripts/run_review.py, skills/public/release/scripts/publish_release_artifact_sections.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- goal-run-evidence: Durable Goal Run provider plans, operations, observations, graph snapshots, and evidence-lineage records.
  source matches: charness-artifacts/goal-runs/798/bodies/parent-bootstrap.md, charness-artifacts/goal-runs/798/bodies/parent-progress-1.md, charness-artifacts/goal-runs/798/bodies/parent-progress-2.md, charness-artifacts/goal-runs/798/consumer-lineage.json, charness-artifacts/goal-runs/798/expected-children.json, charness-artifacts/goal-runs/798/observations/798-add-cli-journey.started.json, charness-artifacts/goal-runs/798/observations/798-add-cli-journey.terminal.json, charness-artifacts/goal-runs/798/observations/798-add-contract-ownership.started.json, charness-artifacts/goal-runs/798/observations/798-add-contract-ownership.terminal.json, charness-artifacts/goal-runs/798/observations/798-add-evidence-meaning.started.json, charness-artifacts/goal-runs/798/observations/798-add-evidence-meaning.terminal.json, charness-artifacts/goal-runs/798/observations/798-add-friction-reduction.started.json, charness-artifacts/goal-runs/798/observations/798-add-friction-reduction.terminal.json, charness-artifacts/goal-runs/798/observations/798-add-publish-closeout.started.json, charness-artifacts/goal-runs/798/observations/798-add-publish-closeout.terminal.json, charness-artifacts/goal-runs/798/observations/798-add-spec-impl-journey.started.json, charness-artifacts/goal-runs/798/observations/798-add-spec-impl-journey.terminal.json, charness-artifacts/goal-runs/798/observations/798-bootstrap-metadata.started.json, charness-artifacts/goal-runs/798/observations/798-bootstrap-metadata.terminal.json, charness-artifacts/goal-runs/798/observations/798-consumer-frontier.started.json, charness-artifacts/goal-runs/798/observations/798-consumer-frontier.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-cli-journey.started.json, charness-artifacts/goal-runs/798/observations/798-create-cli-journey.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-contract-ownership.started.json, charness-artifacts/goal-runs/798/observations/798-create-contract-ownership.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-evidence-meaning.started.json, charness-artifacts/goal-runs/798/observations/798-create-evidence-meaning.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-friction-reduction.started.json, charness-artifacts/goal-runs/798/observations/798-create-friction-reduction.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-publish-closeout.started.json, charness-artifacts/goal-runs/798/observations/798-create-publish-closeout.terminal.json, charness-artifacts/goal-runs/798/observations/798-create-spec-impl-journey.started.json, charness-artifacts/goal-runs/798/observations/798-create-spec-impl-journey.terminal.json, charness-artifacts/goal-runs/798/observations/798-install-progress.started.json, charness-artifacts/goal-runs/798/observations/798-install-progress.terminal.json, charness-artifacts/goal-runs/798/observations/798-verify-initial-graph.started.json, charness-artifacts/goal-runs/798/observations/798-verify-initial-graph.terminal.json, charness-artifacts/goal-runs/798/operations/add-cli-journey.json, charness-artifacts/goal-runs/798/operations/add-contract-ownership.json, charness-artifacts/goal-runs/798/operations/add-evidence-meaning.json, charness-artifacts/goal-runs/798/operations/add-friction-reduction.json, charness-artifacts/goal-runs/798/operations/add-publish-closeout.json, charness-artifacts/goal-runs/798/operations/add-spec-impl-journey.json, charness-artifacts/goal-runs/798/operations/bootstrap-metadata.json, charness-artifacts/goal-runs/798/operations/consumer-frontier.json, charness-artifacts/goal-runs/798/operations/create-cli-journey.json, charness-artifacts/goal-runs/798/operations/create-contract-ownership.json, charness-artifacts/goal-runs/798/operations/create-evidence-meaning.json, charness-artifacts/goal-runs/798/operations/create-friction-reduction.json, charness-artifacts/goal-runs/798/operations/create-publish-closeout.json, charness-artifacts/goal-runs/798/operations/create-spec-impl-journey.json, charness-artifacts/goal-runs/798/operations/install-progress.json, charness-artifacts/goal-runs/798/operations/verify-initial-graph.json
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
Rework issues labelled `rework` created since 2026-08-07 (2 issue(s)):

| Causing skill | Issues |
| --- | --- |
| achieve | 2 |
| issue | 1 |
| retro | 1 |

Counts are per attribution; one issue naming multiple skills is counted once under each skill.

- #774 Charness still projects recent-lessons.md although the operator chose the ledger as the only lesson surface (CLOSED, 2026-09-02; retro, achieve) https://github.com/corca-ai/charness/issues/774
- #773 Goal Run binding hashes content, not identity: one-line child edits and new Work Items force a full re-bootstrap (CLOSED, 2026-09-02; achieve, issue) https://github.com/corca-ai/charness/issues/773
```
