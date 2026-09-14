# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-14T05:07:38Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `1ecda7e64089945046c84335dadeae042e37ef79875c990ab656d4f1f0d57293`
- **Reviewed paths**: 6
  - `scripts/core/git_checkout.py`
  - `scripts/lessons/lesson_ledger_writer_lib.py`
  - `scripts/review/reviewed_input_verification.py`
  - `tests/test_git_checkout.py`
  - `tests/test_lesson_ledger.py`
  - `tests/test_reviewed_input_identity_failures.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v865-delta-operational-followup-packet.json --packet-sha256 5c9c61f8ee888026d87f31a7d9510e665f1a08e100521e5ec00200fa5ab643fd --identity-sha256 1ecda7e64089945046c84335dadeae042e37ef79875c990ab656d4f1f0d57293
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
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "tests/test_lesson_ledger.py"
    ],
    "comparison_identity_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "tests/test_lesson_ledger.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "comparison_identity_sha256": "735b425246101a32b1badaafb07cd80ae5ed0935fe06284fba76642786f21b0d",
    "new_paths": [
      "scripts/core/git_checkout.py",
      "tests/test_git_checkout.py",
      "tests/test_reviewed_input_identity_failures.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 5,
    "selected_changed_prior_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "tests/test_lesson_ledger.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 6968,
  "final_reviewed_input_identity_sha256": "1ecda7e64089945046c84335dadeae042e37ef79875c990ab656d4f1f0d57293",
  "final_selected_path_count": 6,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "v865-delta-operational",
  "prior_findings": [
    {
      "action": "Stop before inspecting a ceiling ancestor, preserving appropriate starting-directory behavior, and add a repository-at-ceiling regression case.",
      "evidence": [
        "scripts/lessons/lesson_ledger_writer_lib.py::_repository_root calls git_dir_at(candidate) before checking whether candidate is in ceilings.",
        "For a ledger below /outer/inner with GIT_CEILING_DIRECTORIES=/outer and a valid /outer/.git, discovery returns /outer instead of stopping before inspecting that ancestor.",
        "test_repository_root_stops_at_the_ceiling places the repository above the ceiling, leaving the repository-at-ceiling case uncovered."
      ],
      "id": "operational-1",
      "severity": "high",
      "summary": "Ledger discovery still selects a repository at the ceiling boundary."
    },
    {
      "action": "Apply ceiling-aware discovery to the ancestor fallback and test an artifact below a ceiling with an unrelated valid repository above it.",
      "evidence": [
        "scripts/review/reviewed_input_verification.py::verify_artifact_binding scans all artifact ancestors using _git_checkout.git_dir_at(parent).",
        "The ancestor scan has no GIT_CEILING_DIRECTORIES check, so when the packet-layout shortcut misses it can select an unrelated real repository beyond the ceiling."
      ],
      "id": "operational-2",
      "severity": "medium",
      "summary": "Artifact ancestor discovery does not honor ceilings."
    }
  ],
  "prior_lens": "operational",
  "prior_next_move": "Fix both ceiling cases, verify wrapper propagation and affected lock namespaces, then regenerate exports and run the declared focused and packaging checks before renewed review.",
  "prior_non_claims": [
    "Reviewed only the five inline semantic files; no workspace edits or test execution.",
    "No exhaustive caller audit, installed-layout verification, or release approval.",
    "No structured prepared targets were supplied.",
    "Goal lineage is not-goal-bound: critique review was run without a Goal Run Work Item identity."
  ],
  "prior_packet_path": "charness-artifacts/critique/2026-09-14-v865-delta-packet.json",
  "prior_packet_sha256": "ff341884c750e47dd3a482918233de1c8563b33b2be5fcac78364fee7bd86f38",
  "prior_reviewed_input_identity_sha256": "e61c26453bb6fc0d116e022a417a5a40b513aa810fcdf9a6b17d3cdb4708631a",
  "prior_reviewed_paths": 5,
  "prior_scope": "v8.6.5 delta review, operational angle: repo-root discovery now requires a real administration directory and honors ceilings; hold_out yields staged destinations for per-owner assertions. Look for missed callers still assuming bare-marker or global-count semantics, lock-path changes for existing installs, and any release-time step this delta needs.",
  "prior_verdict": "block",
  "selected_paths": [
    "scripts/core/git_checkout.py",
    "scripts/lessons/lesson_ledger_writer_lib.py",
    "scripts/review/reviewed_input_verification.py",
    "tests/test_git_checkout.py",
    "tests/test_lesson_ledger.py",
    "tests/test_reviewed_input_identity_failures.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "tests/test_lesson_ledger.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "comparison_identity_sha256": "735b425246101a32b1badaafb07cd80ae5ed0935fe06284fba76642786f21b0d",
    "explicit_paths": true,
    "new_paths": [
      "scripts/core/git_checkout.py",
      "tests/test_git_checkout.py",
      "tests/test_reviewed_input_identity_failures.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "v865-delta-operational",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "ff341884c750e47dd3a482918233de1c8563b33b2be5fcac78364fee7bd86f38",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "v865-delta-operational",
        "partial_result_sha256": "a76ae7a6f1f436cfdbf0831687e8177ac60789faf8eb3192f1a0109108787e91",
        "result_sha256": "ac2585815112cbcf21665a41212c28f33ac739ff62a7198786e77e640ebefe5e",
        "source_path": "charness-artifacts/critique/workers/v865-delta-operational/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "e61c26453bb6fc0d116e022a417a5a40b513aa810fcdf9a6b17d3cdb4708631a",
      "semantic_input": {
        "entries": 5,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "e61c26453bb6fc0d116e022a417a5a40b513aa810fcdf9a6b17d3cdb4708631a",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "tests/test_lesson_ledger.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/v865-delta-operational/partial-result.json",
  "source_sha256": "a76ae7a6f1f436cfdbf0831687e8177ac60789faf8eb3192f1a0109108787e91"
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
      "path_set_sha256": "1d7de930a5832f9d4aea5b63eb7831bd1ccb9edcb5d1cb838d61f6242b302e5b",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 6,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 6,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 6,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "scripts/core/git_checkout.py",
    "scripts/lessons/lesson_ledger_writer_lib.py",
    "scripts/review/reviewed_input_verification.py",
    "tests/test_git_checkout.py",
    "tests/test_lesson_ledger.py",
    "tests/test_reviewed_input_identity_failures.py"
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
- scripts/core/git_checkout.py
- scripts/lessons/lesson_ledger_writer_lib.py
- scripts/review/reviewed_input_verification.py
- tests/test_git_checkout.py
- tests/test_lesson_ledger.py
- tests/test_reviewed_input_identity_failures.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/core/git_checkout.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/review/reviewed_input_verification.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/core/git_checkout.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/review/reviewed_input_verification.py, tests/test_git_checkout.py, tests/test_lesson_ledger.py, tests/test_reviewed_input_identity_failures.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/core/git_checkout.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/review/reviewed_input_verification.py
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
