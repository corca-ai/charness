# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T14:38:22Z
- **Prepared for**: release-8150-final-followup9
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `02b193cd9c2469bff839c77392743e4ae0ef51c03781e7e14241e9a8c0df1086`
- **Reviewed paths**: 12
  - `charness-artifacts/release/2026-10-20-v8.15.0-notes.md`
  - `docs/agent-task-runs.md`
  - `scripts/task_run/task_run_brief_critique.py`
  - `scripts/task_run/task_run_event_timing.py`
  - `scripts/task_run/task_run_progress_rule.py`
  - `scripts/task_run/task_run_runtime.py`
  - `scripts/task_run/task_run_self_review.py`
  - `tests/charness_cli/test_task_run_event_capture.py`
  - `tests/charness_cli/test_task_run_event_timing.py`
  - `tests/charness_cli/test_task_run_premise_gates.py`
  - `tests/charness_cli/test_task_run_progress_rule.py`
  - `tests/charness_cli/test_task_run_self_review.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup9-packet.json --packet-sha256 d9db86c4915fba1f0ad3e1175c8365c328f8cc0ad82a566a9a99c21af9650e8f --identity-sha256 02b193cd9c2469bff839c77392743e4ae0ef51c03781e7e14241e9a8c0df1086
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
      "scripts/task_run/task_run_event_timing.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py"
    ],
    "comparison_identity_sha256": "9da4f0f1b6b68b6228abee35d927523fe704f1f4c9ebaabb7d34dff9767f7c73",
    "new_paths": [
      "docs/agent-task-runs.md",
      "tests/charness_cli/test_task_run_event_capture.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 10,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "scripts/task_run/task_run_event_timing.py"
    ],
    "unchanged_selected_paths": [
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py"
    ]
  },
  "context_size_bytes": 9520,
  "final_reviewed_input_identity_sha256": "02b193cd9c2469bff839c77392743e4ae0ef51c03781e7e14241e9a8c0df1086",
  "final_selected_path_count": 12,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8150-final-followup8",
  "prior_findings": [
    {
      "action": "Revise the claim to say receive-time deltas can understate or overstate producer timing. Do not recommend setting the progress window from them as though they were guaranteed upper bounds.",
      "evidence": [
        "The release notes say pipe buffering makes command and phase durations upper bounds on executor timing.",
        "StampingPipe timestamps lines when the reader receives them; it has no producer-side timestamps. Variable delay for the start and completion lines can make their receive-time difference either larger or smaller than the actual duration.",
        "The timing tests supply fixed timestamps and do not verify that measured durations are upper bounds."
      ],
      "id": "R-001",
      "severity": "high",
      "summary": "The notes overstate receive-time duration estimates as upper bounds."
    },
    {
      "action": "Write until all bytes are accepted or record the unwritten remainder as dropped and the capture as incomplete; add a short-writing sink test.",
      "evidence": [
        "StampingPipe._emit calls self._sink.write(data) but does not check its returned byte count.",
        "capture() reports complete unless there is an error, an open writer at close, or dropped_bytes; a short write without an exception sets none of these.",
        "The release notes promise that event bytes are never silently lost and the supplied pipe test uses BytesIO, which does not exercise short writes."
      ],
      "id": "R-002",
      "severity": "high",
      "summary": "A short sink write can silently lose event bytes while capture reports complete."
    },
    {
      "action": "Qualify the no-blocking guarantee or change the capture path so a stalled sink cannot stop pipe draining, with any resulting loss recorded as incomplete.",
      "evidence": [
        "StampingPipe._emit writes and flushes synchronously on the same thread that drains the executor pipe.",
        "If the sink write or flush stalls, _drain cannot read more bytes; the pipe can fill while the executor is writing.",
        "The notes claim the reader keeps draining so the executor never blocks on a full pipe, but the supplied tests do not exercise a stalled sink."
      ],
      "id": "R-003",
      "severity": "medium",
      "summary": "A blocked log write can stop pipe draining and block the executor on a full pipe."
    }
  ],
  "prior_lens": "release lock-in follow-up",
  "prior_next_move": "Correct the timing-bound claim and close or qualify the sink-write capture guarantees, then review the updated bound inputs.",
  "prior_non_claims": [
    "Reviewed all ten identity-bound inline payloads, including the complete release notes once; did not inspect workspace paths or execute tests.",
    "Goal evidence lineage (copy exactly):\n{\n  \"binding\": null,\n  \"disposition\": \"not-goal-bound\",\n  \"draft\": null,\n  \"goal_run\": null,\n  \"kind\": \"charness.goal-lineage\",\n  \"reason\": \"critique review was run without a Goal Run Work Item identity\",\n  \"schema_version\": 1,\n  \"work_item\": null\n}"
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8150-final-followup8-packet.json",
  "prior_packet_sha256": "95f764b5f3aab0e6d181e67aea4bf9f6338688727292d0122326f99c97d889de",
  "prior_reviewed_input_identity_sha256": "0b004800af56eccbafa16da5bf3dfd897f698580154d1955dcfec7819df01cd1",
  "prior_reviewed_paths": 10,
  "prior_scope": "follow-up at 74ad9d209 on release-8150-final-followup7: repairs from the claims review of the prepared v8.15.0 record (prepared commit withdrawn unpublished): B1 a zero window now turns off the loop check too; B2 the --commands reader keeps a resumed Codex session's reused item ids apart; A6 read-only reviewers drop the lane network key; notes revised for A1-A6",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "docs/agent-task-runs.md",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_progress_rule.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/task_run/task_run_self_review.py",
    "tests/charness_cli/test_task_run_event_capture.py",
    "tests/charness_cli/test_task_run_event_timing.py",
    "tests/charness_cli/test_task_run_premise_gates.py",
    "tests/charness_cli/test_task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_self_review.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py"
    ],
    "comparison_identity_sha256": "9da4f0f1b6b68b6228abee35d927523fe704f1f4c9ebaabb7d34dff9767f7c73",
    "explicit_paths": true,
    "new_paths": [
      "docs/agent-task-runs.md",
      "tests/charness_cli/test_task_run_event_capture.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8150-final-followup8",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "95f764b5f3aab0e6d181e67aea4bf9f6338688727292d0122326f99c97d889de",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8150-final-followup8",
        "partial_result_sha256": null,
        "result_sha256": "d22c9eb5a5fe4572499a981b630e464b1834cd655abcff4f08cf6ece8bd13816",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "0b004800af56eccbafa16da5bf3dfd897f698580154d1955dcfec7819df01cd1",
      "semantic_input": {
        "entries": 10,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "0b004800af56eccbafa16da5bf3dfd897f698580154d1955dcfec7819df01cd1",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "scripts/task_run/task_run_event_timing.py"
    ],
    "unchanged_selected_paths": [
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_progress_rule.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_self_review.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_premise_gates.py",
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8150-final-followup8/result.json",
  "source_sha256": "d22c9eb5a5fe4572499a981b630e464b1834cd655abcff4f08cf6ece8bd13816"
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
      "path_set_sha256": "58274cae44ddfccf1dbf84baff847ba0d20b1c222481f956a4acbbdeeeed8090",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 12,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 12,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 12,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
    "docs/agent-task-runs.md",
    "scripts/task_run/task_run_brief_critique.py",
    "scripts/task_run/task_run_event_timing.py",
    "scripts/task_run/task_run_progress_rule.py",
    "scripts/task_run/task_run_runtime.py",
    "scripts/task_run/task_run_self_review.py",
    "tests/charness_cli/test_task_run_event_capture.py",
    "tests/charness_cli/test_task_run_event_timing.py",
    "tests/charness_cli/test_task_run_premise_gates.py",
    "tests/charness_cli/test_task_run_progress_rule.py",
    "tests/charness_cli/test_task_run_self_review.py"
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
- docs/agent-task-runs.md
- scripts/task_run/task_run_brief_critique.py
- scripts/task_run/task_run_event_timing.py
- scripts/task_run/task_run_progress_rule.py
- scripts/task_run/task_run_runtime.py
- scripts/task_run/task_run_self_review.py
- tests/charness_cli/test_task_run_event_capture.py
- tests/charness_cli/test_task_run_event_timing.py
- tests/charness_cli/test_task_run_premise_gates.py
- tests/charness_cli/test_task_run_progress_rule.py
- tests/charness_cli/test_task_run_self_review.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md, docs/agent-task-runs.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-10-20-v8.15.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py, tests/charness_cli/test_task_run_event_capture.py, tests/charness_cli/test_task_run_event_timing.py, tests/charness_cli/test_task_run_premise_gates.py, tests/charness_cli/test_task_run_progress_rule.py, tests/charness_cli/test_task_run_self_review.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_event_timing.py, scripts/task_run/task_run_progress_rule.py, scripts/task_run/task_run_runtime.py, scripts/task_run/task_run_self_review.py
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
