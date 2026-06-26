# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-06-26T21:27:38Z
- **Prepared for**: release 0.56.5 quality slice
- **Changed ref**: `HEAD`
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
Changed paths for ref `HEAD`:
- charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-4.md
- charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- plugins/charness/scripts/run-quality.sh
- plugins/charness/skills/quality/references/find_inline_prompt_bulk.py
- scripts/run-quality.sh
- skills/public/quality/references/find_inline_prompt_bulk.py
- tests/quality_gates/quality_bootstrap_support.py
- tests/quality_gates/test_quality_adapter_gate_design.py
- tests/quality_gates/test_quality_bootstrap.py
- tests/test_find_inline_prompt_bulk.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/run-quality.sh, skills/public/quality/references/find_inline_prompt_bulk.py
  derived matches: plugins/charness/scripts/run-quality.sh, plugins/charness/skills/quality/references/find_inline_prompt_bulk.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-4.md, charness-artifacts/quality/2026-06-27-round-four-quality-speed-token-review.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md, charness-artifacts/retro/recent-lessons.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json >/dev/null
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/quality/references/find_inline_prompt_bulk.py
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/references/find_inline_prompt_bulk.py
  derived matches: plugins/charness/skills/quality/references/find_inline_prompt_bulk.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/references/find_inline_prompt_bulk.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/references/find_inline_prompt_bulk.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- retro-lesson-selection-index: Generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/run-quality.sh
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/quality_bootstrap_support.py, tests/quality_gates/test_quality_adapter_gate_design.py, tests/quality_gates/test_quality_bootstrap.py, tests/test_find_inline_prompt_bulk.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only

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
