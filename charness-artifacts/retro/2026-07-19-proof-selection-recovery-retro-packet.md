# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-07-19T02:16:47Z
- **Prepared for**: proof selection and release recovery slice
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 1
- **Overall ok**: True


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/quality/2026-07-19-quality-review.md
- charness-artifacts/quality/sloc-inventory/latest.json
- plugins/charness/scripts/check_changed_line_mutation_coverage.py
- plugins/charness/scripts/mutation_changed_files_lib.py
- plugins/charness/scripts/suggest_mutation_coverage_command.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_runtime.py
- scripts/check_changed_line_mutation_coverage.py
- scripts/mutation_changed_files_lib.py
- scripts/suggest_mutation_coverage_command.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_runtime.py
- tests/quality_gates/test_release_publish_resilience.py
- tests/quality_gates/test_release_publish_rollback.py
- tests/quality_gates/test_suggest_mutation_coverage_command.py
- charness-artifacts/critique/2026-07-19-020430-packet.json
- charness-artifacts/critique/2026-07-19-020430-packet.md
- charness-artifacts/critique/2026-07-19-proof-selection-recovery-critique.md
- charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.json
- charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.md
- charness-artifacts/quality/history/2026-07-19-portable-proof-path-learning-review.md

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check_changed_line_mutation_coverage.py, scripts/mutation_changed_files_lib.py, scripts/suggest_mutation_coverage_command.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_runtime.py
  derived matches: plugins/charness/scripts/check_changed_line_mutation_coverage.py, plugins/charness/scripts/mutation_changed_files_lib.py, plugins/charness/scripts/suggest_mutation_coverage_command.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_runtime.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/quality/2026-07-19-quality-review.md, charness-artifacts/critique/2026-07-19-020430-packet.md, charness-artifacts/critique/2026-07-19-proof-selection-recovery-critique.md, charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.md, charness-artifacts/quality/history/2026-07-19-portable-proof-path-learning-review.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_runtime.py
  derived matches: plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_runtime.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_runtime.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_runtime.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-19-020430-packet.json, charness-artifacts/critique/2026-07-19-020430-packet.md, charness-artifacts/critique/2026-07-19-proof-selection-recovery-critique.md, charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.json, charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_changed_line_mutation_coverage.py, plugins/charness/scripts/mutation_changed_files_lib.py, plugins/charness/scripts/suggest_mutation_coverage_command.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/check_changed_line_mutation_coverage.py, scripts/mutation_changed_files_lib.py, scripts/suggest_mutation_coverage_command.py, tests/quality_gates/test_release_publish_resilience.py, tests/quality_gates/test_release_publish_rollback.py, tests/quality_gates/test_suggest_mutation_coverage_command.py
  derived matches: plugins/charness/scripts/check_changed_line_mutation_coverage.py, plugins/charness/scripts/mutation_changed_files_lib.py, plugins/charness/scripts/suggest_mutation_coverage_command.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_changed_line_mutation_coverage.py, scripts/mutation_changed_files_lib.py, scripts/suggest_mutation_coverage_command.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_runtime.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
```
