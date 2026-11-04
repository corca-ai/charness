# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-04T21:59:52Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `cb9ac6a05cac45cade5b5bcad7bf11a3c184ad9abeca136b7891d454963b563f`
- **Reviewed paths**: 8
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `docs/claude-task-executor.md`
  - `scripts/task_run/task_run_claude_auth.py`
  - `scripts/task_run/task_run_claude_sandbox.py`
  - `scripts/task_run/task_run_execution.py`
  - `scripts/task_run/task_run_lane_runner.py`
  - `scripts/task_run/task_run_progress.py`
  - `scripts/task_run/task_run_runtime.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-claude-lane-followup7-packet.json --packet-sha256 582f92d40db7c3216cd60f4965d60bab84711aadcd91bace50d305593588e43d --identity-sha256 cb9ac6a05cac45cade5b5bcad7bf11a3c184ad9abeca136b7891d454963b563f
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
    "changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py"
    ],
    "comparison_identity_sha256": "023ae1b6b73e4f0c3fb88e0d89934ca983c1ab301a1374bb65bb7113dd6a3eb0",
    "new_paths": [
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_execution.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 6,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md"
    ],
    "unchanged_selected_paths": [
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py"
    ]
  },
  "context_size_bytes": 7511,
  "final_reviewed_input_identity_sha256": "cb9ac6a05cac45cade5b5bcad7bf11a3c184ad9abeca136b7891d454963b563f",
  "final_selected_path_count": 8,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-claude-lane-followup6",
  "prior_findings": [
    {
      "action": "Qualify the claim to account for separately masked home `.env*` files, or include that exception in the stated mask list.",
      "evidence": [
        "The release notes and docs say a credential file outside the named directories and files stays readable.",
        "In `task_run_claude_sandbox.py`, `sandbox_prefix` also masks every file found by `_credential_files(worktree)`. That helper additionally adds files matching `Path.home().glob(\".env*\")`, so a home credential such as `~/.env.production` is masked despite being outside `_SECRET_DIRECTORIES` and `_SECRET_FILES`.",
        "The docs later acknowledge masks for known `.env*` files, which conflicts with the unqualified readability claim."
      ],
      "id": "R-001",
      "severity": "medium",
      "summary": "The revised readability claim still misses a separate home-file mask: known home `.env*` files are masked even when they are outside the named directories and files."
    },
    {
      "action": "Reconcile the documentation with this fallback, or change the implementation so the child receives only a proxy invocation token.",
      "evidence": [
        "The release notes say provider credentials stay in a parent-side proxy; the docs say the child receives an invocation token.",
        "In `configure_claude_environment`, when none of `ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, or `ANTHROPIC_AUTH_TOKEN` is set, the code reads `~/.claude/.credentials.json` and assigns its `claudeAiOauth.accessToken` directly to `configured[\"CLAUDE_CODE_OAUTH_TOKEN\"]`.",
        "That fallback places the stored OAuth access token in the environment returned for the child, rather than keeping it solely in the proxy."
      ],
      "id": "R-002",
      "severity": "high",
      "summary": "The claim that real provider credentials stay in a parent-side proxy conflicts with the selected code’s OAuth-token fallback into the child environment."
    }
  ],
  "prior_lens": "Recheck R-001 and compare other changed note and documentation claims against the selected code.",
  "prior_next_move": "Correct the `.env*` readability exception and resolve the OAuth-token fallback claim, then recheck the revised sentences against the code.",
  "prior_non_claims": [
    "Static review of the identity-checked semantic payload only; no tests or sandbox behavior were run.",
    "The proxy implementation and test files were not among the selected inputs."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-claude-lane-followup6-packet.json",
  "prior_packet_sha256": "429df0155a62664945f3f75c89874dbf7435793aedceca27c51b0eac70aeea3e",
  "prior_reviewed_input_identity_sha256": "76886d5b8cb77ec17a1aec1d833dac0c9b012ee490d35f1b039dfd8fb207bd89",
  "prior_reviewed_paths": 6,
  "prior_scope": "Recheck R-001: the notes and docs now say the home masks are a named list of directories and files (including ~/.aws), so only a credential file outside those directories and files stays readable.",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/task_run/task_run_claude_auth.py",
    "scripts/task_run/task_run_claude_sandbox.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_runtime.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py"
    ],
    "comparison_identity_sha256": "023ae1b6b73e4f0c3fb88e0d89934ca983c1ab301a1374bb65bb7113dd6a3eb0",
    "explicit_paths": true,
    "new_paths": [
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_execution.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8160-claude-lane-followup6",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "429df0155a62664945f3f75c89874dbf7435793aedceca27c51b0eac70aeea3e",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-claude-lane-followup6",
        "partial_result_sha256": null,
        "result_sha256": "dc6f5a941fa746d985cd89de4668d1fc3d546b4e391a184be4c9517d135220f6",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "76886d5b8cb77ec17a1aec1d833dac0c9b012ee490d35f1b039dfd8fb207bd89",
      "semantic_input": {
        "entries": 6,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "76886d5b8cb77ec17a1aec1d833dac0c9b012ee490d35f1b039dfd8fb207bd89",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md"
    ],
    "unchanged_selected_paths": [
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8160-claude-lane-followup6/result.json",
  "source_sha256": "dc6f5a941fa746d985cd89de4668d1fc3d546b4e391a184be4c9517d135220f6"
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
      "path_set_sha256": "fcb5f72df78f083eb6711c9241b0a09f3db691b2d52ebf9abd2d69345bd00ebb",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 8,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 8,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 8,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/task_run/task_run_claude_auth.py",
    "scripts/task_run/task_run_claude_sandbox.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_runtime.py"
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
- charness-artifacts/release/2026-11-05-v8.16.0-notes.md
- docs/claude-task-executor.md
- scripts/task_run/task_run_claude_auth.py
- scripts/task_run/task_run_claude_sandbox.py
- scripts/task_run/task_run_execution.py
- scripts/task_run/task_run_lane_runner.py
- scripts/task_run/task_run_progress.py
- scripts/task_run/task_run_runtime.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md, docs/claude-task-executor.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py
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
