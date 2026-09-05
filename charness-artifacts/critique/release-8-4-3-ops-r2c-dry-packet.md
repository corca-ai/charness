# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-05T03:29:56Z
- **Prepared for**: 5d529fbfaefd973280df7f32eebc682c69a3c447..c7f12854f643fb9a962aa34f3b0eee321ce2bf8c
- **Substrate mode**: `committed-ref`
- **Changed ref**: `5d529fbfaefd973280df7f32eebc682c69a3c447..c7f12854f643fb9a962aa34f3b0eee321ce2bf8c`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `e8399c803ff026a418304fcbdf1ee7cca96640be7d00ce6a96dba2a49293c75d`
- **Reviewed paths**: 54
  - `.agents/quality-gates.yaml`
  - `.githooks/pre-commit`
  - `charness-artifacts/critique/2026-09-05-form-identity-commit-5bd6075cc.md`
  - `charness-artifacts/critique/2026-09-05-form-identity-repair-closeout.md`
  - `charness-artifacts/critique/form-identity-r3-blast-packet.json`
  - `charness-artifacts/critique/form-identity-r3-blast-packet.md`
  - `charness-artifacts/critique/form-identity-r3-form-packet.json`
  - `charness-artifacts/critique/form-identity-r3-form-packet.md`
  - `charness-artifacts/critique/form-versus-controller-packet.json`
  - `charness-artifacts/critique/form-versus-controller-packet.md`
  - `charness-artifacts/critique/repo-decided-blast-radius-packet.json`
  - `charness-artifacts/critique/repo-decided-blast-radius-packet.md`
  - `docs/authoring-preflight.md`
  - `docs/validator-timing-layers.md`
  - `integrations/locks/lock.schema.json`
  - `integrations/tools/manifest.schema.json`
  - `scripts/adapters/quality_artifact_skill_ergonomics.py`
  - `scripts/gates/check_coverage_lib.py`
  - `scripts/gates/check_schema_enum_axis.py`
  - `scripts/gates/inventory_measurement_lib.py`
  - `scripts/gates/validate_inventory_consumption.py`
  - `scripts/gates/validate_skill_output_schemas.py`
  - `scripts/gates_support/skill_core_density.py`
  - `scripts/hooks/check_release_lane_receipt.py`
  - `scripts/hooks/check_staged_cheap_owners.py`
  - `scripts/install_tools.py`
  - `scripts/staged_commit_gate_plan.py`
  - `scripts/update_tools.py`
  - `skills/public/create-skill/SKILL.md`
  - `skills/public/create-skill/references/portable-authoring.md`
  - `skills/public/impl/SKILL.md`
  - `skills/public/quality/SKILL.md`
  - `skills/public/quality/references/consumer-validator-catalog.yaml`
  - `skills/public/quality/references/inventory-consumer-fields.json`
  - `skills/public/quality/scripts/inventory_skill_ergonomics.py`
  - `skills/public/quality/scripts/skill_ergonomics_lib.py`
  - `skills/public/setup/SKILL.md`
  - `skills/public/spec/SKILL.md`
  - `skills/public/spec/references/taxonomy-axis-checkpoint.md`
  - `tests/control_plane/test_integrations_validation.py`
  - `tests/control_plane/test_upstream_support_drift.py`
  - `tests/quality_gates/test_inventory_consumption.py`
  - `tests/quality_gates/test_mutation_recovery.py`
  - `tests/quality_gates/test_quality_skill_ergonomics.py`
  - `tests/quality_gates/test_skill_docs_contracts.py`
  - `tests/quality_gates/test_skill_reference_index.py`
  - `tests/quality_gates/test_staged_cheap_owners.py`
  - `tests/quality_gates/test_staged_commit_gate_plan.py`
  - `tests/test_schema_enum_axis.py`
  - `tests/test_skill_output_schemas.py`
  - `tools/check_inventory_declaration_coverage.py`
  - `tools/check_skill_contracts.py`
  - `tools/validate_integrations.py`
  - `tools/validate_inventory_consumption_declaration.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-4-3-ops-r2c-dry-packet.json --packet-sha256 307c7b37e2d1eb08e4f653ed1deef5532c5b9c0b16ff1d90c35bc9e9c156e57b --identity-sha256 e8399c803ff026a418304fcbdf1ee7cca96640be7d00ce6a96dba2a49293c75d
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
- **Execution mode**: `file-backed-worker`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `5d529fbfaefd973280df7f32eebc682c69a3c447..c7f12854f643fb9a962aa34f3b0eee321ce2bf8c`:
- .agents/quality-gates.yaml
- .githooks/pre-commit
- charness-artifacts/critique/2026-09-05-form-identity-commit-5bd6075cc.md
- charness-artifacts/critique/2026-09-05-form-identity-repair-closeout.md
- charness-artifacts/critique/form-identity-r3-blast-packet.json
- charness-artifacts/critique/form-identity-r3-blast-packet.md
- charness-artifacts/critique/form-identity-r3-form-packet.json
- charness-artifacts/critique/form-identity-r3-form-packet.md
- charness-artifacts/critique/form-versus-controller-packet.json
- charness-artifacts/critique/form-versus-controller-packet.md
- charness-artifacts/critique/repo-decided-blast-radius-packet.json
- charness-artifacts/critique/repo-decided-blast-radius-packet.md
- docs/authoring-preflight.md
- docs/validator-timing-layers.md
- integrations/locks/lock.schema.json
- integrations/tools/manifest.schema.json
- scripts/adapters/quality_artifact_skill_ergonomics.py
- scripts/gates/check_coverage_lib.py
- scripts/gates/check_schema_enum_axis.py
- scripts/gates/inventory_measurement_lib.py
- scripts/gates/validate_inventory_consumption.py
- scripts/gates/validate_skill_output_schemas.py
- scripts/gates_support/skill_core_density.py
- scripts/hooks/check_release_lane_receipt.py
- scripts/hooks/check_staged_cheap_owners.py
- scripts/install_tools.py
- scripts/staged_commit_gate_plan.py
- scripts/update_tools.py
- skills/public/create-skill/SKILL.md
- skills/public/create-skill/references/portable-authoring.md
- skills/public/impl/SKILL.md
- skills/public/quality/SKILL.md
- skills/public/quality/references/consumer-validator-catalog.yaml
- skills/public/quality/references/inventory-consumer-fields.json
- skills/public/quality/scripts/inventory_skill_ergonomics.py
- skills/public/quality/scripts/skill_ergonomics_lib.py
- skills/public/setup/SKILL.md
- skills/public/spec/SKILL.md
- skills/public/spec/references/taxonomy-axis-checkpoint.md
- tests/control_plane/test_integrations_validation.py
- tests/control_plane/test_upstream_support_drift.py
- tests/quality_gates/test_inventory_consumption.py
- tests/quality_gates/test_mutation_recovery.py
- tests/quality_gates/test_quality_skill_ergonomics.py
- tests/quality_gates/test_skill_docs_contracts.py
- tests/quality_gates/test_skill_reference_index.py
- tests/quality_gates/test_staged_cheap_owners.py
- tests/quality_gates/test_staged_commit_gate_plan.py
- tests/test_schema_enum_axis.py
- tests/test_skill_output_schemas.py
- tools/check_inventory_declaration_coverage.py
- tools/check_skill_contracts.py
- tools/validate_integrations.py
- tools/validate_inventory_consumption_declaration.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: integrations/locks/lock.schema.json, integrations/tools/manifest.schema.json, scripts/adapters/quality_artifact_skill_ergonomics.py, scripts/gates/check_coverage_lib.py, scripts/gates/check_schema_enum_axis.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/validate_inventory_consumption.py, scripts/gates/validate_skill_output_schemas.py, scripts/gates_support/skill_core_density.py, scripts/hooks/check_release_lane_receipt.py, scripts/hooks/check_staged_cheap_owners.py, scripts/install_tools.py, scripts/staged_commit_gate_plan.py, scripts/update_tools.py, skills/public/create-skill/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_skill_ergonomics.py, skills/public/quality/scripts/skill_ergonomics_lib.py, skills/public/setup/SKILL.md, skills/public/spec/SKILL.md, skills/public/spec/references/taxonomy-axis-checkpoint.md
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-09-05-form-identity-commit-5bd6075cc.md, charness-artifacts/critique/2026-09-05-form-identity-repair-closeout.md, charness-artifacts/critique/form-identity-r3-blast-packet.md, charness-artifacts/critique/form-identity-r3-form-packet.md, charness-artifacts/critique/form-versus-controller-packet.md, charness-artifacts/critique/repo-decided-blast-radius-packet.md, docs/authoring-preflight.md, docs/validator-timing-layers.md, skills/public/create-skill/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/setup/SKILL.md, skills/public/spec/SKILL.md, skills/public/spec/references/taxonomy-axis-checkpoint.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/create-skill/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_skill_ergonomics.py, skills/public/quality/scripts/skill_ergonomics_lib.py, skills/public/setup/SKILL.md, skills/public/spec/SKILL.md, skills/public/spec/references/taxonomy-axis-checkpoint.md
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- consumer-validator-catalog: Explicit packaged consumer-validator inventory, adoption decisions, and the installed/source-layout checker that enforces the contract.
  source matches: scripts/staged_commit_gate_plan.py, skills/public/quality/references/consumer-validator-catalog.yaml
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/gates/check_consumer_validator_catalog.py --repo-root . --adoption-path .agents/consumer-validator-adoption.yaml --require-adoption, python3 -m pytest -q tests/test_consumer_validator_catalog.py tests/test_capability_catalog.py
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/create-skill/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_skill_ergonomics.py, skills/public/quality/scripts/skill_ergonomics_lib.py, skills/public/setup/SKILL.md, skills/public/spec/SKILL.md, skills/public/spec/references/taxonomy-axis-checkpoint.md
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/create-skill/SKILL.md, skills/public/create-skill/references/portable-authoring.md, skills/public/impl/SKILL.md, skills/public/quality/SKILL.md, skills/public/quality/references/consumer-validator-catalog.yaml, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_skill_ergonomics.py, skills/public/quality/scripts/skill_ergonomics_lib.py, skills/public/setup/SKILL.md, skills/public/spec/SKILL.md, skills/public/spec/references/taxonomy-axis-checkpoint.md
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-09-05-form-identity-commit-5bd6075cc.md, charness-artifacts/critique/2026-09-05-form-identity-repair-closeout.md, charness-artifacts/critique/form-identity-r3-blast-packet.json, charness-artifacts/critique/form-identity-r3-blast-packet.md, charness-artifacts/critique/form-identity-r3-form-packet.json, charness-artifacts/critique/form-identity-r3-form-packet.md, charness-artifacts/critique/form-versus-controller-packet.json, charness-artifacts/critique/form-versus-controller-packet.md, charness-artifacts/critique/repo-decided-blast-radius-packet.json, charness-artifacts/critique/repo-decided-blast-radius-packet.md
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: integrations/tools/manifest.schema.json, scripts/install_tools.py, scripts/update_tools.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/locks/lock.schema.json, integrations/tools/manifest.schema.json, scripts/install_tools.py, scripts/update_tools.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- maintainer-hooks: Repo-owned maintainer hook and hook bootstrap validation.
  source matches: .githooks/pre-commit
  verify: python3 scripts/setup/validate_maintainer_setup.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/adapters/quality_artifact_skill_ergonomics.py, scripts/gates/check_coverage_lib.py, scripts/gates/check_schema_enum_axis.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/validate_inventory_consumption.py, scripts/gates/validate_skill_output_schemas.py, scripts/gates_support/skill_core_density.py, scripts/hooks/check_release_lane_receipt.py, scripts/hooks/check_staged_cheap_owners.py, scripts/install_tools.py, scripts/staged_commit_gate_plan.py, scripts/update_tools.py, tests/control_plane/test_integrations_validation.py, tests/control_plane/test_upstream_support_drift.py, tests/quality_gates/test_inventory_consumption.py, tests/quality_gates/test_mutation_recovery.py, tests/quality_gates/test_quality_skill_ergonomics.py, tests/quality_gates/test_skill_docs_contracts.py, tests/quality_gates/test_skill_reference_index.py, tests/quality_gates/test_staged_cheap_owners.py, tests/quality_gates/test_staged_commit_gate_plan.py, tests/test_schema_enum_axis.py, tests/test_skill_output_schemas.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: skills/public/quality/scripts/inventory_skill_ergonomics.py
  verify: python3 -m tools.validate_inference_interpretation --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/adapters/quality_artifact_skill_ergonomics.py, scripts/gates/check_coverage_lib.py, scripts/gates/check_schema_enum_axis.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/validate_inventory_consumption.py, scripts/gates/validate_skill_output_schemas.py, scripts/gates_support/skill_core_density.py, scripts/hooks/check_release_lane_receipt.py, scripts/hooks/check_staged_cheap_owners.py, scripts/install_tools.py, scripts/staged_commit_gate_plan.py, scripts/update_tools.py, skills/public/quality/scripts/inventory_skill_ergonomics.py, skills/public/quality/scripts/skill_ergonomics_lib.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
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
