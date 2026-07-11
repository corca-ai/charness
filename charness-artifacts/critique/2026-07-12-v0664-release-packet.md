# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-11T22:22:06Z
- **Prepared for**: v0.66.4 release candidate
- **Changed ref**: `v0.66.3..HEAD`
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
Changed paths for ref `v0.66.3..HEAD`:
- .agents/surfaces.json
- charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-2-disposition-review.md
- charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.json
- charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.md
- charness-artifacts/critique/2026-07-12-round3-slices-a-b-code-critique.md
- charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.json
- charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.md
- charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-code-critique.md
- charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.json
- charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.md
- charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md
- charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md
- charness-artifacts/probe/2026-07-12-north-star-autonomous-two-hour-release-round-2-host-log.md
- charness-artifacts/quality/2026-07-12-round3-v0664-release-readiness.md
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/latest.md
- charness-artifacts/retro/2026-07-11-151230-packet.json
- charness-artifacts/retro/2026-07-11-151230-packet.md
- charness-artifacts/retro/2026-07-12-v0663-round2-autonomous-release.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- plugins/charness/scripts/mutation_coverage_producer.py
- plugins/charness/scripts/run-quality.sh
- scripts/mutation_coverage_producer.py
- scripts/run-quality.sh
- tests/quality_gates/test_mutation_coverage_producer.py
- tests/quality_gates/test_quality_runner.py
- tests/quality_gates/test_quality_runner_coverage_selection.py
- tests/quality_gates/test_quality_runner_runtime_aggregate.py
- tests/quality_gates/test_surface_obligations.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/mutation_coverage_producer.py, scripts/run-quality.sh
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py, plugins/charness/scripts/run-quality.sh
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-2-disposition-review.md, charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.md, charness-artifacts/critique/2026-07-12-round3-slices-a-b-code-critique.md, charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.md, charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-code-critique.md, charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.md, charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md, charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md, charness-artifacts/probe/2026-07-12-north-star-autonomous-two-hour-release-round-2-host-log.md, charness-artifacts/quality/2026-07-12-round3-v0664-release-readiness.md, charness-artifacts/quality/latest.md, charness-artifacts/release/latest.md, charness-artifacts/retro/2026-07-11-151230-packet.md, charness-artifacts/retro/2026-07-12-v0663-round2-autonomous-release.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-2-disposition-review.md, charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.json, charness-artifacts/critique/2026-07-12-round3-goal-plan-packet.md, charness-artifacts/critique/2026-07-12-round3-slices-a-b-code-critique.md, charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.json, charness-artifacts/critique/2026-07-12-round3-slices-a-b-packet.md, charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-code-critique.md, charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.json, charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-11-151230-packet.json, charness-artifacts/retro/2026-07-11-151230-packet.md, charness-artifacts/retro/2026-07-12-v0663-round2-autonomous-release.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py, plugins/charness/scripts/run-quality.sh
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/mutation_coverage_producer.py, tests/quality_gates/test_mutation_coverage_producer.py, tests/quality_gates/test_quality_runner.py, tests/quality_gates/test_quality_runner_coverage_selection.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py, tests/quality_gates/test_surface_obligations.py
  derived matches: plugins/charness/scripts/mutation_coverage_producer.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/mutation_coverage_producer.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
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
