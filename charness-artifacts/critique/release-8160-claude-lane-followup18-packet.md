# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-05T00:46:40Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00`
- **Reviewed paths**: 22
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `docs/claude-task-executor.md`
  - `scripts/core/subprocess_guard.py`
  - `scripts/task_run/task_run_brief_critique.py`
  - `scripts/task_run/task_run_claude_auth.py`
  - `scripts/task_run/task_run_claude_review.py`
  - `scripts/task_run/task_run_claude_sandbox.py`
  - `scripts/task_run/task_run_execution.py`
  - `scripts/task_run/task_run_lane_options.py`
  - `scripts/task_run/task_run_lane_runner.py`
  - `scripts/task_run/task_run_lane_signals.py`
  - `scripts/task_run/task_run_progress.py`
  - `scripts/task_run/task_run_runtime.py`
  - `scripts/worktree/worktree_exec_lib.py`
  - `skills/public/debug/scripts/debug_artifact_declarations.py`
  - `skills/public/debug/scripts/debug_artifact_state.py`
  - `skills/public/debug/scripts/plan_debug_run.py`
  - `tests/charness_cli/test_task_run_cache_custody.py`
  - `tests/charness_cli/test_task_run_claude_review.py`
  - `tests/charness_cli/test_task_run_claude_sandbox.py`
  - `tests/test_debug_plan.py`
  - `tests/test_debug_risk_class_prose.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-claude-lane-followup18-packet.json --packet-sha256 fe321e8aae48d1cc3def491daa39ea9703d57be50fcef4ea049d33548df7f1a0 --identity-sha256 aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00
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
      "scripts/core/subprocess_guard.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/public/debug/scripts/debug_artifact_state.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ],
    "comparison_identity_sha256": "75f3c79a59eda32b73923561ed202ebcae4ad8d4677cfbc0e2567eb31168ef0c",
    "new_paths": [
      "skills/public/debug/scripts/plan_debug_run.py",
      "tests/test_debug_plan.py",
      "tests/test_debug_risk_class_prose.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 19,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md"
    ],
    "unchanged_selected_paths": [
      "scripts/core/subprocess_guard.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/public/debug/scripts/debug_artifact_state.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ]
  },
  "context_size_bytes": 11346,
  "final_reviewed_input_identity_sha256": "aad5868cc70696ea12fbaf9d6e14e977725947a69abafe71dfbd466f1223de00",
  "final_selected_path_count": 22,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-claude-lane-followup17",
  "prior_findings": [
    {
      "action": "Qualify the claim to say cleanup is attempted and disclose that an unlink failure can leave the copy in the runtime.",
      "evidence": [
        "scripts/task_run/task_run_brief_critique.py calls discard_review_auth in finally, covering setup and review failures.",
        "scripts/task_run/task_run_claude_review.py implements discard_review_auth with unlink(missing_ok=True), which can raise OSError.",
        "tests/charness_cli/test_task_run_claude_review.py covers review failure and partial-copy failure, but not cleanup failure."
      ],
      "id": "R-001",
      "severity": "medium",
      "summary": "The auth-copy cleanup is attempted in a finally block, but the wording states deletion as guaranteed. If unlink fails, the copy remains."
    },
    {
      "action": "Include the planner consumer and its behavioral tests in a follow-up review, or narrow the wording to the route the supplied helpers establish.",
      "evidence": [
        "skills/public/debug/scripts/debug_artifact_declarations.py parses `external-seam (...)` as a forced class.",
        "skills/public/debug/scripts/debug_artifact_state.py keeps unresolved forced risk active in _effective_routing.",
        "The selected paths include neither the planner that consumes this route nor tests for the new-investigation behavior."
      ],
      "id": "R-002",
      "severity": "defer",
      "summary": "The supplied debug helpers identify an open forced-risk declaration and mark its interrupt route active, but the packet omits the planner consumer and behavioral tests needed to verify that a new investigation is actually interrupted."
    }
  ],
  "prior_lens": "Check changed wording against supplied code and tests, including cleanup paths and readers of the auth copy.",
  "prior_next_move": "Qualify the auth cleanup guarantee and review the debug planner consumer and behavior tests before accepting the changed claims.",
  "prior_non_claims": [
    "No tests were executed; review was limited to the supplied semantic payload.",
    "The transient cross-runtime read was assessed from sandbox mount construction, not demonstrated by a selected test.",
    "The selected input does not establish the runtime retention policy or prove cleanup when unlink itself fails."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-claude-lane-followup17-packet.json",
  "prior_packet_sha256": "ae9d5a4cb879a1171cf350c0fda1e65d3cd8f77ae9d7d84570da5949aad973df",
  "prior_reviewed_input_identity_sha256": "2c4f7ce66a561a3a02994c3ec13a989b05223cff97b153094bf6297466a3eaa7",
  "prior_reviewed_paths": 19,
  "prior_scope": "Recheck the fourth claims-round wording: notes and docs now say the runner deletes the preflight auth.json copy when the review ends, including when the review fails; until then another Claude lane can read it, and if the runner is killed or crashes during the preflight the copy stays in the lane runtime until that runtime is removed (#891). Also changed in the notes: --grant-writable already accepted Codex lanes and is refused when the executor list includes Muse; an open earlier debug record declaring a forced class such as external-seam (...) still interrupts new investigati…[truncated]",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/core/subprocess_guard.py",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_claude_auth.py",
    "scripts/task_run/task_run_claude_review.py",
    "scripts/task_run/task_run_claude_sandbox.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_lane_options.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_lane_signals.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/worktree/worktree_exec_lib.py",
    "skills/public/debug/scripts/debug_artifact_declarations.py",
    "skills/public/debug/scripts/debug_artifact_state.py",
    "skills/public/debug/scripts/plan_debug_run.py",
    "tests/charness_cli/test_task_run_cache_custody.py",
    "tests/charness_cli/test_task_run_claude_review.py",
    "tests/charness_cli/test_task_run_claude_sandbox.py",
    "tests/test_debug_plan.py",
    "tests/test_debug_risk_class_prose.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "scripts/core/subprocess_guard.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/public/debug/scripts/debug_artifact_state.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ],
    "comparison_identity_sha256": "75f3c79a59eda32b73923561ed202ebcae4ad8d4677cfbc0e2567eb31168ef0c",
    "explicit_paths": true,
    "new_paths": [
      "skills/public/debug/scripts/plan_debug_run.py",
      "tests/test_debug_plan.py",
      "tests/test_debug_risk_class_prose.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8160-claude-lane-followup17",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "ae9d5a4cb879a1171cf350c0fda1e65d3cd8f77ae9d7d84570da5949aad973df",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-claude-lane-followup17",
        "partial_result_sha256": null,
        "result_sha256": "9edf33cd1cf422f7950bb1798b53e7d88bc142457e479ee339cb1b9b1ef76eac",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "2c4f7ce66a561a3a02994c3ec13a989b05223cff97b153094bf6297466a3eaa7",
      "semantic_input": {
        "entries": 19,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "2c4f7ce66a561a3a02994c3ec13a989b05223cff97b153094bf6297466a3eaa7",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md"
    ],
    "unchanged_selected_paths": [
      "scripts/core/subprocess_guard.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/worktree/worktree_exec_lib.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/public/debug/scripts/debug_artifact_state.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8160-claude-lane-followup17/result.json",
  "source_sha256": "9edf33cd1cf422f7950bb1798b53e7d88bc142457e479ee339cb1b9b1ef76eac"
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
      "path_set_sha256": "cd43eac6ef64cba4442b2b7cf9f7dca4cbac8e3e08965be21ff67a93d615557e",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 22,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 22,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 22,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/core/subprocess_guard.py",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_claude_auth.py",
    "scripts/task_run/task_run_claude_review.py",
    "scripts/task_run/task_run_claude_sandbox.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_lane_options.py",
    "scripts/task_run/task_run_lane_runner.py",
    "scripts/task_run/task_run_lane_signals.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/worktree/worktree_exec_lib.py",
    "skills/public/debug/scripts/debug_artifact_declarations.py",
    "skills/public/debug/scripts/debug_artifact_state.py",
    "skills/public/debug/scripts/plan_debug_run.py",
    "tests/charness_cli/test_task_run_cache_custody.py",
    "tests/charness_cli/test_task_run_claude_review.py",
    "tests/charness_cli/test_task_run_claude_sandbox.py",
    "tests/test_debug_plan.py",
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
- docs/claude-task-executor.md
- scripts/core/subprocess_guard.py
- scripts/task_run/task_run_brief_critique.py
- scripts/task_run/task_run_claude_auth.py
- scripts/task_run/task_run_claude_review.py
- scripts/task_run/task_run_claude_sandbox.py
- scripts/task_run/task_run_execution.py
- scripts/task_run/task_run_lane_options.py
- scripts/task_run/task_run_lane_runner.py
- scripts/task_run/task_run_lane_signals.py
- scripts/task_run/task_run_progress.py
- scripts/task_run/task_run_runtime.py
- scripts/worktree/worktree_exec_lib.py
- skills/public/debug/scripts/debug_artifact_declarations.py
- skills/public/debug/scripts/debug_artifact_state.py
- skills/public/debug/scripts/plan_debug_run.py
- tests/charness_cli/test_task_run_cache_custody.py
- tests/charness_cli/test_task_run_claude_review.py
- tests/charness_cli/test_task_run_claude_sandbox.py
- tests/test_debug_plan.py
- tests/test_debug_risk_class_prose.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/core/subprocess_guard.py, scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_review.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_options.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_lane_signals.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/worktree/worktree_exec_lib.py, skills/public/debug/scripts/debug_artifact_declarations.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/plan_debug_run.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md, docs/claude-task-executor.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/plan_debug_run.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/plan_debug_run.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/debug/scripts/debug_artifact_declarations.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/plan_debug_run.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/core/subprocess_guard.py, scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_review.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_options.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_lane_signals.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/worktree/worktree_exec_lib.py, tests/charness_cli/test_task_run_cache_custody.py, tests/charness_cli/test_task_run_claude_review.py, tests/charness_cli/test_task_run_claude_sandbox.py, tests/test_debug_plan.py, tests/test_debug_risk_class_prose.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/core/subprocess_guard.py, scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_claude_auth.py, scripts/task_run/task_run_claude_review.py, scripts/task_run/task_run_claude_sandbox.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_lane_options.py, scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_lane_signals.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_runtime.py, scripts/worktree/worktree_exec_lib.py, skills/public/debug/scripts/debug_artifact_declarations.py, skills/public/debug/scripts/debug_artifact_state.py, skills/public/debug/scripts/plan_debug_run.py
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
