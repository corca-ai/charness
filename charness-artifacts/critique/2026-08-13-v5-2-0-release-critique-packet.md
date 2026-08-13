# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-13T13:33:02Z
- **Prepared for**: v5.2.0 release critique
- **Changed ref**: `9b2c20d778021346562e9a11657aee280f6381a7..a4c0cb6c745ba21158ee909eeb62bd59c16610d7`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `f20fe1753015877335c2b4b78fcc3b93347fd9783ef79071dd81e00f2c61a140`
- **Reviewed paths**: 130
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
Changed paths for ref `9b2c20d778021346562e9a11657aee280f6381a7..a4c0cb6c745ba21158ee909eeb62bd59c16610d7`:
- .agents/retro-adapter.yaml
- .agents/surfaces.json
- charness-artifacts/create-skill/2026-08-13-handoff-retro-feedback-loop-brief.md
- charness-artifacts/critique/2026-08-13-115535-packet.json
- charness-artifacts/critique/2026-08-13-115535-packet.md
- charness-artifacts/critique/2026-08-13-120041-packet.json
- charness-artifacts/critique/2026-08-13-120041-packet.md
- charness-artifacts/critique/2026-08-13-120724-packet.json
- charness-artifacts/critique/2026-08-13-120724-packet.md
- charness-artifacts/critique/2026-08-13-121401-packet.json
- charness-artifacts/critique/2026-08-13-121401-packet.md
- charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.json
- charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.md
- charness-artifacts/critique/2026-08-13-handoff-lesson-evaluation-continuity.md
- charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md
- charness-artifacts/critique/2026-08-13-issue-614-local-artifact-retention-resolution.md
- charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md
- charness-artifacts/critique/2026-08-13-issue-615-round1-packet.json
- charness-artifacts/critique/2026-08-13-issue-615-round1-packet.md
- charness-artifacts/critique/2026-08-13-issue-615-round2-packet.json
- charness-artifacts/critique/2026-08-13-issue-615-round2-packet.md
- charness-artifacts/critique/2026-08-13-issue-616-applied-lifecycle-resolution.md
- charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.json
- charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.md
- charness-artifacts/critique/2026-08-13-issue-616-round1-packet.json
- charness-artifacts/critique/2026-08-13-issue-616-round1-packet.md
- charness-artifacts/critique/2026-08-13-issue-616-round2-packet.json
- charness-artifacts/critique/2026-08-13-issue-616-round2-packet.md
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round1-packet.json
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round1-packet.md
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.json
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.md
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-implementation.md
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.json
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.md
- charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-spec-critique.md
- charness-artifacts/debug/2026-08-13-issue-614-unbounded-local-artifact-retention.md
- charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md
- charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md
- charness-artifacts/impl/2026-08-13-lesson-evaluation-observability-closeout.md
- charness-artifacts/issue/2026-08-13-issue-614-closeout-commit-message.md
- charness-artifacts/issue/2026-08-13-issue-615-closeout-commit-message.md
- charness-artifacts/issue/2026-08-13-issue-616-closeout-commit-message.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
- charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-08-13-090345-packet.json
- charness-artifacts/retro/2026-08-13-090345-packet.md
- charness-artifacts/retro/2026-08-13-104307-packet.json
- charness-artifacts/retro/2026-08-13-104307-packet.md
- charness-artifacts/retro/2026-08-13-132203-packet.json
- charness-artifacts/retro/2026-08-13-132203-packet.md
- charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.json
- charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.md
- charness-artifacts/retro/2026-08-13-session-retro.md
- charness-artifacts/retro/contract-register.json
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-13-issue-614.json
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md
- charness-artifacts/spec/2026-08-13-issue-615-focused-changed-line-verdict-contract.md
- charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md
- docs/conventions/validator-timing-layers.md
- docs/development.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/apply_contract_transition.py
- plugins/charness/scripts/boundary-bypass-exemptions.txt
- plugins/charness/scripts/check_contract_register.py
- plugins/charness/scripts/check_lesson_evaluation_continuity.py
- plugins/charness/scripts/check_lesson_ledger.py
- plugins/charness/scripts/contract_register_lib.py
- plugins/charness/scripts/contract_unit_inventory_lib.py
- plugins/charness/scripts/lesson_evaluation_continuity_lib.py
- plugins/charness/scripts/lesson_ledger_lib.py
- plugins/charness/scripts/lesson_selection_preview_lib.py
- plugins/charness/scripts/manage_mutation_reports.py
- plugins/charness/scripts/migrate_contract_register.py
- plugins/charness/scripts/migrate_lesson_lifecycle.py
- plugins/charness/scripts/open_lesson_session.py
- plugins/charness/scripts/prepush_focused_changed_line_coverage.py
- plugins/charness/scripts/record_contract_citation.py
- plugins/charness/scripts/record_contract_graduation_proposal.py
- plugins/charness/scripts/record_lesson_lifecycle.py
- plugins/charness/scripts/record_lesson_session.py
- plugins/charness/scripts/render_contract_retention_review.py
- plugins/charness/scripts/render_lesson_selection_preview.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/scripts/run_standing_pytest.py
- plugins/charness/scripts/validate_inventory_consumption.py
- plugins/charness/scripts/validate_retro_artifact.py
- plugins/charness/skills/handoff/SKILL.md
- plugins/charness/skills/handoff/references/spill-targets.md
- plugins/charness/skills/handoff/scripts/handoff_authoring_preflight.py
- plugins/charness/skills/handoff/scripts/plan_handoff_run.py
- plugins/charness/skills/retro/SKILL.md
- plugins/charness/skills/retro/adapter.example.yaml
- plugins/charness/skills/retro/references/adapter-contract.md
- plugins/charness/skills/retro/references/lesson-evaluation.md
- plugins/charness/skills/retro/scripts/plan_retro_run.py
- plugins/charness/skills/retro/scripts/resolve_adapter.py
- plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
- scripts/apply_contract_transition.py
- scripts/boundary-bypass-exemptions.txt
- scripts/check_contract_register.py
- scripts/check_lesson_evaluation_continuity.py
- scripts/check_lesson_ledger.py
- scripts/contract_register_lib.py
- scripts/contract_unit_inventory_lib.py
- scripts/lesson_evaluation_continuity_lib.py
- scripts/lesson_ledger_lib.py
- scripts/lesson_selection_preview_lib.py
- scripts/manage_mutation_reports.py
- scripts/migrate_contract_register.py
- scripts/migrate_lesson_lifecycle.py
- scripts/open_lesson_session.py
- scripts/prepush_focused_changed_line_coverage.py
- scripts/record_contract_citation.py
- scripts/record_contract_graduation_proposal.py
- scripts/record_lesson_lifecycle.py
- scripts/record_lesson_session.py
- scripts/render_contract_retention_review.py
- scripts/render_lesson_selection_preview.py
- scripts/run-quality.sh
- scripts/run_standing_pytest.py
- scripts/validate_inventory_consumption.py
- scripts/validate_retro_artifact.py
- skills/public/handoff/SKILL.md
- skills/public/handoff/references/spill-targets.md
- skills/public/handoff/scripts/handoff_authoring_preflight.py
- skills/public/handoff/scripts/plan_handoff_run.py
- skills/public/retro/SKILL.md
- skills/public/retro/adapter.example.yaml
- skills/public/retro/references/adapter-contract.md
- skills/public/retro/references/lesson-evaluation.md
- skills/public/retro/scripts/plan_retro_run.py
- skills/public/retro/scripts/resolve_adapter.py
- skills/public/retro/scripts/scaffold_retro_artifact.py
- tests/quality_gates/support.py
- tests/quality_gates/test_handoff_skill.py
- tests/quality_gates/test_manage_mutation_reports.py
- tests/quality_gates/test_prepush_focused_changed_line_coverage.py
- tests/quality_gates/test_retention_refusal_coverage.py
- tests/quality_gates/test_retro_skill.py
- tests/quality_gates/test_standing_pytest_runner.py
- tests/test_contract_lifecycle_refusals.py
- tests/test_contract_register.py
- tests/test_handoff_plan.py
- tests/test_lesson_evaluation_continuity.py
- tests/test_lesson_evaluation_contract_boundaries.py
- tests/test_lesson_ledger.py
- tests/test_lesson_ledger_refusals.py
- tests/test_lesson_lifecycle.py
- tests/test_lesson_lifecycle_refusals.py
- tests/test_lesson_selection_preview.py
- tests/test_retro_plan.py
- tests/test_retro_scaffold.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/apply_contract_transition.py, scripts/boundary-bypass-exemptions.txt, scripts/check_contract_register.py, scripts/check_lesson_evaluation_continuity.py, scripts/check_lesson_ledger.py, scripts/contract_register_lib.py, scripts/contract_unit_inventory_lib.py, scripts/lesson_evaluation_continuity_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/manage_mutation_reports.py, scripts/migrate_contract_register.py, scripts/migrate_lesson_lifecycle.py, scripts/open_lesson_session.py, scripts/prepush_focused_changed_line_coverage.py, scripts/record_contract_citation.py, scripts/record_contract_graduation_proposal.py, scripts/record_lesson_lifecycle.py, scripts/record_lesson_session.py, scripts/render_contract_retention_review.py, scripts/render_lesson_selection_preview.py, scripts/run-quality.sh, scripts/run_standing_pytest.py, scripts/validate_inventory_consumption.py, scripts/validate_retro_artifact.py, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/scripts/handoff_authoring_preflight.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  derived matches: plugins/charness/scripts/apply_contract_transition.py, plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_lesson_evaluation_continuity.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/contract_unit_inventory_lib.py, plugins/charness/scripts/lesson_evaluation_continuity_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/migrate_contract_register.py, plugins/charness/scripts/migrate_lesson_lifecycle.py, plugins/charness/scripts/open_lesson_session.py, plugins/charness/scripts/prepush_focused_changed_line_coverage.py, plugins/charness/scripts/record_contract_citation.py, plugins/charness/scripts/record_contract_graduation_proposal.py, plugins/charness/scripts/record_lesson_lifecycle.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_contract_retention_review.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_standing_pytest.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_retro_artifact.py, plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/handoff/scripts/handoff_authoring_preflight.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/adapter.example.yaml, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/lesson-evaluation.md, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/skills/retro/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root . --json
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/create-skill/2026-08-13-handoff-retro-feedback-loop-brief.md, charness-artifacts/critique/2026-08-13-115535-packet.md, charness-artifacts/critique/2026-08-13-120041-packet.md, charness-artifacts/critique/2026-08-13-120724-packet.md, charness-artifacts/critique/2026-08-13-121401-packet.md, charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.md, charness-artifacts/critique/2026-08-13-handoff-lesson-evaluation-continuity.md, charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md, charness-artifacts/critique/2026-08-13-issue-614-local-artifact-retention-resolution.md, charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md, charness-artifacts/critique/2026-08-13-issue-615-round1-packet.md, charness-artifacts/critique/2026-08-13-issue-615-round2-packet.md, charness-artifacts/critique/2026-08-13-issue-616-applied-lifecycle-resolution.md, charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.md, charness-artifacts/critique/2026-08-13-issue-616-round1-packet.md, charness-artifacts/critique/2026-08-13-issue-616-round2-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round1-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-implementation.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-spec-critique.md, charness-artifacts/debug/2026-08-13-issue-614-unbounded-local-artifact-retention.md, charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md, charness-artifacts/debug/latest.md, charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md, charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md, charness-artifacts/impl/2026-08-13-lesson-evaluation-observability-closeout.md, charness-artifacts/issue/2026-08-13-issue-614-closeout-commit-message.md, charness-artifacts/issue/2026-08-13-issue-615-closeout-commit-message.md, charness-artifacts/issue/2026-08-13-issue-616-closeout-commit-message.md, charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-08-13-090345-packet.md, charness-artifacts/retro/2026-08-13-104307-packet.md, charness-artifacts/retro/2026-08-13-132203-packet.md, charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.md, charness-artifacts/retro/2026-08-13-session-retro.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md, charness-artifacts/spec/2026-08-13-issue-615-focused-changed-line-verdict-contract.md, charness-artifacts/spec/2026-08-13-lesson-evaluation-observability-contract.md, docs/conventions/validator-timing-layers.md, docs/development.md, docs/handoff.md, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md
  derived matches: plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/lesson-evaluation.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- handoff-machine-readers: docs/handoff.md is a rotating human document that is ALSO a machine-read source: the publish-state ledger declares it as a source locator, and the retro-memory gate requires its recent-lessons reference.
  source matches: docs/handoff.md
  verify: python3 scripts/publish_state_ledger.py --repo-root ., python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/retro-adapter.yaml, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/scripts/handoff_authoring_preflight.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  derived matches: plugins/charness/skills/handoff/SKILL.md, plugins/charness/skills/handoff/references/spill-targets.md, plugins/charness/skills/handoff/scripts/handoff_authoring_preflight.py, plugins/charness/skills/handoff/scripts/plan_handoff_run.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/adapter.example.yaml, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/lesson-evaluation.md, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/skills/retro/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/scripts/handoff_authoring_preflight.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/handoff/SKILL.md, skills/public/handoff/references/spill-targets.md, skills/public/handoff/scripts/handoff_authoring_preflight.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/lesson-evaluation.md, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/retro-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-13-115535-packet.json, charness-artifacts/critique/2026-08-13-115535-packet.md, charness-artifacts/critique/2026-08-13-120041-packet.json, charness-artifacts/critique/2026-08-13-120041-packet.md, charness-artifacts/critique/2026-08-13-120724-packet.json, charness-artifacts/critique/2026-08-13-120724-packet.md, charness-artifacts/critique/2026-08-13-121401-packet.json, charness-artifacts/critique/2026-08-13-121401-packet.md, charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.json, charness-artifacts/critique/2026-08-13-handoff-lesson-audit-packet.md, charness-artifacts/critique/2026-08-13-handoff-lesson-evaluation-continuity.md, charness-artifacts/critique/2026-08-13-handoff-retro-skill-feedback-loop.md, charness-artifacts/critique/2026-08-13-issue-614-local-artifact-retention-resolution.md, charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md, charness-artifacts/critique/2026-08-13-issue-615-round1-packet.json, charness-artifacts/critique/2026-08-13-issue-615-round1-packet.md, charness-artifacts/critique/2026-08-13-issue-615-round2-packet.json, charness-artifacts/critique/2026-08-13-issue-615-round2-packet.md, charness-artifacts/critique/2026-08-13-issue-616-applied-lifecycle-resolution.md, charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.json, charness-artifacts/critique/2026-08-13-issue-616-final-binding-packet.md, charness-artifacts/critique/2026-08-13-issue-616-round1-packet.json, charness-artifacts/critique/2026-08-13-issue-616-round1-packet.md, charness-artifacts/critique/2026-08-13-issue-616-round2-packet.json, charness-artifacts/critique/2026-08-13-issue-616-round2-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round1-packet.json, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round1-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.json, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-code-round2-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-implementation.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.json, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-preimpl-packet.md, charness-artifacts/critique/2026-08-13-lesson-evaluation-observability-spec-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-13-issue-614-unbounded-local-artifact-retention.md, charness-artifacts/debug/2026-08-13-issue-615-focused-changed-line-false-clean.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-13-090345-packet.json, charness-artifacts/retro/2026-08-13-090345-packet.md, charness-artifacts/retro/2026-08-13-104307-packet.json, charness-artifacts/retro/2026-08-13-104307-packet.md, charness-artifacts/retro/2026-08-13-132203-packet.json, charness-artifacts/retro/2026-08-13-132203-packet.md, charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.json, charness-artifacts/retro/2026-08-13-issue-615-memory-audit-packet.md, charness-artifacts/retro/2026-08-13-session-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/contract-register.json, charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-13-issue-614.json, scripts/apply_contract_transition.py, scripts/check_contract_register.py, scripts/check_lesson_ledger.py, scripts/contract_register_lib.py, scripts/contract_unit_inventory_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/migrate_contract_register.py, scripts/migrate_lesson_lifecycle.py, scripts/record_contract_citation.py, scripts/record_contract_graduation_proposal.py, scripts/record_lesson_lifecycle.py, scripts/record_lesson_session.py, scripts/render_contract_retention_review.py
  derived matches: plugins/charness/scripts/apply_contract_transition.py, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/contract_unit_inventory_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/migrate_contract_register.py, plugins/charness/scripts/migrate_lesson_lifecycle.py, plugins/charness/scripts/record_contract_citation.py, plugins/charness/scripts/record_contract_graduation_proposal.py, plugins/charness/scripts/record_lesson_lifecycle.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_contract_retention_review.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/apply_contract_transition.py, plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_lesson_evaluation_continuity.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/contract_unit_inventory_lib.py, plugins/charness/scripts/lesson_evaluation_continuity_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/migrate_contract_register.py, plugins/charness/scripts/migrate_lesson_lifecycle.py, plugins/charness/scripts/open_lesson_session.py, plugins/charness/scripts/prepush_focused_changed_line_coverage.py, plugins/charness/scripts/record_contract_citation.py, plugins/charness/scripts/record_contract_graduation_proposal.py, plugins/charness/scripts/record_lesson_lifecycle.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_contract_retention_review.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_standing_pytest.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/apply_contract_transition.py, scripts/check_contract_register.py, scripts/check_lesson_evaluation_continuity.py, scripts/check_lesson_ledger.py, scripts/contract_register_lib.py, scripts/contract_unit_inventory_lib.py, scripts/lesson_evaluation_continuity_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/manage_mutation_reports.py, scripts/migrate_contract_register.py, scripts/migrate_lesson_lifecycle.py, scripts/open_lesson_session.py, scripts/prepush_focused_changed_line_coverage.py, scripts/record_contract_citation.py, scripts/record_contract_graduation_proposal.py, scripts/record_lesson_lifecycle.py, scripts/record_lesson_session.py, scripts/render_contract_retention_review.py, scripts/render_lesson_selection_preview.py, scripts/run_standing_pytest.py, scripts/validate_inventory_consumption.py, scripts/validate_retro_artifact.py, tests/quality_gates/support.py, tests/quality_gates/test_handoff_skill.py, tests/quality_gates/test_manage_mutation_reports.py, tests/quality_gates/test_prepush_focused_changed_line_coverage.py, tests/quality_gates/test_retention_refusal_coverage.py, tests/quality_gates/test_retro_skill.py, tests/quality_gates/test_standing_pytest_runner.py, tests/test_contract_lifecycle_refusals.py, tests/test_contract_register.py, tests/test_handoff_plan.py, tests/test_lesson_evaluation_continuity.py, tests/test_lesson_evaluation_contract_boundaries.py, tests/test_lesson_ledger.py, tests/test_lesson_ledger_refusals.py, tests/test_lesson_lifecycle.py, tests/test_lesson_lifecycle_refusals.py, tests/test_lesson_selection_preview.py, tests/test_retro_plan.py, tests/test_retro_scaffold.py
  derived matches: plugins/charness/scripts/apply_contract_transition.py, plugins/charness/scripts/check_contract_register.py, plugins/charness/scripts/check_lesson_evaluation_continuity.py, plugins/charness/scripts/check_lesson_ledger.py, plugins/charness/scripts/contract_register_lib.py, plugins/charness/scripts/contract_unit_inventory_lib.py, plugins/charness/scripts/lesson_evaluation_continuity_lib.py, plugins/charness/scripts/lesson_ledger_lib.py, plugins/charness/scripts/lesson_selection_preview_lib.py, plugins/charness/scripts/manage_mutation_reports.py, plugins/charness/scripts/migrate_contract_register.py, plugins/charness/scripts/migrate_lesson_lifecycle.py, plugins/charness/scripts/open_lesson_session.py, plugins/charness/scripts/prepush_focused_changed_line_coverage.py, plugins/charness/scripts/record_contract_citation.py, plugins/charness/scripts/record_contract_graduation_proposal.py, plugins/charness/scripts/record_lesson_lifecycle.py, plugins/charness/scripts/record_lesson_session.py, plugins/charness/scripts/render_contract_retention_review.py, plugins/charness/scripts/render_lesson_selection_preview.py, plugins/charness/scripts/run_standing_pytest.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/apply_contract_transition.py, scripts/check_contract_register.py, scripts/check_lesson_evaluation_continuity.py, scripts/check_lesson_ledger.py, scripts/contract_register_lib.py, scripts/contract_unit_inventory_lib.py, scripts/lesson_evaluation_continuity_lib.py, scripts/lesson_ledger_lib.py, scripts/lesson_selection_preview_lib.py, scripts/manage_mutation_reports.py, scripts/migrate_contract_register.py, scripts/migrate_lesson_lifecycle.py, scripts/open_lesson_session.py, scripts/prepush_focused_changed_line_coverage.py, scripts/record_contract_citation.py, scripts/record_contract_graduation_proposal.py, scripts/record_lesson_lifecycle.py, scripts/record_lesson_session.py, scripts/render_contract_retention_review.py, scripts/render_lesson_selection_preview.py, scripts/run_standing_pytest.py, scripts/validate_inventory_consumption.py, scripts/validate_retro_artifact.py, skills/public/handoff/scripts/handoff_authoring_preflight.py, skills/public/handoff/scripts/plan_handoff_run.py, skills/public/retro/scripts/plan_retro_run.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
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
