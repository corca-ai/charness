# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T10:25:24Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `c20ab185cdb5ec15fbb2128ac85ee0bed8aa9a6a4b681175ff28f14d743cb52b`
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
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/impl-followup-b-packet.json --packet-sha256 0ea72132529274d5893af4aee06fce76cf7f569b9f9867b7bac549822e834307 --identity-sha256 c20ab185cdb5ec15fbb2128ac85ee0bed8aa9a6a4b681175ff28f14d743cb52b
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
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "comparison_identity_sha256": "c20ab185cdb5ec15fbb2128ac85ee0bed8aa9a6a4b681175ff28f14d743cb52b",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 7,
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 10692,
  "final_reviewed_input_identity_sha256": "c20ab185cdb5ec15fbb2128ac85ee0bed8aa9a6a4b681175ff28f14d743cb52b",
  "final_selected_path_count": 7,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "impl-followup-a",
  "prior_findings": [
    {
      "action": "Apply the in-flight age rule to stop actions too. Track command start times and defer a kill until the active command has run at least W; add a real pipe/process test for a command started late in the request window.",
      "evidence": [
        "ProgressRule.on_tick checks commands_in_flight only when the request is None or deferred; with a delivered request it falls through to stop even when a command is in flight.",
        "After a request is delivered at W, the resumed lane can start a command just before 2W. Command start is not progress, so the next check stops the lane and kills that command after only a short run.",
        "The deferred-command unit test starts its command before the first check; it does not cover a command started after request delivery."
      ],
      "id": "LP-2",
      "severity": "blocker",
      "summary": "A stop can kill a command younger than W after a checkpoint request was delivered."
    },
    {
      "action": "Count a command completion as progress only when its fingerprint is observable and its pair is new. Add a test with repeated identical completions while the fingerprint remains None.",
      "evidence": [
        "ProgressRule._on_complete increments _new_outcomes and returns whenever the fingerprint is None, without checking whether the command/tree pair is new.",
        "Repeated commands on an unreadable worktree therefore reset each progress window indefinitely, although the spec says an unobservable worktree contributes neither progress nor its absence.",
        "The unobservable-worktree test covers a file-change event and silence, but not repeated command completions."
      ],
      "id": "LP-4a",
      "severity": "blocker",
      "summary": "An unobservable worktree makes every command completion count as progress."
    },
    {
      "action": "Make an unrecoverable or repeated watch failure produce a recorded terminal stop and kill, or provide an independent bounded reclamation path. Test a persistent polling failure.",
      "evidence": [
        "LaneProgressWatch._run catches any exception from tick and continues polling without recording a fault or stopping the executor.",
        "An exception before ProgressRule.on_tick, such as a persistent steer-queue read or log-read failure, can prevent every check from reaching the rule. With the wall-clock default removed, no other timer reclaims the lane."
      ],
      "id": "LP-4b",
      "severity": "blocker",
      "summary": "Persistent watcher errors can leave a lane running forever."
    },
    {
      "action": "Serialize action delivery and stop under one first-wins state transition. Suppress and account for actions that lose to stop; add a deterministic race test covering queue state, preemption count, and final result.",
      "evidence": [
        "observe_event obtains an action from ProgressRule and calls _apply after the rule lock is released; the watch thread can meanwhile reach _stop_now, which uses a separate lock.",
        "_apply does not recheck stop_reason or coordinate with _stop_now. It can enqueue a steer, set _preempted, increment preemptions, and kill after the stop has already won; _execute_codex then sees stop_reason and exits before delivering the queued steer.",
        "take_preempted returns one boolean per invocation, while LaneProgressWatch.preemptions increments per _apply call, so overlapping actions can also disagree in their receipts."
      ],
      "id": "LP-3",
      "severity": "high",
      "summary": "Preemption and stop side effects are not serialized, so a losing preemption can still queue a steer and count as delivered work."
    },
    {
      "action": "Add a lane-finish transition that records a delivered request as answered when the lane ends with its final report or BLOCKED response, and test that receipt outcome.",
      "evidence": [
        "ProgressRule._mark_answered is called only when a later progress check observes progress; there is no finish/finalization method for a normal final report or BLOCKED turn ending.",
        "LaneProgressWatch.stop halts polling but does not resolve the delivered request, so the receipt can leave answered absent even when the executor ended as the spec defines an answer."
      ],
      "id": "B-2",
      "severity": "high",
      "summary": "A lane ending after a checkpoint request is not recorded as answering it."
    }
  ],
  "prior_lens": "Gawande — operational correctness of the wired lane progress rule",
  "prior_next_move": "Fix the late-start kill, unknown-fingerprint command accounting, watcher failure handling, and action/stop serialization; add focused process-level and deterministic race tests, then finalize request-answer receipts and re-review the wired behavior.",
  "prior_non_claims": [
    "LP-1 remains a recorded non-claim and was not re-litigated as a defect.",
    "Live Codex and Muse resume semantics were not established by these fake-executor tests.",
    "Downstream attempt and WIP classification was not established because its owners are outside the selected paths."
  ],
  "prior_packet_path": "charness-artifacts/critique/impl-followup-a-packet.json",
  "prior_packet_sha256": "6432311496272658385e53c43932f6ec7e9d2ae96e339a29c2c1890029e844fc",
  "prior_reviewed_input_identity_sha256": "4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3",
  "prior_reviewed_paths": 7,
  "prior_scope": "follow-up of the lane progress rule design premortem, now implemented (commits c9ba15393 and fec6ba651 on feat/lane-progress-rule): does the implementation honor the revised spec and resolve LP-2 (no kill of a command younger than the window), LP-3 (preemption distinct from failed resume, attempts, relaunch friction, WIP), LP-4 (three-valued observation; silent executor still reclaimed) and B-2 (request answer semantics)? LP-1 is a recorded non-claim.",
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
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "comparison_identity_sha256": "c20ab185cdb5ec15fbb2128ac85ee0bed8aa9a6a4b681175ff28f14d743cb52b",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "impl-followup-a",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "6432311496272658385e53c43932f6ec7e9d2ae96e339a29c2c1890029e844fc",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "impl-followup-a",
        "partial_result_sha256": null,
        "result_sha256": "2f296bcf543d11f997dde7936665312b1e92ea4f3e7887273ee741fada43ff50",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3",
      "semantic_input": {
        "entries": 7,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "4761b20162d63ec8aa4514fae1201b29c3d98515fb84e0d57b0a51c567dba7d3",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_preemption.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/impl-followup-a/result.json",
  "source_sha256": "2f296bcf543d11f997dde7936665312b1e92ea4f3e7887273ee741fada43ff50"
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
