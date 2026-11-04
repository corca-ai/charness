# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-04T20:41:16Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148`
- **Reviewed paths**: 8
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `scripts/runtime_scratch.py`
  - `skills/public/debug/scripts/debug_artifact_declarations.py`
  - `skills/shared/scripts/reviewer_process.py`
  - `tests/charness_cli/test_codex_cache_refresh.py`
  - `tests/charness_cli/test_entry_cov_e4_874.py`
  - `tests/quality_gates/test_semantic_review_worker_timeout.py`
  - `tests/test_debug_risk_class_prose.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-rest-followup1-packet.json --packet-sha256 801bc917c58f460c0e8e5650c5f8324636c49995930cb112bf2a2cfbb035504c --identity-sha256 40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148
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
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "scripts/cli/install_delivery.py",
      "scripts/review/critique_packet_lib.py",
      "scripts/runtime_bootstrap.py",
      "scripts/runtime_scratch.py",
      "scripts/runtime_scratch_registry.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py",
      "tests/charness_cli/test_task_run_implementation_lane.py",
      "tests/charness_cli/test_task_run_muse_stream_886.py",
      "tests/charness_cli/test_worktree_exec.py",
      "tests/coverage_debt/test_batch10.py",
      "tests/quality_gates/fixtures/release_publish_fake_git.sh",
      "tests/quality_gates/support.py",
      "tests/quality_gates/test_chmod_allowlist.py",
      "tests/quality_gates/test_quality_runner.py",
      "tests/quality_gates/test_release_publish_fake_git.py",
      "tests/test_critique_prepare_packet.py",
      "tests/test_debug_risk_class_prose.py",
      "tests/test_reviewer_process_shell_line.py",
      "tests/test_runtime_root_snapshot.py",
      "tests/test_runtime_scratch.py"
    ],
    "comparison_identity_sha256": "c07d7e41ffa544a98f9b0b83cdbfc9307a5d21b3047c8c09136dc93573ec7f75",
    "new_paths": [
      "tests/quality_gates/test_semantic_review_worker_timeout.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 27,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py"
    ],
    "unchanged_selected_paths": [
      "scripts/runtime_scratch.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/test_debug_risk_class_prose.py"
    ]
  },
  "context_size_bytes": 11868,
  "final_reviewed_input_identity_sha256": "40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148",
  "final_selected_path_count": 8,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-rest",
  "prior_findings": [
    {
      "action": "Avoid cmd.exe parsing for this invocation, or add cmd.exe-specific escaping and tests for metacharacters before claiming this path is portable.",
      "evidence": [
        "skills/shared/scripts/reviewer_process.py: shell_command_line uses subprocess.list2cmdline for Windows, and run_bounded_process passes the resulting string to run_monitored_phase with shell=True.",
        "tests/test_reviewer_process_shell_line.py: the Windows case covers paths with spaces only; it does not exercise cmd.exe metacharacters."
      ],
      "id": "windows-cmd-quoting",
      "severity": "high",
      "summary": "The Windows command builder uses Windows argv quoting, then passes the result through cmd.exe with shell=True. That does not escape cmd.exe metacharacters, so valid paths or arguments containing characters such as & or % can be split or expanded. The note's claim that commands are quoted for cmd.exe overstates what the code does."
    },
    {
      "action": "Add a mixed known-forced and unknown-class case that pins the intended planner behavior, then qualify the note or adjust the planner and helper to match it.",
      "evidence": [
        "skills/public/debug/scripts/debug_artifact_declarations.py: _recovered_risk_classes preserves allowed classes; risk_scope_established permits a parse error when forced is true.",
        "tests/test_debug_risk_class_prose.py: unknown-class cases cover none, bogus and prose-first values, but not a forced class combined with an unknown class."
      ],
      "id": "risk-unknown-with-forced-class",
      "severity": "medium",
      "summary": "The note says any unknown Risk Class still routes to repair. The declaration helper recovers recognized classes after a parse error, and marks the risk scope established when one of those classes forces an interrupt. For example, external-seam, bogus is not covered by the unknown-class tests and does not follow the helper's general repair signal."
    },
    {
      "action": "Include the owning implementation and behavior tests in the review evidence, or defer approval of those note claims until they are independently verified.",
      "evidence": [
        "The supplied sources include scripts/worktree/worktree_exec_lib.py and lane progress modules, but no Claude executor, task status command, or lane environment builder for the Go cache and writable-root claims.",
        "No supplied test exercises command-duration events or task status --commands against a running lane."
      ],
      "id": "unverified-release-note-claims",
      "severity": "defer",
      "summary": "Several substantial notes claims have no corresponding implementation or test in the supplied semantic input: Claude executor sandbox and grant behavior, command duration and live status observation, Go cache overrides, and Codex writable-root filtering. The supplied lane environment and progress files establish only part of those behaviors."
    },
    {
      "action": "Narrow the test-coverage claim or add a focused test that forces and checks the lock fallback.",
      "evidence": [
        "scripts/runtime_scratch.py: the Windows locking fallback is created when importing fcntl fails.",
        "tests/test_runtime_scratch.py: test_windows_branch_chmods_files_before_unlink exercises chmod behavior; it does not force or test the msvcrt lock fallback and is marked skipif os.name == \"nt\".",
        "The notes disclose Linux-only CI and no Windows-host run, but still say unit tests cover these paths."
      ],
      "id": "windows-lock-test-coverage",
      "severity": "medium",
      "summary": "The note says unit tests cover the Windows portability paths, but the supplied tests do not exercise the msvcrt byte-range lock fallback on this Linux-only CI. The Windows chmod test covers a different branch and is explicitly skipped on Windows."
    }
  ],
  "prior_lens": "Minto claims and Weinberg layer",
  "prior_next_move": "Fix or qualify the cmd.exe quoting claim, pin the mixed unknown-risk case, and supply evidence for the deferred lane claims before treating the notes as release-ready.",
  "prior_non_claims": [
    "This review does not claim that the release was run on Windows.",
    "The supplied input does not include validate_debug_artifact.py, so its strictness claim is not independently verified here.",
    "The packet has no structured prepared_targets, so no per-target observations are made."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-rest-packet.json",
  "prior_packet_sha256": "36653a6733dc65a54f6170501d603358bd71c6246a666f4b94f7537c5e1d662c",
  "prior_reviewed_input_identity_sha256": "801153337b2daf6287e9c12aedaddd6759122fd9e78328fd3df30a7954a28b8b",
  "prior_reviewed_paths": 27,
  "prior_scope": "Release critique for charness v8.16.0 (minor), part 2 of 2: the debug planner Risk Class fix, lane environment and progress-observation changes, Windows portability repairs, release-gate test repairs, and the v8.16.0 notes. Files are the current tree; git diff v8.15.0..HEAD shows what changed.",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "scripts/runtime_scratch.py",
    "skills/public/debug/scripts/debug_artifact_declarations.py",
    "skills/shared/scripts/reviewer_process.py",
    "tests/charness_cli/test_codex_cache_refresh.py",
    "tests/charness_cli/test_entry_cov_e4_874.py",
    "tests/quality_gates/test_semantic_review_worker_timeout.py",
    "tests/test_debug_risk_class_prose.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "scripts/cli/install_delivery.py",
      "scripts/review/critique_packet_lib.py",
      "scripts/runtime_bootstrap.py",
      "scripts/runtime_scratch.py",
      "scripts/runtime_scratch_registry.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py",
      "tests/charness_cli/test_task_run_implementation_lane.py",
      "tests/charness_cli/test_task_run_muse_stream_886.py",
      "tests/charness_cli/test_worktree_exec.py",
      "tests/coverage_debt/test_batch10.py",
      "tests/quality_gates/fixtures/release_publish_fake_git.sh",
      "tests/quality_gates/support.py",
      "tests/quality_gates/test_chmod_allowlist.py",
      "tests/quality_gates/test_quality_runner.py",
      "tests/quality_gates/test_release_publish_fake_git.py",
      "tests/test_critique_prepare_packet.py",
      "tests/test_debug_risk_class_prose.py",
      "tests/test_reviewer_process_shell_line.py",
      "tests/test_runtime_root_snapshot.py",
      "tests/test_runtime_scratch.py"
    ],
    "comparison_identity_sha256": "c07d7e41ffa544a98f9b0b83cdbfc9307a5d21b3047c8c09136dc93573ec7f75",
    "explicit_paths": true,
    "new_paths": [
      "tests/quality_gates/test_semantic_review_worker_timeout.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8160-rest",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "36653a6733dc65a54f6170501d603358bd71c6246a666f4b94f7537c5e1d662c",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-rest",
        "partial_result_sha256": null,
        "result_sha256": "1931350500ab745326172db255eac7fc1c3027161de6eb2d309875ed0ca42d8f",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "801153337b2daf6287e9c12aedaddd6759122fd9e78328fd3df30a7954a28b8b",
      "semantic_input": {
        "entries": 27,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "801153337b2daf6287e9c12aedaddd6759122fd9e78328fd3df30a7954a28b8b",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py"
    ],
    "unchanged_selected_paths": [
      "scripts/runtime_scratch.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/test_debug_risk_class_prose.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8160-rest/result.json",
  "source_sha256": "1931350500ab745326172db255eac7fc1c3027161de6eb2d309875ed0ca42d8f"
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
      "path_set_sha256": "c7ad4b0ac20a5cca6e1c3a1af7f50816d69bcf2194f3eb280146391aaae4ce80",
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
    "scripts/runtime_scratch.py",
    "skills/public/debug/scripts/debug_artifact_declarations.py",
    "skills/shared/scripts/reviewer_process.py",
    "tests/charness_cli/test_codex_cache_refresh.py",
    "tests/charness_cli/test_entry_cov_e4_874.py",
    "tests/quality_gates/test_semantic_review_worker_timeout.py",
    "tests/test_debug_risk_class_prose.py"
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
- scripts/runtime_scratch.py
- skills/public/debug/scripts/debug_artifact_declarations.py
- skills/shared/scripts/reviewer_process.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/charness_cli/test_entry_cov_e4_874.py
- tests/quality_gates/test_semantic_review_worker_timeout.py
- tests/test_debug_risk_class_prose.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/runtime_scratch.py, skills/public/debug/scripts/debug_artifact_declarations.py, skills/shared/scripts/reviewer_process.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/shared/scripts/reviewer_process.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/shared/scripts/reviewer_process.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/shared/scripts/reviewer_process.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/runtime_scratch.py, tests/charness_cli/test_codex_cache_refresh.py, tests/charness_cli/test_entry_cov_e4_874.py, tests/quality_gates/test_semantic_review_worker_timeout.py, tests/test_debug_risk_class_prose.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/runtime_scratch.py, skills/public/debug/scripts/debug_artifact_declarations.py
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
