# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-18T17:57:27Z
- **Prepared for**: release observer fail-closed simplification
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `c365742377dd4c007c8963fd3042b7d333fa58d2d05a8e3c9bcba240b5be38fe`
- **Reviewed paths**: 3
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
- plugins/charness/skills/release/scripts/release_observer.py
- skills/public/release/scripts/release_observer.py
- tests/quality_gates/test_release_observer.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/release/scripts/release_observer.py
  derived matches: plugins/charness/skills/release/scripts/release_observer.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/release/scripts/release_observer.py
  derived matches: plugins/charness/skills/release/scripts/release_observer.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/release/scripts/release_observer.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/release/scripts/release_observer.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/test_release_observer.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/release/scripts/release_observer.py
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
