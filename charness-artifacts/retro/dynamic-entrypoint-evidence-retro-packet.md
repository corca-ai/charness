# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-07-18T14:49:07Z
- **Prepared for**: working tree
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
- charness-artifacts/quality/latest.md
- plugins/charness/skills/quality/scripts/run_dead_code_advisory.py
- skills/public/quality/scripts/run_dead_code_advisory.py
- tests/quality_gates/test_quality_dead_code_advisory.py
- charness-artifacts/critique/2026-07-18-dynamic-entrypoint-evidence.md
- charness-artifacts/critique/dynamic-entrypoint-evidence-packet.json
- charness-artifacts/critique/dynamic-entrypoint-evidence-packet.md
- charness-artifacts/quality/2026-07-18-dynamic-entrypoint-structural-quality.md
- plugins/charness/skills/quality/scripts/dynamic_entrypoint_evidence.py
- plugins/charness/skills/quality/scripts/source_role_evidence.py
- skills/public/quality/scripts/dynamic_entrypoint_evidence.py
- skills/public/quality/scripts/source_role_evidence.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/dynamic_entrypoint_evidence.py, skills/public/quality/scripts/source_role_evidence.py
  derived matches: plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/dynamic_entrypoint_evidence.py, plugins/charness/skills/quality/scripts/source_role_evidence.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/quality/latest.md, charness-artifacts/critique/2026-07-18-dynamic-entrypoint-evidence.md, charness-artifacts/critique/dynamic-entrypoint-evidence-packet.md, charness-artifacts/quality/2026-07-18-dynamic-entrypoint-structural-quality.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/dynamic_entrypoint_evidence.py, skills/public/quality/scripts/source_role_evidence.py
  derived matches: plugins/charness/skills/quality/scripts/run_dead_code_advisory.py, plugins/charness/skills/quality/scripts/dynamic_entrypoint_evidence.py, plugins/charness/skills/quality/scripts/source_role_evidence.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/dynamic_entrypoint_evidence.py, skills/public/quality/scripts/source_role_evidence.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/dynamic_entrypoint_evidence.py, skills/public/quality/scripts/source_role_evidence.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-18-dynamic-entrypoint-evidence.md, charness-artifacts/critique/dynamic-entrypoint-evidence-packet.json, charness-artifacts/critique/dynamic-entrypoint-evidence-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_quality_dead_code_advisory.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/quality/scripts/run_dead_code_advisory.py, skills/public/quality/scripts/dynamic_entrypoint_evidence.py, skills/public/quality/scripts/source_role_evidence.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```
