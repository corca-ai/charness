# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-09-12T08:40:54Z
- **Prepared for**: v8.6.3 operator release boundary
- **Prepared targets**: 1
  - `v8.6.3`
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `79f0cfeba5700e9adc8dffea8717bb31b43a04ecd659f0b1a551b6f0a1f75ee3`
- **Reviewed paths**: 38
  - `charness-artifacts/critique/workers/release-8-6-3-operator-final/result.json`
  - `charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md`
  - `charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json`
  - `charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md`
  - `docs/release-workflow-dogfood.md`
  - `scripts/agent-runtime/codex-eval-runtime.mjs`
  - `scripts/agent-runtime/run-local-eval-test.mjs`
  - `scripts/evidence/probe_stimulus_replay.py`
  - `scripts/lessons/lesson_ledger_writer_lib.py`
  - `scripts/plugin_export/validate_packaging_install_surface.py`
  - `scripts/prepush_close_keyword_guard.py`
  - `scripts/run_quality_engine.py`
  - `scripts/run_quality_engine_runtime.py`
  - `scripts/support_sync_lib.py`
  - `skills/public/quality/scripts/check_provenance_contract.py`
  - `skills/public/quality/scripts/inventory_empty_scope_honesty.py`
  - `skills/public/release/scripts/check_fresh_checkout_probes.py`
  - `skills/public/release/scripts/publish_release_artifact.py`
  - `skills/public/release/scripts/publish_release_common.py`
  - `skills/public/release/scripts/publish_release_resume.py`
  - `skills/public/release/scripts/publish_release_resume_closeout.py`
  - `skills/public/release/scripts/publish_release_resume_publish.py`
  - `skills/public/release/scripts/publish_release_resume_state.py`
  - `skills/support/markdown-preview/scripts/markdown_preview_render.py`
  - `tests/agent-runtime/native.test.mjs`
  - `tests/control_plane/test_support_sync_helpers.py`
  - `tests/quality_gates/quality_runner_seed.py`
  - `tests/quality_gates/support.py`
  - `tests/quality_gates/test_empty_scope_honesty_inventory.py`
  - `tests/quality_gates/test_packaging_validation.py`
  - `tests/quality_gates/test_prepush_close_keyword_guard.py`
  - `tests/quality_gates/test_quality_runner.py`
  - `tests/quality_gates/test_release_quality_status_binding.py`
  - `tests/quality_gates/test_release_resume_edge_coverage.py`
  - `tests/quality_gates/test_release_resume_state_validation.py`
  - `tests/quality_gates/test_release_resume_surface_revalidation.py`
  - `tests/quality_gates/test_semantic_review_command.py`
  - `tests/test_lesson_ledger.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/release-863-bounded-operator-20260912-packet.json --packet-sha256 9bbfe16db0d72d13d0edafa6106acbe852a6f5dda4e93a459c962c6484095e05 --identity-sha256 79f0cfeba5700e9adc8dffea8717bb31b43a04ecd659f0b1a551b6f0a1f75ee3
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
Bound review paths for working tree: (narrow follow-up scope)
Exact reviewed-path manifest:
- charness-artifacts/critique/workers/release-8-6-3-operator-final/result.json
- charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md
- charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json
- charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md
- docs/release-workflow-dogfood.md
- scripts/agent-runtime/codex-eval-runtime.mjs
- scripts/agent-runtime/run-local-eval-test.mjs
- scripts/evidence/probe_stimulus_replay.py
- scripts/lessons/lesson_ledger_writer_lib.py
- scripts/plugin_export/validate_packaging_install_surface.py
- scripts/prepush_close_keyword_guard.py
- scripts/run_quality_engine.py
- scripts/run_quality_engine_runtime.py
- scripts/support_sync_lib.py
- skills/public/quality/scripts/check_provenance_contract.py
- skills/public/quality/scripts/inventory_empty_scope_honesty.py
- skills/public/release/scripts/check_fresh_checkout_probes.py
- skills/public/release/scripts/publish_release_artifact.py
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_resume.py
- skills/public/release/scripts/publish_release_resume_closeout.py
- skills/public/release/scripts/publish_release_resume_publish.py
- skills/public/release/scripts/publish_release_resume_state.py
- skills/support/markdown-preview/scripts/markdown_preview_render.py
- tests/agent-runtime/native.test.mjs
- tests/control_plane/test_support_sync_helpers.py
- tests/quality_gates/quality_runner_seed.py
- tests/quality_gates/support.py
- tests/quality_gates/test_empty_scope_honesty_inventory.py
- tests/quality_gates/test_packaging_validation.py
- tests/quality_gates/test_prepush_close_keyword_guard.py
- tests/quality_gates/test_quality_runner.py
- tests/quality_gates/test_release_quality_status_binding.py
- tests/quality_gates/test_release_resume_edge_coverage.py
- tests/quality_gates/test_release_resume_state_validation.py
- tests/quality_gates/test_release_resume_surface_revalidation.py
- tests/quality_gates/test_semantic_review_command.py
- tests/test_lesson_ledger.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/agent-runtime/codex-eval-runtime.mjs, scripts/agent-runtime/run-local-eval-test.mjs, scripts/evidence/probe_stimulus_replay.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/prepush_close_keyword_guard.py, scripts/run_quality_engine.py, scripts/run_quality_engine_runtime.py, scripts/support_sync_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py, skills/support/markdown-preview/scripts/markdown_preview_render.py
  sync: python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/plugin_export/validate_packaging.py --repo-root ., python3 -m tools.validate_packaging_committed --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md, charness-artifacts/spec/2026-09-12-release-consumer-acceptance.md, docs/release-workflow-dogfood.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/release/2026-09-12-cross-repo-release-workflow-incident.json
  verify: python3 scripts/gates/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/gates/validate_quality_artifact.py --repo-root ., python3 scripts/gates/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py, skills/support/markdown-preview/scripts/markdown_preview_render.py
  verify: python3 -m tools.validate_skills --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/gates/check_skill_ownership_overlap.py --repo-root ., python3 scripts/gates/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 -m tools.validate_public_skill_validation --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py
  verify: python3 -m tools.validate_public_skill_dogfood --repo-root .
- agent-runtime-js: Repo-owned JavaScript agent-runtime modules and their native test command.
  source matches: scripts/agent-runtime/codex-eval-runtime.mjs, scripts/agent-runtime/run-local-eval-test.mjs, tests/agent-runtime/native.test.mjs
  verify: npm run test:agent-runtime, npm run test:mutation:js:dry-run
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/workers/release-8-6-3-operator-final/result.json
  verify: python3 scripts/review/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-09-12-release-workflow-dogfood-blocked.md
  sync: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --check
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: scripts/support_sync_lib.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: scripts/support_sync_lib.py
  verify: python3 -m tools.validate_integrations --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/evidence/probe_stimulus_replay.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/prepush_close_keyword_guard.py, scripts/run_quality_engine.py, scripts/run_quality_engine_runtime.py, scripts/support_sync_lib.py, tests/control_plane/test_support_sync_helpers.py, tests/quality_gates/quality_runner_seed.py, tests/quality_gates/support.py, tests/quality_gates/test_empty_scope_honesty_inventory.py, tests/quality_gates/test_packaging_validation.py, tests/quality_gates/test_prepush_close_keyword_guard.py, tests/quality_gates/test_quality_runner.py, tests/quality_gates/test_release_quality_status_binding.py, tests/quality_gates/test_release_resume_edge_coverage.py, tests/quality_gates/test_release_resume_state_validation.py, tests/quality_gates/test_release_resume_surface_revalidation.py, tests/quality_gates/test_semantic_review_command.py, tests/test_lesson_ledger.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/gates/check_code_lengths.py --repo-root . --require-git-file-listing, python3 -m tools.validate_attention_state_visibility --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/gates/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/gates/check_subprocess_form.py --repo-root . --require-git-file-listing, ./scripts/check-shell.sh, python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/evidence/probe_stimulus_replay.py, scripts/lessons/lesson_ledger_writer_lib.py, scripts/plugin_export/validate_packaging_install_surface.py, scripts/prepush_close_keyword_guard.py, scripts/run_quality_engine.py, scripts/run_quality_engine_runtime.py, scripts/support_sync_lib.py, skills/public/quality/scripts/check_provenance_contract.py, skills/public/quality/scripts/inventory_empty_scope_honesty.py, skills/public/release/scripts/check_fresh_checkout_probes.py, skills/public/release/scripts/publish_release_artifact.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_resume.py, skills/public/release/scripts/publish_release_resume_closeout.py, skills/public/release/scripts/publish_release_resume_publish.py, skills/public/release/scripts/publish_release_resume_state.py, skills/support/markdown-preview/scripts/markdown_preview_render.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/plugin_export/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/retro_debug/build_debug_seam_risk_index.py --repo-root . --write
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
