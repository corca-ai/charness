# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-05-17T08:48:46Z
- **Prepared for**: issue-171-usage-episodes-branch-critique
- **Changed ref**: `origin/main..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths:
- .gitignore
- charness-artifacts/critique/2026-05-17-080239-packet.json
- charness-artifacts/critique/2026-05-17-080239-packet.md
- charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-impl.md
- charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-post-commit.md
- charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec-blocked.md
- charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec.md
- charness-artifacts/find-skills/latest.json
- charness-artifacts/find-skills/latest.md
- charness-artifacts/spec/issue-171-hlam-usage-episodes.md
- docs/public-skill-dogfood.json
- integrations/usage-episodes/adapter.example.yaml
- integrations/usage-episodes/episode.schema.json
- integrations/usage-episodes/manifest.schema.json
- plugins/charness/integrations/usage-episodes/adapter.example.yaml
- plugins/charness/integrations/usage-episodes/episode.schema.json
- plugins/charness/integrations/usage-episodes/manifest.schema.json
- plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt
- plugins/charness/scripts/packaging_lib.py
- plugins/charness/scripts/validate_usage_episodes.py
- plugins/charness/skills/setup/SKILL.md
- plugins/charness/skills/setup/scripts/seed_usage_episodes_adapter.py
- scripts/check_skill_ownership_overlap.allowlist.txt
- scripts/packaging_lib.py
- scripts/validate_usage_episodes.py
- skills/public/setup/SKILL.md
- skills/public/setup/scripts/seed_usage_episodes_adapter.py
- tests/quality_gates/test_setup_seed_usage_episodes.py
- tests/test_usage_episodes_schema.py
- tests/test_usage_episodes_validator.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: integrations/usage-episodes/adapter.example.yaml, integrations/usage-episodes/episode.schema.json, integrations/usage-episodes/manifest.schema.json, scripts/check_skill_ownership_overlap.allowlist.txt, scripts/packaging_lib.py, scripts/validate_usage_episodes.py, skills/public/setup/SKILL.md, skills/public/setup/scripts/seed_usage_episodes_adapter.py
  derived matches: plugins/charness/integrations/usage-episodes/adapter.example.yaml, plugins/charness/integrations/usage-episodes/episode.schema.json, plugins/charness/integrations/usage-episodes/manifest.schema.json, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/packaging_lib.py, plugins/charness/scripts/validate_usage_episodes.py, plugins/charness/skills/setup/SKILL.md, plugins/charness/skills/setup/scripts/seed_usage_episodes_adapter.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-05-17-080239-packet.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-impl.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-post-commit.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec-blocked.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec.md, charness-artifacts/find-skills/latest.md, charness-artifacts/spec/issue-171-hlam-usage-episodes.md, skills/public/setup/SKILL.md
  derived matches: plugins/charness/skills/setup/SKILL.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/setup/SKILL.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/setup/SKILL.md, skills/public/setup/scripts/seed_usage_episodes_adapter.py
  derived matches: charness-artifacts/find-skills/latest.json, charness-artifacts/find-skills/latest.md, plugins/charness/skills/setup/SKILL.md, plugins/charness/skills/setup/scripts/seed_usage_episodes_adapter.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/setup/SKILL.md, skills/public/setup/scripts/seed_usage_episodes_adapter.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/setup/SKILL.md, skills/public/setup/scripts/seed_usage_episodes_adapter.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-05-17-080239-packet.json, charness-artifacts/critique/2026-05-17-080239-packet.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-impl.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-post-commit.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec-blocked.md, charness-artifacts/critique/2026-05-17-issue-171-hlam-usage-episodes-spec.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/usage-episodes/adapter.example.yaml, integrations/usage-episodes/episode.schema.json, integrations/usage-episodes/manifest.schema.json
  derived matches: plugins/charness/integrations/usage-episodes/adapter.example.yaml, plugins/charness/integrations/usage-episodes/episode.schema.json, plugins/charness/integrations/usage-episodes/manifest.schema.json, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/packaging_lib.py, plugins/charness/scripts/validate_usage_episodes.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: .gitignore, tests/quality_gates/test_setup_seed_usage_episodes.py, tests/test_usage_episodes_schema.py, tests/test_usage_episodes_validator.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- The retro skill does not consume this packet today. A retro-side prepare slot (retro-adapter.yaml packet_sections) is a separate follow-up.
```
