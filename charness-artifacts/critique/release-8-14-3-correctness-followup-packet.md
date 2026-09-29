# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-29T09:15:02Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c`
- **Reviewed paths**: 5
  - `scripts/task_run/task_run.py`
  - `scripts/task_run/task_run_contract.py`
  - `scripts/task_run/task_run_lane_runner.py`
  - `scripts/task_run/task_run_support.py`
  - `tests/charness_cli/test_task_run_merge_checkpoint_877.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-14-3-correctness-followup-packet.json --packet-sha256 8d91b163336d620da93b1b6fd11413ddb59b03bbc0b9501f36cdc2a50fcfb0f5 --identity-sha256 6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-6-luna, reasoning_effort=xhigh, service_tier=priority`
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
    "changed_paths": 5,
    "comparison_identity_paths": [
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_git.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_plan.py",
      "scripts/task_run/task_run_scope_evidence.py",
      "scripts/task_run/task_run_support.py",
      "skills/shared/scripts/reviewer_worker_backend.py",
      "tests/charness_cli/test_task_run_merge_checkpoint_877.py",
      "tests/charness_cli/test_task_run_scope_evidence_879.py",
      "tests/quality_gates/test_reviewer_worker_backend.py"
    ],
    "comparison_identity_sha256": "d663f3fb5c40212368ad2aa3c739542c3ae8991faf5d0c805812c78213266e65",
    "prior_paths": 11
  },
  "context_size_bytes": 6486,
  "final_reviewed_input_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
  "final_selected_path_count": 5,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8-14-3-correctness",
  "prior_findings": [
    {
      "action": "Before committing a resolved merge, verify that the complete merge candidate and everything staging would include are scope-admitted. If preserving the merge requires out-of-scope content, retain the worktree and return a distinct blocker without staging or committing it. Add regression cases for out-of-scope merge changes and unrelated staged/untracked residue.",
      "evidence": [
        "scripts/task_run/task_run_lane_runner.py::_checkpoint_interrupted_lane checks only that some candidate paths are scoped before invoking _commit_merge_candidate; it does not establish that all merge and dirty paths are admitted.",
        "scripts/task_run/task_run_git.py::_commit_merge_candidate passes paths=None to _commit_lane_snapshot, which executes git add --all -- . and commits without a path restriction.",
        "Counterexample: a resolved merge changes scoped module.py while an unrelated out-of-scope file is staged, modified, or untracked. The checkpoint stages and commits that unrelated file along with the merge.",
        "tests/charness_cli/test_task_run_merge_checkpoint_877.py tests a resolved merge involving only module.py; it does not cover mixed-scope merge contents or unrelated residue."
      ],
      "id": "F1",
      "severity": "high",
      "summary": "Resolved-merge checkpointing commits out-of-scope changes, violating the pinned checkpoint discipline."
    }
  ],
  "prior_lens": "correctness and contract preservation",
  "prior_next_move": "Fix the resolved-merge scope escape, add mixed-scope regression coverage, and submit a newly bound review packet.",
  "prior_non_claims": [
    "Reviewed the eleven supplied semantic payloads; did not substitute current workspace contents.",
    "No tests or live backend executions were performed.",
    "This is not release approval or verification of packaging, worker delivery, or requested reviewer tier application.",
    "Goal evidence lineage: not-goal-bound; critique review was run without a Goal Run Work Item identity."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8-14-3-correctness-packet.json",
  "prior_packet_sha256": "b70bcfcc539aae78fff31ca37b98bdcad0a74d9e1655fb57287a2c4483bd0b4a",
  "prior_reviewed_input_identity_sha256": "77bcdf33b86992299c08edb518ffa99ec0de6c20cc705834b418c454d1936bc6",
  "prior_reviewed_paths": 11,
  "prior_scope": "v8.14.3 patch: three issue fixes (877/878/879) plus focused tests",
  "prior_verdict": "block",
  "selected_paths": [
    "scripts/task_run/task_run.py",
    "scripts/task_run/task_run_contract.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_support.py",
    "tests/charness_cli/test_task_run_merge_checkpoint_877.py"
  ],
  "selection": "changed-prior-inputs",
  "selection_receipt": {
    "comparison_identity_paths": [
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_git.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_plan.py",
      "scripts/task_run/task_run_scope_evidence.py",
      "scripts/task_run/task_run_support.py",
      "skills/shared/scripts/reviewer_worker_backend.py",
      "tests/charness_cli/test_task_run_merge_checkpoint_877.py",
      "tests/charness_cli/test_task_run_scope_evidence_879.py",
      "tests/quality_gates/test_reviewer_worker_backend.py"
    ],
    "comparison_identity_sha256": "d663f3fb5c40212368ad2aa3c739542c3ae8991faf5d0c805812c78213266e65",
    "explicit_paths": false,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8-14-3-correctness",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "b70bcfcc539aae78fff31ca37b98bdcad0a74d9e1655fb57287a2c4483bd0b4a",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8-14-3-correctness",
        "partial_result_sha256": "ff240dd122a9ddccad6992af8ddac9a7f94eee9777fcfa7811c27205258dd481",
        "result_sha256": "eeaa5a2ad269f23ab539c57aabaad5dee1908a0358507d4e44081a5abd80e467",
        "source_path": "charness-artifacts/critique/workers/release-8-14-3-correctness/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "77bcdf33b86992299c08edb518ffa99ec0de6c20cc705834b418c454d1936bc6",
      "semantic_input": {
        "entries": 11,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "77bcdf33b86992299c08edb518ffa99ec0de6c20cc705834b418c454d1936bc6",
    "selected_changed_prior_paths": [
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_support.py",
      "tests/charness_cli/test_task_run_merge_checkpoint_877.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/release-8-14-3-correctness/partial-result.json",
  "source_sha256": "ff240dd122a9ddccad6992af8ddac9a7f94eee9777fcfa7811c27205258dd481"
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
      "path_set_sha256": "a5e4648e722d86e484a21f3629a78c4260918c7f7106e51d0df716f57cec7c3d",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 5,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 5,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 5,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "scripts/task_run/task_run.py",
    "scripts/task_run/task_run_contract.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_support.py",
    "tests/charness_cli/test_task_run_merge_checkpoint_877.py"
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
- scripts/task_run/task_run.py
- scripts/task_run/task_run_contract.py
- scripts/task_run/task_run_lane_runner.py
- scripts/task_run/task_run_support.py
- tests/charness_cli/test_task_run_merge_checkpoint_877.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_contract.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_support.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_contract.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_support.py, tests/charness_cli/test_task_run_merge_checkpoint_877.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_contract.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_support.py
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
