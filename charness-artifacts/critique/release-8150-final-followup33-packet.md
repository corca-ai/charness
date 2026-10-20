# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-10-20T17:24:38Z
- **Prepared for**: release-8150-final-followup33
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `741de47d00b862330e5ec9502f339f925049745c794aaeed586437d509830d1c`
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
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8150-final-followup33-packet.json --packet-sha256 9d44016be7e0cce31fc8dc4fa1331e642b26727ffc6bac70c4e3b8bc21dc41c8 --identity-sha256 741de47d00b862330e5ec9502f339f925049745c794aaeed586437d509830d1c
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
      "scripts/task_run/task_run_progress_rule.py"
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
    "comparison_identity_sha256": "741de47d00b862330e5ec9502f339f925049745c794aaeed586437d509830d1c",
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_paths": 19,
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
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
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ]
  },
  "context_size_bytes": 11673,
  "final_reviewed_input_identity_sha256": "741de47d00b862330e5ec9502f339f925049745c794aaeed586437d509830d1c",
  "final_selected_path_count": 19,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8150-final-followup32",
  "prior_findings": [
    {
      "action": "Scope the source docstring and comment to starts the check has seen. Qualify the spec's interruption inventory as covering observed commands, and state how an unseen interrupted command is represented or omitted.",
      "evidence": [
        "`scripts/task_run/task_run_progress_rule.py` says: “A command that started since the previous check and is still running defers the request, and so the stop, by one check,” without qualifying that the check must have seen the start.",
        "The same file's `on_tick` comment says “nothing is killed before it has run a full window,” although a start held behind the serialized reader's completion probe or event-log write can be killed moments after starting.",
        "The spec says the message reports every interrupted command and the stop reason names those commands the same way. An unseen start is absent from `in_flight`, so it cannot be named or counted there even when the process-group kill interrupts it.",
        "`test_a_completion_probe_does_not_hold_the_rule_lock` now states that the production reader is single-threaded and reads the next line only after the probe; its name describes the lock property it tests."
      ],
      "id": "unseen-start-guarantee-remains-in-source",
      "severity": "medium",
      "summary": "The release notes, spec, and guide now disclose that an unseen start can be interrupted, and the renamed test accurately limits its claim to rule-lock behavior. The bound progress-rule docstring and code comment still state a broader age guarantee. The spec also promises that interruption messages and stop reasons name the commands they kill, though an unseen start is absent from the in-flight state used to build those messages."
    },
    {
      "action": "Describe later starts as unseen while the write remains blocked and unavailable to the due check, while allowing that the reader could resume after close.",
      "evidence": [
        "`StampingPipe.close()` joins and waits for the sink lock only for bounded periods, then marks the pipe released while the reader may still be alive.",
        "`_feed()` calls `_observe(line)` after `_emit(...)`; if an in-flight sink write eventually returns, the reader can observe subsequent lines even though their bytes are dropped.",
        "The release notes and spec say that after a hung log write no later command start is seen."
      ],
      "id": "hung-write-never-seen-is-too-absolute",
      "severity": "low",
      "summary": "The disclosure that a hung event-log write blocks timely observation is accurate, but saying later starts are “never seen” is stronger than the implementation guarantees. Close is bounded and may return while the write remains in flight; if it later returns, the reader can continue to call the observer for buffered lines after close, although no later due check may remain to act on them."
    }
  ],
  "prior_lens": "release lock-in final pass",
  "prior_next_move": "Correct the remaining source and spec claims about unseen commands, then narrow the hung-write wording to the observation window relevant to a due check.",
  "prior_non_claims": [
    "Reviewed only the packet's inline semantic input; did not inspect workspace paths.",
    "Did not run tests or independently verify the reported probe measurements or live executor behavior.",
    "The supplied goal lineage is not-goal-bound; this review does not close a Goal Run."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8150-final-followup32-packet.json",
  "prior_packet_sha256": "86f4a3d539613f8e5a00a91a1b89cf2c25417a6781f9f95346ae531dc5b60a6e",
  "prior_reviewed_input_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
  "prior_reviewed_paths": 19,
  "prior_scope": "follow-up at fbf0c0bd9 on release-8150-final-followup31: the young-command guarantee is now scoped to commands the check has seen; spec, notes and guide disclose that a start held behind the reader completion probe or an event-log write is unseen and can be interrupted moments after it started, and that after a hung log write no later start is seen; the rule-lock test is renamed to what it proves; no code change",
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
    "comparison_identity_sha256": "741de47d00b862330e5ec9502f339f925049745c794aaeed586437d509830d1c",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [],
    "prior_binding": {
      "attempt_id": "release-8150-final-followup32",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "86f4a3d539613f8e5a00a91a1b89cf2c25417a6781f9f95346ae531dc5b60a6e",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8150-final-followup32",
        "partial_result_sha256": null,
        "result_sha256": "aaf8794a8d4145bcd10a69932aab67912ab7df59d0f925a574f9f406cba3ccba",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
      "semantic_input": {
        "entries": 19,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "e28dfbaff006a1bbe900dd0cf36542846ebc432b6897df74f1e82ceb1760b45d",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness-artifacts/release/2026-10-20-v8.15.0-notes.md",
      "charness-artifacts/spec/lane-progress-rule.md",
      "scripts/task_run/task_run_progress_rule.py"
    ],
    "unchanged_selected_paths": [
      "charness",
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
      "tests/charness_cli/test_task_run_progress_rule.py",
      "tests/charness_cli/test_task_run_self_review.py",
      "tests/test_debug_scaffold.py"
    ]
  },
  "source": "charness-artifacts/critique/workers/release-8150-final-followup32/result.json",
  "source_sha256": "aaf8794a8d4145bcd10a69932aab67912ab7df59d0f925a574f9f406cba3ccba"
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
