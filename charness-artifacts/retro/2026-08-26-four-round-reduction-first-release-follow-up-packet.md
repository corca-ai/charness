# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-08-25T23:17:46Z
- **Prepared for**: four-round reduction-first release follow-up
- **Substrate mode**: `committed-ref`
- **Changed ref**: `7eaa46939^..62abfd5f7`
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 1
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
Changed paths for ref `7eaa46939^..62abfd5f7`:
- charness-artifacts/critique/2026-08-26-4-round-reduction-first-verification-follow-up-for-the-6-4-1-to-6-5-0-release.md
- charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.json
- charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.md
- charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.json
- charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.md
- charness-artifacts/critique/reduction-first-verification-final-packet.json
- charness-artifacts/critique/reduction-first-verification-final-packet.md
- charness-artifacts/critique/reduction-first-verification-r3-packet.json
- charness-artifacts/critique/reduction-first-verification-r3-packet.md
- charness-artifacts/critique/reduction-first-verification-r4-packet.json
- charness-artifacts/critique/reduction-first-verification-r4-packet.md
- plugins/charness/scripts/critique_verification_scope.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/references/cadence.md
- plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py
- plugins/charness/skills/critique/scripts/verification_retry.py
- plugins/charness/skills/quality/SKILL.md
- plugins/charness/skills/release/SKILL.md
- plugins/charness/skills/release/scripts/publish_release_artifact_sections.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_common.py
- plugins/charness/skills/release/scripts/publish_release_post_create.py
- plugins/charness/skills/release/scripts/publish_release_verification_sections.py
- plugins/charness/skills/release/scripts/publish_release_verification_state.py
- scripts/critique_verification_scope.py
- scripts/validate_critique_artifacts.py
- skills/public/critique/SKILL.md
- skills/public/critique/references/cadence.md
- skills/public/critique/scripts/scaffold_critique_artifact.py
- skills/public/critique/scripts/verification_retry.py
- skills/public/quality/SKILL.md
- skills/public/release/SKILL.md
- skills/public/release/scripts/publish_release_artifact_sections.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_common.py
- skills/public/release/scripts/publish_release_post_create.py
- skills/public/release/scripts/publish_release_verification_sections.py
- skills/public/release/scripts/publish_release_verification_state.py
- tests/quality_gates/test_release_distinct_channel.py
- tests/quality_gates/test_release_observer.py
- tests/quality_gates/test_release_publish.py
- tests/quality_gates/test_release_publish_resilience.py
- tests/test_critique_scaffold.py
- tests/test_verification_retry.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_sections.py, skills/public/release/scripts/publish_release_verification_state.py
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/critique/scripts/verification_retry.py, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/publish_release_verification_sections.py, plugins/charness/skills/release/scripts/publish_release_verification_state.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-26-4-round-reduction-first-verification-follow-up-for-the-6-4-1-to-6-5-0-release.md, charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.md, charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.md, charness-artifacts/critique/reduction-first-verification-final-packet.md, charness-artifacts/critique/reduction-first-verification-r3-packet.md, charness-artifacts/critique/reduction-first-verification-r4-packet.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/quality/SKILL.md, skills/public/release/SKILL.md
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md
  verify: ./scripts/check-docs.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/quality/SKILL.md, skills/public/release/SKILL.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_sections.py, skills/public/release/scripts/publish_release_verification_state.py
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md, plugins/charness/skills/critique/scripts/scaffold_critique_artifact.py, plugins/charness/skills/critique/scripts/verification_retry.py, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/SKILL.md, plugins/charness/skills/release/scripts/publish_release_artifact_sections.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_common.py, plugins/charness/skills/release/scripts/publish_release_post_create.py, plugins/charness/skills/release/scripts/publish_release_verification_sections.py, plugins/charness/skills/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_sections.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/quality/SKILL.md, skills/public/release/SKILL.md, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_sections.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-26-4-round-reduction-first-verification-follow-up-for-the-6-4-1-to-6-5-0-release.md, charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.json, charness-artifacts/critique/2026-08-26-reduction-first-verification-packet.md, charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.json, charness-artifacts/critique/2026-08-26-reduction-first-verification-r2-packet.md, charness-artifacts/critique/reduction-first-verification-final-packet.json, charness-artifacts/critique/reduction-first-verification-final-packet.md, charness-artifacts/critique/reduction-first-verification-r3-packet.json, charness-artifacts/critique/reduction-first-verification-r3-packet.md, charness-artifacts/critique/reduction-first-verification-r4-packet.json, charness-artifacts/critique/reduction-first-verification-r4-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, tests/quality_gates/test_release_distinct_channel.py, tests/quality_gates/test_release_observer.py, tests/quality_gates/test_release_publish.py, tests/quality_gates/test_release_publish_resilience.py, tests/test_critique_scaffold.py, tests/test_verification_retry.py
  derived matches: plugins/charness/scripts/critique_verification_scope.py, plugins/charness/scripts/validate_critique_artifacts.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/critique_verification_scope.py, scripts/validate_critique_artifacts.py, skills/public/critique/scripts/scaffold_critique_artifact.py, skills/public/critique/scripts/verification_retry.py, skills/public/release/scripts/publish_release_artifact_sections.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_common.py, skills/public/release/scripts/publish_release_post_create.py, skills/public/release/scripts/publish_release_verification_sections.py, skills/public/release/scripts/publish_release_verification_state.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```
