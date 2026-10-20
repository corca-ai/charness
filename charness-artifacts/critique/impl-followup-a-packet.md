# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T10:14:35Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3`
- **Reviewed paths**: 7
  - `charness-artifacts/spec/lane-progress-rule.md`
  - `scripts/task_run/task_run_event_timing.py`
  - `scripts/task_run/task_run_execution.py`
  - `scripts/task_run/task_run_progress.py`
  - `scripts/task_run/task_run_progress_rule.py`
  - `tests/charness_cli/test_task_run_progress_preemption.py`
  - `tests/charness_cli/test_task_run_progress_rule.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/impl-followup-a-packet.json --packet-sha256 6432311496272658385e53c43932f6ec7e9d2ae96e339a29c2c1890029e844fc --identity-sha256 4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3
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
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py"
    ],
    "comparison_identity_sha256": "aed6a5626497a641bb8e0ad79c779a3d0756d98df75a197837775859f7950180",
    "new_paths": [
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "omitted_changed_prior_paths": [
      "scripts/task_run/task_run_lane_runner.py"
    ],
    "prior_paths": 5,
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 10792,
  "final_reviewed_input_identity_sha256": "4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3",
  "final_selected_path_count": 7,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "design-premortem-a",
  "prior_findings": [
    {
      "action": "Define command equivalence and outcome semantics before implementation. Specify how syntactic variations, exit status, and output affect the loop budget, while bounding false alarms across distinct commands in the same family.",
      "evidence": [
        "The spec counts a new outcome by the pair (command text, worktree fingerprint at completion), and keys the 3rd/4th/5th family actions by that same pair.",
        "task_run_event_timing.command_families uses regexes to identify families, but does not normalize commands into equivalent keys.",
        "A loop that varies flags, wrappers, or command text can produce a fresh key each time, count as progress, and avoid the repeat thresholds. Conversely, the same command and tree with a changed external test result is still the same key."
      ],
      "id": "LP-1",
      "severity": "blocker",
      "summary": "Exact command-text keys let recurring loops evade the family guard and can misclassify changed outcomes."
    },
    {
      "action": "Set the interruption contract for long commands, including side effects, lost output, reruns, and the second-W stop. Demonstrate that the supported executors can recover safely, or revise the rule so productive long work is not indistinguishable from a hung command.",
      "evidence": [
        "The spec counts completed command outcomes, not an active command, as progress; after W without a qualifying signal, checkpoint delivery preempts by killing the executor process group.",
        "A command longer than W is interrupted, and if the resumed lane has no qualifying progress in the next W, the outstanding request causes a stop.",
        "The cited Codex probe covered `sleep 40` and observed a missing tool-call output. It does not establish safe recovery for arbitrary commands or their side effects; Muse resume was not probed."
      ],
      "id": "LP-2",
      "severity": "blocker",
      "summary": "The 1200-second window still SIGKILLs productive long commands and can turn one interruption into a stop."
    },
    {
      "action": "Define an explicit preempted result and its transitions across normal exit races, resume failure, attempt/retry accounting, checkpoint creation, and terminal-state classification. Include the attempt and checkpoint/state owners in the implementation contract and establish Muse resume and fallback behavior before relying on it.",
      "evidence": [
        "task_run_execution._run_executor_invocation initializes `timed_out` and `interrupted`; a child killed by SIGKILL can instead return a nonzero exit code.",
        "In _execute_codex, a nonzero result for `resume_path == \"session-resume\"` enters the existing `relaunch-in-place` branch. A deliberate preemption during a resumed invocation can therefore take the failed-resume relaunch path.",
        "The spec says preemption is not a failure, attempt, or WIP checkpoint, but task_run_progress._execute_watched_lane delegates attempt handling to task_run_attempts, and the supplied reviewed paths do not include that owner or the checkpoint/state owner.",
        "Muse resume is explicitly unprobed, while the shared execution flow also has a relaunch-in-place fallback that may repeat work in the same worktree."
      ],
      "id": "LP-3",
      "severity": "blocker",
      "summary": "Expected preemption is not distinguished from failed execution or failed session resume."
    },
    {
      "action": "Specify tri-state progress and watcher-failure behavior. Identify independent observable signals that allow a silent executor to be reclaimed while the worktree is unavailable, and ensure observer failure itself cannot leave an executor running indefinitely after the default timeout is removed.",
      "evidence": [
        "The spec promises autonomous reclamation within 2W plus a poll, including for a dead or silent executor, and applies the rule to every lane.",
        "task_run_progress._worktree_liveliness returns None when observation fails; scoped_diff_present returns None and suppresses the existing first-edit stop in that case.",
        "LaneProgressWatch._run catches polling exceptions and continues. The existing build_progress_watch also returns None for non-require-change lanes, so the proposed all-lane coverage needs a new always-running observation path.",
        "The spec does not say whether an unknown fingerprint pauses the window, counts as no progress, or triggers a stop. Those choices respectively risk unreclaimed silence or killing productive but unobservable work."
      ],
      "id": "LP-4",
      "severity": "high",
      "summary": "The no-second-timer claim is not supported when the worktree or watcher is unobservable."
    }
  ],
  "prior_lens": "Gawande premortem, operational",
  "prior_next_move": "Revise the design contract before implementation: define command equivalence and outcome identity, settle safe preemption behavior for long commands, specify preempted versus failed-resume state transitions across attempt/checkpoint owners, and define fail-safe behavior when worktree or watcher observations are unavailable.",
  "prior_non_claims": [
    "{\n  \"binding\": null,\n  \"disposition\": \"not-goal-bound\",\n  \"draft\": null,\n  \"goal_run\": null,\n  \"kind\": \"charness.goal-lineage\",\n  \"reason\": \"critique review was run without a Goal Run Work Item identity\",\n  \"schema_version\": 1,\n  \"work_item\": null\n}",
    "No implementation, tests, or runtime verification were performed; this review evaluates the supplied semantic payload.",
    "Muse resume behavior and the reported consuming-repo lane counts were not independently verified."
  ],
  "prior_packet_path": "charness-artifacts/critique/design-premortem-a-packet.json",
  "prior_packet_sha256": "8020406687a2dec30afd4b2caa153288e4c1f60123ba903c26a5af941c410a98",
  "prior_reviewed_input_identity_sha256": "5bd0c6d7ac632081ac4a62b530e7fd0b0342bf6d154f2266a2511edbbd9d2271",
  "prior_reviewed_paths": 5,
  "prior_scope": "design premortem for replacing the task-run lane wall-clock timeout with a single progress rule (charness-artifacts/spec/lane-progress-rule.md), before implementation; the listed code files are the current owners it would extend",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/spec/lane-progress-rule.md",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_progress_preemption.py",
    "tests/charness_cli/test_task_run_progress_rule.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_progress.py"
    ],
    "comparison_identity_sha256": "aed6a5626497a641bb8e0ad79c779a3d0756d98df75a197837775859f7950180",
    "explicit_paths": true,
    "new_paths": [
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "omitted_changed_prior_paths": [
      "scripts/task_run/task_run_lane_runner.py"
    ],
    "prior_binding": {
      "attempt_id": "design-premortem-a",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "8020406687a2dec30afd4b2caa153288e4c1f60123ba903c26a5af941c410a98",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "design-premortem-a",
        "partial_result_sha256": null,
        "result_sha256": "55158be3a1cb968e21e774536f552ca9460a0a644f6443d398c74e8501933581",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "5bd0c6d7ac632081ac4a62b530e7fd0b0342bf6d154f2266a2511edbbd9d2271",
      "semantic_input": {
        "entries": 5,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "5bd0c6d7ac632081ac4a62b530e7fd0b0342bf6d154f2266a2511edbbd9d2271",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/design-premortem-a/result.json",
  "source_sha256": "55158be3a1cb968e21e774536f552ca9460a0a644f6443d398c74e8501933581"
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
      "path_set_sha256": "533338b020b7ee845d694adc0b5d1670eb75ab355f357262792ff35b9afcb136",
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
    "charness-artifacts/spec/lane-progress-rule.md",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_progress_preemption.py",
    "tests/charness_cli/test_task_run_progress_rule.py"
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
- charness-artifacts/spec/lane-progress-rule.md
- scripts/task_run/task_run_event_timing.py
- scripts/task_run/task_run_execution.py
- scripts/task_run/task_run_progress.py
- scripts/task_run/task_run_progress_rule.py
- tests/charness_cli/test_task_run_progress_preemption.py
- tests/charness_cli/test_task_run_progress_rule.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/spec/lane-progress-rule.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py, tests/charness_cli/test_task_run_progress_preemption.py, tests/charness_cli/test_task_run_progress_rule.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py
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
