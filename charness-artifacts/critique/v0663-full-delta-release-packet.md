# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-11T14:14:53Z
- **Prepared for**: v0.66.3 full published-tag delta and notes
- **Changed ref**: `v0.66.2..HEAD`
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
Changed paths for ref `v0.66.2..HEAD`:
- charness-artifacts/critique/2026-07-11-133455-packet.json
- charness-artifacts/critique/2026-07-11-133455-packet.md
- charness-artifacts/critique/2026-07-11-north-star-autonomous-two-hour-release-disposition-review.md
- charness-artifacts/critique/round2-slices-a-b-post-change-packet.json
- charness-artifacts/critique/round2-slices-a-b-post-change-packet.md
- charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md
- charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md
- charness-artifacts/probe/2026-07-11-north-star-autonomous-two-hour-release.json
- charness-artifacts/quality/2026-07-11-quality-review.md
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/2026-07-11-v0.66.3-notes.md
- charness-artifacts/release/latest.md
- charness-artifacts/retro/2026-07-11-131833-packet.json
- charness-artifacts/retro/2026-07-11-131833-packet.md
- charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- plugins/charness/scripts/record_usage_feedback.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/slice_closeout_command_executor.py
- scripts/record_usage_feedback.py
- scripts/run_slice_closeout.py
- scripts/slice_closeout_command_executor.py
- tests/quality_gates/test_slice_closeout_broad_gate.py
- tests/test_usage_feedback.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-11-133455-packet.md, charness-artifacts/critique/2026-07-11-north-star-autonomous-two-hour-release-disposition-review.md, charness-artifacts/critique/round2-slices-a-b-post-change-packet.md, charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md, charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release.md, charness-artifacts/quality/2026-07-11-quality-review.md, charness-artifacts/quality/latest.md, charness-artifacts/release/2026-07-11-v0.66.3-notes.md, charness-artifacts/release/latest.md, charness-artifacts/retro/2026-07-11-131833-packet.md, charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  verify: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-11-133455-packet.json, charness-artifacts/critique/2026-07-11-133455-packet.md, charness-artifacts/critique/2026-07-11-north-star-autonomous-two-hour-release-disposition-review.md, charness-artifacts/critique/round2-slices-a-b-post-change-packet.json, charness-artifacts/critique/round2-slices-a-b-post-change-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-11-north-star-autonomous-two-hour-release.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-11-131833-packet.json, charness-artifacts/retro/2026-07-11-131833-packet.md, charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py, tests/quality_gates/test_slice_closeout_broad_gate.py, tests/test_usage_feedback.py
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_command_executor.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/record_usage_feedback.py, scripts/run_slice_closeout.py, scripts/slice_closeout_command_executor.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

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

## Release Critique Result

- **Fresh-eye verdict**: conditional **HOLD** until the normal pre-publication
  proof is complete; no permanent design, semver, or notes blocker found.
- **Fresh-eye satisfaction**: `v0663_release_critique`, requested
  `model=gpt-5.5` with high reasoning, used only the bounded read-only command
  set. Reviewer-boundary verification returned `ok=true` with zero drift.
- **Semver**: patch is honest. The delta repairs internal orchestration and
  concurrent replay without removing or adding a public command, schema, skill,
  or invocation contract.
- **Notes**: value, compatibility, no-binary-assets expectation, issue-state
  non-claim, and mixed-writer non-claim are accurate and proportionate.

### Conditions to lift the hold

1. Commit this critique packet so the release helper consumes tracked proof.
2. Run the clean-HEAD verification lock with broad pytest and changed-line
   mutation coverage, then preserve that exact HEAD until release mutation.
3. Run the release dry-run and inspect exact arguments, generated release
   commit message, and notes for zero issue-close flags or close keywords.
4. Publish only through the helper/resume path; treat its green result as
   provisional until a different observer verifies unauthenticated public HTTPS
   content and the maintainer install/version/doctor readback.

### Counterweight and non-claims

- Do not hold merely because `charness-artifacts/release/latest.md` still names
  v0.66.2 before publication; the helper owns its post-publish ledger update.
- Do not inflate to minor for compatible internal reliability repairs.
- No issue close, whole-stream locking, public sync-only CLI, binary asset, or
  public-release success is claimed by this pre-publication critique.
