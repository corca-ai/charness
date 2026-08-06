# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-06T08:57:10Z
- **Prepared for**: release-3.3.0-final-prepublish-v4
- **Changed ref**: `e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5..de5e1461`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `6a8a4f9ffefc3c8d824cba0001c046a59a5524ae14addb6ee12fcb9fab617c8c`
- **Reviewed paths**: 48
- **Sections**: 3
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
Changed paths for ref `e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5..de5e1461`:
- .agents/surfaces.json
- charness-artifacts/critique/2026-08-06-020720-packet.json
- charness-artifacts/critique/2026-08-06-020720-packet.md
- charness-artifacts/critique/2026-08-06-021609-packet.json
- charness-artifacts/critique/2026-08-06-021609-packet.md
- charness-artifacts/critique/2026-08-06-022434-packet.json
- charness-artifacts/critique/2026-08-06-022434-packet.md
- charness-artifacts/critique/2026-08-06-030456-packet.json
- charness-artifacts/critique/2026-08-06-030456-packet.md
- charness-artifacts/critique/2026-08-06-031648-packet.json
- charness-artifacts/critique/2026-08-06-031648-packet.md
- charness-artifacts/critique/2026-08-06-032554-packet.json
- charness-artifacts/critique/2026-08-06-032554-packet.md
- charness-artifacts/critique/2026-08-06-033900-contract-final-packet.json
- charness-artifacts/critique/2026-08-06-033900-contract-final-packet.md
- charness-artifacts/critique/2026-08-06-036800-post-commit-ledger-packet.json
- charness-artifacts/critique/2026-08-06-036800-post-commit-ledger-packet.md
- charness-artifacts/critique/2026-08-06-040107-packet.json
- charness-artifacts/critique/2026-08-06-040107-packet.md
- charness-artifacts/critique/2026-08-06-041213-packet.json
- charness-artifacts/critique/2026-08-06-041213-packet.md
- charness-artifacts/critique/2026-08-06-041231-packet.json
- charness-artifacts/critique/2026-08-06-041231-packet.md
- charness-artifacts/critique/2026-08-06-041942-packet.json
- charness-artifacts/critique/2026-08-06-041942-packet.md
- charness-artifacts/critique/2026-08-06-050405-packet.json
- charness-artifacts/critique/2026-08-06-050405-packet.md
- charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md
- charness-artifacts/critique/2026-08-06-post-push-operational-proof-runtime-evidence-closeout-claims-review.md
- charness-artifacts/critique/2026-08-06-post-ratchet-ledger-packet.json
- charness-artifacts/critique/2026-08-06-post-ratchet-ledger-packet.md
- charness-artifacts/critique/2026-08-06-post-split-ledger-packet.json
- charness-artifacts/critique/2026-08-06-post-split-ledger-packet.md
- charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.json
- charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.md
- charness-artifacts/critique/2026-08-06-slice-1-manifest-contract.md
- charness-artifacts/critique/2026-08-06-slice-1-manifest-implementation-review.md
- charness-artifacts/critique/2026-08-06-slice-2-premise-contract.md
- charness-artifacts/critique/2026-08-06-slice-2-premise-implementation-review.md
- charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md
- charness-artifacts/critique/2026-08-06-slice-3-final-bundle-implementation-review.md
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.json
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.md
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-packet.json
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-packet.md
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review.md
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-critique.md
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.json
- charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.md
- charness-artifacts/critique/release-3-3-0-final-prepublish-v2-packet.json
- charness-artifacts/critique/release-3-3-0-final-prepublish-v2-packet.md
- charness-artifacts/critique/release-3-3-0-final-prepublish-v3-packet.json
- charness-artifacts/critique/release-3-3-0-final-prepublish-v3-packet.md
- charness-artifacts/critique/release-3-3-0-prepublish-packet.json
- charness-artifacts/critique/release-3-3-0-prepublish-packet.md
- charness-artifacts/critique/release-3-3-0-prepublish.md
- charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md
- charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json
- charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md
- charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json
- charness-artifacts/goals/2026-08-06-slice-2-premise-decisions.jsonl
- charness-artifacts/goals/fixtures/2026-08-06-slice-2-premise-closed-issue-readback.json
- charness-artifacts/goals/fixtures/2026-08-06-slice-2-premise.json
- charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
- charness-artifacts/probe/2026-08-01-inventory-marker-rule.json
- charness-artifacts/quality/2026-08-06-mutation-producer-discovery.md
- charness-artifacts/quality/2026-08-06-quality-review.md
- charness-artifacts/quality/2026-08-06-runtime-ab-evidence.md
- charness-artifacts/quality/2026-08-06-slice-2-prelock-closeout.md
- charness-artifacts/quality/2026-08-06-slice-3-final-bundle-preflight.md
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/latest.md
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release/v3.3.0-notes.md
- charness-artifacts/retro/2026-08-06-session-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/spec/2026-08-06-final-bundle-preflight-contract.md
- charness-artifacts/spec/2026-08-06-issue-510-markdown-negotiation-contract.md
- charness-artifacts/spec/2026-08-06-premise-preflight-contract.md
- charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md
- docs/handoff.md
- plugins/charness/scripts/boundary-bypass-exemptions.txt
- plugins/charness/scripts/check_premise_preflight.py
- plugins/charness/scripts/final_bundle_preflight.py
- plugins/charness/scripts/final_bundle_preflight_evidence.py
- plugins/charness/scripts/final_bundle_preflight_lib.py
- plugins/charness/scripts/premise_preflight_lib.py
- plugins/charness/scripts/publish_state_ledger.py
- plugins/charness/scripts/slice_manifest_lib.py
- plugins/charness/scripts/validate_slice_manifest.py
- scripts/boundary-bypass-exemptions.txt
- scripts/check_premise_preflight.py
- scripts/final_bundle_preflight.py
- scripts/final_bundle_preflight_evidence.py
- scripts/final_bundle_preflight_lib.py
- scripts/premise_preflight_lib.py
- scripts/publish_state_ledger.py
- scripts/slice_manifest_lib.py
- scripts/validate_slice_manifest.py
- tests/quality_gates/test_final_bundle_preflight.py
- tests/quality_gates/test_premise_preflight.py
- tests/quality_gates/test_publish_state_ledger.py
- tests/quality_gates/test_slice_manifest.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/boundary-bypass-exemptions.txt, scripts/check_premise_preflight.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_evidence.py, scripts/final_bundle_preflight_lib.py, scripts/premise_preflight_lib.py, scripts/publish_state_ledger.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py
  derived matches: plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_evidence.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/publish_state_ledger.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-06-020720-packet.md, charness-artifacts/critique/2026-08-06-021609-packet.md, charness-artifacts/critique/2026-08-06-022434-packet.md, charness-artifacts/critique/2026-08-06-030456-packet.md, charness-artifacts/critique/2026-08-06-031648-packet.md, charness-artifacts/critique/2026-08-06-032554-packet.md, charness-artifacts/critique/2026-08-06-033900-contract-final-packet.md, charness-artifacts/critique/2026-08-06-036800-post-commit-ledger-packet.md, charness-artifacts/critique/2026-08-06-040107-packet.md, charness-artifacts/critique/2026-08-06-041213-packet.md, charness-artifacts/critique/2026-08-06-041231-packet.md, charness-artifacts/critique/2026-08-06-041942-packet.md, charness-artifacts/critique/2026-08-06-050405-packet.md, charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md, charness-artifacts/critique/2026-08-06-post-push-operational-proof-runtime-evidence-closeout-claims-review.md, charness-artifacts/critique/2026-08-06-post-ratchet-ledger-packet.md, charness-artifacts/critique/2026-08-06-post-split-ledger-packet.md, charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.md, charness-artifacts/critique/2026-08-06-slice-1-manifest-contract.md, charness-artifacts/critique/2026-08-06-slice-1-manifest-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-2-premise-contract.md, charness-artifacts/critique/2026-08-06-slice-2-premise-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md, charness-artifacts/critique/2026-08-06-slice-3-final-bundle-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-packet.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-critique.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.md, charness-artifacts/critique/release-3-3-0-final-prepublish-v2-packet.md, charness-artifacts/critique/release-3-3-0-final-prepublish-v3-packet.md, charness-artifacts/critique/release-3-3-0-prepublish-packet.md, charness-artifacts/critique/release-3-3-0-prepublish.md, charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md, charness-artifacts/goals/2026-08-06-post-push-operational-proof-runtime-evidence.md, charness-artifacts/quality/2026-08-06-mutation-producer-discovery.md, charness-artifacts/quality/2026-08-06-quality-review.md, charness-artifacts/quality/2026-08-06-runtime-ab-evidence.md, charness-artifacts/quality/2026-08-06-slice-2-prelock-closeout.md, charness-artifacts/quality/2026-08-06-slice-3-final-bundle-preflight.md, charness-artifacts/quality/latest.md, charness-artifacts/release/v3.3.0-notes.md, charness-artifacts/retro/2026-08-06-session-retro.md, charness-artifacts/spec/2026-08-06-final-bundle-preflight-contract.md, charness-artifacts/spec/2026-08-06-issue-510-markdown-negotiation-contract.md, charness-artifacts/spec/2026-08-06-premise-preflight-contract.md, charness-artifacts/spec/2026-08-06-publish-state-ledger-contract.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- goal-evidence-json: Machine-readable evidence captured beside achieve goal artifacts.
  source matches: charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json, charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json, charness-artifacts/goals/2026-08-06-slice-2-premise-decisions.jsonl, charness-artifacts/goals/fixtures/2026-08-06-slice-2-premise-closed-issue-readback.json, charness-artifacts/goals/fixtures/2026-08-06-slice-2-premise.json
  verify: for evidence_file in charness-artifacts/goals/*.json; do python3 -m json.tool "$evidence_file" >/dev/null || exit $?; done, python3 -c 'import json, pathlib; [json.loads(line) for path in pathlib.Path("charness-artifacts/goals").glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]', python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- surface-obligations: Repo-owned changed-surface manifest that drives slice closeout obligations.
  source matches: .agents/surfaces.json
  verify: python3 scripts/validate_surfaces.py --repo-root .
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-06-020720-packet.json, charness-artifacts/critique/2026-08-06-020720-packet.md, charness-artifacts/critique/2026-08-06-021609-packet.json, charness-artifacts/critique/2026-08-06-021609-packet.md, charness-artifacts/critique/2026-08-06-022434-packet.json, charness-artifacts/critique/2026-08-06-022434-packet.md, charness-artifacts/critique/2026-08-06-030456-packet.json, charness-artifacts/critique/2026-08-06-030456-packet.md, charness-artifacts/critique/2026-08-06-031648-packet.json, charness-artifacts/critique/2026-08-06-031648-packet.md, charness-artifacts/critique/2026-08-06-032554-packet.json, charness-artifacts/critique/2026-08-06-032554-packet.md, charness-artifacts/critique/2026-08-06-033900-contract-final-packet.json, charness-artifacts/critique/2026-08-06-033900-contract-final-packet.md, charness-artifacts/critique/2026-08-06-036800-post-commit-ledger-packet.json, charness-artifacts/critique/2026-08-06-036800-post-commit-ledger-packet.md, charness-artifacts/critique/2026-08-06-040107-packet.json, charness-artifacts/critique/2026-08-06-040107-packet.md, charness-artifacts/critique/2026-08-06-041213-packet.json, charness-artifacts/critique/2026-08-06-041213-packet.md, charness-artifacts/critique/2026-08-06-041231-packet.json, charness-artifacts/critique/2026-08-06-041231-packet.md, charness-artifacts/critique/2026-08-06-041942-packet.json, charness-artifacts/critique/2026-08-06-041942-packet.md, charness-artifacts/critique/2026-08-06-050405-packet.json, charness-artifacts/critique/2026-08-06-050405-packet.md, charness-artifacts/critique/2026-08-06-close-all-open-issues-generative-sequence-goal-claims-review.md, charness-artifacts/critique/2026-08-06-post-push-operational-proof-runtime-evidence-closeout-claims-review.md, charness-artifacts/critique/2026-08-06-post-ratchet-ledger-packet.json, charness-artifacts/critique/2026-08-06-post-ratchet-ledger-packet.md, charness-artifacts/critique/2026-08-06-post-split-ledger-packet.json, charness-artifacts/critique/2026-08-06-post-split-ledger-packet.md, charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.json, charness-artifacts/critique/2026-08-06-slice-1-final-proof-v8-packet.md, charness-artifacts/critique/2026-08-06-slice-1-manifest-contract.md, charness-artifacts/critique/2026-08-06-slice-1-manifest-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-2-premise-contract.md, charness-artifacts/critique/2026-08-06-slice-2-premise-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-3-final-bundle-contract.md, charness-artifacts/critique/2026-08-06-slice-3-final-bundle-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.json, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-final-packet.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-packet.json, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review-packet.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-implementation-review.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-critique.md, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.json, charness-artifacts/critique/2026-08-06-slice-6-publish-state-ledger-spec-final-packet.md, charness-artifacts/critique/release-3-3-0-final-prepublish-v2-packet.json, charness-artifacts/critique/release-3-3-0-final-prepublish-v2-packet.md, charness-artifacts/critique/release-3-3-0-final-prepublish-v3-packet.json, charness-artifacts/critique/release-3-3-0-final-prepublish-v3-packet.md, charness-artifacts/critique/release-3-3-0-prepublish-packet.json, charness-artifacts/critique/release-3-3-0-prepublish-packet.md, charness-artifacts/critique/release-3-3-0-prepublish.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json, charness-artifacts/probe/2026-08-01-inventory-marker-rule.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-06-session-retro.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/boundary-bypass-exemptions.txt, plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_evidence.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/publish_state_ledger.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/check_premise_preflight.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_evidence.py, scripts/final_bundle_preflight_lib.py, scripts/premise_preflight_lib.py, scripts/publish_state_ledger.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py, tests/quality_gates/test_final_bundle_preflight.py, tests/quality_gates/test_premise_preflight.py, tests/quality_gates/test_publish_state_ledger.py, tests/quality_gates/test_slice_manifest.py
  derived matches: plugins/charness/scripts/check_premise_preflight.py, plugins/charness/scripts/final_bundle_preflight.py, plugins/charness/scripts/final_bundle_preflight_evidence.py, plugins/charness/scripts/final_bundle_preflight_lib.py, plugins/charness/scripts/premise_preflight_lib.py, plugins/charness/scripts/publish_state_ledger.py, plugins/charness/scripts/slice_manifest_lib.py, plugins/charness/scripts/validate_slice_manifest.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/check_premise_preflight.py, scripts/final_bundle_preflight.py, scripts/final_bundle_preflight_evidence.py, scripts/final_bundle_preflight_lib.py, scripts/premise_preflight_lib.py, scripts/publish_state_ledger.py, scripts/slice_manifest_lib.py, scripts/validate_slice_manifest.py
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

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section ok**: True

```text
# Reviewer-Packet Semantic Question

Use this question when a slice changes a guard, reference, claim, or verdict
surface. It keeps a reviewer packet anchored to what a reader or control must
know, rather than to the observable form that happened to expose the problem.

## Ask Before Broad Sampling

The packet author and reviewer should use all four parts when they apply. If a
part is not applicable or cannot be established, record `not applicable` or
`insufficient evidence` with the reason; do not silently claim the control is
proven.

1. **Semantic fact or invariant:** what must be true, independently of the
   current representation or failure spelling?
2. **Owning boundary:** which source, helper, renderer, reference, or workflow
   boundary carries or derives that fact, and who reads it?
3. **Recorded instance:** which concrete observed instance must this slice catch,
   explain, or preserve?
4. **Axis-varying counterexample:** what changes the semantic axis while keeping
   the observed form similar enough to expose a proxy-based control?

The question is a review aid, not a packet-readiness predicate. A clean tree is
not evidence that the selected control catches a recorded instance.

## Compare the Proposed Control

After naming the four parts, state the proposed predicate, claim, or surface
change and compare it with the counterexample:

- If the observed form changes while the semantic fact does not, reject or
  repair a control that changes its verdict with that form.
- If the semantic fact changes while the observed form stays similar, reject or
  repair a control that cannot distinguish the changed outcome.
- If the comparison cannot be made, record `unproven — defer`; do not approve it
  as though a clean-tree result were proof.
- For a behavior-changing helper or command, first record the bounded candidate
  search and scope. When that change has a reader-facing or copy-paste reference
  in scope, identify the first reader and verify that its demonstrated invocation
  preserves the claimed behavior. Disposition each discovered reference as
  updated, not applicable, or insufficient evidence with a reason. If no such
  reference is in scope, record `not applicable` with the search scope; if the
  reader cannot be checked, record `insufficient evidence` or `unproven — defer`
  rather than treating the helper's own tests as proof of reference safety.

These are reviewer dispositions, not an automated semantic gate.

## Decision Boundary

- Prefer a surface fix when the owning surface can carry or derive the semantic
  fact and prove the recorded instance.
- Keep the control as a reviewer question when the fact is judgment-bound or
  cannot be mechanically observed without guessing.
- Add a gate only when the predicate is mechanically observable, its false-fire
  cost is understood, and a recorded escape supports the addition.

This is a reviewer question, not a semantic meta-gate. It does not claim that a
host renders the packet, that a reviewer reaches the right judgment, or that a
clean-tree run proves the control.
```
