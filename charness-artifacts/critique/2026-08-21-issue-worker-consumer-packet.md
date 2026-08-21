# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-21T04:30:20Z
- **Prepared for**: issue closeout worker carrier consumer boundary
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `e16fbc5be314e9f6313c71dc06b765a40068e67b3bbd96126df87e603bd66561`
- **Reviewed paths**: 11
- **Sections**: 3
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md
- charness-artifacts/metrics/rca-ledger.jsonl
- plugins/charness/scripts/critique_reviewed_input_binding.py
- plugins/charness/scripts/critique_reviewer_evidence.py
- plugins/charness/scripts/retro_persistence_lib.py
- plugins/charness/scripts/reviewed_input_identity.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/shared/references/fresh-eye-subagent-review.md
- plugins/charness/shared/scripts/reviewer_delivery_fields.py
- plugins/charness/shared/scripts/reviewer_delivery_state.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py
- plugins/charness/skills/issue/SKILL.md
- plugins/charness/skills/issue/references/closeout-discipline.md
- plugins/charness/skills/issue/scripts/issue_critique_observer.py
- plugins/charness/skills/issue/scripts/issue_resolution_critique.py
- plugins/charness/skills/prove/SKILL.md
- plugins/charness/skills/retro/scripts/plan_retro_run.py
- scripts/critique_reviewed_input_binding.py
- scripts/critique_reviewer_evidence.py
- scripts/retro_persistence_lib.py
- scripts/reviewed_input_identity.py
- scripts/validate_critique_artifacts.py
- skills/public/critique/SKILL.md
- skills/public/critique/scripts/scaffold_critique_artifact.py
- skills/public/issue/SKILL.md
- skills/public/issue/references/closeout-discipline.md
- skills/public/issue/scripts/issue_critique_observer.py
- skills/public/issue/scripts/issue_resolution_critique.py
- skills/public/prove/SKILL.md
- skills/public/retro/scripts/plan_retro_run.py
- skills/shared/references/fresh-eye-subagent-review.md
- skills/shared/scripts/reviewer_delivery_fields.py
- skills/shared/scripts/reviewer_delivery_state.py
- tests/quality_gates/test_critique_enforcement_scope.py
- tests/quality_gates/test_critique_fresh_eye_presence.py
- tests/quality_gates/test_issue_critique_observer.py
- tests/quality_gates/test_retro_persistence.py
- tests/quality_gates/test_reviewer_delivery_state_machine.py
- charness-artifacts/critique/2026-08-21-retro-portability-685-686-r2.md
- charness-artifacts/critique/r2-retro-portability-685-686-final-packet.json
- charness-artifacts/critique/r2-retro-portability-685-686-final-packet.md
- charness-artifacts/critique/r2-retro-portability-685-686-final2-packet.json
- charness-artifacts/critique/r2-retro-portability-685-686-final2-packet.md
- charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.json
- charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.md
- charness-artifacts/critique/r2-retro-portability-685-686-packet.json
- charness-artifacts/critique/r2-retro-portability-685-686-packet.md
- charness-artifacts/critique/r2-retro-portability-685-686-readiness-packet.json
- charness-artifacts/critique/r2-retro-portability-685-686-readiness-packet.md
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-consumer-20260821.md
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-counterweight-20260821.md
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-validator-20260821.md
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-operator-retry-20260821-worker-report.yaml
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-operator-retry-20260821.md
- charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-ownership-20260821.md
- charness-artifacts/debug/2026-08-21-retro-portability-boundary-685-686.md
- plugins/charness/shared/scripts/reviewer_worker_carrier.py
- skills/shared/scripts/reviewer_worker_carrier.py
- tests/quality_gates/test_retro_installed_plan_path.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/critique_reviewed_input_binding.py, scripts/critique_reviewer_evidence.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/validate_critique_artifacts.py, skills/public/critique/SKILL.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/prove/SKILL.md, skills/public/retro/scripts/plan_retro_run.py, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_state.py, skills/shared/scripts/reviewer_worker_carrier.py
  derived matches: plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/critique_reviewer_evidence.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/shared/references/fresh-eye-subagent-review.md, plugins/charness/shared/scripts/reviewer_delivery_fields.py, plugins/charness/shared/scripts/reviewer_delivery_state.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/issue/scripts/issue_critique_observer.py, plugins/charness/skills/issue/scripts/issue_resolution_critique.py, plugins/charness/skills/prove/SKILL.md, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/shared/scripts/reviewer_worker_carrier.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md, skills/public/critique/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/prove/SKILL.md, skills/shared/references/fresh-eye-subagent-review.md, charness-artifacts/critique/2026-08-21-retro-portability-685-686-r2.md, charness-artifacts/critique/r2-retro-portability-685-686-final-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-final2-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-readiness-packet.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-consumer-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-counterweight-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-validator-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-operator-retry-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-ownership-20260821.md, charness-artifacts/debug/2026-08-21-retro-portability-boundary-685-686.md
  derived matches: plugins/charness/shared/references/fresh-eye-subagent-review.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/prove/SKILL.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, python3 scripts/check_docs_graph.py --repo-root . || { [ "$?" -eq 3 ] && ! command -v awiki >/dev/null; }, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/critique/SKILL.md, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/prove/SKILL.md, skills/shared/references/fresh-eye-subagent-review.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/prove/SKILL.md, skills/public/retro/scripts/plan_retro_run.py, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_state.py, skills/shared/scripts/reviewer_worker_carrier.py
  derived matches: plugins/charness/shared/references/fresh-eye-subagent-review.md, plugins/charness/shared/scripts/reviewer_delivery_fields.py, plugins/charness/shared/scripts/reviewer_delivery_state.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/issue/SKILL.md, plugins/charness/skills/issue/references/closeout-discipline.md, plugins/charness/skills/issue/scripts/issue_critique_observer.py, plugins/charness/skills/issue/scripts/issue_resolution_critique.py, plugins/charness/skills/prove/SKILL.md, plugins/charness/skills/retro/scripts/plan_retro_run.py, plugins/charness/shared/scripts/reviewer_worker_carrier.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/prove/SKILL.md, skills/public/retro/scripts/plan_retro_run.py, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_state.py, skills/shared/scripts/reviewer_worker_carrier.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/issue/SKILL.md, skills/public/issue/references/closeout-discipline.md, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/prove/SKILL.md, skills/public/retro/scripts/plan_retro_run.py, skills/shared/references/fresh-eye-subagent-review.md, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_state.py, skills/shared/scripts/reviewer_worker_carrier.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-21-retro-portability-685-686-r2.md, charness-artifacts/critique/r2-retro-portability-685-686-final-packet.json, charness-artifacts/critique/r2-retro-portability-685-686-final-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-final2-packet.json, charness-artifacts/critique/r2-retro-portability-685-686-final2-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.json, charness-artifacts/critique/r2-retro-portability-685-686-final3-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-packet.json, charness-artifacts/critique/r2-retro-portability-685-686-packet.md, charness-artifacts/critique/r2-retro-portability-685-686-readiness-packet.json, charness-artifacts/critique/r2-retro-portability-685-686-readiness-packet.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-consumer-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-counterweight-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-final-validator-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-operator-retry-20260821-worker-report.yaml, charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-operator-retry-20260821.md, charness-artifacts/critique/rounds/2026-08-21-r2-retro-portability-ownership-20260821.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-21-retro-portability-boundary-685-686.md
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: scripts/retro_persistence_lib.py
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/critique_reviewer_evidence.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/critique_reviewed_input_binding.py, scripts/critique_reviewer_evidence.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/validate_critique_artifacts.py, tests/quality_gates/test_critique_enforcement_scope.py, tests/quality_gates/test_critique_fresh_eye_presence.py, tests/quality_gates/test_issue_critique_observer.py, tests/quality_gates/test_retro_persistence.py, tests/quality_gates/test_reviewer_delivery_state_machine.py, tests/quality_gates/test_retro_installed_plan_path.py
  derived matches: plugins/charness/scripts/critique_reviewed_input_binding.py, plugins/charness/scripts/critique_reviewer_evidence.py, plugins/charness/scripts/retro_persistence_lib.py, plugins/charness/scripts/reviewed_input_identity.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/critique_reviewed_input_binding.py, scripts/critique_reviewer_evidence.py, scripts/retro_persistence_lib.py, scripts/reviewed_input_identity.py, scripts/validate_critique_artifacts.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py, skills/public/retro/scripts/plan_retro_run.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing
- closeout-floor-matrix: Declared floor x classification x carrier matrix for issue closeout, and the behavioral probe that re-derives it from the real carriers.
  source matches: skills/public/issue/scripts/issue_critique_observer.py, skills/public/issue/scripts/issue_resolution_critique.py
  verify: python3 scripts/check_closeout_floor_matrix.py --repo-root .

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section ok**: True

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
