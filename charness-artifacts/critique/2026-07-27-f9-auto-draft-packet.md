# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-27T04:10:37Z
- **Prepared for**: auto-draft stale-citation markers (F9)
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `0ece08a736c49385ca38c40f5ce8e8ee8f4569fc7f90b883586bd38152ee1b58`
- **Reviewed paths**: 6
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
- charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.json
- charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.md
- charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md
- charness-artifacts/quality/sloc-inventory/latest.json
- docs/handoff-chunked-routing.md
- docs/handoff.md
- plugins/charness/skills/handoff/references/chunked-routing.md
- plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py
- skills/public/handoff/references/chunked-routing.md
- skills/public/handoff/scripts/chunked_routing_auto_draft.py
- tests/test_handoff_chunker_auto_draft.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: skills/public/handoff/references/chunked-routing.md, skills/public/handoff/scripts/chunked_routing_auto_draft.py
  derived matches: plugins/charness/skills/handoff/references/chunked-routing.md, plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.md, charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md, docs/handoff-chunked-routing.md, docs/handoff.md, skills/public/handoff/references/chunked-routing.md
  derived matches: plugins/charness/skills/handoff/references/chunked-routing.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/handoff/references/chunked-routing.md
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/handoff/references/chunked-routing.md, skills/public/handoff/scripts/chunked_routing_auto_draft.py
  derived matches: plugins/charness/skills/handoff/references/chunked-routing.md, plugins/charness/skills/handoff/scripts/chunked_routing_auto_draft.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/handoff/references/chunked-routing.md, skills/public/handoff/scripts/chunked_routing_auto_draft.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/handoff/references/chunked-routing.md, skills/public/handoff/scripts/chunked_routing_auto_draft.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.json, charness-artifacts/critique/2026-07-27-f9-auto-draft-packet.md, charness-artifacts/critique/2026-07-27-handoff-auto-draft-stale-citation-markers-f9.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- repo-python: Repo-owned Python code and tests.
  source matches: tests/test_handoff_chunker_auto_draft.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: skills/public/handoff/scripts/chunked_routing_auto_draft.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
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
