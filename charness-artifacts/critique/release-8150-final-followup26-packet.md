# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T17:01:34Z
- **Prepared for**: release-8150-final-followup26
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `4a8ea1e3407411ea20e5d10563007eafdfd2d2a0210479b02b36d6cd86846e34`
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
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup26-packet.json --packet-sha256 7a417812425e8fa719f7961f629c697322c72d2ed9857e6ff1c523c281b2b946 --identity-sha256 4a8ea1e3407411ea20e5d10563007eafdfd2d2a0210479b02b36d6cd86846e34
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
      "scripts/task_run/task_run_progress_rule.py",
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
    "comparison_identity_sha256": "4a8ea1e3407411ea20e5d10563007eafdfd2d2a0210479b02b36d6cd86846e34",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 19,
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "docs/agent-task-runs.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
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
  "context_size_bytes": 9931,
  "final_reviewed_input_identity_sha256": "4a8ea1e3407411ea20e5d10563007eafdfd2d2a0210479b02b36d6cd86846e34",
  "final_selected_path_count": 19,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8150-final-followup25",
  "prior_findings": [
    {
      "action": "Preserve command identity from an earlier Muse lifecycle event when available; otherwise explicitly report the number of unnamed running commands as unidentified. Add a regression test for a Muse command interrupted before command text is observed, and align the claim with that behavior.",
      "evidence": [
        "In `task_run_event_timing._Timeline._feed_muse`, a `task.lifecycle.started` event starts the command with `None`; the command text is populated only by a later `task.lifecycle.output` event.",
        "`_Timeline.in_flight()` converts a missing command to an empty string, and `_checkpoint_request()` renders that as empty backticks. The lane then receives no usable name for that interrupted command.",
        "`test_the_checkpoint_names_every_command_the_kill_interrupts` covers two Codex events with command text; it does not cover a Muse command interrupted before its first output event.",
        "The spec and release notes say the checkpoint message names every interrupted command."
      ],
      "id": "parallel-command-interrupt-not-disclosed",
      "severity": "high",
      "summary": "The checkpoint names all tracked command texts when available, but a running Muse command may be unnamed when the request is delivered."
    }
  ],
  "prior_lens": "release lock-in final pass",
  "prior_next_move": "Hold release lock-in until the Muse unknown-command case is disclosed and covered by a regression test; then recheck the checkpoint wording.",
  "prior_non_claims": [
    "Reviewed the identity-bound inline payload only.",
    "Inspected the bound regression tests but did not execute them or verify live Codex or Muse process-group behavior."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8150-final-followup25-packet.json",
  "prior_packet_sha256": "3f4063ee097e2a4ca0badab62aaad3334883acb1e2883c3aa419376a6bf22078",
  "prior_reviewed_input_identity_sha256": "0e3a18e430abd98e7b81b27f0805631dbd6d1b8315f53958730ffdb767ffee96",
  "prior_reviewed_paths": 19,
  "prior_scope": "follow-up at fdcc6d80f on release-8150-final-followup24: finding 2 the checkpoint request now names every running command the process-group kill interrupts (test; spec updated); finding 1 is answered with a regression test: in _on_complete the deferred-delivery branch returns before the loop branch, so a loop repeat that resolves a deferred request delivers the checkpoint and the between-checks state matches what the lane received",
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
    "comparison_identity_sha256": "4a8ea1e3407411ea20e5d10563007eafdfd2d2a0210479b02b36d6cd86846e34",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8150-final-followup25",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "3f4063ee097e2a4ca0badab62aaad3334883acb1e2883c3aa419376a6bf22078",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8150-final-followup25",
        "partial_result_sha256": null,
        "result_sha256": "47c81b120427481edc61090d4783e7123202624f5b2390c665cb2f394707ff62",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "0e3a18e430abd98e7b81b27f0805631dbd6d1b8315f53958730ffdb767ffee96",
      "semantic_input": {
        "entries": 19,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "0e3a18e430abd98e7b81b27f0805631dbd6d1b8315f53958730ffdb767ffee96",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "docs/agent-task-runs.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_progress.py",
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
  "source": "charness-artifacts/critique/workers/release-8150-final-followup25/result.json",
  "source_sha256": "47c81b120427481edc61090d4783e7123202624f5b2390c665cb2f394707ff62"
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
