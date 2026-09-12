# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-12T08:47:53Z
- **Prepared for**: working tree
- **Prepared targets**: 1
  - `v8.6.3`
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf`
- **Reviewed paths**: 9
  - `scripts/runtime_scratch.py`
  - `skills/public/critique/scripts/run_review_carrier.py`
  - `skills/public/critique/scripts/run_review_execution.py`
  - `skills/public/critique/scripts/run_review_hold_out.py`
  - `skills/public/critique/scripts/run_review_promotion.py`
  - `skills/public/critique/scripts/run_review_promotion_storage.py`
  - `skills/public/critique/scripts/run_review_recovery.py`
  - `skills/public/critique/scripts/run_review_recovery_inputs.py`
  - `tests/test_run_review_declared_path_resolution.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-863-repair-lifecycle-20260912-packet.json --packet-sha256 ff941d23eab058054fa10f359c2207516aaaafa6c4cc869ea29e6db62b966575 --identity-sha256 eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf
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

## Follow-up Context

This is prior review evidence, not approval. The new reviewer must judge the selected current paths and bind this new packet independently.

```json
{
  "approval_rule": "This is prior evidence only. Reuse findings as hypotheses; do not treat a prior block, defer, timeout, or partial result as approval. The new reviewer must bind the new packet and current selected paths independently.",
  "comparison": {
    "changed_prior_paths": [
      "skills/public/critique/scripts/run_review_carrier.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "skills/public/critique/scripts/run_review_promotion.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "comparison_identity_paths": [
      ".agents/critique-adapter.yaml",
      "charness-artifacts/critique/workers/release-8-6-3-lifecycle-final/result.json",
      "docs/agent-task-runs.md",
      "docs/development.md",
      "docs/index.md",
      "scripts/gates/check_test_production_ratio.py",
      "scripts/review/critique_adapter_lib.py",
      "scripts/review/critique_artifact_paths.py",
      "scripts/review/critique_followup_scope.py",
      "scripts/review/critique_packet_lib.py",
      "scripts/review/render_critique_section_changed_surfaces.py",
      "scripts/review/reviewed_input_verification.py",
      "scripts/runtime_scratch.py",
      "scripts/runtime_scratch_cli.py",
      "scripts/runtime_scratch_promotion.py",
      "scripts/runtime_scratch_registry.py",
      "scripts/task_run/task_run_completion.py",
      "scripts/task_run/task_run_completion_next_step.py",
      "scripts/task_run/task_run_execution.py",
      "skills/public/critique/SKILL.md",
      "skills/public/critique/references/adapter-contract.md",
      "skills/public/critique/references/prepare-packet.md",
      "skills/public/critique/scripts/followup_scope_consumer.py",
      "skills/public/critique/scripts/prepare_packet.py",
      "skills/public/critique/scripts/review_followup.py",
      "skills/public/critique/scripts/review_followup_context.py",
      "skills/public/critique/scripts/review_followup_provenance.py",
      "skills/public/critique/scripts/review_followup_selection.py",
      "skills/public/critique/scripts/run_review.py",
      "skills/public/critique/scripts/run_review_carrier.py",
      "skills/public/critique/scripts/run_review_execution.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "skills/public/critique/scripts/run_review_identity.py",
      "skills/public/critique/scripts/run_review_packet.py",
      "skills/public/critique/scripts/run_review_promotion.py",
      "skills/public/critique/scripts/run_review_promotion_storage.py",
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py",
      "skills/public/critique/scripts/run_review_support.py",
      "skills/shared/scripts/reviewer_result_contract.py",
      "skills/shared/scripts/reviewer_worker_carrier_support.py",
      "tests/charness_cli/test_task_run_completion.py",
      "tests/charness_cli/test_task_run_result.py",
      "tests/test_critique_prepare_packet.py",
      "tests/test_review_followup.py",
      "tests/test_run_review_declared_path_resolution.py",
      "tests/test_runtime_scratch.py"
    ],
    "comparison_identity_sha256": "368210feeaa92a1d83566d46edc0077d2f6ff30b2bcea8660bb6444a51aac952",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 47,
    "selected_changed_prior_paths": [
      "skills/public/critique/scripts/run_review_carrier.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "skills/public/critique/scripts/run_review_promotion.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "unchanged_selected_paths": [
      "scripts/runtime_scratch.py",
      "skills/public/critique/scripts/run_review_execution.py",
      "skills/public/critique/scripts/run_review_promotion_storage.py",
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py"
    ]
  },
  "context_size_bytes": 14858,
  "final_reviewed_input_identity_sha256": "eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf",
  "final_selected_path_count": 9,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-863-bounded-lifecycle-20260912",
  "prior_findings": [
    {
      "action": "Retain staging before propagating any restoration failure, preserving the recorded mappings. Add a restore-failure test that reads back the original staged bytes after context exit.",
      "evidence": [
        "skills/public/critique/scripts/run_review_hold_out.py: the final restoration loop calls shutil.move without retaining the owner if that call raises.",
        "Concrete stimulus: move an in-progress artifact into staging, then inject an OSError on the move back. The outer OwnedScratch.__exit__ calls close(state='failed'); because the owner is neither retained nor promoted, scripts/runtime_scratch.py removes its tree, including the original artifact.",
        "The included hold-out tests cover worker failure and source collision, but neither covers restoration I/O failure."
      ],
      "id": "LIFECYCLE-001",
      "severity": "blocker",
      "summary": "A failed hold-out restoration deletes the staged original."
    },
    {
      "action": "Keep the published manifest non-approval throughout finalization; publish approval only after the complete durable chain has passed readback. Test failure immediately after manifest publication.",
      "evidence": [
        "skills/public/critique/scripts/run_review_carrier.py: finalize_carrier passes final_carrier into promote_attempt_metadata before writing and checking the rebound lifecycle.",
        "skills/public/critique/scripts/run_review_promotion.py: promote_attempt_metadata writes approval_eligible=true and use_class='approval' before refresh_manifest_integrity returns.",
        "Concrete stimulus: a terminal passing run reaches the manifest write, then its integrity refresh fails persistently. The exception finalization follows the same failing path, leaving the already-published approval manifest while run_live reports failed durable promotion and retains scratch."
      ],
      "id": "LIFECYCLE-002",
      "severity": "blocker",
      "summary": "Final promotion still publishes approval before its final readback succeeds."
    },
    {
      "action": "Make retry recognize and validate an already-finalized lifecycle or replace that derived carrier transactionally. Verify recovery after a failure immediately following the rebound lifecycle write.",
      "evidence": [
        "skills/public/critique/scripts/run_review_carrier.py: finalize_carrier rewrites durable lifecycle.yaml with updated paths, then performs another manifest integrity refresh.",
        "skills/public/critique/scripts/run_review_promotion.py: a retry first sends the scratch lifecycle.yaml through STORAGE.write_or_verify.",
        "skills/public/critique/scripts/run_review_promotion_storage.py: write_or_verify rejects an existing destination whose bytes differ.",
        "Concrete stimulus: let the rebound lifecycle write succeed, then fail the following refresh. Scratch retains its earlier lifecycle representation; both exception finalization and --resume-retained-attempt encounter the differing durable lifecycle before reaching the rewrite step."
      ],
      "id": "LIFECYCLE-003",
      "severity": "major",
      "summary": "A failure after lifecycle rebinding can make retained promotion permanently refuse its own prior output."
    }
  ],
  "prior_lens": "Weinberg lifecycle evidence retention, identity binding and failure-atomic cleanup",
  "prior_next_move": "Repair the three concrete lifecycle failures and obtain focused failure/retry readback. Parent retains ownership of full quality and public readback; this result does not approve release.",
  "prior_non_claims": [
    "Reviewed the supplied inline semantic bytes; no workspace edits or test execution were performed.",
    "Historical findings were independently reassessed, never inherited as approval.",
    "No whole-workflow acceptance, production-consumer proof, #764 scheduled proof, or public release readback is claimed.",
    "Goal lineage is not-goal-bound: critique review was run without a Goal Run Work Item identity.",
    "Retained, partial, failed, deferred, and timed-out evidence is not approval."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-863-bounded-lifecycle-20260912-packet.json",
  "prior_packet_sha256": "991dccac7153dd7d9002608a3a786f774d29eaa2bbe2eb38750efc0b61f71087",
  "prior_reviewed_input_identity_sha256": "7edfcaefcf2a3842d8056e92c8e11558bb954953eba2ba8c9181a9fd0eff0d7b",
  "prior_reviewed_paths": 47,
  "prior_scope": "Review the current v8.6.3 patch repairs and explicitly reassess the included prior lifecycle-final result findings as historical evidence, never inherited approval. Release workflow experiment retired because no production consumers; whole workflow acceptance remains unproven. Success: safe failure recovery and honest claims. Out of scope: #764 scheduled proof and new workflow implementation. Parent owns full quality and public readback. Require concrete changed-consumer counterexamples before blockers; do not expand into hypothetical redesign.",
  "prior_verdict": "block",
  "selected_paths": [
    "scripts/runtime_scratch.py",
    "skills/public/critique/scripts/run_review_carrier.py",
    "skills/public/critique/scripts/run_review_execution.py",
    "skills/public/critique/scripts/run_review_hold_out.py",
    "skills/public/critique/scripts/run_review_promotion.py",
    "skills/public/critique/scripts/run_review_promotion_storage.py",
    "skills/public/critique/scripts/run_review_recovery.py",
    "skills/public/critique/scripts/run_review_recovery_inputs.py",
    "tests/test_run_review_declared_path_resolution.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      ".agents/critique-adapter.yaml",
      "charness-artifacts/critique/workers/release-8-6-3-lifecycle-final/result.json",
      "docs/agent-task-runs.md",
      "docs/development.md",
      "docs/index.md",
      "scripts/gates/check_test_production_ratio.py",
      "scripts/review/critique_adapter_lib.py",
      "scripts/review/critique_artifact_paths.py",
      "scripts/review/critique_followup_scope.py",
      "scripts/review/critique_packet_lib.py",
      "scripts/review/render_critique_section_changed_surfaces.py",
      "scripts/review/reviewed_input_verification.py",
      "scripts/runtime_scratch.py",
      "scripts/runtime_scratch_cli.py",
      "scripts/runtime_scratch_promotion.py",
      "scripts/runtime_scratch_registry.py",
      "scripts/task_run/task_run_completion.py",
      "scripts/task_run/task_run_completion_next_step.py",
      "scripts/task_run/task_run_execution.py",
      "skills/public/critique/SKILL.md",
      "skills/public/critique/references/adapter-contract.md",
      "skills/public/critique/references/prepare-packet.md",
      "skills/public/critique/scripts/followup_scope_consumer.py",
      "skills/public/critique/scripts/prepare_packet.py",
      "skills/public/critique/scripts/review_followup.py",
      "skills/public/critique/scripts/review_followup_context.py",
      "skills/public/critique/scripts/review_followup_provenance.py",
      "skills/public/critique/scripts/review_followup_selection.py",
      "skills/public/critique/scripts/run_review.py",
      "skills/public/critique/scripts/run_review_carrier.py",
      "skills/public/critique/scripts/run_review_execution.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "skills/public/critique/scripts/run_review_identity.py",
      "skills/public/critique/scripts/run_review_packet.py",
      "skills/public/critique/scripts/run_review_promotion.py",
      "skills/public/critique/scripts/run_review_promotion_storage.py",
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py",
      "skills/public/critique/scripts/run_review_support.py",
      "skills/shared/scripts/reviewer_result_contract.py",
      "skills/shared/scripts/reviewer_worker_carrier_support.py",
      "tests/charness_cli/test_task_run_completion.py",
      "tests/charness_cli/test_task_run_result.py",
      "tests/test_critique_prepare_packet.py",
      "tests/test_review_followup.py",
      "tests/test_run_review_declared_path_resolution.py",
      "tests/test_runtime_scratch.py"
    ],
    "comparison_identity_sha256": "368210feeaa92a1d83566d46edc0077d2f6ff30b2bcea8660bb6444a51aac952",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-863-bounded-lifecycle-20260912",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "991dccac7153dd7d9002608a3a786f774d29eaa2bbe2eb38750efc0b61f71087",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-863-bounded-lifecycle-20260912",
        "partial_result_sha256": "9ad2b827bc41c8aabccc143887693e6857ca2542e776d9bd1f0bb00193ae162f",
        "result_sha256": "e5036ce11b048e1c5de7fa25b117ba8034de758ae0fcea421b868725747feee6",
        "source_path": "charness-artifacts/critique/workers/release-863-bounded-lifecycle-20260912/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "7edfcaefcf2a3842d8056e92c8e11558bb954953eba2ba8c9181a9fd0eff0d7b",
      "semantic_input": {
        "entries": 47,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "7edfcaefcf2a3842d8056e92c8e11558bb954953eba2ba8c9181a9fd0eff0d7b",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "skills/public/critique/scripts/run_review_carrier.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "skills/public/critique/scripts/run_review_promotion.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "unchanged_selected_paths": [
      "scripts/runtime_scratch.py",
      "skills/public/critique/scripts/run_review_execution.py",
      "skills/public/critique/scripts/run_review_promotion_storage.py",
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-863-bounded-lifecycle-20260912/partial-result.json",
  "source_sha256": "9ad2b827bc41c8aabccc143887693e6857ca2542e776d9bd1f0bb00193ae162f"
}
```

## Follow-up Producer Scope

This receipt proves the adapter-declared producer scope; it is not reviewer approval.

```json
{
  "contract": "Adapter-declared follow-up scope; selected-path sections must expose every identity-bound path, and static sections must declare that they are not path-bearing.",
  "kind": "charness.follow_up_scope_receipt.v1",
  "sections": [
    {
      "binding": "CHARNESS_CRITIQUE_REVIEWED_PATHS",
      "mode": "selected-paths",
      "path_binding": "exact-path-manifest",
      "path_check": "exact-manifest",
      "path_set_sha256": "cf791b81cbbef9063cfdd4bbdcb25003df05b97f6a8894682657a54b2b0c4826",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 9,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 9,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 9,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "scripts/runtime_scratch.py",
    "skills/public/critique/scripts/run_review_carrier.py",
    "skills/public/critique/scripts/run_review_execution.py",
    "skills/public/critique/scripts/run_review_hold_out.py",
    "skills/public/critique/scripts/run_review_promotion.py",
    "skills/public/critique/scripts/run_review_promotion_storage.py",
    "skills/public/critique/scripts/run_review_recovery.py",
    "skills/public/critique/scripts/run_review_recovery_inputs.py",
    "tests/test_run_review_declared_path_resolution.py"
  ],
  "status": "verified"
}
```

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Bound review paths for working tree: (narrow follow-up scope)
Exact reviewed-path manifest:
- scripts/runtime_scratch.py
- skills/public/critique/scripts/run_review_carrier.py
- skills/public/critique/scripts/run_review_execution.py
- skills/public/critique/scripts/run_review_hold_out.py
- skills/public/critique/scripts/run_review_promotion.py
- skills/public/critique/scripts/run_review_promotion_storage.py
- skills/public/critique/scripts/run_review_recovery.py
- skills/public/critique/scripts/run_review_recovery_inputs.py
- tests/test_run_review_declared_path_resolution.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/runtime_scratch.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_hold_out.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_hold_out.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_hold_out.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_hold_out.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/runtime_scratch.py, tests/test_run_review_declared_path_resolution.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/runtime_scratch.py, skills/public/critique/scripts/run_review_carrier.py, skills/public/critique/scripts/run_review_execution.py, skills/public/critique/scripts/run_review_hold_out.py, skills/public/critique/scripts/run_review_promotion.py, skills/public/critique/scripts/run_review_promotion_storage.py, skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
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
