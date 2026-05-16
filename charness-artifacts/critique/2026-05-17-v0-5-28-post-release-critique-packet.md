# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-05-16T23:42:00Z
- **Prepared for**: v0.5.28 post-release critique
- **Changed ref**: `8a6281f^..8a6281f`
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
- .claude-plugin/marketplace.json
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/latest.md
- packaging/charness.json
- plugins/charness/.claude-plugin/plugin.json
- plugins/charness/.codex-plugin/plugin.json
- plugins/charness/scripts/check_mutation_score.py
- scripts/check_mutation_score.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: packaging/charness.json, scripts/check_mutation_score.py
  derived matches: .claude-plugin/marketplace.json, plugins/charness/.claude-plugin/plugin.json, plugins/charness/.codex-plugin/plugin.json, plugins/charness/scripts/check_mutation_score.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/release/latest.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  verify: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- mutation-testing-workflow: Repo-owned scheduled mutation testing workflow, runner config, and adapter slot behavior.
  source matches: scripts/check_mutation_score.py
  derived matches: plugins/charness/scripts/check_mutation_score.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py, python3 scripts/validate_adapters.py --repo-root ., python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check_mutation_score.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json

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
