# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-06-01T22:19:00Z
- **Prepared for**: workflow-review critique cadence slice
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
Changed paths for working tree:
- docs/conventions/operating-contract.md
- docs/public-skill-dogfood.json
- plugins/charness/skills/achieve/references/goal-artifact.md
- plugins/charness/skills/achieve/references/lifecycle.md
- plugins/charness/skills/achieve/scripts/goal_artifact_template.md
- plugins/charness/skills/critique/SKILL.md
- skills/public/achieve/references/goal-artifact.md
- skills/public/achieve/references/lifecycle.md
- skills/public/achieve/scripts/goal_artifact_template.md
- skills/public/critique/SKILL.md
- tests/quality_gates/test_critique_skill.py
- tests/quality_gates/test_goal_artifact_lib.py
- plugins/charness/skills/critique/references/cadence.md
- skills/public/critique/references/cadence.md

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/goal_artifact_template.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  derived matches: plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/achieve/scripts/goal_artifact_template.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: docs/conventions/operating-contract.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/goal_artifact_template.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  derived matches: plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/achieve/scripts/goal_artifact_template.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/goal_artifact_template.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  derived matches: plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle.md, plugins/charness/skills/achieve/scripts/goal_artifact_template.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/cadence.md
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/goal_artifact_template.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle.md, skills/public/achieve/scripts/goal_artifact_template.md, skills/public/critique/SKILL.md, skills/public/critique/references/cadence.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_critique_skill.py, tests/quality_gates/test_goal_artifact_lib.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py

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
