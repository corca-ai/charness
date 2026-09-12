# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-12T09:37:13Z
- **Prepared for**: release-v8.6.3-refusal-repair
- **Prepared targets**: 1
  - `v8.6.3`
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca`
- **Reviewed paths**: 4
  - `skills/public/critique/scripts/run_review_recovery.py`
  - `skills/public/critique/scripts/run_review_recovery_inputs.py`
  - `tests/test_review_retained_integrity_matrix.py`
  - `tests/test_review_runner_terminal_paths.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release863-refusal-repair-20260912-packet.json --packet-sha256 438cc4ecbaba7d5af3d3e3c28b8f688d0da01e3ad3e9d6f4bf95b22d57bdb8a6 --identity-sha256 222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca
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
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py"
    ],
    "comparison_identity_paths": [
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
    "comparison_identity_sha256": "fe9057a87e766d81846ca17f7695a635de15573dc77f683cda8088f8baef09c7",
    "new_paths": [
      "tests/test_review_retained_integrity_matrix.py",
      "tests/test_review_runner_terminal_paths.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 9,
    "selected_changed_prior_paths": [
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 6856,
  "final_reviewed_input_identity_sha256": "222a2616ec01bb4835ef5f70ebfc3f76708acc31858d684cee97a383928241ca",
  "final_selected_path_count": 4,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-863-repair-lifecycle-20260912",
  "prior_findings": [],
  "prior_lens": "lifecycle repaired consumer failure paths",
  "prior_next_move": "Accept these bounded lifecycle repairs; parent retains release authorization and remaining verification ownership.",
  "prior_non_claims": [
    "Reviewed all nine supplied inline semantic inputs; no workspace edits or test execution were performed.",
    "The reported 79 focused tests and 20 release edge tests were not independently rerun.",
    "Historical findings were reassessed as hypotheses, never inherited as approval.",
    "Classifier and authorization-consumer implementation were not supplied in this selected input and are not independently verified here.",
    "No whole-workflow acceptance, whole-host isolation, #764 scheduled proof, full quality approval, or public release readback is claimed.",
    "Retained, partial, failed, deferred, and timed-out evidence is not approval.",
    "Goal evidence lineage: {\"binding\":null,\"disposition\":\"not-goal-bound\",\"draft\":null,\"goal_run\":null,\"kind\":\"charness.goal-lineage\",\"reason\":\"critique review was run without a Goal Run Work Item identity\",\"schema_version\":1,\"work_item\":null}"
  ],
  "prior_packet_path": "charness-artifacts/critique/release-863-repair-lifecycle-20260912-packet.json",
  "prior_packet_sha256": "ff941d23eab058054fa10f359c2207516aaaafa6c4cc869ea29e6db62b966575",
  "prior_reviewed_input_identity_sha256": "eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf",
  "prior_reviewed_paths": 9,
  "prior_scope": "Bounded follow-up of your retained lifecycle findings. Four red tests reproduced the concrete failures; repaired paths plus consumers are bound here. 79 focused tests and 20 release edge tests passed. Reassess only repaired findings and direct regression risk; no new workflow implementation, whole-host isolation, #764 or full quality requests. Approval is final-manifest commit after lifecycle and integrity readback; lifecycle projection may be rewritten within the same identity-bound attempt on retry. Classifier exposes the verified generated-commit boundary to the authorizatio…[truncated]",
  "prior_verdict": "pass",
  "selected_paths": [
    "skills/public/critique/scripts/run_review_recovery.py",
    "skills/public/critique/scripts/run_review_recovery_inputs.py",
    "tests/test_review_retained_integrity_matrix.py",
    "tests/test_review_runner_terminal_paths.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
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
    "comparison_identity_sha256": "fe9057a87e766d81846ca17f7695a635de15573dc77f683cda8088f8baef09c7",
    "explicit_paths": true,
    "new_paths": [
      "tests/test_review_retained_integrity_matrix.py",
      "tests/test_review_runner_terminal_paths.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-863-repair-lifecycle-20260912",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "ff941d23eab058054fa10f359c2207516aaaafa6c4cc869ea29e6db62b966575",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-863-repair-lifecycle-20260912",
        "partial_result_sha256": "d10aa4e10a9e47ae3fc403352e14bbcac307dd8eff1dc89cf225284378ba1f04",
        "result_sha256": "5e43645580681529d982b0a755360e6a768d3f5882eecf5ede42d0c88b6f3756",
        "source_path": "charness-artifacts/critique/workers/release-863-repair-lifecycle-20260912/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf",
      "semantic_input": {
        "entries": 9,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "eec12df9d9d310c2767efc6022fab3f125d93033c68e9e14763a99fbb3f4b8cf",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "skills/public/critique/scripts/run_review_recovery.py",
      "skills/public/critique/scripts/run_review_recovery_inputs.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/release-863-repair-lifecycle-20260912/partial-result.json",
  "source_sha256": "d10aa4e10a9e47ae3fc403352e14bbcac307dd8eff1dc89cf225284378ba1f04"
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
      "path_set_sha256": "c533ef05d24cb8095e018ecf9bcb5e69557b08e6a57273cda27117f3905ba530",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 4,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 4,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 4,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "skills/public/critique/scripts/run_review_recovery.py",
    "skills/public/critique/scripts/run_review_recovery_inputs.py",
    "tests/test_review_retained_integrity_matrix.py",
    "tests/test_review_runner_terminal_paths.py"
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
- skills/public/critique/scripts/run_review_recovery.py
- skills/public/critique/scripts/run_review_recovery_inputs.py
- tests/test_review_retained_integrity_matrix.py
- tests/test_review_runner_terminal_paths.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: tests/test_review_retained_integrity_matrix.py, tests/test_review_runner_terminal_paths.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/critique/scripts/run_review_recovery.py, skills/public/critique/scripts/run_review_recovery_inputs.py
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
