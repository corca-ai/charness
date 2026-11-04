# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-11-04T20:41:16Z
- **Prepared for**: working tree
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `778de6f15d22d4f9da70feb547c89f004cda4454c53a0836ed2a6d76626a53a0`
- **Reviewed paths**: 5
  - `charness`
  - `charness-artifacts/release/2026-11-05-v8.16.0-notes.md`
  - `docs/claude-task-executor.md`
  - `scripts/task_run/task_run_claude_sandbox.py`
  - `tests/charness_cli/test_task_run_claude_sandbox.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-8160-claude-lane-followup1-packet.json --packet-sha256 a9b9b65c522f5d76482ddda0ed0f9cb9ddee259cf16e4ca1070718a201b2b640 --identity-sha256 778de6f15d22d4f9da70feb547c89f004cda4454c53a0836ed2a6d76626a53a0
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
      "charness",
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "docs/cli-reference.md",
      "scripts/task_run/task_run_claude_sandbox.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ],
    "comparison_identity_paths": [
      ".agents/temp-producers.yaml",
      "charness",
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/agent-task-runs.md",
      "docs/claude-task-executor.md",
      "docs/cli-reference.md",
      "scripts/cli/cmd_task.py",
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_attempts.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_events.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_detach.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_steering.py",
      "scripts/task_run/task_run_support.py",
      "tests/charness_cli/test_task_run.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_events.py",
      "tests/charness_cli/test_task_run_claude_model.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_executor_probe.py",
      "tests/charness_cli/test_task_run_steer.py",
      "tests/coverage_debt/test_batch13.py"
    ],
    "comparison_identity_sha256": "f4b0c06e44c73bc1b6e811adecc056e027e9e0c964c463bb52295164e37ea2c1",
    "new_paths": [],
    "omitted_changed_prior_paths": [
      "docs/cli-reference.md"
    ],
    "prior_paths": 33,
    "selected_changed_prior_paths": [
      "charness",
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "scripts/task_run/task_run_claude_sandbox.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ],
    "unchanged_selected_paths": []
  },
  "context_size_bytes": 12034,
  "final_reviewed_input_identity_sha256": "778de6f15d22d4f9da70feb547c89f004cda4454c53a0836ed2a6d76626a53a0",
  "final_selected_path_count": 5,
  "kind": "charness.review_followup_context.v1",
  "omitted_finding_ids": [],
  "prior_attempt_id": "release-8160-claude-lane",
  "prior_findings": [
    {
      "action": "Enforce an egress boundary that permits the authenticated Anthropic proxy while blocking direct access to metadata and other host or network services. Add an arbitrary-subprocess boundary test before claiming provider credentials are isolated.",
      "evidence": [
        "scripts/task_run/task_run_claude_sandbox.py builds bwrap with --unshare-pid, --unshare-ipc, and --unshare-uts, but no network namespace or egress restriction.",
        "scripts/task_run/task_run_claude_auth.py forwards authenticated proxy requests to api.anthropic.com; nothing in the sandbox forces other child traffic through that proxy.",
        "On hosts exposing credential-bearing metadata or internal services, an arbitrary Claude subprocess can attempt direct requests to them."
      ],
      "id": "F-001",
      "severity": "high",
      "summary": "The Claude sandbox does not restrict network access, so the fixed-upstream auth proxy does not prevent direct access to host or cloud credential services."
    },
    {
      "action": "Mask Docker credential state and audit other known host credential locations, or deny home reads by default. Add a sandbox test that proves a synthetic credential at the host path cannot be read.",
      "evidence": [
        "scripts/task_run/task_run_claude_sandbox.py mounts the host root read-only and masks only the listed _SECRET_DIRECTORIES and _SECRET_FILES.",
        "Those lists omit ~/.docker and ~/.docker/config.json, which can contain registry authentication data.",
        "The worktree credential scan does not cover this host-home path."
      ],
      "id": "F-002",
      "severity": "high",
      "summary": "The home credential masks omit common Docker credentials, leaving them readable inside the sandbox when present."
    },
    {
      "action": "Hide host control sockets from the sandbox, including container and other daemon APIs, and add a boundary test that confirms they cannot be reached.",
      "evidence": [
        "scripts/task_run/task_run_claude_sandbox.py masks only /run/user/<uid> while preserving the rest of the root filesystem with --ro-bind / /.",
        "Sockets such as /run/docker.sock or /var/run/docker.sock are not masked; read-only mounting does not prevent connecting to a socket.",
        "Where the lane retains permission to use such a socket, a daemon can perform writes on its behalf beyond the lane worktree, runtime, and explicit grants."
      ],
      "id": "F-003",
      "severity": "high",
      "summary": "Host daemon sockets remain visible, allowing a lane with socket access to request host-side actions outside the filesystem grants."
    },
    {
      "action": "Make the release CI job require bubblewrap and fail if it is missing; record that the OS-boundary tests ran rather than skipped.",
      "evidence": [
        "tests/charness_cli/test_task_run_claude_sandbox.py skips its OS-boundary tests when shutil.which(\"bwrap\") is false.",
        "The release notes say CI runs only on Linux, but the supplied packet does not show that CI provisions bubblewrap or records these tests as executed."
      ],
      "id": "F-004",
      "severity": "medium",
      "summary": "The real bubblewrap boundary tests can skip, and the packet does not establish that release CI runs them with bubblewrap installed."
    },
    {
      "action": "Update the parser help to describe Claude’s supported effort and grant behavior, then regenerate docs/cli-reference.md.",
      "evidence": [
        "The charness --effort help lists Codex and Muse effort sets, and --grant-writable says a Codex lane may write.",
        "docs/cli-reference.md reproduces those descriptions.",
        "The v8.16.0 notes state that Claude lanes accept --grant-writable and that Claude is a supported executor."
      ],
      "id": "F-005",
      "severity": "low",
      "summary": "The task-run CLI help and generated CLI reference underdescribe Claude support and writable grants."
    }
  ],
  "prior_lens": "Gawande operational and boundary safety",
  "prior_next_move": "Close the three host-boundary paths, require the bubblewrap tests to run in release CI, update CLI help and its generated reference, then rerun the bounded review.",
  "prior_non_claims": [
    "This review is limited to the supplied inline semantic bytes; it does not establish the exact delta from v8.15.0 because no patch bytes were included.",
    "The metadata-service risk depends on the host exposing such a service; the sandbox currently does not block attempts to reach it.",
    "No claim is made that all possible credential locations or host IPC endpoints were exhaustively enumerated."
  ],
  "prior_packet_path": "charness-artifacts/critique/release-8160-claude-lane-packet.json",
  "prior_packet_sha256": "0e81c7573ad9f9f1b57ec6a72b373b9018ac393ceb8707ca7f91f5a48659f0ec",
  "prior_reviewed_input_identity_sha256": "6954404e7e7699bd558350186afc0b8c4681bcd6a50b2d090d073499395c5f2f",
  "prior_reviewed_paths": 33,
  "prior_scope": "Release critique for charness v8.16.0 (minor), part 1 of 2: the Claude task-run executor and the task-run CLI/runtime changes since tag v8.15.0, plus the v8.16.0 notes. Files are the current tree; git diff v8.15.0..HEAD shows what changed.",
  "prior_verdict": "block",
  "selected_paths": [
    "charness",
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/task_run/task_run_claude_sandbox.py",
    "tests/charness_cli/test_task_run_claude_sandbox.py"
  ],
  "selection": "explicit-with-selection-receipt",
  "selection_receipt": {
    "comparison_identity_paths": [
      ".agents/temp-producers.yaml",
      "charness",
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/agent-task-runs.md",
      "docs/claude-task-executor.md",
      "docs/cli-reference.md",
      "scripts/cli/cmd_task.py",
      "scripts/task_run/task_run.py",
      "scripts/task_run/task_run_attempts.py",
      "scripts/task_run/task_run_brief_critique.py",
      "scripts/task_run/task_run_claude_auth.py",
      "scripts/task_run/task_run_claude_events.py",
      "scripts/task_run/task_run_claude_review.py",
      "scripts/task_run/task_run_claude_sandbox.py",
      "scripts/task_run/task_run_contract.py",
      "scripts/task_run/task_run_detach.py",
      "scripts/task_run/task_run_event_timing.py",
      "scripts/task_run/task_run_execution.py",
      "scripts/task_run/task_run_lane_options.py",
      "scripts/task_run/task_run_lane_runner.py",
      "scripts/task_run/task_run_runtime.py",
      "scripts/task_run/task_run_steering.py",
      "scripts/task_run/task_run_support.py",
      "tests/charness_cli/test_task_run.py",
      "tests/charness_cli/test_task_run_cache_custody.py",
      "tests/charness_cli/test_task_run_claude_events.py",
      "tests/charness_cli/test_task_run_claude_model.py",
      "tests/charness_cli/test_task_run_claude_review.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py",
      "tests/charness_cli/test_task_run_event_timing.py",
      "tests/charness_cli/test_task_run_executor_probe.py",
      "tests/charness_cli/test_task_run_steer.py",
      "tests/coverage_debt/test_batch13.py"
    ],
    "comparison_identity_sha256": "f4b0c06e44c73bc1b6e811adecc056e027e9e0c964c463bb52295164e37ea2c1",
    "explicit_paths": true,
    "new_paths": [],
    "omitted_changed_prior_paths": [
      "docs/cli-reference.md"
    ],
    "prior_binding": {
      "attempt_id": "release-8160-claude-lane",
      "identity_verification": "recorded-self-digest",
      "packet_sha256": "0e81c7573ad9f9f1b57ec6a72b373b9018ac393ceb8707ca7f91f5a48659f0ec",
      "packet_verification": "canonical-integrity-only",
      "result_carrier": {
        "attempt_id": "release-8160-claude-lane",
        "partial_result_sha256": null,
        "result_sha256": "01149c86360833ccd81af6ad7dc363d52130394dae5f1a0b34e9a9c3165001e2",
        "source_path": null,
        "status": "verified"
      },
      "reviewed_input_identity_sha256": "6954404e7e7699bd558350186afc0b8c4681bcd6a50b2d090d073499395c5f2f",
      "semantic_input": {
        "entries": 33,
        "status": "verified"
      },
      "status": "verified"
    },
    "prior_identity_sha256": "6954404e7e7699bd558350186afc0b8c4681bcd6a50b2d090d073499395c5f2f",
    "rationale": "Explicit paths were supplied to include newly introduced consumers or intentionally widen the stimulus; selection is not approval.",
    "selected_changed_prior_paths": [
      "charness",
      "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
      "docs/claude-task-executor.md",
      "scripts/task_run/task_run_claude_sandbox.py",
      "tests/charness_cli/test_task_run_claude_sandbox.py"
    ],
    "unchanged_selected_paths": []
  },
  "source": "charness-artifacts/critique/workers/release-8160-claude-lane/result.json",
  "source_sha256": "01149c86360833ccd81af6ad7dc363d52130394dae5f1a0b34e9a9c3165001e2"
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
      "path_set_sha256": "2eca3e1bcbd4097d4aed7290c4886873b54332650b27aecd20cf8fb31ab31f1e",
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
    "charness",
    "charness-artifacts/release/2026-11-05-v8.16.0-notes.md",
    "docs/claude-task-executor.md",
    "scripts/task_run/task_run_claude_sandbox.py",
    "tests/charness_cli/test_task_run_claude_sandbox.py"
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
- charness-artifacts/release/2026-11-05-v8.16.0-notes.md
- docs/claude-task-executor.md
- scripts/task_run/task_run_claude_sandbox.py
- tests/charness_cli/test_task_run_claude_sandbox.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run_claude_sandbox.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md, docs/claude-task-executor.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-11-05-v8.16.0-notes.md
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 -m tools.validate_current_pointer_freshness --repo-root ., python3 -m json.tool .agents/surfaces.json
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/task_run/task_run_claude_sandbox.py, tests/charness_cli/test_task_run_claude_sandbox.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run_claude_sandbox.py
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
