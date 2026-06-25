# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-06-25T03:56:31Z
- **Prepared for**: v0.55.0 release
- **Changed ref**: `origin/main..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Sections**: 2
- **Overall ok**: True

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `model=gpt-5.5, reasoning_effort=medium, service_tier=priority`
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
Changed paths for ref `origin/main..HEAD`:
- .agents/critique-adapter.yaml
- .agents/release-adapter.yaml
- .agents/retro-adapter.yaml
- charness-artifacts/critique/2026-06-25-004012-packet.json
- charness-artifacts/critique/2026-06-25-004012-packet.md
- charness-artifacts/critique/2026-06-25-release-adapter-update-instructions-decoupling.md
- charness-artifacts/find-skills/latest.json
- charness-artifacts/find-skills/latest.md
- charness-artifacts/quality/dup-ratchet-baseline.json
- charness-artifacts/quality/history/2026-06-25-retro-skill-quality-review.md
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/nose-baseline.json
- docs/conventions/authoring-preflight.md
- docs/handoff.md
- docs/public-skill-dogfood.json
- plugins/charness/scripts/artifact_validator.py
- plugins/charness/scripts/check_skill_contracts.py
- plugins/charness/scripts/critique_packet_lib.py
- plugins/charness/scripts/public_skill_dogfood_lib.py
- plugins/charness/scripts/render_critique_section_changed_surfaces.py
- plugins/charness/scripts/validate_adapters.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/scripts/validate_ideation_artifact.py
- plugins/charness/scripts/validate_inventory_consumption.py
- plugins/charness/scripts/validate_quality_artifact.py
- plugins/charness/scripts/validate_retro_artifact.py
- plugins/charness/skills/quality/SKILL.md
- plugins/charness/skills/quality/scripts/plan_quality_run.py
- plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py
- plugins/charness/skills/release/adapter.example.yaml
- plugins/charness/skills/release/references/adapter-contract.md
- plugins/charness/skills/release/references/critique-boundary.md
- plugins/charness/skills/release/references/install-refresh.md
- plugins/charness/skills/release/scripts/plan_release_run_packets.py
- plugins/charness/skills/release/scripts/publish_release_cli.py
- plugins/charness/skills/release/scripts/publish_release_preflight.py
- plugins/charness/skills/retro/SKILL.md
- plugins/charness/skills/retro/adapter.example.yaml
- plugins/charness/skills/retro/references/adapter-contract.md
- plugins/charness/skills/retro/references/prepare-packet.md
- plugins/charness/skills/retro/scripts/prepare_packet.py
- plugins/charness/skills/retro/scripts/resolve_adapter.py
- plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
- scripts/artifact_validator.py
- scripts/check_skill_contracts.py
- scripts/critique_packet_lib.py
- scripts/public_skill_dogfood_lib.py
- scripts/render_critique_section_changed_surfaces.py
- scripts/validate_adapters.py
- scripts/validate_critique_artifacts.py
- scripts/validate_ideation_artifact.py
- scripts/validate_inventory_consumption.py
- scripts/validate_quality_artifact.py
- scripts/validate_retro_artifact.py
- skills/public/quality/SKILL.md
- skills/public/quality/scripts/plan_quality_run.py
- skills/public/quality/scripts/scaffold_quality_artifact.py
- skills/public/release/adapter.example.yaml
- skills/public/release/references/adapter-contract.md
- skills/public/release/references/critique-boundary.md
- skills/public/release/references/install-refresh.md
- skills/public/release/scripts/plan_release_run_packets.py
- skills/public/release/scripts/publish_release_cli.py
- skills/public/release/scripts/publish_release_preflight.py
- skills/public/retro/SKILL.md
- skills/public/retro/adapter.example.yaml
- skills/public/retro/references/adapter-contract.md
- skills/public/retro/references/prepare-packet.md
- skills/public/retro/scripts/prepare_packet.py
- skills/public/retro/scripts/resolve_adapter.py
- skills/public/retro/scripts/scaffold_retro_artifact.py
- tests/quality_gates/test_inventory_consumption.py
- tests/quality_gates/test_quality_run_planner.py
- tests/quality_gates/test_release_publish_resilience.py
- tests/quality_gates/test_release_run_planner.py
- tests/quality_gates/test_retro_skill.py
- tests/test_ideation_artifact.py
- tests/test_quality_artifact.py
- tests/test_quality_scaffold.py
- tests/test_retro_artifact.py
- tests/test_retro_prepare_packet.py
- tests/test_retro_scaffold.py
- tests/test_validate_adapters_integration_schema.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/artifact_validator.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/public_skill_dogfood_lib.py, scripts/render_critique_section_changed_surfaces.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_quality_artifact.py, scripts/validate_retro_artifact.py, skills/public/quality/SKILL.md, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/adapter.example.yaml, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md, skills/public/retro/scripts/prepare_packet.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  derived matches: plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/render_critique_section_changed_surfaces.py, plugins/charness/scripts/validate_adapters.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_quality_artifact.py, plugins/charness/scripts/validate_retro_artifact.py, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/release/adapter.example.yaml, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/critique-boundary.md, plugins/charness/skills/release/references/install-refresh.md, plugins/charness/skills/release/scripts/plan_release_run_packets.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_preflight.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/adapter.example.yaml, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/prepare-packet.md, plugins/charness/skills/retro/scripts/prepare_packet.py, plugins/charness/skills/retro/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-06-25-004012-packet.md, charness-artifacts/critique/2026-06-25-release-adapter-update-instructions-decoupling.md, charness-artifacts/find-skills/latest.md, charness-artifacts/quality/history/2026-06-25-retro-skill-quality-review.md, charness-artifacts/quality/latest.md, docs/conventions/authoring-preflight.md, docs/handoff.md, skills/public/quality/SKILL.md, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md
  derived matches: plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/critique-boundary.md, plugins/charness/skills/release/references/install-refresh.md, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/prepare-packet.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-ratchet-baseline.json, charness-artifacts/quality/nose-baseline.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json >/dev/null
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/critique-adapter.yaml, .agents/release-adapter.yaml, .agents/retro-adapter.yaml, skills/public/quality/SKILL.md, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/retro/SKILL.md, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/SKILL.md, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/adapter.example.yaml, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md, skills/public/retro/scripts/prepare_packet.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  derived matches: charness-artifacts/find-skills/latest.json, charness-artifacts/find-skills/latest.md, plugins/charness/skills/quality/SKILL.md, plugins/charness/skills/quality/scripts/plan_quality_run.py, plugins/charness/skills/quality/scripts/scaffold_quality_artifact.py, plugins/charness/skills/release/adapter.example.yaml, plugins/charness/skills/release/references/adapter-contract.md, plugins/charness/skills/release/references/critique-boundary.md, plugins/charness/skills/release/references/install-refresh.md, plugins/charness/skills/release/scripts/plan_release_run_packets.py, plugins/charness/skills/release/scripts/publish_release_cli.py, plugins/charness/skills/release/scripts/publish_release_preflight.py, plugins/charness/skills/retro/SKILL.md, plugins/charness/skills/retro/adapter.example.yaml, plugins/charness/skills/retro/references/adapter-contract.md, plugins/charness/skills/retro/references/prepare-packet.md, plugins/charness/skills/retro/scripts/prepare_packet.py, plugins/charness/skills/retro/scripts/resolve_adapter.py, plugins/charness/skills/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/SKILL.md, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/adapter.example.yaml, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md, skills/public/retro/scripts/prepare_packet.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, scripts/public_skill_dogfood_lib.py, skills/public/quality/SKILL.md, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/adapter.example.yaml, skills/public/release/references/adapter-contract.md, skills/public/release/references/critique-boundary.md, skills/public/release/references/install-refresh.md, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/retro/SKILL.md, skills/public/retro/adapter.example.yaml, skills/public/retro/references/adapter-contract.md, skills/public/retro/references/prepare-packet.md, skills/public/retro/scripts/prepare_packet.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/critique-adapter.yaml, .agents/release-adapter.yaml, .agents/retro-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-06-25-004012-packet.json, charness-artifacts/critique/2026-06-25-004012-packet.md, charness-artifacts/critique/2026-06-25-release-adapter-update-instructions-decoupling.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/render_critique_section_changed_surfaces.py, plugins/charness/scripts/validate_adapters.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_quality_artifact.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/artifact_validator.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/public_skill_dogfood_lib.py, scripts/render_critique_section_changed_surfaces.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_quality_artifact.py, scripts/validate_retro_artifact.py, tests/quality_gates/test_inventory_consumption.py, tests/quality_gates/test_quality_run_planner.py, tests/quality_gates/test_release_publish_resilience.py, tests/quality_gates/test_release_run_planner.py, tests/quality_gates/test_retro_skill.py, tests/test_ideation_artifact.py, tests/test_quality_artifact.py, tests/test_quality_scaffold.py, tests/test_retro_artifact.py, tests/test_retro_prepare_packet.py, tests/test_retro_scaffold.py, tests/test_validate_adapters_integration_schema.py
  derived matches: plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/public_skill_dogfood_lib.py, plugins/charness/scripts/render_critique_section_changed_surfaces.py, plugins/charness/scripts/validate_adapters.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_inventory_consumption.py, plugins/charness/scripts/validate_quality_artifact.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/artifact_validator.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/public_skill_dogfood_lib.py, scripts/render_critique_section_changed_surfaces.py, scripts/validate_adapters.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_inventory_consumption.py, scripts/validate_quality_artifact.py, scripts/validate_retro_artifact.py, skills/public/quality/scripts/plan_quality_run.py, skills/public/quality/scripts/scaffold_quality_artifact.py, skills/public/release/scripts/plan_release_run_packets.py, skills/public/release/scripts/publish_release_cli.py, skills/public/release/scripts/publish_release_preflight.py, skills/public/retro/scripts/prepare_packet.py, skills/public/retro/scripts/resolve_adapter.py, skills/public/retro/scripts/scaffold_retro_artifact.py
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
