# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-04T20:46:50Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `065c4fb62f6f45bb9194fb16ae93ef616fe8656ff1ddfa27033cf31ce826fe13`
- **Reviewed paths**: 5
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `tests/charness_cli/test_codex_cache_refresh.py`
  - `tests/quality_gates/test_semantic_review_worker_timeout.py`
  - `tests/test_debug_plan.py`
  - `tests/test_debug_risk_class_prose.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-rest-followup2-packet.json --packet-sha256 a37c9f71cd21242b86b8340c1819b1e79d893ee1e46b90f4503459934767c40b --identity-sha256 065c4fb62f6f45bb9194fb16ae93ef616fe8656ff1ddfa27033cf31ce826fe13
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
      "tests/test_debug_risk_class_prose.py"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "scripts/runtime_scratch.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py",
      "tests/quality_gates/test_semantic_review_worker_timeout.py",
      "tests/test_debug_risk_class_prose.py"
    ],
    "comparison_identity_sha256": "a7475e56690ca5d0582575e40db59d274b45f6931ca47ee24d3db561081314cc",
    "new_paths": [
      "tests/test_debug_plan.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_paths": 8,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/test_debug_risk_class_prose.py"
    ],
    "unchanged_selected_paths": [
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/quality_gates/test_semantic_review_worker_timeout.py"
    ]
  },
  "context_size_bytes": 6955,
  "final_reviewed_input_identity_sha256": "065c4fb62f6f45bb9194fb16ae93ef616fe8656ff1ddfa27033cf31ce826fe13",
  "final_selected_path_count": 5,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-rest-followup1",
  "prior_findings": [
    {
      "action": "Add a test for `external-seam, bogus` that asserts the interrupt and planner outcome, or qualify the note to identify this behavior as untested.",
      "evidence": [
        "debug_artifact_declarations.py recovers allowed classes after a parse error and sets `requires_interrupt` when a recovered class is forced.",
        "test_debug_risk_class_prose.py tests unknown values such as `none, bogus`, but has no forced-class-plus-unknown case."
      ],
      "id": "risk-forced-unknown-test-gap",
      "severity": "medium",
      "summary": "The note’s `external-seam, bogus` behavior matches the helper, but the selected tests still do not cover that mixed case."
    },
    {
      "action": "Keep verdicts event-driven while adding a separate bounded failure path, such as a controllable timeout signal or a test watchdog that cannot decide the behavior under test.",
      "evidence": [
        "test_codex_cache_refresh.py freezes the reader clock and replaces `select` with a call that omits its timeout; a missing pipe event therefore has no test-level deadline.",
        "test_semantic_review_worker_timeout.py removes the outer runner timeout while the fake backend sleeps for 3600 seconds; if the worker timeout path breaks, the test can remain running until that sleep ends."
      ],
      "id": "event-driven-tests-unbounded-on-missing-event",
      "severity": "medium",
      "summary": "Some timing repairs can wait indefinitely instead of failing when the expected event never arrives."
    }
  ],
  "prior_lens": "Fresh-eye follow-up: claim-to-code alignment and timing-test failure behavior",
  "prior_next_move": "Add the mixed forced-plus-unknown risk test and give the event-driven timing tests a bounded failure path that does not restore load-sensitive verdict deadlines.",
  "prior_non_claims": [
    "No Windows-host execution was verified.",
    "The packet contains no structured prepared_targets, so no per-target observations are made."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-rest-followup1-packet.json",
  "prior_packet_sha256": "801bc917c58f460c0e8e5650c5f8324636c49995930cb112bf2a2cfbb035504c",
  "prior_reviewed_input_identity_sha256": "40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148",
  "prior_reviewed_paths": 8,
  "prior_scope": "Follow-up on release-8160-rest: notes reworded for the forced-class Risk Class case, cmd.exe quoting limits (issue #890) and the untested Windows lock fallback; three load-dependent tests made event-driven (7d5435040).",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "tests/charness_cli/test_codex_cache_refresh.py",
    "tests/quality_gates/test_semantic_review_worker_timeout.py",
    "tests/test_debug_plan.py",
    "tests/test_debug_risk_class_prose.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "scripts/runtime_scratch.py",
      "skills/public/debug/scripts/debug_artifact_declarations.py",
      "skills/shared/scripts/reviewer_process.py",
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/charness_cli/test_entry_cov_e4_874.py",
      "tests/quality_gates/test_semantic_review_worker_timeout.py",
      "tests/test_debug_risk_class_prose.py"
    ],
    "comparison_identity_sha256": "a7475e56690ca5d0582575e40db59d274b45f6931ca47ee24d3db561081314cc",
    "explicit_paths": true,
    "new_paths": [
      "tests/test_debug_plan.py"
    ],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8160-rest-followup1",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "801bc917c58f460c0e8e5650c5f8324636c49995930cb112bf2a2cfbb035504c",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-rest-followup1",
        "partial_result_sha256": null,
        "result_sha256": "a0fd058b1c262333e323c35e109dfdfc5211e7bf80d77446d0cceba9326e8cd6",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148",
      "semantic_input": {
        "entries": 8,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "40982770650b7bce8001276aabfa2fc2042481ccc71dd673facb713e82050148",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/test_debug_risk_class_prose.py"
    ],
    "unchanged_selected_paths": [
      "tests/charness_cli/test_codex_cache_refresh.py",
      "tests/quality_gates/test_semantic_review_worker_timeout.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8160-rest-followup1/result.json",
  "source_sha256": "a0fd058b1c262333e323c35e109dfdfc5211e7bf80d77446d0cceba9326e8cd6"
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
      "path_set_sha256": "633bdfaf8e8a6fa30304e6df5143b705a521010d9f680db9577a26f3cb9204be",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 5,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 5,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 5,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "tests/charness_cli/test_codex_cache_refresh.py",
    "tests/quality_gates/test_semantic_review_worker_timeout.py",
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
- tests/charness_cli/test_codex_cache_refresh.py
- tests/quality_gates/test_semantic_review_worker_timeout.py
- tests/test_debug_plan.py
- tests/test_debug_risk_class_prose.py

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- repo-python: Repo-owned Python code and tests.
  source matches: tests/charness_cli/test_codex_cache_refresh.py, tests/quality_gates/test_semantic_review_worker_timeout.py, tests/test_debug_plan.py, tests/test_debug_risk_class_prose.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
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
