# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-04T20:53:38Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `58931872a3677d9c1a061acda1c587607b1a77519dcb30514851016e8e432249`
- **Reviewed paths**: 2
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `tests/charness_cli/test_codex_cache_refresh.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-rest-followup4-packet.json --packet-sha256 b634d5d19dd2498b2b88500dd0767810d45ccd402a6c1a812f2495e2b7bccc0b --identity-sha256 58931872a3677d9c1a061acda1c587607b1a77519dcb30514851016e8e432249
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
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md"
    ],
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/charness_cli/test_codex_cache_refresh.py"
    ],
    "comparison_identity_sha256": "58931872a3677d9c1a061acda1c587607b1a77519dcb30514851016e8e432249",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 2,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md"
    ],
    "unchanged_selected_paths": [
      "tests/charness_cli/test_codex_cache_refresh.py"
    ]
  },
  "context_size_bytes": 5149,
  "final_reviewed_input_identity_sha256": "58931872a3677d9c1a061acda1c587607b1a77519dcb30514851016e8e432249",
  "final_selected_path_count": 2,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-rest-followup3",
  "prior_findings": [
    {
      "action": "Narrow the clock-injection claim to the output-backed cases; describe EOF as waiting for process exit and unrelated-stream as timing out via the injected clock.",
      "evidence": [
        "The note says the named lifecycle test “and the other Codex app-server refresh tests inject the reader's clock.”",
        "In `test_codex_cache_refresh_maps_transport_failures_to_existing_envelope`, the `eof` branch skips `_wait_on_app_server_events`, waits with `proc.wait()`, then calls the response waiter with `deadline=0.0`.",
        "The `unrelated-stream` branch does inject a clock that advances past the deadline; the other mapped cases use the event-wait helper."
      ],
      "id": "release-note-overstates-codex-test-timing",
      "severity": "medium",
      "summary": "The note still overstates clock injection: the EOF case waits for the fake process to exit but does not inject the reader's clock."
    }
  ],
  "prior_lens": "Recheck release-note-overstates-codex-test-timing only",
  "prior_next_move": "Revise the bullet to distinguish output-backed cases, EOF's process-exit wait, and unrelated-stream's injected-clock timeout.",
  "prior_non_claims": [
    "No assessment of the entry-spawn or worker-timeout claims.",
    "No tests were run; review is limited to the supplied notes and test file."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-rest-followup3-packet.json",
  "prior_packet_sha256": "d7102d9bb8ce12eae3bc78a4135c621b0931c76bb79813b6d297657a37410bda",
  "prior_reviewed_input_identity_sha256": "9b6846995dc1f8e8161a741f795092c39eab68b91c53a549596986f8c06a3a04",
  "prior_reviewed_paths": 2,
  "prior_scope": "Third follow-up on release-8160-rest (522aa1769): the notes now say the unrelated-stream case takes its timeout from an injected clock, and the success and error cases wait on the fake output or exit.",
  "prior_verdict": "block",
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "tests/charness_cli/test_codex_cache_refresh.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "tests/charness_cli/test_codex_cache_refresh.py"
    ],
    "comparison_identity_sha256": "58931872a3677d9c1a061acda1c587607b1a77519dcb30514851016e8e432249",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8160-rest-followup3",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "d7102d9bb8ce12eae3bc78a4135c621b0931c76bb79813b6d297657a37410bda",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-rest-followup3",
        "partial_result_sha256": null,
        "result_sha256": "e10b2da2146c35bf653079659d1a59fd621334bf4cf79d12b13d22d8f8af760c",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "9b6846995dc1f8e8161a741f795092c39eab68b91c53a549596986f8c06a3a04",
      "semantic_input": {
        "entries": 2,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "9b6846995dc1f8e8161a741f795092c39eab68b91c53a549596986f8c06a3a04",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md"
    ],
    "unchanged_selected_paths": [
      "tests/charness_cli/test_codex_cache_refresh.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8160-rest-followup3/result.json",
  "source_sha256": "e10b2da2146c35bf653079659d1a59fd621334bf4cf79d12b13d22d8f8af760c"
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
      "path_set_sha256": "56b2fcdfcbbd3ecd5c25c406361c853048915ada7ab72cf27894e3b668acdcfc",
      "section_id": "changed-files-and-owning-surfaces",
      "selected_path_count": 2,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "critique-prepare-non-goals",
      "selected_path_count": 2,
      "status": "verified"
    },
    {
      "binding": "adapter-static-content",
      "mode": "static",
      "path_binding": null,
      "path_check": "not-applicable",
      "path_set_sha256": null,
      "section_id": "reviewer-packet-semantic-question",
      "selected_path_count": 2,
      "status": "verified"
    }
  ],
  "selected_paths": [
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "tests/charness_cli/test_codex_cache_refresh.py"
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

Owning surfaces:
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- repo-python: Repo-owned Python code and tests.
  source matches: tests/charness_cli/test_codex_cache_refresh.py
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
