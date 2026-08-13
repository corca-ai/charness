# Retro Prepare Packet — charness

- **Kind**: `charness.retro_prepare_packet` (v1)
- **Generated**: 2026-08-13T22:14:08Z
- **Prepared for**: current-contract cleanup, durable lesson bundles, and streamed runner lifecycle
- **Adapter**: `.agents/retro-adapter.yaml`
- **Sections**: 1
- **Overall ok**: True


Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section ok**: True

```text
Changed paths for working tree:
- charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md
- charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/sloc-inventory/latest.json
- plugins/charness/scripts/run-quality.sh
- scripts/run-quality.sh
- tests/test_reviewed_input_identity_failures.py
- charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.json
- charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.md

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/run-quality.sh
  derived matches: plugins/charness/scripts/run-quality.sh
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md, charness-artifacts/quality/2026-08-13-issue-616-applied-lifecycle.md, charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md, charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.json, charness-artifacts/critique/2026-08-14-current-contract-cleanup-final-binding-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/run-quality.sh
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/test_reviewed_input_identity_failures.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
```
