# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T17:21:50Z
- **Prepared for**: release-8150-final-followup32
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d`
- **Reviewed paths**: 19
  - `charness`
  - `charness-artifacts/release/2026-10-20-v8.15.0-notes.md`
  - `charness-artifacts/spec/lane-progress-rule.md`
  - `docs/agent-task-runs.md`
  - `docs/cli-reference.md`
  - `scripts/task_run/task_run_brief_critique.py`
  - `scripts/task_run/task_run_event_timing.py`
  - `scripts/task_run/task_run_execution.py`
  - `scripts/task_run/task_run_progress.py`
  - `scripts/task_run/task_run_progress_rule.py`
  - `scripts/task_run/task_run_runtime.py`
  - `scripts/task_run/task_run_self_review.py`
  - `skills/public/debug/scripts/debug_followup_routing.py`
  - `tests/charness_cli/test_task_run_event_capture.py`
  - `tests/charness_cli/test_task_run_event_timing.py`
  - `tests/charness_cli/test_task_run_premise_gates.py`
  - `tests/charness_cli/test_task_run_progress_rule.py`
  - `tests/charness_cli/test_task_run_self_review.py`
  - `tests/test_debug_scaffold.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup32-packet.json --packet-sha256 86f4a3d539613f8e5a00a91a1b89cf2c25417a6781f9f95346ae531dc5b60a6e --identity-sha256 e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d
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
      "docs/agent-task-runs.md",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "comparison_identity_paths": [
      "charness",
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "docs/agent-task-runs.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ],
    "comparison_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 19,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "docs/agent-task-runs.md",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ]
  },
  "context_size_bytes": 10528,
  "final_reviewed_input_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
  "final_selected_path_count": 19,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8150-final-followup31",
  "prior_findings": [
    {
      "action": "Align the spec and task-runs summary with the actual limitation: when the start is not yet observed, a due check may act on stale state and kill a younger command. Clarify the effect of a hung sink write as well, and rename the rule-lock test or add a serialized-reader regression before making a production-reader guarantee.",
      "evidence": [
        "In `task_run_progress_rule.py`, completion handling fingerprints before taking the rule lock, and its comment acknowledges that the serialized event reader cannot read the next line until that probe returns.",
        "In `on_tick`, the check bases its age decision on events already observed. If the following start is still queued behind the completion probe, the check may see only the previous command and preempt or stop without recognizing the new command.",
        "The spec acknowledges that a start can be missed, then says it defers the request or stop and that only commands run for at least W are killed. That assurance does not hold when the start is still unseen.",
        "`docs/agent-task-runs.md` says without qualification that a young command delays either step by a check."
      ],
      "id": "completion-probe-exception-overpromises-age-protection",
      "severity": "medium",
      "summary": "The reader-probe exception is disclosed, but the spec then promises protection the implementation cannot provide: a check can act on stale in-flight state before the following start is observed, potentially killing a command younger than W. The task-runs summary also states the protection without the exception, and the test name suggests production-reader coverage it does not provide."
    }
  ],
  "prior_lens": "release lock-in final pass",
  "prior_next_move": "Correct the age-protection statements and narrow the test's claim, or change the event path so checks cannot act on an unseen start. Then re-review the bound consumer surfaces.",
  "prior_non_claims": [
    "Reviewed the packet's inline semantic input only; did not inspect workspace paths.",
    "Did not run tests or independently verify the stated 0.03–0.09 second probe measurements or live Codex/Muse behavior.",
    "The supplied goal lineage is not-goal-bound; this review does not close a Goal Run."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8150-final-followup31-packet.json",
  "prior_packet_sha256": "da0490f34f981ffc748a9c53ae2c492d9bfb27044f9a96eb7e30a6bff50a999d",
  "prior_reviewed_input_identity_sha256": "c25ce2595c4b27455a19ee29a4e6d4c40d2debb4c60e2e6b6aadc118ea9da7c8",
  "prior_reviewed_paths": 19,
  "prior_scope": "follow-up at d2a274056 on release-8150-final-followup30: finding 0 is dispositioned as a disclosed narrow exception (the reader probes the tree for a completion before reading the next line; measured 0.03-0.09 s on the ceal and charness trees), stated in the notes, spec and the code comment; finding 1 the spec due-check count covers a mid-probe start; finding 2 the notes already list merge among the families",
  "prior_verdict": "block",
  "selected_paths": [
    "charness",
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "charness-artifacts/spec/lane-progress-rule.md",
    "docs/agent-task-runs.md",
    "docs/cli-reference.md",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_progress_rule.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/task_run/task_run_self_review.py",
    "skills/public/debug/scripts/debug_followup_routing.py",
    "tests/charness_cli/test_task_run_event_capture.py",
    "tests/charness_cli/test_task_run_event_timing.py",
    "tests/charness_cli/test_task_run_premise_gates.py",
    "tests/charness_cli/test_task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_self_review.py",
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
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ],
    "comparison_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8150-final-followup31",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "da0490f34f981ffc748a9c53ae2c492d9bfb27044f9a96eb7e30a6bff50a999d",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8150-final-followup31",
        "partial_result_sha256": null,
        "result_sha256": "7f15635177e1b9379994d9eb3bdaf050ea1ae9434938ec4652bcd50599f35833",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "c25ce2595c4b27455a19ee29a4e6d4c40d2debb4c60e2e6b6aadc118ea9da7c8",
      "semantic_input": {
        "entries": 19,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "c25ce2595c4b27455a19ee29a4e6d4c40d2debb4c60e2e6b6aadc118ea9da7c8",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "docs/agent-task-runs.md",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "skills/public/debug/scripts/debug_followup_routing.py",
      "tests/charness_cli/test_task_run_event_capture.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8150-final-followup31/result.json",
  "source_sha256": "7f15635177e1b9379994d9eb3bdaf050ea1ae9434938ec4652bcd50599f35833"
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
      "path_set_sha256": "ab0443cde8d17219f01ca911395fbdb72f4f53e06872662b7f662b2c755dbf0a",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 19,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 19,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 19,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness",
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "charness-artifacts/spec/lane-progress-rule.md",
    "docs/agent-task-runs.md",
    "docs/cli-reference.md",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_execution.py",
    "scripts/task_run/task_run_progress.py",
    "scripts/task_run/task_run_progress_rule.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/task_run/task_run_self_review.py",
    "skills/public/debug/scripts/debug_followup_routing.py",
    "tests/charness_cli/test_task_run_event_capture.py",
    "tests/charness_cli/test_task_run_event_timing.py",
    "tests/charness_cli/test_task_run_premise_gates.py",
    "tests/charness_cli/test_task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_self_review.py",
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
- charness
- charness-artifacts/release/2026-10-20-v8.15.0-notes.md
- charness-artifacts/spec/lane-progress-rule.md
- docs/agent-task-runs.md
- docs/cli-reference.md
- scripts/task_run/task_run_brief_critique.py
- scripts/task_run/task_run_event_timing.py
- scripts/task_run/task_run_execution.py
- scripts/task_run/task_run_progress.py
- scripts/task_run/task_run_progress_rule.py
- scripts/task_run/task_run_runtime.py
- scripts/task_run/task_run_self_review.py
- skills/public/debug/scripts/debug_followup_routing.py
- tests/charness_cli/test_task_run_event_capture.py
- tests/charness_cli/test_task_run_event_timing.py
- tests/charness_cli/test_task_run_premise_gates.py
- tests/charness_cli/test_task_run_progress_rule.py
- tests/charness_cli/test_task_run_self_review.py
- tests/test_debug_scaffold.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, skills/public/debug/scripts/debug_followup_routing.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md, charness-artifacts/spec/lane-progress-rule.md, docs/agent-task-runs.md, docs/cli-reference.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 -m tools.validate_current_pointer_freshness --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/debug/scripts/debug_followup_routing.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, tests/charness_cli/test_task_run_event_capture.py, tests/charness_cli/test_task_run_event_timing.py, tests/charness_cli/test_task_run_premise_gates.py, tests/charness_cli/test_task_run_progress_rule.py, tests/charness_cli/test_task_run_self_review.py, tests/test_debug_scaffold.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_execution.py, scripts/task_run/task_run_progress.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, skills/public/debug/scripts/debug_followup_routing.py
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
