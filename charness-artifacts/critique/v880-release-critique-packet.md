# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-16T01:32:57Z
- **Prepared for**: 8.8.0 minor release critique: #818 body-revision chain, #819 coverage floor, staged-tree changed-line analysis
- **Prepared targets**: 1
  - `8.8.0-release`
- **Substrate mode**: `committed-ref`
- **Changed ref**: `99bb29a66bc95e159c9cc2e06beb21746ca1177f`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `3dbe5c27838ee3ac35ac23525a075b8ab0caddb3545668fbd8707d0782b086cf`
- **Reviewed paths**: 19
  - `.agents/temp-producers.yaml`
  - `scripts/gates_support/changed_line_gate_cli.py`
  - `scripts/gates_support/changed_line_run_trust.py`
  - `scripts/gates_support/changed_line_staged_head.py`
  - `scripts/mutation/check_changed_line_mutation_coverage.py`
  - `scripts/mutation/release_changed_line_coverage.py`
  - `skills/public/achieve/scripts/goal_run_pickup_contract.py`
  - `skills/public/issue/scripts/issue_goal_run_binding.py`
  - `skills/public/issue/scripts/issue_goal_run_body_chain.py`
  - `skills/public/issue/scripts/issue_goal_run_close.py`
  - `skills/public/issue/scripts/issue_goal_run_operations.py`
  - `skills/shared/scripts/reviewer_result_contract.py`
  - `skills/shared/scripts/reviewer_runner_support.py`
  - `skills/shared/scripts/reviewer_worker_carrier_support.py`
  - `skills/shared/scripts/reviewer_worker_report.py`
  - `tests/quality_gates/test_changed_line_staged_head.py`
  - `tests/quality_gates/test_issue_goal_run.py`
  - `tests/quality_gates/test_issue_goal_run_body_revisions.py`
  - `tests/test_reviewer_result_coverage.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v880-release-critique-packet.json --packet-sha256 80057df89efdf5839961131d5cbfaaadb8dd46f5609d5e3a2ac35b4c7a87c424 --identity-sha256 3dbe5c27838ee3ac35ac23525a075b8ab0caddb3545668fbd8707d0782b086cf
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
Changed paths for ref `99bb29a66bc95e159c9cc2e06beb21746ca1177f`:
Exact reviewed-path manifest:
- .agents/temp-producers.yaml
- scripts/gates_support/changed_line_gate_cli.py
- scripts/gates_support/changed_line_run_trust.py
- scripts/gates_support/changed_line_staged_head.py
- scripts/mutation/check_changed_line_mutation_coverage.py
- scripts/mutation/release_changed_line_coverage.py
- skills/public/achieve/scripts/goal_run_pickup_contract.py
- skills/public/issue/scripts/issue_goal_run_binding.py
- skills/public/issue/scripts/issue_goal_run_body_chain.py
- skills/public/issue/scripts/issue_goal_run_close.py
- skills/public/issue/scripts/issue_goal_run_operations.py
- skills/shared/scripts/reviewer_result_contract.py
- skills/shared/scripts/reviewer_runner_support.py
- skills/shared/scripts/reviewer_worker_carrier_support.py
- skills/shared/scripts/reviewer_worker_report.py
- tests/quality_gates/test_changed_line_staged_head.py
- tests/quality_gates/test_issue_goal_run.py
- tests/quality_gates/test_issue_goal_run_body_revisions.py
- tests/test_reviewer_result_coverage.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/gates_support/changed_line_gate_cli.py, scripts/gates_support/changed_line_run_trust.py, scripts/gates_support/changed_line_staged_head.py, scripts/mutation/check_changed_line_mutation_coverage.py, scripts/mutation/release_changed_line_coverage.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/issue/scripts/issue_goal_run_binding.py, skills/public/issue/scripts/issue_goal_run_body_chain.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_operations.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_runner_support.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/issue/scripts/issue_goal_run_binding.py, skills/public/issue/scripts/issue_goal_run_body_chain.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_operations.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_runner_support.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/issue/scripts/issue_goal_run_binding.py, skills/public/issue/scripts/issue_goal_run_body_chain.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_operations.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_runner_support.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/issue/scripts/issue_goal_run_binding.py, skills/public/issue/scripts/issue_goal_run_body_chain.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_operations.py, skills/shared/scripts/reviewer_result_contract.py, skills/shared/scripts/reviewer_runner_support.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: scripts/mutation/check_changed_line_mutation_coverage.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 -m pytest -q tests/quality_gates/test_coverage_builder_policy_parity.py, python3 scripts/gates/check_github_actions.py --repo-root ., python3 scripts/gates/validate_adapters.py --repo-root ., python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/gates_support/changed_line_gate_cli.py, scripts/gates_support/changed_line_run_trust.py, scripts/gates_support/changed_line_staged_head.py, scripts/mutation/check_changed_line_mutation_coverage.py, scripts/mutation/release_changed_line_coverage.py, tests/quality_gates/test_changed_line_staged_head.py, tests/quality_gates/test_issue_goal_run.py, tests/quality_gates/test_issue_goal_run_body_revisions.py, tests/test_reviewer_result_coverage.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/gates_support/changed_line_gate_cli.py, scripts/gates_support/changed_line_run_trust.py, scripts/gates_support/changed_line_staged_head.py, scripts/mutation/check_changed_line_mutation_coverage.py, scripts/mutation/release_changed_line_coverage.py, skills/public/achieve/scripts/goal_run_pickup_contract.py, skills/public/issue/scripts/issue_goal_run_binding.py, skills/public/issue/scripts/issue_goal_run_body_chain.py, skills/public/issue/scripts/issue_goal_run_close.py, skills/public/issue/scripts/issue_goal_run_operations.py
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
