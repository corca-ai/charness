# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-07-10T00:27:59Z
- **Prepared for**: v0.64.0 release bundle
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
- .agents/surfaces.json
- .agents/usage-episodes-adapter.yaml
- charness
- charness-artifacts/critique/2026-07-09-211611-packet.json
- charness-artifacts/critique/2026-07-09-211611-packet.md
- charness-artifacts/critique/2026-07-09-212954-packet.json
- charness-artifacts/critique/2026-07-09-212954-packet.md
- charness-artifacts/critique/2026-07-10-outcome-driven-autonomous-improvement-disposition-review.md
- charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md
- charness-artifacts/critique/2026-07-10-plain-version-readonly-critique.md
- charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.json
- charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.md
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-critique.md
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.json
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.md
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-critique.md
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.json
- charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.md
- charness-artifacts/critique/2026-07-10-usage-feedback-code-critique.md
- charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md
- charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md
- charness-artifacts/probe/2026-07-10-outcome-driven-autonomous-improvement-host-log.json
- charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md
- charness-artifacts/quality/2026-07-10-outcome-driven-feedback.md
- charness-artifacts/quality/2026-07-10-repo-wide-quality-speed-release.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-07-10-session-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/outcome-driven-feedback-retro-packet.json
- charness-artifacts/retro/outcome-driven-feedback-retro-packet.md
- charness-artifacts/retro/recent-lessons.md
- docs/handoff.md
- docs/product-success-metrics.md
- docs/public-skill-dogfood.json
- integrations/usage-episodes/adapter.example.yaml
- integrations/usage-episodes/episode.schema.json
- integrations/usage-episodes/manifest.schema.json
- plugins/charness/integrations/usage-episodes/adapter.example.yaml
- plugins/charness/integrations/usage-episodes/episode.schema.json
- plugins/charness/integrations/usage-episodes/manifest.schema.json
- plugins/charness/scripts/check-markdown.sh
- plugins/charness/scripts/record_usage_feedback.py
- plugins/charness/scripts/report_usage_episodes.py
- plugins/charness/scripts/slice_closeout_usage_episode.py
- plugins/charness/scripts/usage_episode_feedback.py
- plugins/charness/scripts/usage_episode_product_evidence.py
- plugins/charness/scripts/usage_episode_product_review.py
- plugins/charness/scripts/usage_episode_records.py
- plugins/charness/scripts/validate_usage_episodes.py
- plugins/charness/skills/quality/references/attention-state-visibility.json
- plugins/charness/skills/setup/scripts/templates/usage_episodes_adapter.yaml
- scripts/check-markdown.sh
- scripts/record_usage_feedback.py
- scripts/report_usage_episodes.py
- scripts/slice_closeout_usage_episode.py
- scripts/usage_episode_feedback.py
- scripts/usage_episode_product_evidence.py
- scripts/usage_episode_product_review.py
- scripts/usage_episode_records.py
- scripts/validate_usage_episodes.py
- skills/public/quality/references/attention-state-visibility.json
- skills/public/setup/scripts/templates/usage_episodes_adapter.yaml
- tests/charness_cli/test_bootstrap_runtime.py
- tests/charness_cli/test_version_surface.py
- tests/quality_gates/test_python_and_security_gates.py
- tests/quality_gates/test_surface_obligations.py
- tests/test_usage_episodes_report.py
- tests/test_usage_feedback.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: integrations/usage-episodes/adapter.example.yaml, integrations/usage-episodes/episode.schema.json, integrations/usage-episodes/manifest.schema.json, scripts/check-markdown.sh, scripts/record_usage_feedback.py, scripts/report_usage_episodes.py, scripts/slice_closeout_usage_episode.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, scripts/usage_episode_product_review.py, scripts/usage_episode_records.py, scripts/validate_usage_episodes.py, skills/public/quality/references/attention-state-visibility.json, skills/public/setup/scripts/templates/usage_episodes_adapter.yaml
  derived matches: plugins/charness/integrations/usage-episodes/adapter.example.yaml, plugins/charness/integrations/usage-episodes/episode.schema.json, plugins/charness/integrations/usage-episodes/manifest.schema.json, plugins/charness/scripts/check-markdown.sh, plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/slice_closeout_usage_episode.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/scripts/usage_episode_product_review.py, plugins/charness/scripts/usage_episode_records.py, plugins/charness/scripts/validate_usage_episodes.py, plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/setup/scripts/templates/usage_episodes_adapter.yaml
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-07-09-211611-packet.md, charness-artifacts/critique/2026-07-09-212954-packet.md, charness-artifacts/critique/2026-07-10-outcome-driven-autonomous-improvement-disposition-review.md, charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md, charness-artifacts/critique/2026-07-10-plain-version-readonly-critique.md, charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-critique.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-critique.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.md, charness-artifacts/critique/2026-07-10-usage-feedback-code-critique.md, charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md, charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md, charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md, charness-artifacts/quality/2026-07-10-outcome-driven-feedback.md, charness-artifacts/quality/2026-07-10-repo-wide-quality-speed-release.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-07-10-session-retro.md, charness-artifacts/retro/outcome-driven-feedback-retro-packet.md, charness-artifacts/retro/recent-lessons.md, docs/handoff.md, docs/product-success-metrics.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json >/dev/null
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: .agents/usage-episodes-adapter.yaml, skills/public/quality/references/attention-state-visibility.json
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/public/setup/scripts/templates/usage_episodes_adapter.yaml
  derived matches: plugins/charness/skills/quality/references/attention-state-visibility.json, plugins/charness/skills/setup/scripts/templates/usage_episodes_adapter.yaml
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root .
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/quality/references/attention-state-visibility.json, skills/public/setup/scripts/templates/usage_episodes_adapter.yaml
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: docs/public-skill-dogfood.json, skills/public/quality/references/attention-state-visibility.json, skills/public/setup/scripts/templates/usage_episodes_adapter.yaml
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- adapters: Repo-local adapter contracts and adapter helper libraries.
  source matches: .agents/usage-episodes-adapter.yaml
  verify: python3 scripts/validate_adapters.py --repo-root .
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-07-09-211611-packet.json, charness-artifacts/critique/2026-07-09-211611-packet.md, charness-artifacts/critique/2026-07-09-212954-packet.json, charness-artifacts/critique/2026-07-09-212954-packet.md, charness-artifacts/critique/2026-07-10-outcome-driven-autonomous-improvement-disposition-review.md, charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md, charness-artifacts/critique/2026-07-10-plain-version-readonly-critique.md, charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.json, charness-artifacts/critique/2026-07-10-plain-version-readonly-packet.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-critique.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.json, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-critique.md, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.json, charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-plan-packet.md, charness-artifacts/critique/2026-07-10-usage-feedback-code-critique.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-07-10-outcome-driven-autonomous-improvement-host-log.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- prompt-mutation-artifacts: Prompt-mutation experiment manifests, configs, scores, judge packets, and reports.
  source matches: charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md
  verify: for path in charness-artifacts/prompt-mutation/*.json; do [ -e "$path" ] && { python3 -m json.tool "$path" >/dev/null || exit $?; }; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-07-10-session-retro.md, charness-artifacts/retro/outcome-driven-feedback-retro-packet.json, charness-artifacts/retro/outcome-driven-feedback-retro-packet.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  source matches: integrations/usage-episodes/adapter.example.yaml, integrations/usage-episodes/episode.schema.json, integrations/usage-episodes/manifest.schema.json
  derived matches: plugins/charness/integrations/usage-episodes/adapter.example.yaml, plugins/charness/integrations/usage-episodes/episode.schema.json, plugins/charness/integrations/usage-episodes/manifest.schema.json, plugins/charness/scripts/check-markdown.sh, plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/slice_closeout_usage_episode.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/scripts/usage_episode_product_review.py, plugins/charness/scripts/usage_episode_records.py, plugins/charness/scripts/validate_usage_episodes.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: charness, scripts/record_usage_feedback.py, scripts/report_usage_episodes.py, scripts/slice_closeout_usage_episode.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, scripts/usage_episode_product_review.py, scripts/usage_episode_records.py, scripts/validate_usage_episodes.py, tests/charness_cli/test_bootstrap_runtime.py, tests/charness_cli/test_version_surface.py, tests/quality_gates/test_python_and_security_gates.py, tests/quality_gates/test_surface_obligations.py, tests/test_usage_episodes_report.py, tests/test_usage_feedback.py
  derived matches: plugins/charness/scripts/record_usage_feedback.py, plugins/charness/scripts/report_usage_episodes.py, plugins/charness/scripts/slice_closeout_usage_episode.py, plugins/charness/scripts/usage_episode_feedback.py, plugins/charness/scripts/usage_episode_product_evidence.py, plugins/charness/scripts/usage_episode_product_review.py, plugins/charness/scripts/usage_episode_records.py, plugins/charness/scripts/validate_usage_episodes.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/record_usage_feedback.py, scripts/report_usage_episodes.py, scripts/slice_closeout_usage_episode.py, scripts/usage_episode_feedback.py, scripts/usage_episode_product_evidence.py, scripts/usage_episode_product_review.py, scripts/usage_episode_records.py, scripts/validate_usage_episodes.py
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

## Fresh-Eye Satisfaction

parent-delegated — independent release operations and story reviewers plus a
separate counterweight consumed this packet before publication.

## Boundary Ownership

- Producer: locked v0.64.0 source bundle and repo-owned release helper.
- Consumer: GitHub release readers and installed Claude/Codex operators.
- Owning surface: release helper, release artifact, and adapter-owned install refresh.
- Verdict: owned-correctly
