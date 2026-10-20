# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T12:14:52Z
- **Prepared for**: release-8150-final-followup
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `685426898746e57610c268e23bff93c0f5ca47b8885aad1edc3421bbda12a337`
- **Reviewed paths**: 6
  - `charness-artifacts/release/2026-10-20-v8.15.0-notes.md`
  - `charness-artifacts/spec/lane-progress-rule.md`
  - `scripts/task_run/task_run_progress.py`
  - `skills/public/debug/scripts/debug_followup_routing.py`
  - `tests/charness_cli/test_task_run_progress_preemption.py`
  - `tests/test_debug_scaffold.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup-packet.json --packet-sha256 0a1c4dd99a4135eb06d37ead34af2ca53e2754363a517554327d249a109db2de --identity-sha256 685426898746e57610c268e23bff93c0f5ca47b8885aad1edc3421bbda12a337
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
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/test_debug_scaffold.py"
    ],
    "comparison_identity_paths": [
      "charness",
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "docs/agent-task-runs.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_attempts.py",
      "scripts/task_run/task_run_detach.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_plan.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_implementation_lane.py",
      "tests/charness_cli/test_task_run_muse_executor.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/charness_cli/test_task_run_steer.py",
      "tests/test_debug_scaffold.py"
    ],
    "comparison_identity_sha256": "3bbb68abe9ab8c4babc36ac5761afb5891378de8afeafeea03c70c48aa81ced0",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 27,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/test_debug_scaffold.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 12597,
  "final_reviewed_input_identity_sha256": "685426898746e57610c268e23bff93c0f5ca47b8885aad1edc3421bbda12a337",
  "final_selected_path_count": 6,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8150-final",
  "prior_findings": [
    {
      "action": "Before lock-in, define how consumers protect legitimate commands longer than the default window, and state that requirement in the launcher guidance.",
      "evidence": [
        "scripts/task_run/task_run_progress_rule.py: an in-flight command is deferred while young, but on the next no-progress check the rule delivers the checkpoint request and preempts it.",
        "scripts/task_run/task_run_execution.py: a preemption kills the executor process group; the default window is 1200 seconds, so a command with no other observable progress can be killed after roughly two windows.",
        "charness-artifacts/spec/lane-progress-rule.md says to set W above the longest legitimate command, but the release Update section does not tell launchers to account for that."
      ],
      "id": "R-001",
      "severity": "high",
      "summary": "The default progress rule can kill a productive long-running command."
    },
    {
      "action": "Reject negative window values or fall back to the positive default. If the documented zero opt-out remains, make the resulting unbounded behavior an explicit launcher decision paired with a hard timeout.",
      "evidence": [
        "scripts/task_run/task_run_progress.py parses the progress-window environment value through _env_seconds without rejecting negative finite values.",
        "scripts/task_run/task_run_progress_rule.py returns no action when window_seconds <= 0; for non-require-change lanes, build_progress_watch returns None for a nonpositive window.",
        "With --timeout-seconds omitted, a require-change lane can also have its separate first-edit budget disabled with --no-progress-seconds 0, leaving no effective stop."
      ],
      "id": "R-002",
      "severity": "high",
      "summary": "A negative progress window silently disables the only general lane bound after the timeout default is removed."
    },
    {
      "action": "Use an injective lane identifier or add a stable hash of the original branch or lane id to the record name, and add collision cases to the tests.",
      "evidence": [
        "skills/public/debug/scripts/debug_followup_routing.py lowercases lane tokens and replaces runs of non-alphanumeric characters with hyphens.",
        "Distinct valid task branches such as task/foo_bar and task/foo-bar both produce the token foo-bar; task/Foo and task/foo also collapse to the same token.",
        "tests/test_debug_scaffold.py checks several token examples but does not exercise colliding lane identities."
      ],
      "id": "R-003",
      "severity": "high",
      "summary": "Debug follow-up lane tokens are lossy, so distinct lanes can still choose the same record path."
    },
    {
      "action": "Define a parallel integration rule for latest.md, such as updating the pointer after lane records are integrated, and verify that two lane records merge without a pointer conflict.",
      "evidence": [
        "skills/public/debug/scripts/debug_followup_routing.py routes each lane to a distinct follow-up record, while tests/test_debug_scaffold.py asserts update_current_pointer_after_write is true for those records.",
        "Parallel lanes from the same base can therefore refresh the same latest.md path to different lane-specific targets; the reviewed tests verify the update flag but not merging those pointer changes."
      ],
      "id": "R-004",
      "severity": "medium",
      "summary": "Distinct follow-up filenames do not prevent parallel lanes from conflicting on the shared latest.md pointer."
    },
    {
      "action": "Qualify the same-session claim by executor and evidence level, and describe network access as enabled by configuration unless a bind/fetch test supports the success claim.",
      "evidence": [
        "The notes say the progress rule resumes the same session; the spec records a live Codex probe but explicitly says Muse resume after SIGKILL is unprobed.",
        "The notes say tests that bind a local port or fetch through the proxy no longer fail; the reviewed Codex and Muse tests assert command arguments, but do not demonstrate successful bind or fetch behavior."
      ],
      "id": "R-005",
      "severity": "medium",
      "summary": "The release notes claim behavior beyond the evidence in the reviewed tests."
    },
    {
      "action": "Say that original event payload bytes are retained, with timestamps added to JSON lines and a newline added to an unterminated final line.",
      "evidence": [
        "The notes say executor output reaches the events log byte for byte, while scripts/task_run/task_run_event_timing.py inserts a timestamp into JSON lines.",
        "tests/charness_cli/test_task_run_event_capture.py expects an unterminated final line to gain a newline during retention."
      ],
      "id": "R-006",
      "severity": "low",
      "summary": "The event-capture note's byte-for-byte wording is not literal."
    }
  ],
  "prior_lens": "release lock-in",
  "prior_next_move": "Resolve the progress-window safety and debug-routing issues, revise the release notes to match demonstrated behavior, then run a fresh bounded review before lock-in.",
  "prior_non_claims": [
    "This review judges only the supplied inline semantic payload; no workspace paths were read and no tests were run.",
    "Publish-helper version, manifest, and claims-review surfaces were out of scope."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8150-final-packet.json",
  "prior_packet_sha256": "69b47fe61f359038464b0e4492490bdd0814023a859c86eda8dc0d379d155c35",
  "prior_reviewed_input_identity_sha256": "7bade79e814a4b9ba70f3055afd4de35c16871997e6c99df9707c6ef2c1ca70c",
  "prior_reviewed_paths": 27,
  "prior_scope": "release v8.15.0 final candidate at 9b6e75a7e: everything since the approved 526fbaa17 candidate review (ddab9c888..9b6e75a7e): event-capture close/clock repair, network access in executor lanes, the lane progress rule replacing the wall-clock default, debug follow-up naming per lane, and the extended release notes",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "charness-artifacts/spec/lane-progress-rule.md",
    "scripts/task_run/task_run_progress.py",
    "skills/public/debug/scripts/debug_followup_routing.py",
    "tests/charness_cli/test_task_run_progress_preemption.py",
    "tests/test_debug_scaffold.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness",
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "docs/agent-task-runs.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_attempts.py",
      "scripts/task_run/task_run_detach.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_lane_signals.py",
      "scripts/task_run/task_run_plan.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_implementation_lane.py",
      "tests/charness_cli/test_task_run_muse_executor.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/charness_cli/test_task_run_steer.py",
      "tests/test_debug_scaffold.py"
    ],
    "comparison_identity_sha256": "3bbb68abe9ab8c4babc36ac5761afb5891378de8afeafeea03c70c48aa81ced0",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8150-final",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "69b47fe61f359038464b0e4492490bdd0814023a859c86eda8dc0d379d155c35",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8150-final",
        "partial_result_sha256": null,
        "result_sha256": "24f57583531d6cf6fdda620853e809388c1827f8a143194226360701e9ec178c",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "7bade79e814a4b9ba70f3055afd4de35c16871997e6c99df9707c6ef2c1ca70c",
      "semantic_input": {
        "entries": 27,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "7bade79e814a4b9ba70f3055afd4de35c16871997e6c99df9707c6ef2c1ca70c",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/test_debug_scaffold.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/release-8150-final/result.json",
  "source_sha256": "24f57583531d6cf6fdda620853e809388c1827f8a143194226360701e9ec178c"
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
      "path_set_sha256": "b50119edbee061fb43c5e21e98f0c227197f455e713062e9f12fd7e7b7c5f7cf",
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
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "charness-artifacts/spec/lane-progress-rule.md",
    "scripts/task_run/task_run_progress.py",
    "skills/public/debug/scripts/debug_followup_routing.py",
    "tests/charness_cli/test_task_run_progress_preemption.py",
    "tests/test_debug_scaffold.py"
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
- charness-artifacts/release/2026-10-20-v8.15.0-notes.md
- charness-artifacts/spec/lane-progress-rule.md
- scripts/task_run/task_run_progress.py
- skills/public/debug/scripts/debug_followup_routing.py
- tests/charness_cli/test_task_run_progress_preemption.py
- tests/test_debug_scaffold.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_progress.py, skills/public/debug/scripts/debug_followup_routing.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md, charness-artifacts/spec/lane-progress-rule.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run_progress.py, tests/charness_cli/test_task_run_progress_preemption.py, tests/test_debug_scaffold.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_progress.py, skills/public/debug/scripts/debug_followup_routing.py
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
