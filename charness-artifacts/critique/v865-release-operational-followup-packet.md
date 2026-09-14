# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-14T05:19:00Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `d02fc5f98dfbc4aa9ed1bad090218cc97545f0c88eeb50b495d9934a8c265bdb`
- **Reviewed paths**: 2
  - `scripts/lessons/lesson_ledger_writer_lib.py`
  - `tests/test_lesson_ledger.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v865-release-operational-followup-packet.json --packet-sha256 aff5a6cb41d9398b99aca23c2988440e99d982f46f315dfffe11a31dd016cf2d --identity-sha256 d02fc5f98dfbc4aa9ed1bad090218cc97545f0c88eeb50b495d9934a8c265bdb
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
      "tests/test_lesson_ledger.py"
    ],
    "comparison_identity_paths": [
      "scripts/core/git_checkout.py",
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "tests/test_git_checkout.py",
      "tests/test_lesson_ledger.py",
      "tests/test_reviewed_input_identity_failures.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "comparison_identity_sha256": "b05890d1283d6f873be0e9b0a0c8ee4ed5534e77a589453313cd8d3124cf37df",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 8,
    "selected_changed_prior_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "tests/test_lesson_ledger.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 6707,
  "final_reviewed_input_identity_sha256": "d02fc5f98dfbc4aa9ed1bad090218cc97545f0c88eeb50b495d9934a8c265bdb",
  "final_selected_path_count": 2,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "v865-release-operational",
  "prior_findings": [
    {
      "action": "Make the cooperative lock identity independent of discovery ceilings, or refuse writes when a ceiling would move an existing repository ledger into another lock namespace. Add a concurrent-writer regression across differing ceiling environments. If upgrading changes an existing lock location, require all old writers to finish before new writers start.",
      "evidence": [
        "lesson_ledger_writer_lib._lock_path hashes the resolved ledger path but chooses the lock directory through the ceiling-sensitive _repository_root.",
        "For /repo/inner/ledger.json, a writer without a ceiling selects runtime_root(/repo)/locks/lesson-ledger/<digest>.lock. A writer with GIT_CEILING_DIRECTORIES=/repo selects the temporary-directory fallback for the identical ledger.",
        "test_repository_root_stops_before_a_repository_at_the_ceiling explicitly establishes the latter discovery result; no supplied test establishes mutual exclusion across those two environments.",
        "Atomic replacement protects each individual replacement, but cannot serialize read-modify-write operations protected by different lock files."
      ],
      "id": "operational-1",
      "severity": "high",
      "summary": "The same ledger can acquire different locks depending on the writer's ceiling environment, allowing concurrent writes to lose updates."
    }
  ],
  "prior_lens": "operational",
  "prior_next_move": "Resolve the lock-namespace split, verify affected callers, then synchronize plugin exports and complete the packet-listed release checks before publishing v8.6.5.",
  "prior_non_claims": [
    "Reviewed only the supplied semantic bytes; no tests were executed.",
    "No approval of broader v8.6.4 changes or completed release validation.",
    "Goal lineage is not-goal-bound: critique review was run without a Goal Run Work Item identity.",
    "Requested reviewer tier application is unverified by the packet."
  ],
  "prior_packet_path": "charness-artifacts/critique/2026-09-14-v865-release-packet.json",
  "prior_packet_sha256": "e131e86af2b75378e2869de68aad85f777b3f5d27e3cf71ca04822e34765cd9f",
  "prior_reviewed_input_identity_sha256": "329366b830f1adc1a7c8f9daa5d5bbd3223b866e50efc7ee7cdc490d12b094c3",
  "prior_reviewed_paths": 8,
  "prior_scope": "v8.6.5 release critique, operational angle: ship v8.6.5 patch (ceiling-aware repo discovery centralized in git_checkout; ledger and artifact binding consume the shared walk; hold_out yields staged destinations). Judge whether the release is safe to ship: missed callers assuming pre-ceiling semantics, lock-path changes for existing installs, and any release-time step this publish needs. Broader mutation/sampler delta was covered by the v8.6.4 critique rounds with blockers fixed in-tree; this round covers only the new ceiling repair surface.",
  "prior_verdict": "block",
  "selected_paths": [
    "scripts/lessons/lesson_ledger_writer_lib.py",
    "tests/test_lesson_ledger.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "scripts/core/git_checkout.py",
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "scripts/review/reviewed_input_verification.py",
      "skills/public/critique/scripts/run_review_hold_out.py",
      "tests/test_git_checkout.py",
      "tests/test_lesson_ledger.py",
      "tests/test_reviewed_input_identity_failures.py",
      "tests/test_run_review_declared_path_resolution.py"
    ],
    "comparison_identity_sha256": "b05890d1283d6f873be0e9b0a0c8ee4ed5534e77a589453313cd8d3124cf37df",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "v865-release-operational",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "e131e86af2b75378e2869de68aad85f777b3f5d27e3cf71ca04822e34765cd9f",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "v865-release-operational",
        "partial_result_sha256": "190de3f06e63699c3c56bfa8ae26d7c68ad6bbefd0fc9cb3ce7249d8ce57e4b3",
        "result_sha256": "c32348b79a6de357a8036e48ced3af9640a96e5bac4200ac81af57fcd2f598f1",
        "source_path": "charness-artifacts/critique/workers/v865-release-operational/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "329366b830f1adc1a7c8f9daa5d5bbd3223b866e50efc7ee7cdc490d12b094c3",
      "semantic_input": {
        "entries": 8,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "329366b830f1adc1a7c8f9daa5d5bbd3223b866e50efc7ee7cdc490d12b094c3",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "scripts/lessons/lesson_ledger_writer_lib.py",
      "tests/test_lesson_ledger.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/v865-release-operational/partial-result.json",
  "source_sha256": "190de3f06e63699c3c56bfa8ae26d7c68ad6bbefd0fc9cb3ce7249d8ce57e4b3"
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
      "path_set_sha256": "3a8ea574d0fd16bb8a66f435fa0fd0096fd67a5a253754bad82506053b47db55",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 2,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 2,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 2,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "scripts/lessons/lesson_ledger_writer_lib.py",
    "tests/test_lesson_ledger.py"
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
- scripts/lessons/lesson_ledger_writer_lib.py
- tests/test_lesson_ledger.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/lessons/lesson_ledger_writer_lib.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/lessons/lesson_ledger_writer_lib.py, tests/test_lesson_ledger.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/lessons/lesson_ledger_writer_lib.py
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
