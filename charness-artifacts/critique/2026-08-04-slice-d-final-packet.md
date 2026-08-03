# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-03T23:27:03Z
- **Prepared for**: Slice D final implementation and repair-read
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `cd41715084c073b734c91acd1f342e29f482d4decf7490012f52cf75ec7aa63d`
- **Reviewed paths**: 23
- **Sections**: 3
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/critique/2026-08-03-225320-packet.json
- charness-artifacts/critique/2026-08-03-225320-packet.md
- charness-artifacts/critique/2026-08-04-critique-review.md
- charness-artifacts/critique/2026-08-04-slice-d-final-packet.json
- charness-artifacts/critique/2026-08-04-slice-d-final-packet.md
- charness-artifacts/debug/2026-08-04-debug-review-followup.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/quality/2026-08-04-quality-review.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/sloc-inventory/latest.json
- plugins/charness/scripts/check_export_safe_imports.py
- plugins/charness/scripts/validate_adapters.py
- plugins/charness/skills/achieve/scripts/goal_artifact_lib.py
- plugins/charness/skills/achieve/scripts/upsert_goal.py
- plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py
- plugins/charness/skills/handoff/scripts/chunked_routing_lib.py
- plugins/charness/skills/handoff/scripts/draft_goal_from_chunk.py
- scripts/check_export_safe_imports.py
- scripts/validate_adapters.py
- skills/public/achieve/scripts/goal_artifact_lib.py
- skills/public/achieve/scripts/upsert_goal.py
- skills/public/handoff/scripts/chunked_routing_auto_draft.py
- skills/public/handoff/scripts/chunked_routing_lib.py
- skills/public/handoff/scripts/draft_goal_from_chunk.py
- tests/quality_gates/test_export_safe_asset_paths.py
- tests/quality_gates/test_profile_and_preset_validation.py
- tests/test_handoff_chunker_auto_draft.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check_export_safe_imports.py, scripts/validate_adapters.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/upsert_goal.py, skills/public/handoff/scripts/chunked_routing_auto_draft.py, skills/public/handoff/scripts/chunked_routing_lib.py, skills/public/handoff/scripts/draft_goal_from_chunk.py
  derived matches: plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/validate_adapters.py, plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/upsert_goal.py, plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py, plugins/charness/skills/handoff/scripts/chunked_routing_lib.py, plugins/charness/skills/handoff/scripts/draft_goal_from_chunk.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-03-225320-packet.md, charness-artifacts/critique/2026-08-04-critique-review.md, charness-artifacts/critique/2026-08-04-slice-d-final-packet.md, charness-artifacts/debug/2026-08-04-debug-review-followup.md, charness-artifacts/debug/latest.md, charness-artifacts/quality/2026-08-04-quality-review.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/upsert_goal.py, skills/public/handoff/scripts/chunked_routing_auto_draft.py, skills/public/handoff/scripts/chunked_routing_lib.py, skills/public/handoff/scripts/draft_goal_from_chunk.py
  derived matches: plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/upsert_goal.py, plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py, plugins/charness/skills/handoff/scripts/chunked_routing_lib.py, plugins/charness/skills/handoff/scripts/draft_goal_from_chunk.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/upsert_goal.py, skills/public/handoff/scripts/chunked_routing_auto_draft.py, skills/public/handoff/scripts/chunked_routing_lib.py, skills/public/handoff/scripts/draft_goal_from_chunk.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/upsert_goal.py, skills/public/handoff/scripts/chunked_routing_auto_draft.py, skills/public/handoff/scripts/chunked_routing_lib.py, skills/public/handoff/scripts/draft_goal_from_chunk.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-03-225320-packet.json, charness-artifacts/critique/2026-08-03-225320-packet.md, charness-artifacts/critique/2026-08-04-critique-review.md, charness-artifacts/critique/2026-08-04-slice-d-final-packet.json, charness-artifacts/critique/2026-08-04-slice-d-final-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-04-debug-review-followup.md, charness-artifacts/debug/latest.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/validate_adapters.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/check_export_safe_imports.py, scripts/validate_adapters.py, tests/quality_gates/test_export_safe_asset_paths.py, tests/quality_gates/test_profile_and_preset_validation.py, tests/test_handoff_chunker_auto_draft.py
  derived matches: plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/validate_adapters.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_export_safe_imports.py, scripts/validate_adapters.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/upsert_goal.py, skills/public/handoff/scripts/chunked_routing_auto_draft.py, skills/public/handoff/scripts/chunked_routing_lib.py, skills/public/handoff/scripts/draft_goal_from_chunk.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
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
