# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-27T10:05:22Z
- **Prepared for**: empty-scope refusal family (A4/A7/C5/E2) + RCA cause-4 scoping
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `aa03827375b8dd007f4e4496131f96205c07d96599802cfd4e8623e1a553a29d`
- **Reviewed paths**: 21
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
- charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md
- charness-artifacts/critique/2026-07-27-empty-scope-family-packet.json
- charness-artifacts/critique/2026-07-27-empty-scope-family-packet.md
- charness-artifacts/critique/2026-07-27-empty-scope-family.md
- charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md
- plugins/charness/scripts/artifact_run_scope.py
- plugins/charness/scripts/artifact_validator.py
- plugins/charness/scripts/check_bootstrap_shim_consistency.py
- plugins/charness/scripts/check_export_safe_imports.py
- plugins/charness/scripts/check_mutation_run_proof.py
- plugins/charness/scripts/validate_critique_artifacts.py
- plugins/charness/scripts/validate_ideation_artifact.py
- plugins/charness/scripts/validate_packaging.py
- plugins/charness/scripts/validate_retro_artifact.py
- scripts/artifact_run_scope.py
- scripts/artifact_validator.py
- scripts/check_bootstrap_shim_consistency.py
- scripts/check_export_safe_imports.py
- scripts/check_mutation_run_proof.py
- scripts/validate_critique_artifacts.py
- scripts/validate_ideation_artifact.py
- scripts/validate_packaging.py
- scripts/validate_retro_artifact.py
- tests/quality_gates/test_empty_scope_refusals.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/artifact_run_scope.py, scripts/artifact_validator.py, scripts/check_bootstrap_shim_consistency.py, scripts/check_export_safe_imports.py, scripts/check_mutation_run_proof.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_packaging.py, scripts/validate_retro_artifact.py
  derived matches: plugins/charness/scripts/artifact_run_scope.py, plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_bootstrap_shim_consistency.py, plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/check_mutation_run_proof.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_packaging.py, plugins/charness/scripts/validate_retro_artifact.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md, charness-artifacts/critique/2026-07-27-empty-scope-family-packet.md, charness-artifacts/critique/2026-07-27-empty-scope-family.md, charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-27-empty-scope-family-packet.json, charness-artifacts/critique/2026-07-27-empty-scope-family-packet.md, charness-artifacts/critique/2026-07-27-empty-scope-family.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/artifact_run_scope.py, plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_bootstrap_shim_consistency.py, plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/check_mutation_run_proof.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_packaging.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/artifact_run_scope.py, scripts/artifact_validator.py, scripts/check_bootstrap_shim_consistency.py, scripts/check_export_safe_imports.py, scripts/check_mutation_run_proof.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_packaging.py, scripts/validate_retro_artifact.py, tests/quality_gates/test_empty_scope_refusals.py
  derived matches: plugins/charness/scripts/artifact_run_scope.py, plugins/charness/scripts/artifact_validator.py, plugins/charness/scripts/check_bootstrap_shim_consistency.py, plugins/charness/scripts/check_export_safe_imports.py, plugins/charness/scripts/check_mutation_run_proof.py, plugins/charness/scripts/validate_critique_artifacts.py, plugins/charness/scripts/validate_ideation_artifact.py, plugins/charness/scripts/validate_packaging.py, plugins/charness/scripts/validate_retro_artifact.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/artifact_run_scope.py, scripts/artifact_validator.py, scripts/check_bootstrap_shim_consistency.py, scripts/check_export_safe_imports.py, scripts/check_mutation_run_proof.py, scripts/validate_critique_artifacts.py, scripts/validate_ideation_artifact.py, scripts/validate_packaging.py, scripts/validate_retro_artifact.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
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
