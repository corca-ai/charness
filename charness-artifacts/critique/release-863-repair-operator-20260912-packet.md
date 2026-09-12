# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-12T08:47:53Z
- **Prepared for**: working tree
- **Prepared targets**: 1
  - `v8.6.3`
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `28c436ccd78e8d1da2f2dd62be472b8791856fb98e5028db4687ecd5b9d5e159`
- **Reviewed paths**: 7
  - `charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
  - `skills/public/release/scripts/publish_release_resume_state.py`
  - `tests/quality_gates/test_release_resume_edge_coverage.py`
  - `tests/quality_gates/test_release_resume_state_validation.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-863-repair-operator-20260912-packet.json --packet-sha256 0854e56836daec8ff5df94f77632c1328ef06ef5109d9a7c95703f49e0291cea --identity-sha256 28c436ccd78e8d1da2f2dd62be472b8791856fb98e5028db4687ecd5b9d5e159
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
      "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
      "skills/public/release/scripts/publish_release_resume.py",
      "skills/public/release/scripts/publish_release_resume_state.py",
      "tests/quality_gates/test_release_resume_edge_coverage.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/critique/workers/release-8-6-3-operator-final/result.json",
      "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
      "charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json",
      "charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md",
      "docs/release-workflow-dogfood.md",
      "scripts/agent-runtime/codex-eval-runtime.mjs",
      "scripts/agent-runtime/run-local-eval-test.mjs",
      "scripts/evidence/probe_stimulus_replay.py",
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/plugin_export/validate_packaging_install_surface.py",
      "scripts/prepush_close_keyword_guard.py",
      "scripts/run_quality_engine.py",
      "scripts/run_quality_engine_runtime.py",
      "scripts/support_sync_lib.py",
      "skills/public/quality/scripts/check_provenance_contract.py",
      "skills/public/quality/scripts/inventory_empty_scope_honesty.py",
      "skills/public/release/scripts/check_fresh_checkout_probes.py",
      "skills/public/release/scripts/publish_release_artifact.py",
      "skills/public/release/scripts/publish_release_common.py",
      "skills/public/release/scripts/publish_release_resume.py",
      "skills/public/release/scripts/publish_release_resume_closeout.py",
      "skills/public/release/scripts/publish_release_resume_publish.py",
      "skills/public/release/scripts/publish_release_resume_state.py",
      "skills/support/markdown-preview/scripts/markdown_preview_render.py",
      "tests/agent-runtime/native.test.mjs",
      "tests/control_plane/test_support_sync_helpers.py",
      "tests/quality_gates/quality_runner_seed.py",
      "tests/quality_gates/support.py",
      "tests/quality_gates/test_empty_scope_honesty_inventory.py",
      "tests/quality_gates/test_packaging_validation.py",
      "tests/quality_gates/test_prepush_close_keyword_guard.py",
      "tests/quality_gates/test_quality_runner.py",
      "tests/quality_gates/test_release_quality_status_binding.py",
      "tests/quality_gates/test_release_resume_edge_coverage.py",
      "tests/quality_gates/test_release_resume_state_validation.py",
      "tests/quality_gates/test_release_resume_surface_revalidation.py",
      "tests/quality_gates/test_semantic_review_command.py",
      "tests/test_lesson_ledger.py"
    ],
    "comparison_identity_sha256": "cecb45342f4a8294ded816856e154d1f25a19b45a39569805f7e58eea462355d",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 38,
    "selected_changed_prior_paths": [
      "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
      "skills/public/release/scripts/publish_release_resume.py",
      "skills/public/release/scripts/publish_release_resume_state.py",
      "tests/quality_gates/test_release_resume_edge_coverage.py"
    ],
    "unchanged_selected_paths": [
      "skills/public/release/scripts/publish_release_resume_closeout.py",
      "skills/public/release/scripts/publish_release_resume_publish.py",
      "tests/quality_gates/test_release_resume_state_validation.py"
    ]
  },
  "context_size_bytes": 12449,
  "final_reviewed_input_identity_sha256": "28c436ccd78e8d1da2f2dd62be472b8791856fb98e5028db4687ecd5b9d5e159",
  "final_selected_path_count": 7,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-863-bounded-operator-20260912",
  "prior_findings": [
    {
      "action": "Make closeout authorization validate the same bounded generated-commit ancestry recognized by the classifier, including the actual permitted remote branch boundary. Add a consumer regression that feeds classification into assert_resumable and closeout recovery for P -> R -> C -> carrier and its final commit.",
      "evidence": [
        "publish_release_resume_publish.py invokes commit_artifact_before_push after quality and receipt promotion, permitting generated commit C after claims evidence R.",
        "publish_release_resume_state.py::_is_claims_evidence walks C and classifies P -> R -> C -> carrier as post-publication-claims-carrier, while binding claims_evidence_commit to R.",
        "publish_release_resume.py::_assert_post_publication_resumable then checks parent_sha == claims_evidence_commit. For this sequence C != R, so it raises 'claims carrier is not directly based on its claims evidence'. The final phase similarly compares the immediate grandparent against R.",
        "test_the_claims_carrier_still_classifies_across_the_resumes_own_artifact_commit verifies classification only; it does not pass that result through assert_resumable. Remote-branch validation also excludes C when C is the published branch tip before the carrier push."
      ],
      "id": "REC-001",
      "severity": "blocker",
      "summary": "Generated artifact commits remain an unrecoverable boundary between claims evidence and closeout."
    }
  ],
  "prior_lens": "Gawande operational release recovery and Minto honest claims",
  "prior_next_move": "Repair REC-001 and review the resulting consumer regression. Parent retains ownership of full quality, release-specific probe evidence, and public readback.",
  "prior_non_claims": [
    "Reviewed only the supplied semantic bytes; no workspace inspection, edits, test execution, or live publication readback.",
    "Prior operator-final findings were independently reassessed as historical evidence, never inherited approval.",
    "Whole release-workflow acceptance remains unproven; experiment deletion was not independently verified from a bound deletion manifest.",
    "#764 scheduled proof and new workflow implementation are outside scope.",
    "Goal lineage is not-goal-bound; no Goal Run completion is claimed."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-863-bounded-operator-20260912-packet.json",
  "prior_packet_sha256": "9bbfe16db0d72d13d0edafa6106acbe852a6f5dda4e93a459c962c6484095e05",
  "prior_reviewed_input_identity_sha256": "79f0cfeba5700e9adc8dffea8717bb31b43a04ecd659f0b1a551b6f0a1f75ee3",
  "prior_reviewed_paths": 38,
  "prior_scope": "Review the current v8.6.3 patch repairs and explicitly reassess the included prior operator-final result findings as historical evidence, never inherited approval. Release workflow experiment retired because no production consumers; whole workflow acceptance remains unproven. Success: safe failure recovery and honest claims. Out of scope: #764 scheduled proof and new workflow implementation. Parent owns full quality and public readback. Require concrete changed-consumer counterexamples before blockers; do not expand into hypothetical redesign.",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
    "skills/public/release/scripts/publish_release_resume.py",
    "skills/public/release/scripts/publish_release_resume_closeout.py",
    "skills/public/release/scripts/publish_release_resume_publish.py",
    "skills/public/release/scripts/publish_release_resume_state.py",
    "tests/quality_gates/test_release_resume_edge_coverage.py",
    "tests/quality_gates/test_release_resume_state_validation.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/critique/workers/release-8-6-3-operator-final/result.json",
      "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
      "charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json",
      "charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md",
      "docs/release-workflow-dogfood.md",
      "scripts/agent-runtime/codex-eval-runtime.mjs",
      "scripts/agent-runtime/run-local-eval-test.mjs",
      "scripts/evidence/probe_stimulus_replay.py",
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/plugin_export/validate_packaging_install_surface.py",
      "scripts/prepush_close_keyword_guard.py",
      "scripts/run_quality_engine.py",
      "scripts/run_quality_engine_runtime.py",
      "scripts/support_sync_lib.py",
      "skills/public/quality/scripts/check_provenance_contract.py",
      "skills/public/quality/scripts/inventory_empty_scope_honesty.py",
      "skills/public/release/scripts/check_fresh_checkout_probes.py",
      "skills/public/release/scripts/publish_release_artifact.py",
      "skills/public/release/scripts/publish_release_common.py",
      "skills/public/release/scripts/publish_release_resume.py",
      "skills/public/release/scripts/publish_release_resume_closeout.py",
      "skills/public/release/scripts/publish_release_resume_publish.py",
      "skills/public/release/scripts/publish_release_resume_state.py",
      "skills/support/markdown-preview/scripts/markdown_preview_render.py",
      "tests/agent-runtime/native.test.mjs",
      "tests/control_plane/test_support_sync_helpers.py",
      "tests/quality_gates/quality_runner_seed.py",
      "tests/quality_gates/support.py",
      "tests/quality_gates/test_empty_scope_honesty_inventory.py",
      "tests/quality_gates/test_packaging_validation.py",
      "tests/quality_gates/test_prepush_close_keyword_guard.py",
      "tests/quality_gates/test_quality_runner.py",
      "tests/quality_gates/test_release_quality_status_binding.py",
      "tests/quality_gates/test_release_resume_edge_coverage.py",
      "tests/quality_gates/test_release_resume_state_validation.py",
      "tests/quality_gates/test_release_resume_surface_revalidation.py",
      "tests/quality_gates/test_semantic_review_command.py",
      "tests/test_lesson_ledger.py"
    ],
    "comparison_identity_sha256": "cecb45342f4a8294ded816856e154d1f25a19b45a39569805f7e58eea462355d",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-863-bounded-operator-20260912",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "9bbfe16db0d72d13d0edafa6106acbe852a6f5dda4e93a459c962c6484095e05",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-863-bounded-operator-20260912",
        "partial_result_sha256": "0f444017e0c49c4e98612fdfcb021dcf4c242655260f5e04be298dcf426fa093",
        "result_sha256": "53280b83ee92ec091b3e798abc226ee7d55c5edb88a7e3631c07cee327490a9d",
        "source_path": "charness-artifacts/critique/workers/release-863-bounded-operator-20260912/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "79f0cfeba5700e9adc8dffea8717bb31b43a04ecd659f0b1a551b6f0a1f75ee3",
      "semantic_input": {
        "entries": 38,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "79f0cfeba5700e9adc8dffea8717bb31b43a04ecd659f0b1a551b6f0a1f75ee3",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
      "skills/public/release/scripts/publish_release_resume.py",
      "skills/public/release/scripts/publish_release_resume_state.py",
      "tests/quality_gates/test_release_resume_edge_coverage.py"
    ],
    "unchanged_selected_paths": [
      "skills/public/release/scripts/publish_release_resume_closeout.py",
      "skills/public/release/scripts/publish_release_resume_publish.py",
      "tests/quality_gates/test_release_resume_state_validation.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-863-bounded-operator-20260912/partial-result.json",
  "source_sha256": "0f444017e0c49c4e98612fdfcb021dcf4c242655260f5e04be298dcf426fa093"
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
      "path_set_sha256": "264f0be3001009f6d5b30039c2bbd7d4afbb20ffdbff5c1f7a54439aa21cb9d4",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 7,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 7,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 7,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md",
    "skills/public/release/scripts/publish_release_resume.py",
    "skills/public/release/scripts/publish_release_resume_closeout.py",
    "skills/public/release/scripts/publish_release_resume_publish.py",
    "skills/public/release/scripts/publish_release_resume_state.py",
    "tests/quality_gates/test_release_resume_edge_coverage.py",
    "tests/quality_gates/test_release_resume_state_validation.py"
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
- charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md
- skills/public/release/scripts/publish_release_resume.py
- skills/public/release/scripts/publish_release_resume_closeout.py
- skills/public/release/scripts/publish_release_resume_publish.py
- skills/public/release/scripts/publish_release_resume_state.py
- tests/quality_gates/test_release_resume_edge_coverage.py
- tests/quality_gates/test_release_resume_state_validation.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md
  sync: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --check
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_release_resume_edge_coverage.py, tests/quality_gates/test_release_resume_state_validation.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
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
