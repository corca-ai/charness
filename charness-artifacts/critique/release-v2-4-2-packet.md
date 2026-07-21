# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-21T23:01:28Z
- **Prepared for**: release-v2.4.2
- **Changed ref**: `v2.4.1..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `2c22f0e9a47092ef5a94f70c8333963efd8339abbc3da7a6d5894b19a053f69d`
- **Reviewed paths**: 29
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
Changed paths for ref `v2.4.1..HEAD`:
- .agents/surfaces.json
- charness-artifacts/critique/2026-07-22-five-pass-quality-review-critique.md
- charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.json
- charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.md
- charness-artifacts/critique/2026-07-22-issue-450-resolution-critique.md
- charness-artifacts/critique/five-pass-quality-final-packet-packet.json
- charness-artifacts/critique/five-pass-quality-final-packet-packet.md
- charness-artifacts/debug/2026-07-22-debug-review.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/issue/2026-07-22-issue-449-brief.md
- charness-artifacts/probe/2026-07-20-v2.4.1-release-observer.json
- charness-artifacts/quality/2026-07-22-quality-review.md
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/latest.md
- docs/handoff.md
- integrations/tools/defuddle.json
- plugins/charness/integrations/tools/defuddle.json
- plugins/charness/scripts/lint_ignore_inventory_lib.py
- plugins/charness/scripts/quality_bootstrap_detect.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/skills/quality/scripts/standing_gate_verbosity_lib.py
- scripts/lint_ignore_inventory_lib.py
- scripts/quality_bootstrap_detect.py
- scripts/run-quality.sh
- skills/public/quality/scripts/standing_gate_verbosity_lib.py
- tests/quality_gates/test_quality_bootstrap.py
- tests/quality_gates/test_quality_runner.py
- tests/quality_gates/test_quality_standing_gate_verbosity.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: integrations/tools/defuddle.json, scripts/lint_ignore_inventory_lib.py, scripts/quality_bootstrap_detect.py, scripts/run-quality.sh, skills/public/quality/scripts/standing_gate_verbosity_lib.py
  derived matches: plugins/charness/integrations/tools/defuddle.json, plugins/charness/scripts/lint_ignore_inventory_lib.py, plugins/charness/scripts/quality_bootstrap_detect.py, plugins/charness/scripts/run-quality.sh, plugins/charness/skills/quality/scripts/standing_gate_verbosity_lib.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-22-five-pass-quality-review-critique.md, charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.md, charness-artifacts/critique/2026-07-22-issue-450-resolution-critique.md, charness-artifacts/critique/five-pass-quality-final-packet-packet.md, charness-artifacts/debug/2026-07-22-debug-review.md, charness-artifacts/issue/2026-07-22-issue-449-brief.md, charness-artifacts/quality/2026-07-22-quality-review.md, charness-artifacts/quality/latest.md, charness-artifacts/release/latest.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/scripts/standing_gate_verbosity_lib.py
  derived matches: plugins/charness/skills/quality/scripts/standing_gate_verbosity_lib.py
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/scripts/standing_gate_verbosity_lib.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/quality/scripts/standing_gate_verbosity_lib.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-22-five-pass-quality-review-critique.md, charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.json, charness-artifacts/critique/2026-07-22-issue-450-resolution-critique-packet.md, charness-artifacts/critique/2026-07-22-issue-450-resolution-critique.md, charness-artifacts/critique/five-pass-quality-final-packet-packet.json, charness-artifacts/critique/five-pass-quality-final-packet-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-20-v2.4.1-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-07-22-debug-review.md
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- external-tool-control-plane: External tool manifests and install, update, doctor, support-sync, and upstream-release helpers whose behavior depends on host state.
  source matches: integrations/tools/defuddle.json
  derived matches: plugins/charness/integrations/tools/defuddle.json
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/tools/defuddle.json
  derived matches: plugins/charness/integrations/tools/defuddle.json, plugins/charness/scripts/lint_ignore_inventory_lib.py, plugins/charness/scripts/quality_bootstrap_detect.py, plugins/charness/scripts/run-quality.sh
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/lint_ignore_inventory_lib.py, scripts/quality_bootstrap_detect.py, tests/quality_gates/test_quality_bootstrap.py, tests/quality_gates/test_quality_runner.py, tests/quality_gates/test_quality_standing_gate_verbosity.py
  derived matches: plugins/charness/scripts/lint_ignore_inventory_lib.py, plugins/charness/scripts/quality_bootstrap_detect.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- inference-interpretation-contract: Advisory-interpretation contract meta-validator (#330): the inference-layer surface registry plus every registered Python/prose declaration and its paired consumer reference.
  source matches: scripts/lint_ignore_inventory_lib.py
  verify: python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/lint_ignore_inventory_lib.py, scripts/quality_bootstrap_detect.py, skills/public/quality/scripts/standing_gate_verbosity_lib.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
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
