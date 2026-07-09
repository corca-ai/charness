# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-09T14:44:12Z
- **Prepared for**: v0.63.1 patch release
- **Changed ref**: `origin/main..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
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
Changed paths for ref `origin/main..HEAD`:
- .gitignore
- charness-artifacts/critique/2026-07-09-124539-packet.json
- charness-artifacts/critique/2026-07-09-124539-packet.md
- charness-artifacts/critique/2026-07-09-131243-packet.json
- charness-artifacts/critique/2026-07-09-131243-packet.md
- charness-artifacts/critique/2026-07-09-142102-packet.json
- charness-artifacts/critique/2026-07-09-142102-packet.md
- charness-artifacts/critique/2026-07-09-143422-packet.json
- charness-artifacts/critique/2026-07-09-143422-packet.md
- charness-artifacts/critique/2026-07-09-ab-schema-validation-followup-critique.md
- charness-artifacts/critique/2026-07-09-autonomous-quality-repair-critique.md
- charness-artifacts/critique/2026-07-09-critique-review.md
- charness-artifacts/critique/2026-07-09-debug-planner-help-critique.md
- charness-artifacts/critique/2026-07-09-markdown-preview-help-critique.md
- charness-artifacts/critique/2026-07-09-standing-test-economics-bucket-critique.md
- charness-artifacts/goals/2026-07-09-autonomous-repo-improvement-issues.md
- charness-artifacts/quality/2026-07-09-ab-schema-test-economics-followup.md
- charness-artifacts/quality/2026-07-09-autonomous-quality-repair.md
- charness-artifacts/quality/2026-07-09-debug-planner-help-quality.md
- charness-artifacts/quality/2026-07-09-markdown-preview-help-quality.md
- charness-artifacts/quality/2026-07-09-standing-test-economics-bucket-repair.md
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-07-09-125409-packet.md
- charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- docs/prompt-mutation-policy.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/run_skill_efficiency_ab.py
- plugins/charness/scripts/run_skill_efficiency_ab_validation.py
- plugins/charness/scripts/score_prompt_mutation_survival_lib.py
- plugins/charness/skills/debug/scripts/plan_debug_run.py
- plugins/charness/skills/quality/references/inventory-consumer-fields.json
- plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py
- plugins/charness/skills/quality/scripts/standing_test_economics_lib.py
- plugins/charness/skills/quality/scripts/surface_marker_lib.py
- plugins/charness/support/markdown-preview/scripts/markdown_preview_lib.py
- plugins/charness/support/markdown-preview/scripts/render_markdown_preview.py
- scripts/run_skill_efficiency_ab.py
- scripts/run_skill_efficiency_ab_validation.py
- scripts/score_prompt_mutation_survival_lib.py
- skills/public/debug/scripts/plan_debug_run.py
- skills/public/quality/references/inventory-consumer-fields.json
- skills/public/quality/scripts/inventory_standing_test_economics.py
- skills/public/quality/scripts/standing_test_economics_lib.py
- skills/public/quality/scripts/surface_marker_lib.py
- skills/support/markdown-preview/scripts/markdown_preview_lib.py
- skills/support/markdown-preview/scripts/render_markdown_preview.py
- tests/quality_gates/test_standing_test_economics.py
- tests/test_debug_plan.py
- tests/test_markdown_preview_support.py
- tests/test_score_prompt_mutation_survival.py
- tests/test_skill_efficiency_ab.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/score_prompt_mutation_survival_lib.py, skills/public/debug/scripts/plan_debug_run.py, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/support/markdown-preview/scripts/markdown_preview_lib.py, skills/support/markdown-preview/scripts/render_markdown_preview.py
  derived matches: plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/score_prompt_mutation_survival_lib.py, plugins/charness/skills/debug/scripts/plan_debug_run.py, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py, plugins/charness/skills/quality/scripts/standing_test_economics_lib.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/support/markdown-preview/scripts/markdown_preview_lib.py, plugins/charness/support/markdown-preview/scripts/render_markdown_preview.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-09-124539-packet.md, charness-artifacts/critique/2026-07-09-131243-packet.md, charness-artifacts/critique/2026-07-09-142102-packet.md, charness-artifacts/critique/2026-07-09-143422-packet.md, charness-artifacts/critique/2026-07-09-ab-schema-validation-followup-critique.md, charness-artifacts/critique/2026-07-09-autonomous-quality-repair-critique.md, charness-artifacts/critique/2026-07-09-critique-review.md, charness-artifacts/critique/2026-07-09-debug-planner-help-critique.md, charness-artifacts/critique/2026-07-09-markdown-preview-help-critique.md, charness-artifacts/critique/2026-07-09-standing-test-economics-bucket-critique.md, charness-artifacts/goals/2026-07-09-autonomous-repo-improvement-issues.md, charness-artifacts/quality/2026-07-09-ab-schema-test-economics-followup.md, charness-artifacts/quality/2026-07-09-autonomous-quality-repair.md, charness-artifacts/quality/2026-07-09-debug-planner-help-quality.md, charness-artifacts/quality/2026-07-09-markdown-preview-help-quality.md, charness-artifacts/quality/2026-07-09-standing-test-economics-bucket-repair.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-07-09-125409-packet.md, charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, docs/prompt-mutation-policy.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/quality/references/inventory-consumer-fields.json
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/debug/scripts/plan_debug_run.py, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/support/markdown-preview/scripts/markdown_preview_lib.py, skills/support/markdown-preview/scripts/render_markdown_preview.py
  derived matches: plugins/charness/skills/debug/scripts/plan_debug_run.py, plugins/charness/skills/quality/references/inventory-consumer-fields.json, plugins/charness/skills/quality/scripts/inventory_standing_test_economics.py, plugins/charness/skills/quality/scripts/standing_test_economics_lib.py, plugins/charness/skills/quality/scripts/surface_marker_lib.py, plugins/charness/support/markdown-preview/scripts/markdown_preview_lib.py, plugins/charness/support/markdown-preview/scripts/render_markdown_preview.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/debug/scripts/plan_debug_run.py, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/surface_marker_lib.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/debug/scripts/plan_debug_run.py, skills/public/quality/references/inventory-consumer-fields.json, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/surface_marker_lib.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-09-124539-packet.json, charness-artifacts/critique/2026-07-09-124539-packet.md, charness-artifacts/critique/2026-07-09-131243-packet.json, charness-artifacts/critique/2026-07-09-131243-packet.md, charness-artifacts/critique/2026-07-09-142102-packet.json, charness-artifacts/critique/2026-07-09-142102-packet.md, charness-artifacts/critique/2026-07-09-143422-packet.json, charness-artifacts/critique/2026-07-09-143422-packet.md, charness-artifacts/critique/2026-07-09-ab-schema-validation-followup-critique.md, charness-artifacts/critique/2026-07-09-autonomous-quality-repair-critique.md, charness-artifacts/critique/2026-07-09-critique-review.md, charness-artifacts/critique/2026-07-09-debug-planner-help-critique.md, charness-artifacts/critique/2026-07-09-markdown-preview-help-critique.md, charness-artifacts/critique/2026-07-09-standing-test-economics-bucket-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-09-125409-packet.md, charness-artifacts/retro/2026-07-09-autonomous-repo-improvement-issues-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/score_prompt_mutation_survival_lib.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: .gitignore, scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/score_prompt_mutation_survival_lib.py, tests/quality_gates/test_standing_test_economics.py, tests/test_debug_plan.py, tests/test_markdown_preview_support.py, tests/test_score_prompt_mutation_survival.py, tests/test_skill_efficiency_ab.py
  derived matches: plugins/charness/scripts/run_skill_efficiency_ab.py, plugins/charness/scripts/run_skill_efficiency_ab_validation.py, plugins/charness/scripts/score_prompt_mutation_survival_lib.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: skills/public/quality/scripts/inventory_standing_test_economics.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/run_skill_efficiency_ab.py, scripts/run_skill_efficiency_ab_validation.py, scripts/score_prompt_mutation_survival_lib.py, skills/public/debug/scripts/plan_debug_run.py, skills/public/quality/scripts/inventory_standing_test_economics.py, skills/public/quality/scripts/standing_test_economics_lib.py, skills/public/quality/scripts/surface_marker_lib.py, skills/support/markdown-preview/scripts/markdown_preview_lib.py, skills/support/markdown-preview/scripts/render_markdown_preview.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
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

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: release helper and checked-in plugin/package release surfaces.
- Consumer: operators installing or updating Charness through the published release.
- Owning surface: release skill plus `.agents/release-adapter.yaml`.
- Verdict: owned-correctly
