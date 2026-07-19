# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-19T00:34:17Z
- **Prepared for**: fake git shell proxy speed slice final shell lint ownership
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `f328b40cf0b23ec69b90ad1b35b7519afa4b95d22e2a97b706445a27bf4c23eb`
- **Reviewed paths**: 10
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
- .agents/surfaces.json
- charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-critique.md
- charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.json
- charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.md
- charness-artifacts/quality/2026-07-19-quality-review.md
- charness-artifacts/retro/2026-07-19-003309-packet.json
- charness-artifacts/retro/2026-07-19-003309-packet.md
- charness-artifacts/retro/2026-07-19-fake-git-proxy-speed-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- docs/handoff.md
- plugins/charness/scripts/check-shell.sh
- scripts/check-shell.sh
- tests/quality_gates/fixtures/release_publish_fake_git.py
- tests/quality_gates/fixtures/release_publish_fake_git.sh
- tests/quality_gates/release_publish_fixtures.py
- tests/quality_gates/test_python_and_security_gates.py
- tests/quality_gates/test_release_publish_fake_git.py
- tests/quality_gates/test_release_publish_real_host_delta.py
- tests/quality_gates/test_surface_obligations.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/check-shell.sh
  derived matches: plugins/charness/scripts/check-shell.sh
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-critique.md, charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.md, charness-artifacts/quality/2026-07-19-quality-review.md, charness-artifacts/retro/2026-07-19-003309-packet.md, charness-artifacts/retro/2026-07-19-fake-git-proxy-speed-retro.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-critique.md, charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.json, charness-artifacts/critique/2026-07-19-fake-git-shell-proxy-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-19-003309-packet.json, charness-artifacts/retro/2026-07-19-003309-packet.md, charness-artifacts/retro/2026-07-19-fake-git-proxy-speed-retro.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/check-shell.sh
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: tests/quality_gates/fixtures/release_publish_fake_git.py, tests/quality_gates/fixtures/release_publish_fake_git.sh, tests/quality_gates/release_publish_fixtures.py, tests/quality_gates/test_python_and_security_gates.py, tests/quality_gates/test_release_publish_fake_git.py, tests/quality_gates/test_release_publish_real_host_delta.py, tests/quality_gates/test_surface_obligations.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
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
