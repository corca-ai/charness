# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-09-02T03:48:10Z
- **Prepared for**: issue-771 rework instrument (Goal Run #765)
- **Substrate mode**: `working-tree`
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 2
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for working tree:
- .agents/retro-adapter.yaml
- scripts/render_retro_section_rework_issues.py
- skills/public/issue/SKILL.md
- skills/public/issue/references/issue-shaping.md
- skills/public/retro/SKILL.md
- skills/public/retro/references/prepare-packet.md
- tests/test_retro_section_rework_issues.py

Owning surfaces:
- materialized-plugin-export: Materialized plugin export and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/render_retro_section_rework_issues.py, skills/public/issue/SKILL.md, skills/public/issue/references/issue-shaping.md, skills/public/retro/SKILL.md, skills/public/retro/references/prepare-packet.md
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: skills/public/issue/SKILL.md, skills/public/issue/references/issue-shaping.md, skills/public/retro/SKILL.md, skills/public/retro/references/prepare-packet.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/issue/SKILL.md, skills/public/issue/references/issue-shaping.md, skills/public/retro/SKILL.md, skills/public/retro/references/prepare-packet.md
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/issue/SKILL.md, skills/public/issue/references/issue-shaping.md, skills/public/retro/SKILL.md, skills/public/retro/references/prepare-packet.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/issue/SKILL.md, skills/public/issue/references/issue-shaping.md, skills/public/retro/SKILL.md, skills/public/retro/references/prepare-packet.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/retro-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/render_retro_section_rework_issues.py, tests/test_retro_section_rework_issues.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_code_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/render_retro_section_rework_issues.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

## Rework Issues By Causing Skill

- **Section id**: `rework-issues-by-causing-skill`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_retro_section_rework_issues.py --repo corca-ai/charness`
- **Section shape validation ok**: True

```text
Rework issues labelled `rework` created since 2026-08-03 (1 issue(s)):

| Causing skill | Issues |
| --- | --- |
| achieve | 1 |
| issue | 1 |

Counts are per attribution; one issue naming multiple skills is counted once under each skill.

- #773 Goal Run binding hashes content, not identity: one-line child edits and new Work Items force a full re-bootstrap (OPEN, 2026-09-02; achieve, issue) https://github.com/corca-ai/charness/issues/773
```
