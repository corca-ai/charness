# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-05-16T23:12:59Z
- **Prepared for**: 71119a6 trigger correction third critique
- **Changed ref**: `71119a6^..71119a6`
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
- charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.json
- charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.md
- charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique.md
- plugins/charness/skills/quality/references/agent-production-runtime.md
- plugins/charness/skills/quality/references/inventory-dispatch.md
- skills/public/quality/references/agent-production-runtime.md
- skills/public/quality/references/inventory-dispatch.md
- tests/quality_gates/test_quality_skill_docs.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  derived matches: plugins/charness/skills/quality/references/agent-production-runtime.md, plugins/charness/skills/quality/references/inventory-dispatch.md
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.md, charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique.md, skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  derived matches: plugins/charness/skills/quality/references/agent-production-runtime.md, plugins/charness/skills/quality/references/inventory-dispatch.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  derived matches: plugins/charness/skills/quality/references/agent-production-runtime.md, plugins/charness/skills/quality/references/inventory-dispatch.md
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/references/agent-production-runtime.md, skills/public/quality/references/inventory-dispatch.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.json, charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.md, charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_quality_skill_docs.py
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
