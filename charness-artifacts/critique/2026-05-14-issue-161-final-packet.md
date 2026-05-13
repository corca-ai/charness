# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-05-13T22:41:57Z
- **Prepared for**: issue-161 final state
- **Adapter**: `/home/hwidong/codes/charness/.agents/critique-adapter.yaml`
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
- plugins/charness/scripts/critique_adapter_lib.py
- plugins/charness/scripts/validate_critique_packet.py
- scripts/critique_adapter_lib.py
- scripts/validate_critique_packet.py
- .agents/critique-adapter.yaml
- charness-artifacts/critique/2026-05-14-issue-161-final-packet.json
- charness-artifacts/critique/2026-05-14-issue-161-final-packet.md
- charness-artifacts/issue/2026-05-13-issue-161-brief.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt
- plugins/charness/scripts/critique_packet_lib.py
- plugins/charness/scripts/render_critique_section_changed_surfaces.py
- plugins/charness/scripts/validate_adapters.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/adapter.example.yaml
- plugins/charness/skills/critique/references/adapter-contract.md
- plugins/charness/skills/critique/references/prepare-packet.md
- plugins/charness/skills/critique/scripts/init_adapter.py
- plugins/charness/skills/critique/scripts/prepare_packet.py
- plugins/charness/skills/critique/scripts/resolve_adapter.py
- scripts/check_skill_ownership_overlap.allowlist.txt
- scripts/critique_packet_lib.py
- scripts/render_critique_section_changed_surfaces.py
- scripts/validate_adapters.py
- skills/public/critique/SKILL.md
- skills/public/critique/adapter.example.yaml
- skills/public/critique/references/adapter-contract.md
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/init_adapter.py
- skills/public/critique/scripts/prepare_packet.py
- skills/public/critique/scripts/resolve_adapter.py
- tests/test_critique_prepare_packet.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/critique_adapter_lib.py, scripts/validate_critique_packet.py, scripts/check_skill_ownership_overlap.allowlist.txt, scripts/critique_packet_lib.py, scripts/render_critique_section_changed_surfaces.py, scripts/validate_adapters.py, skills/public/critique/SKILL.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/init_adapter.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/resolve_adapter.py
  derived matches: plugins/charness/scripts/critique_adapter_lib.py, plugins/charness/scripts/validate_critique_packet.py, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/render_critique_section_changed_surfaces.py, plugins/charness/scripts/validate_adapters.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/adapter.example.yaml, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/init_adapter.py, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/resolve_adapter.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-05-14-issue-161-final-packet.md, charness-artifacts/issue/2026-05-13-issue-161-brief.md, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/critique-adapter.yaml, skills/public/critique/SKILL.md, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/init_adapter.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/resolve_adapter.py
  derived matches: plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/adapter.example.yaml, plugins/charness/skills/critique/references/adapter-contract.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/init_adapter.py, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/resolve_adapter.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/SKILL.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/init_adapter.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/resolve_adapter.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/critique/SKILL.md, skills/public/critique/adapter.example.yaml, skills/public/critique/references/adapter-contract.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/init_adapter.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/resolve_adapter.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/critique-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/critique_adapter_lib.py, plugins/charness/scripts/validate_critique_packet.py, plugins/charness/scripts/check_skill_ownership_overlap.allowlist.txt, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/render_critique_section_changed_surfaces.py, plugins/charness/scripts/validate_adapters.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/test_critique_prepare_packet.py
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
