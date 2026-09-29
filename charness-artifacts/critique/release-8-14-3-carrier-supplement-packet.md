# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-29T09:17:50Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `b95ac40703419a2028558486293ada651441078003f882bdbbb202c1f16b125a`
- **Reviewed paths**: 3
  - `scripts/task_run/task_run_carrier.py`
  - `scripts/task_run/task_run_git.py`
  - `scripts/worktree/checkout_view.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8-14-3-carrier-supplement-packet.json --packet-sha256 907c5833432655f1b58145645e1bacdf09cbde39c743f9a1ce64f00f4d06d4aa --identity-sha256 b95ac40703419a2028558486293ada651441078003f882bdbbb202c1f16b125a
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
    "changed_prior_paths": [],
    "comparison_identity_paths": [
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_support.py",
      "tests/charness_cli/test_task_run_merge_checkpoint_877.py"
    ],
    "comparison_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
    "new_paths": [
      "scripts/task_run/task_run_carrier.py",
      "scripts/task_run/task_run_git.py",
      "scripts/worktree/checkout_view.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 5,
    "selected_changed_prior_paths": [],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 6017,
  "final_reviewed_input_identity_sha256": "b95ac40703419a2028558486293ada651441078003f882bdbbb202c1f16b125a",
  "final_selected_path_count": 3,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8-14-3-correctness-followup",
  "prior_findings": [
    {
      "action": "Provide identity-bound implementations of the candidate population and merge staging helpers, plus their relevant path collectors, so the guard's coverage can be compared with the actual committed population.",
      "evidence": [
        "task_run_lane_runner.py::_checkpoint_interrupted_lane compares carrier['changed_paths'] against the admitted set before calling _commit_merge_candidate.",
        "task_run_support.py delegates _candidate_carrier to task_run_carrier and _commit_merge_candidate to task_run_git; neither implementation is included in the supplied semantic bytes.",
        "The supplied regression tests assert rejection of staged and untracked residue, but no execution results are supplied. Their source alone does not establish the delegated population's completeness."
      ],
      "id": "F1-evidence",
      "severity": "evidence-gap",
      "summary": "The new guard rejects reported out-of-scope paths, but the packet does not establish that its path population covers everything the merge checkpoint commits."
    }
  ],
  "prior_lens": "recheck the F1 repair: the resolved-merge path refuses out-of-scope content without breaking in-scope merges, tip reuse, or the unresolved-merge blocker",
  "prior_next_move": "Submit a supplemental bound packet containing the population and staging owners to finish the F1 recheck.",
  "prior_non_claims": [
    "Reviewed all five supplied semantic payloads without substituting workspace contents.",
    "No tests or live backend executions were performed.",
    "This is not release approval or verification of packaging, worker delivery, or reviewer tier application.",
    "Goal evidence lineage: {\"binding\":null,\"disposition\":\"not-goal-bound\",\"draft\":null,\"goal_run\":null,\"kind\":\"charness.goal-lineage\",\"reason\":\"critique review was run without a Goal Run Work Item identity\",\"schema_version\":1,\"work_item\":null}"
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8-14-3-correctness-followup-packet.json",
  "prior_packet_sha256": "8d91b163336d620da93b1b6fd11413ddb59b03bbc0b9501f36cdc2a50fcfb0f5",
  "prior_reviewed_input_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
  "prior_reviewed_paths": 5,
  "prior_scope": "repair of F1: mixed-scope merge refusal in the interrupted-lane checkpoint",
  "prior_verdict": "defer",
  "selected_paths": [
    "scripts/task_run/task_run_carrier.py",
    "scripts/task_run/task_run_git.py",
    "scripts/worktree/checkout_view.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_support.py",
      "tests/charness_cli/test_task_run_merge_checkpoint_877.py"
    ],
    "comparison_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
    "explicit_paths": true,
    "new_paths": [
      "scripts/task_run/task_run_carrier.py",
      "scripts/task_run/task_run_git.py",
      "scripts/worktree/checkout_view.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8-14-3-correctness-followup",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "8d91b163336d620da93b1b6fd11413ddb59b03bbc0b9501f36cdc2a50fcfb0f5",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8-14-3-correctness-followup",
        "partial_result_sha256": "5c080f5209a7b4419c802174e518b1dc77ab9d3fd05354f7f8322bf5f2e94e81",
        "result_sha256": "f6a33eebc7045759742ec4b39b9823ad19c0f71e130276ef520335303c578368",
        "source_path": "charness-artifacts/critique/workers/release-8-14-3-correctness-followup/backend.stdout",
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
      "semantic_input": {
        "entries": 5,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "6d5f3fa255be6197e6e2c4443ac90b7cc90fe5d4d9d96ce773f88339e3268f2c",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/release-8-14-3-correctness-followup/partial-result.json",
  "source_sha256": "5c080f5209a7b4419c802174e518b1dc77ab9d3fd05354f7f8322bf5f2e94e81"
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
      "path_set_sha256": "34d73efad1455975101b1256f853f24723c883bac36352a1bea0f11bdc0fc8a5",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 3,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 3,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 3,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "scripts/task_run/task_run_carrier.py",
    "scripts/task_run/task_run_git.py",
    "scripts/worktree/checkout_view.py"
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
- scripts/task_run/task_run_carrier.py
- scripts/task_run/task_run_git.py
- scripts/worktree/checkout_view.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_carrier.py, scripts/task_run/task_run_git.py, scripts/worktree/checkout_view.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run_carrier.py, scripts/task_run/task_run_git.py, scripts/worktree/checkout_view.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_carrier.py, scripts/task_run/task_run_git.py, scripts/worktree/checkout_view.py
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
