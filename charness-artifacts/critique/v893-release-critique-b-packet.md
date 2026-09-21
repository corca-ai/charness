# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-21T02:10:06Z
- **Prepared for**: 849119829220c85d63ca20a20be1308b4e4c7a2b..a2b18fcf2169a3636995d0ed94b3dfe88c66ed02
- **Substrate mode**: `committed-ref`
- **Changed ref**: `849119829220c85d63ca20a20be1308b4e4c7a2b..a2b18fcf2169a3636995d0ed94b3dfe88c66ed02`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `a91b1b080a6be7c8da5251b2280597e0087254780d6e5cde7ea48c35eb174ac5`
- **Reviewed paths**: 51
  - `charness-artifacts/critique/review-20260921T103959Z-762925-packet.json`
  - `charness-artifacts/critique/review-20260921T103959Z-762925-packet.md`
  - `charness-artifacts/critique/review-20260921T104030Z-763442-packet.json`
  - `charness-artifacts/critique/review-20260921T104030Z-763442-packet.md`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/attempt-manifest.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stderr`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stdout`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/bounded-review-result.schema.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/capability.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/delivery.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/lifecycle.yaml`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/partial-result.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/receipt.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/result.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/review-prompt.md`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/run-plan.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stderr`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stdout`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0000-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0001-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0002-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0003-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/manifest.json`
  - `charness-artifacts/critique/workers/review-20260921T103959Z-762925/worker-report.yaml`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/attempt-manifest.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stderr`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stdout`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/bounded-review-result.schema.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/capability.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/delivery.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/lifecycle.yaml`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/partial-result.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/receipt.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/result.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/review-prompt.md`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/run-plan.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stderr`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stdout`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0000-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0001-content.bin`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/manifest.json`
  - `charness-artifacts/critique/workers/review-20260921T104030Z-763442/worker-report.yaml`
  - `docs/implementation-discipline.md`
  - `scripts/task_run/task_run.py`
  - `scripts/task_run/task_run_completion_next_step.py`
  - `scripts/task_run/task_run_git.py`
  - `scripts/task_run/task_run_lane_runner.py`
  - `skills/public/quality/references/attention-state-visibility.json`
  - `skills/public/release/references/adapter-contract.md`
  - `tests/charness_cli/test_task_run.py`
  - `tests/quality_gates/test_release_run_planner.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v893-release-critique-b-packet.json --packet-sha256 06c1566f0e31b6caaf6261a38bc9e9e15014955a20981232234880f7c4f07ba8 --identity-sha256 a91b1b080a6be7c8da5251b2280597e0087254780d6e5cde7ea48c35eb174ac5
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Execution mode**: `file-backed-worker`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/review/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Bound review paths for ref `849119829220c85d63ca20a20be1308b4e4c7a2b..a2b18fcf2169a3636995d0ed94b3dfe88c66ed02`: (narrow follow-up scope)
Exact reviewed-path manifest:
- charness-artifacts/critique/review-20260921T103959Z-762925-packet.json
- charness-artifacts/critique/review-20260921T103959Z-762925-packet.md
- charness-artifacts/critique/review-20260921T104030Z-763442-packet.json
- charness-artifacts/critique/review-20260921T104030Z-763442-packet.md
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/attempt-manifest.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stderr
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stdout
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/bounded-review-result.schema.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/capability.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/delivery.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/lifecycle.yaml
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/partial-result.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/receipt.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/result.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/review-prompt.md
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/run-plan.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stderr
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stdout
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0000-content.bin
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0001-content.bin
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0002-content.bin
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0003-content.bin
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/manifest.json
- charness-artifacts/critique/workers/review-20260921T103959Z-762925/worker-report.yaml
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/attempt-manifest.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stderr
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stdout
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/bounded-review-result.schema.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/capability.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/delivery.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/lifecycle.yaml
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/partial-result.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/receipt.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/result.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/review-prompt.md
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/run-plan.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stderr
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stdout
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0000-content.bin
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0001-content.bin
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/manifest.json
- charness-artifacts/critique/workers/review-20260921T104030Z-763442/worker-report.yaml
- docs/implementation-discipline.md
- scripts/task_run/task_run.py
- scripts/task_run/task_run_completion_next_step.py
- scripts/task_run/task_run_git.py
- scripts/task_run/task_run_lane_runner.py
- skills/public/quality/references/attention-state-visibility.json
- skills/public/release/references/adapter-contract.md
- tests/charness_cli/test_task_run.py
- tests/quality_gates/test_release_run_planner.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_completion_next_step.py, scripts/task_run/task_run_git.py, scripts/task_run/task_run_lane_runner.py, skills/public/quality/references/attention-state-visibility.json, skills/public/release/references/adapter-contract.md
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/review-20260921T103959Z-762925-packet.md, charness-artifacts/critique/review-20260921T104030Z-763442-packet.md, charness-artifacts/critique/workers/review-20260921T103959Z-762925/review-prompt.md, charness-artifacts/critique/workers/review-20260921T104030Z-763442/review-prompt.md, docs/implementation-discipline.md, skills/public/release/references/adapter-contract.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/public/release/references/adapter-contract.md
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/public/release/references/adapter-contract.md
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/public/release/references/adapter-contract.md
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/review-20260921T103959Z-762925-packet.json, charness-artifacts/critique/review-20260921T103959Z-762925-packet.md, charness-artifacts/critique/review-20260921T104030Z-763442-packet.json, charness-artifacts/critique/review-20260921T104030Z-763442-packet.md, charness-artifacts/critique/workers/review-20260921T103959Z-762925/attempt-manifest.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stderr, charness-artifacts/critique/workers/review-20260921T103959Z-762925/backend.stdout, charness-artifacts/critique/workers/review-20260921T103959Z-762925/bounded-review-result.schema.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/capability.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/delivery.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/lifecycle.yaml, charness-artifacts/critique/workers/review-20260921T103959Z-762925/partial-result.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/receipt.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/result.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/review-prompt.md, charness-artifacts/critique/workers/review-20260921T103959Z-762925/run-plan.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stderr, charness-artifacts/critique/workers/review-20260921T103959Z-762925/runner.stdout, charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0000-content.bin, charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0001-content.bin, charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0002-content.bin, charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/0003-content.bin, charness-artifacts/critique/workers/review-20260921T103959Z-762925/semantic-input/manifest.json, charness-artifacts/critique/workers/review-20260921T103959Z-762925/worker-report.yaml, charness-artifacts/critique/workers/review-20260921T104030Z-763442/attempt-manifest.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stderr, charness-artifacts/critique/workers/review-20260921T104030Z-763442/backend.stdout, charness-artifacts/critique/workers/review-20260921T104030Z-763442/bounded-review-result.schema.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/capability.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/delivery.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/lifecycle.yaml, charness-artifacts/critique/workers/review-20260921T104030Z-763442/partial-result.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/receipt.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/result.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/review-prompt.md, charness-artifacts/critique/workers/review-20260921T104030Z-763442/run-plan.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stderr, charness-artifacts/critique/workers/review-20260921T104030Z-763442/runner.stdout, charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0000-content.bin, charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/0001-content.bin, charness-artifacts/critique/workers/review-20260921T104030Z-763442/semantic-input/manifest.json, charness-artifacts/critique/workers/review-20260921T104030Z-763442/worker-report.yaml
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_completion_next_step.py, scripts/task_run/task_run_git.py, scripts/task_run/task_run_lane_runner.py, tests/charness_cli/test_task_run.py, tests/quality_gates/test_release_run_planner.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/task_run/task_run.py, scripts/task_run/task_run_completion_next_step.py, scripts/task_run/task_run_git.py, scripts/task_run/task_run_lane_runner.py
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
