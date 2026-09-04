# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-04T08:38:18Z
- **Prepared for**: release-8.4.1-docs-cut
- **Substrate mode**: `committed-ref`
- **Changed ref**: `85ede6996471d7867fdff1f49bb32885251ead53..1e9c5e2e899d1209cdebd05a31f51a1080efd910`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `1b35f452f6e01106fc572fd2f9b6be9ee4bc3ebf77ac1a5f15962e7c52133c15`
- **Reviewed paths**: 75
  - `.agents/claude-host.md`
  - `.agents/codex-host.md`
  - `.agents/quality-adapter.yaml`
  - `AGENTS.md`
  - `README.md`
  - `charness-artifacts/probe/2026-09-04-v8.4.0-release-observer.json`
  - `charness-artifacts/quality/docs-length-baseline.json`
  - `charness-artifacts/release-review/2026-09-04-v8.4.0-claims-review.md`
  - `charness-artifacts/release-review/2026-09-04-v8.4.0-prepared-claims-review.json`
  - `charness-artifacts/release/latest.md`
  - `charness-artifacts/spec/2026-09-04-copy-held-by-test.md`
  - `charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md`
  - `docs/agent-task-runs.md`
  - `docs/artifact-policy.md`
  - `docs/authoring-preflight.md`
  - `docs/capability-resolution.md`
  - `docs/control-plane.md`
  - `docs/development.md`
  - `docs/documentation-principles.md`
  - `docs/export-boundary.md`
  - `docs/external-integrations.md`
  - `docs/goal-lifecycle.md`
  - `docs/harness-composition.md`
  - `docs/host-packaging.md`
  - `docs/index.md`
  - `docs/operating-contract.md`
  - `docs/operator-acceptance.md`
  - `docs/parallel-execution.md`
  - `docs/proof-semantics-adapter.md`
  - `docs/provenance-placement.md`
  - `docs/runtime-capability-contract.md`
  - `docs/support-skill-policy.md`
  - `docs/validator-timing-layers.md`
  - `docs/workflow-routes.md`
  - `docs/worktree-prepare.md`
  - `integrations/locks/README.md`
  - `integrations/tools/README.md`
  - `scripts/adapters/proof_semantics_adapter_lib.py`
  - `scripts/gates/check_code_lengths.py`
  - `scripts/gates/inventory_measurement_lib.py`
  - `scripts/gates/measure_inventory_consumption_floor.py`
  - `scripts/gates/measure_inventory_marker_rule.py`
  - `scripts/gates/validate_inventory_consumption.py`
  - `scripts/gates_support/classify_t_signal.py`
  - `scripts/gates_support/command_carrier_discovery.py`
  - `scripts/gates_support/operator_acceptance_lib.py`
  - `skills/public/announcement/references/delivery-seams.md`
  - `skills/public/critique/adapter.example.yaml`
  - `skills/public/critique/references/adapter-contract.md`
  - `skills/public/critique/references/prepare-packet.md`
  - `skills/public/issue/SKILL.md`
  - `skills/public/issue/references/closeout-discipline.md`
  - `skills/public/issue/references/issue-backend.md`
  - `skills/public/issue/references/resolve-flow.md`
  - `skills/public/issue/scripts/resolve_adapter.py`
  - `skills/public/quality/SKILL.md`
  - `skills/public/quality/references/adapter-contract.md`
  - `skills/public/quality/references/mutation-testing.md`
  - `skills/public/quality/references/standing-doc-provenance.md`
  - `skills/public/release/SKILL.md`
  - `skills/public/release/references/critique-boundary.md`
  - `skills/public/setup/references/operator-acceptance-synthesis.md`
  - `skills/shared/references/bootstrap-resolution.md`
  - `skills/shared/references/fresh-eye-subagent-review.md`
  - `skills/support/markdown-preview/SKILL.md`
  - `skills/support/markdown-preview/references/runtime-contract.md`
  - `skills/support/web-fetch/SKILL.md`
  - `skills/support/web-fetch/references/routing-table.md`
  - `skills/support/web-fetch/references/runtime-contract.md`
  - `tests/coverage_debt/test_batch7.py`
  - `tests/quality_gates/test_inventory_ci_local_gate_parity.py`
  - `tests/quality_gates/test_issue_closeout_discipline.py`
  - `tests/test_authoring_preflight_reference.py`
  - `tests/test_classify_t_signal.py`
  - `tests/test_inventory_marker_rule_measurement.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-4-1-packet.json --packet-sha256 c9b323ac70ab7ac4e9c0699cb25c6ecabf872df9c65c595a034ba64c364181f8 --identity-sha256 1b35f452f6e01106fc572fd2f9b6be9ee4bc3ebf77ac1a5f15962e7c52133c15
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
Changed paths for ref `85ede6996471d7867fdff1f49bb32885251ead53..1e9c5e2e899d1209cdebd05a31f51a1080efd910`:
- .agents/claude-host.md
- .agents/codex-host.md
- .agents/quality-adapter.yaml
- AGENTS.md
- README.md
- charness-artifacts/probe/2026-09-04-v8.4.0-release-observer.json
- charness-artifacts/quality/docs-length-baseline.json
- charness-artifacts/release-review/2026-09-04-v8.4.0-claims-review.md
- charness-artifacts/release-review/2026-09-04-v8.4.0-prepared-claims-review.json
- charness-artifacts/release/latest.md
- charness-artifacts/spec/2026-09-04-copy-held-by-test.md
- charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md
- docs/agent-task-runs.md
- docs/artifact-policy.md
- docs/authoring-preflight.md
- docs/capability-resolution.md
- docs/control-plane.md
- docs/development.md
- docs/documentation-principles.md
- docs/export-boundary.md
- docs/external-integrations.md
- docs/goal-lifecycle.md
- docs/harness-composition.md
- docs/host-packaging.md
- docs/index.md
- docs/operating-contract.md
- docs/operator-acceptance.md
- docs/parallel-execution.md
- docs/proof-semantics-adapter.md
- docs/provenance-placement.md
- docs/runtime-capability-contract.md
- docs/support-skill-policy.md
- docs/validator-timing-layers.md
- docs/workflow-routes.md
- docs/worktree-prepare.md
- integrations/locks/README.md
- integrations/tools/README.md
- scripts/adapters/proof_semantics_adapter_lib.py
- scripts/gates/check_code_lengths.py
- scripts/gates/inventory_measurement_lib.py
- scripts/gates/measure_inventory_consumption_floor.py
- scripts/gates/measure_inventory_marker_rule.py
- scripts/gates/validate_inventory_consumption.py
- scripts/gates_support/classify_t_signal.py
- scripts/gates_support/command_carrier_discovery.py
- scripts/gates_support/operator_acceptance_lib.py
- skills/public/announcement/references/delivery-seams.md
- skills/public/critique/adapter.example.yaml
- skills/public/critique/references/adapter-contract.md
- skills/public/critique/references/prepare-packet.md
- skills/public/issue/SKILL.md
- skills/public/issue/references/closeout-discipline.md
- skills/public/issue/references/issue-backend.md
- skills/public/issue/references/resolve-flow.md
- skills/public/issue/scripts/resolve_adapter.py
- skills/public/quality/SKILL.md
- skills/public/quality/references/adapter-contract.md
- skills/public/quality/references/mutation-testing.md
- skills/public/quality/references/standing-doc-provenance.md
- skills/public/release/SKILL.md
- skills/public/release/references/critique-boundary.md
- skills/public/setup/references/operator-acceptance-synthesis.md
- skills/shared/references/bootstrap-resolution.md
- skills/shared/references/fresh-eye-subagent-review.md
- skills/support/markdown-preview/SKILL.md
- skills/support/markdown-preview/references/runtime-contract.md
- skills/support/web-fetch/SKILL.md
- skills/support/web-fetch/references/routing-table.md
- skills/support/web-fetch/references/runtime-contract.md
- tests/coverage_debt/test_batch7.py
- tests/quality_gates/test_inventory_ci_local_gate_parity.py
- tests/quality_gates/test_issue_closeout_discipline.py
- tests/test_authoring_preflight_reference.py
- tests/test_classify_t_signal.py
- tests/test_inventory_marker_rule_measurement.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: README.md, integrations/locks/README.md, integrations/tools/README.md, scripts/adapters/proof_semantics_adapter_lib.py, scripts/gates/check_code_lengths.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/measure_inventory_consumption_floor.py, scripts/gates/measure_inventory_marker_rule.py, scripts/gates/validate_inventory_consumption.py, scripts/gates_support/classify_t_signal.py, scripts/gates_support/command_carrier_discovery.py, scripts/gates_support/operator_acceptance_lib.py, skills/public/announcement/references/delivery-seams.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/references/issue-backend.md, skills/public/issue/references/resolve-flow.md, skills/public/issue/scripts/resolve_adapter.py, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/mutation-testing.md, skills/public/quality/references/standing-doc-provenance.md, skills/public/release/SKILL.md, skills/public/release/references/critique-boundary.md, skills/public/setup/references/operator-acceptance-synthesis.md, skills/shared/references/bootstrap-resolution.md, skills/shared/references/fresh-eye-subagent-review.md, skills/support/markdown-preview/SKILL.md, skills/support/markdown-preview/references/runtime-contract.md, skills/support/web-fetch/SKILL.md, skills/support/web-fetch/references/routing-table.md, skills/support/web-fetch/references/runtime-contract.md
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: AGENTS.md, README.md, charness-artifacts/release-review/2026-09-04-v8.4.0-claims-review.md, charness-artifacts/release/latest.md, charness-artifacts/spec/2026-09-04-copy-held-by-test.md, charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md, docs/agent-task-runs.md, docs/artifact-policy.md, docs/authoring-preflight.md, docs/capability-resolution.md, docs/control-plane.md, docs/development.md, docs/documentation-principles.md, docs/export-boundary.md, docs/external-integrations.md, docs/goal-lifecycle.md, docs/harness-composition.md, docs/host-packaging.md, docs/index.md, docs/operating-contract.md, docs/operator-acceptance.md, docs/parallel-execution.md, docs/proof-semantics-adapter.md, docs/provenance-placement.md, docs/runtime-capability-contract.md, docs/support-skill-policy.md, docs/validator-timing-layers.md, docs/workflow-routes.md, docs/worktree-prepare.md, integrations/locks/README.md, integrations/tools/README.md, skills/public/announcement/references/delivery-seams.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/references/issue-backend.md, skills/public/issue/references/resolve-flow.md, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/mutation-testing.md, skills/public/quality/references/standing-doc-provenance.md, skills/public/release/SKILL.md, skills/public/release/references/critique-boundary.md, skills/public/setup/references/operator-acceptance-synthesis.md, skills/shared/references/bootstrap-resolution.md, skills/shared/references/fresh-eye-subagent-review.md, skills/support/markdown-preview/SKILL.md, skills/support/markdown-preview/references/runtime-contract.md, skills/support/web-fetch/SKILL.md, skills/support/web-fetch/references/routing-table.md, skills/support/web-fetch/references/runtime-contract.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/quality/docs-length-baseline.json, charness-artifacts/release/latest.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/announcement/references/delivery-seams.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/references/issue-backend.md, skills/public/issue/references/resolve-flow.md, skills/public/issue/scripts/resolve_adapter.py, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/mutation-testing.md, skills/public/quality/references/standing-doc-provenance.md, skills/public/release/SKILL.md, skills/public/release/references/critique-boundary.md, skills/public/setup/references/operator-acceptance-synthesis.md, skills/shared/references/bootstrap-resolution.md, skills/shared/references/fresh-eye-subagent-review.md, skills/support/markdown-preview/SKILL.md, skills/support/markdown-preview/references/runtime-contract.md, skills/support/web-fetch/SKILL.md, skills/support/web-fetch/references/routing-table.md, skills/support/web-fetch/references/runtime-contract.md
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/announcement/references/delivery-seams.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/references/issue-backend.md, skills/public/issue/references/resolve-flow.md, skills/public/issue/scripts/resolve_adapter.py, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/mutation-testing.md, skills/public/quality/references/standing-doc-provenance.md, skills/public/release/SKILL.md, skills/public/release/references/critique-boundary.md, skills/public/setup/references/operator-acceptance-synthesis.md, skills/shared/references/bootstrap-resolution.md, skills/shared/references/fresh-eye-subagent-review.md
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/announcement/references/delivery-seams.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/references/issue-backend.md, skills/public/issue/references/resolve-flow.md, skills/public/issue/scripts/resolve_adapter.py, skills/public/quality/SKILL.md, skills/public/quality/references/adapter-contract.md, skills/public/quality/references/mutation-testing.md, skills/public/quality/references/standing-doc-provenance.md, skills/public/release/SKILL.md, skills/public/release/references/critique-boundary.md, skills/public/setup/references/operator-acceptance-synthesis.md, skills/shared/references/bootstrap-resolution.md, skills/shared/references/fresh-eye-subagent-review.md
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/quality-adapter.yaml, scripts/adapters/proof_semantics_adapter_lib.py
  verify: python3 scripts/gates/validate_adapters.py --repo-root .
- release-claims-review-evidence: Committed, machine-readable claims-review evidence that binds a prepared local release record before publication may resume.
  source matches: charness-artifacts/release-review/2026-09-04-v8.4.0-claims-review.md, charness-artifacts/release-review/2026-09-04-v8.4.0-prepared-claims-review.json
  verify: for review_record in charness-artifacts/release-review/*.json; do [ -e "$review_record" ] && python3 -m json.tool "$review_record" >/dev/null || exit $?; done
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: .agents/quality-adapter.yaml
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 -m pytest -q tests/quality_gates/test_coverage_builder_policy_parity.py, python3 scripts/gates/check_github_actions.py --repo-root ., python3 scripts/gates/validate_adapters.py --repo-root ., python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-09-04-v8.4.0-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: integrations/tools/README.md
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/locks/README.md, integrations/tools/README.md
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/adapters/proof_semantics_adapter_lib.py, scripts/gates/check_code_lengths.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/measure_inventory_consumption_floor.py, scripts/gates/measure_inventory_marker_rule.py, scripts/gates/validate_inventory_consumption.py, scripts/gates_support/classify_t_signal.py, scripts/gates_support/command_carrier_discovery.py, scripts/gates_support/operator_acceptance_lib.py, tests/coverage_debt/test_batch7.py, tests/quality_gates/test_inventory_ci_local_gate_parity.py, tests/quality_gates/test_issue_closeout_discipline.py, tests/test_authoring_preflight_reference.py, tests/test_classify_t_signal.py, tests/test_inventory_marker_rule_measurement.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: scripts/gates/check_code_lengths.py
  verify: python3 -m tools.validate_inference_interpretation --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/adapters/proof_semantics_adapter_lib.py, scripts/gates/check_code_lengths.py, scripts/gates/inventory_measurement_lib.py, scripts/gates/measure_inventory_consumption_floor.py, scripts/gates/measure_inventory_marker_rule.py, scripts/gates/validate_inventory_consumption.py, scripts/gates_support/classify_t_signal.py, scripts/gates_support/command_carrier_discovery.py, scripts/gates_support/operator_acceptance_lib.py, skills/public/issue/scripts/resolve_adapter.py
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
