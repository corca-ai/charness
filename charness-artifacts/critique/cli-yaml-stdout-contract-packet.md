# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-15T03:40:55Z
- **Prepared for**: CLI YAML stdout contract
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
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
Changed paths for working tree:
- .agents/command-docs.yaml
- .agents/release-adapter.yaml
- .charness/specdown/report.json
- .charness/specdown/report/index.html
- .charness/specdown/report/on-demand-validation.html
- .charness/specdown/report/readme-proof.html
- .charness/specdown/report/tool-doctor.html
- AGENTS.md
- charness
- docs/agent-task-envelope.md
- docs/capability-resolution.md
- docs/deferred-decisions.md
- docs/generated/cli-reference.md
- docs/operator-progressive-path.md
- docs/public-skill-dogfood.json
- docs/worktree-prepare.md
- integrations/tools/nose.json
- plugins/charness/integrations/tools/nose.json
- plugins/charness/scripts/check_coverage.py
- plugins/charness/scripts/doctor_lib.py
- plugins/charness/scripts/eval_setup.py
- plugins/charness/scripts/render_cli_reference.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/scripts/session_start_routing.py
- plugins/charness/scripts/support_sync_lib.py
- plugins/charness/skills/critique/references/code-critique.md
- plugins/charness/skills/hitl/SKILL.md
- plugins/charness/skills/impl/SKILL.md
- plugins/charness/skills/impl/references/verification-ladder.md
- plugins/charness/skills/quality/references/skill-ergonomics.md
- plugins/charness/skills/setup/references/default-surfaces.md
- plugins/charness/skills/setup/scripts/render_skill_routing.py
- plugins/charness/skills/spec/SKILL.md
- scripts/check_coverage.py
- scripts/doctor_lib.py
- scripts/eval_setup.py
- scripts/render_cli_reference.py
- scripts/run-quality.sh
- scripts/session_start_routing.py
- scripts/support_sync_lib.py
- skills/public/critique/references/code-critique.md
- skills/public/hitl/SKILL.md
- skills/public/impl/SKILL.md
- skills/public/impl/references/verification-ladder.md
- skills/public/quality/references/skill-ergonomics.md
- skills/public/setup/references/default-surfaces.md
- skills/public/setup/scripts/render_skill_routing.py
- skills/public/spec/SKILL.md
- specs/tool-doctor.spec.md
- tests/charness_cli/test_capability_resolution.py
- tests/charness_cli/test_codex_cache_refresh.py
- tests/charness_cli/test_codex_managed_install.py
- tests/charness_cli/test_doctor_cache_selection.py
- tests/charness_cli/test_doctor_next_action.py
- tests/charness_cli/test_goal_helpers.py
- tests/charness_cli/test_managed_install.py
- tests/charness_cli/test_managed_install_extended.py
- tests/charness_cli/test_managed_install_release_checks.py
- tests/charness_cli/test_task_envelope.py
- tests/charness_cli/test_tool_lifecycle.py
- tests/charness_cli/test_update_output.py
- tests/charness_cli/test_update_propagation.py
- tests/charness_cli/test_version_surface.py
- tests/charness_cli/test_worktree_create.py
- tests/charness_cli/test_worktree_doctor.py
- tests/control_plane/test_integrations_validation.py
- tests/quality_gates/test_setup_commit_discipline.py
- tests/quality_gates/test_setup_inspect_policy.py
- tests/quality_gates/test_setup_normalize_host_docs.py
- tests/quality_gates/test_setup_render_skill_routing.py
- tests/test_usage_episodes_host_hooks.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: integrations/tools/nose.json, scripts/check_coverage.py, scripts/doctor_lib.py, scripts/eval_setup.py, scripts/render_cli_reference.py, scripts/run-quality.sh, scripts/session_start_routing.py, scripts/support_sync_lib.py, skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/setup/scripts/render_skill_routing.py, skills/public/spec/SKILL.md
  derived matches: plugins/charness/integrations/tools/nose.json, plugins/charness/scripts/check_coverage.py, plugins/charness/scripts/doctor_lib.py, plugins/charness/scripts/eval_setup.py, plugins/charness/scripts/render_cli_reference.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/support_sync_lib.py, plugins/charness/skills/critique/references/code-critique.md, plugins/charness/skills/hitl/SKILL.md, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/impl/references/verification-ladder.md, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/setup/references/default-surfaces.md, plugins/charness/skills/setup/scripts/render_skill_routing.py, plugins/charness/skills/spec/SKILL.md
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: .agents/command-docs.yaml, AGENTS.md, docs/agent-task-envelope.md, docs/capability-resolution.md, docs/deferred-decisions.md, docs/generated/cli-reference.md, docs/operator-progressive-path.md, docs/worktree-prepare.md, skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/spec/SKILL.md
  derived matches: plugins/charness/skills/critique/references/code-critique.md, plugins/charness/skills/hitl/SKILL.md, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/impl/references/verification-ladder.md, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/setup/references/default-surfaces.md, plugins/charness/skills/spec/SKILL.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/release-adapter.yaml, AGENTS.md, skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/spec/SKILL.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/setup/scripts/render_skill_routing.py, skills/public/spec/SKILL.md
  derived matches: plugins/charness/skills/critique/references/code-critique.md, plugins/charness/skills/hitl/SKILL.md, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/impl/references/verification-ladder.md, plugins/charness/skills/quality/references/skill-ergonomics.md, plugins/charness/skills/setup/references/default-surfaces.md, plugins/charness/skills/setup/scripts/render_skill_routing.py, plugins/charness/skills/spec/SKILL.md
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- capability-catalog: Deterministic capability inventory, stale-path resolver, and canonical current-pointer artifacts.
  source matches: charness
  verify: python3 -m pytest -q tests/test_capability_catalog.py, python3 scripts/validate_current_pointer_freshness.py --repo-root ., python3 -m json.tool .agents/surfaces.json
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/setup/scripts/render_skill_routing.py, skills/public/spec/SKILL.md
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/critique/references/code-critique.md, skills/public/hitl/SKILL.md, skills/public/impl/SKILL.md, skills/public/impl/references/verification-ladder.md, skills/public/quality/references/skill-ergonomics.md, skills/public/setup/references/default-surfaces.md, skills/public/setup/scripts/render_skill_routing.py, skills/public/spec/SKILL.md
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/release-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- executable-specs: Repo-owned specdown executable acceptance specs and their config.
  source matches: specs/tool-doctor.spec.md
  verify: specdown run -quiet -no-report
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: integrations/tools/nose.json, scripts/doctor_lib.py, scripts/support_sync_lib.py
  derived matches: plugins/charness/integrations/tools/nose.json, plugins/charness/scripts/doctor_lib.py, plugins/charness/scripts/support_sync_lib.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/tools/nose.json, scripts/support_sync_lib.py
  derived matches: .charness/specdown/report.json, plugins/charness/integrations/tools/nose.json, plugins/charness/scripts/check_coverage.py, plugins/charness/scripts/doctor_lib.py, plugins/charness/scripts/eval_setup.py, plugins/charness/scripts/render_cli_reference.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/support_sync_lib.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/check_coverage.py, scripts/doctor_lib.py, scripts/eval_setup.py, scripts/render_cli_reference.py, scripts/session_start_routing.py, scripts/support_sync_lib.py, tests/charness_cli/test_capability_resolution.py, tests/charness_cli/test_codex_cache_refresh.py, tests/charness_cli/test_codex_managed_install.py, tests/charness_cli/test_doctor_cache_selection.py, tests/charness_cli/test_doctor_next_action.py, tests/charness_cli/test_goal_helpers.py, tests/charness_cli/test_managed_install.py, tests/charness_cli/test_managed_install_extended.py, tests/charness_cli/test_managed_install_release_checks.py, tests/charness_cli/test_task_envelope.py, tests/charness_cli/test_tool_lifecycle.py, tests/charness_cli/test_update_output.py, tests/charness_cli/test_update_propagation.py, tests/charness_cli/test_version_surface.py, tests/charness_cli/test_worktree_create.py, tests/charness_cli/test_worktree_doctor.py, tests/control_plane/test_integrations_validation.py, tests/quality_gates/test_setup_commit_discipline.py, tests/quality_gates/test_setup_inspect_policy.py, tests/quality_gates/test_setup_normalize_host_docs.py, tests/quality_gates/test_setup_render_skill_routing.py, tests/test_usage_episodes_host_hooks.py
  derived matches: plugins/charness/scripts/check_coverage.py, plugins/charness/scripts/doctor_lib.py, plugins/charness/scripts/eval_setup.py, plugins/charness/scripts/render_cli_reference.py, plugins/charness/scripts/session_start_routing.py, plugins/charness/scripts/support_sync_lib.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_coverage.py, scripts/doctor_lib.py, scripts/eval_setup.py, scripts/render_cli_reference.py, scripts/session_start_routing.py, scripts/support_sync_lib.py, skills/public/setup/scripts/render_skill_routing.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

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
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```
