# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-24T18:21:21Z
- **Prepared for**: release 6.4.1 consumer-friction proof fixes
- **Changed ref**: `v6.4.0..HEAD`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `3ee0a55f5bfcf1ce1469a1bea71b5530c56568167ec689cc5d9eba8116bb9b96`
- **Reviewed paths**: 19
  - `.agents/release-adapter.yaml`
  - `scripts/artifact_referents.py`
  - `scripts/build_debug_seam_risk_index.py`
  - `scripts/check_skill_contracts.py`
  - `scripts/mutation_test_reporters.py`
  - `scripts/run_slice_closeout.py`
  - `scripts/slice_closeout_risk_interrupt.py`
  - `skills/public/achieve/scripts/goal_artifact_lifecycle.py`
  - `skills/public/achieve/scripts/goal_artifact_pursue.py`
  - `skills/public/critique/scripts/prepare_packet.py`
  - `skills/public/critique/scripts/verify_packet.py`
  - `skills/shared/scripts/reviewer_worker.py`
  - `skills/shared/scripts/run_reviewer_worker.py`
  - `tests/quality_gates/test_artifact_referents.py`
  - `tests/quality_gates/test_debug_seam_risk_index.py`
  - `tests/quality_gates/test_goal_artifact_pursue.py`
  - `tests/quality_gates/test_mutation_test_reporters.py`
  - `tests/quality_gates/test_reviewer_worker.py`
  - `tests/test_critique_verify_packet.py`
- **Auto-excluded paths**: 0

## Verify Packet

Run this exact command from the repository root:

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/2026-08-25-release-6-4-1-packet.json --packet-sha256 71f7ae3924f48db1a93806a1414be264887629324cc8e4e6366b82fb1ece2643 --identity-sha256 3ee0a55f5bfcf1ce1469a1bea71b5530c56568167ec689cc5d9eba8116bb9b96
```

Raw sha256sum is not the contract; the verifier owns the domain-separated packet identity check.
- **Sections**: 3
- **Shape validation ok**: True
- **Release approval**: not claimed

_This packet reports deterministic prepare-packet shape validation only; it is not a release-readiness or reviewer-verdict approval._

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- **Host exposure state**: `pending-parent-spawn`
- **Application state**: `unverified-by-packet`
- **Reviewer runner**: `backend=codex_exec, mode=file-backed-worker, timeout_seconds=900`
- **Instruction**: Review artifacts must record requested_fields_sent, metadata-hidden, host-defaulted, unsupported, or applied only when host-confirmed. Consume the worker receipt and delivery ledger; do not infer approval from a file or exit code.

Read this packet first. Then judge what the deterministic surface leaves uncovered before broad repo sampling.

## Changed Files And Owning Surfaces

- **Section id**: `changed-files-and-owning-surfaces`
- **Content kind**: `script`
- **Producer**: `python3 scripts/render_critique_section_changed_surfaces.py`
- **Section shape validation ok**: True

```text
Changed paths for ref `v6.4.0..HEAD`:
- charness-artifacts/critique/2026-08-24-consumer-friction-file-backed-work.md
- charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.json
- charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.md
- charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json
- charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.json
- charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json
- charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.json
- charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.json
- charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.json
- charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.md
- charness-artifacts/critique/2026-08-24-external-worker-capability-round2-resolution.md
- charness-artifacts/critique/2026-08-24-issue-689-resolution-critique.md
- charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.json
- charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.md
- charness-artifacts/critique/2026-08-24-issue-713-implementation-r1-packet.json
- charness-artifacts/critique/2026-08-24-issue-713-implementation-r1-packet.md
- charness-artifacts/critique/2026-08-24-issue-713-implementation-r2-packet.json
- charness-artifacts/critique/2026-08-24-issue-713-implementation-r2-packet.md
- charness-artifacts/critique/2026-08-24-issue-713-implementation.md
- charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.json
- charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.md
- charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.json
- charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.md
- charness-artifacts/critique/2026-08-24-issue-714-round2-packet.json
- charness-artifacts/critique/2026-08-24-issue-714-round2-packet.md
- charness-artifacts/critique/2026-08-24-issue-714-round2-resolution.md
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r1-packet.json
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r1-packet.md
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.json
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.md
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.json
- charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.md
- charness-artifacts/critique/2026-08-24-issues-690-691-round2-resolution.md
- charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.json
- charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.md
- charness-artifacts/critique/2026-08-24-packet-verifier-r1-packet.json
- charness-artifacts/critique/2026-08-24-packet-verifier-r1-packet.md
- charness-artifacts/critique/2026-08-24-packet-verifier-r2-packet.json
- charness-artifacts/critique/2026-08-24-packet-verifier-r2-packet.md
- charness-artifacts/critique/2026-08-24-packet-verifier-resolution-critique.md
- charness-artifacts/critique/2026-08-25-artifact-referent-uuid-identity-resolution.md
- charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r1-packet.json
- charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r1-packet.md
- charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.json
- charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.md
- charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.json
- charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.md
- charness-artifacts/critique/2026-08-25-debug-seam-index-round2-resolution.md
- charness-artifacts/critique/rounds/2026-08-24-issue713-r1-counterweight-retry.md
- charness-artifacts/critique/rounds/2026-08-24-issue713-r1-jackson.md
- charness-artifacts/critique/rounds/2026-08-24-issue713-r1-weinberg.md
- charness-artifacts/critique/rounds/2026-08-24-issue713-r2.md
- charness-artifacts/critique/workers/2026-08-24-counterweight-prompt.txt
- charness-artifacts/critique/workers/2026-08-24-counterweight-result.json
- charness-artifacts/critique/workers/2026-08-24-framing-prompt.txt
- charness-artifacts/critique/workers/2026-08-24-framing-result.json
- charness-artifacts/critique/workers/2026-08-24-integrity-prompt.txt
- charness-artifacts/critique/workers/2026-08-24-integrity-result.json
- charness-artifacts/critique/workers/2026-08-24-operator-prompt.txt
- charness-artifacts/critique/workers/2026-08-24-operator-result.json
- charness-artifacts/critique/workers/2026-08-24-post-repair-ledger.json
- charness-artifacts/critique/workers/2026-08-24-post-repair-prompt.txt
- charness-artifacts/critique/workers/2026-08-24-post-repair-receipt.json
- charness-artifacts/critique/workers/2026-08-24-post-repair-report.yaml
- charness-artifacts/critique/workers/2026-08-24-post-repair-result.json
- charness-artifacts/debug/2026-08-24-gh-auth-network-misclassification.md
- charness-artifacts/debug/2026-08-24-issue-689-node-tap-accounting.md
- charness-artifacts/debug/2026-08-24-issue-714.md
- charness-artifacts/debug/2026-08-24-issues-690-691-goal-readiness.md
- charness-artifacts/debug/2026-08-24-worker-boundary-identity-pattern.md
- charness-artifacts/debug/latest.md
- charness-artifacts/debug/seam-risk-index.json
- charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md
- charness-artifacts/ideation/2026-08-24-open-issue-consumer-friction-matrix.md
- charness-artifacts/impl/2026-08-24-external-worker-capability-envelope-first-slice.md
- charness-artifacts/metrics/rca-ledger.jsonl
- charness-artifacts/probe/2026-08-23-v6.4.0-release-observer.json
- charness-artifacts/quality/dup-ratchet-baseline.json
- charness-artifacts/quality/dup-review.json
- charness-artifacts/quality/sloc-inventory/latest.json
- charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.json
- charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.md
- charness-artifacts/release/latest.md
- charness-artifacts/retro/2026-08-23-v6-4-0-release-auto-retro.md
- charness-artifacts/retro/2026-08-24-151441-packet.json
- charness-artifacts/retro/2026-08-24-151441-packet.md
- charness-artifacts/retro/2026-08-25-consumer-friction-session-retro.md
- charness-artifacts/retro/2026-08-25-initial-consumer-friction-session-disposition.md
- charness-artifacts/retro/lesson-ledger.json
- charness-artifacts/retro/lesson-selection-index.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d99824.json
- charness-artifacts/retro/lesson-session-receipts/2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d99824.md
- charness-artifacts/retro/lesson-session-receipts/27605bc2-5cff-4ca0-a1e9-563dee69e9ba.json
- charness-artifacts/retro/lesson-session-receipts/27605bc2-5cff-4ca0-a1e9-563dee69e9ba.md
- charness-artifacts/retro/recent-lessons.md
- charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md
- charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md
- charness-artifacts/spec/2026-08-24-issue-689-node-tap-accounting.md
- charness-artifacts/spec/2026-08-24-issue-713-ceal-consumer-friction-p0.md
- charness-artifacts/spec/2026-08-24-issue-714-run-window.md
- charness-artifacts/spec/2026-08-24-issues-690-691-goal-readiness.md
- charness-artifacts/spec/2026-08-24-worker-boundary-identity-pattern.md
- plugins/charness/scripts/artifact_referents.py
- plugins/charness/scripts/build_debug_seam_risk_index.py
- plugins/charness/scripts/check_skill_contracts.py
- plugins/charness/scripts/critique_packet_lib.py
- plugins/charness/scripts/mutation_test_reporters.py
- plugins/charness/scripts/risk_interrupt_lib.py
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/slice_closeout_risk_interrupt.py
- plugins/charness/shared/references/bounded-review-result.schema.json
- plugins/charness/shared/scripts/reviewer_capability.py
- plugins/charness/shared/scripts/reviewer_capability_preflight.py
- plugins/charness/shared/scripts/reviewer_delivery.py
- plugins/charness/shared/scripts/reviewer_delivery_attempt.py
- plugins/charness/shared/scripts/reviewer_delivery_fields.py
- plugins/charness/shared/scripts/reviewer_delivery_schema.py
- plugins/charness/shared/scripts/reviewer_process.py
- plugins/charness/shared/scripts/reviewer_worker.py
- plugins/charness/shared/scripts/reviewer_worker_capability.py
- plugins/charness/shared/scripts/reviewer_worker_carrier_support.py
- plugins/charness/shared/scripts/reviewer_worker_report.py
- plugins/charness/shared/scripts/reviewer_worker_runtime.py
- plugins/charness/shared/scripts/run_reviewer_worker.py
- plugins/charness/skills/achieve/SKILL.md
- plugins/charness/skills/achieve/references/goal-artifact.md
- plugins/charness/skills/achieve/references/lifecycle-before.md
- plugins/charness/skills/achieve/scripts/goal_artifact_hollow_sections.py
- plugins/charness/skills/achieve/scripts/goal_artifact_lib.py
- plugins/charness/skills/achieve/scripts/goal_artifact_lifecycle.py
- plugins/charness/skills/achieve/scripts/goal_artifact_markdown.py
- plugins/charness/skills/achieve/scripts/goal_artifact_pursue.py
- plugins/charness/skills/critique/SKILL.md
- plugins/charness/skills/critique/references/prepare-packet.md
- plugins/charness/skills/critique/scripts/prepare_packet.py
- plugins/charness/skills/critique/scripts/verify_packet.py
- plugins/charness/skills/impl/SKILL.md
- plugins/charness/skills/quality/references/attention-state-visibility.json
- scripts/artifact_referents.py
- scripts/build_debug_seam_risk_index.py
- scripts/check_skill_contracts.py
- scripts/critique_packet_lib.py
- scripts/mutation_test_reporters.py
- scripts/risk_interrupt_lib.py
- scripts/run_slice_closeout.py
- scripts/slice_closeout_risk_interrupt.py
- skills/public/achieve/SKILL.md
- skills/public/achieve/references/goal-artifact.md
- skills/public/achieve/references/lifecycle-before.md
- skills/public/achieve/scripts/goal_artifact_hollow_sections.py
- skills/public/achieve/scripts/goal_artifact_lib.py
- skills/public/achieve/scripts/goal_artifact_lifecycle.py
- skills/public/achieve/scripts/goal_artifact_markdown.py
- skills/public/achieve/scripts/goal_artifact_pursue.py
- skills/public/critique/SKILL.md
- skills/public/critique/references/prepare-packet.md
- skills/public/critique/scripts/prepare_packet.py
- skills/public/critique/scripts/verify_packet.py
- skills/public/impl/SKILL.md
- skills/public/quality/references/attention-state-visibility.json
- skills/shared/references/bounded-review-result.schema.json
- skills/shared/scripts/reviewer_capability.py
- skills/shared/scripts/reviewer_capability_preflight.py
- skills/shared/scripts/reviewer_delivery.py
- skills/shared/scripts/reviewer_delivery_attempt.py
- skills/shared/scripts/reviewer_delivery_fields.py
- skills/shared/scripts/reviewer_delivery_schema.py
- skills/shared/scripts/reviewer_process.py
- skills/shared/scripts/reviewer_worker.py
- skills/shared/scripts/reviewer_worker_capability.py
- skills/shared/scripts/reviewer_worker_carrier_support.py
- skills/shared/scripts/reviewer_worker_report.py
- skills/shared/scripts/reviewer_worker_runtime.py
- skills/shared/scripts/run_reviewer_worker.py
- tests/charness_cli/test_goal_helpers.py
- tests/quality_gates/reviewer_capability_support.py
- tests/quality_gates/test_artifact_referents.py
- tests/quality_gates/test_debug_seam_risk_index.py
- tests/quality_gates/test_goal_artifact_backlog.py
- tests/quality_gates/test_goal_artifact_lifecycle.py
- tests/quality_gates/test_goal_artifact_pursue.py
- tests/quality_gates/test_goal_head_freshness.py
- tests/quality_gates/test_goal_hollow_sections.py
- tests/quality_gates/test_goal_superseded_status.py
- tests/quality_gates/test_issue_worker_carrier.py
- tests/quality_gates/test_mutation_test_reporters.py
- tests/quality_gates/test_reviewer_capability.py
- tests/quality_gates/test_reviewer_runner.py
- tests/quality_gates/test_reviewer_worker.py
- tests/quality_gates/test_reviewer_worker_capability.py
- tests/quality_gates/test_reviewer_worker_report.py
- tests/quality_gates/test_run_slice_closeout_review_obligations.py
- tests/quality_gates/test_run_slice_closeout_surface_obligations.py
- tests/quality_gates/test_skill_docs_contracts.py
- tests/quality_gates/test_slice_closeout_artifact_citations.py
- tests/test_critique_verify_packet.py
- tests/test_risk_interrupt.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/artifact_referents.py, scripts/build_debug_seam_risk_index.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/mutation_test_reporters.py, scripts/risk_interrupt_lib.py, scripts/run_slice_closeout.py, scripts/slice_closeout_risk_interrupt.py, skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/scripts/goal_artifact_hollow_sections.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_lifecycle.py, skills/public/achieve/scripts/goal_artifact_markdown.py, skills/public/achieve/scripts/goal_artifact_pursue.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/verify_packet.py, skills/public/impl/SKILL.md, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_capability.py, skills/shared/scripts/reviewer_capability_preflight.py, skills/shared/scripts/reviewer_delivery.py, skills/shared/scripts/reviewer_delivery_attempt.py, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_schema.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_capability.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  derived matches: plugins/charness/scripts/artifact_referents.py, plugins/charness/scripts/build_debug_seam_risk_index.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/mutation_test_reporters.py, plugins/charness/scripts/risk_interrupt_lib.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_risk_interrupt.py, plugins/charness/shared/references/bounded-review-result.schema.json, plugins/charness/shared/scripts/reviewer_capability.py, plugins/charness/shared/scripts/reviewer_capability_preflight.py, plugins/charness/shared/scripts/reviewer_delivery.py, plugins/charness/shared/scripts/reviewer_delivery_attempt.py, plugins/charness/shared/scripts/reviewer_delivery_fields.py, plugins/charness/shared/scripts/reviewer_delivery_schema.py, plugins/charness/shared/scripts/reviewer_process.py, plugins/charness/shared/scripts/reviewer_worker.py, plugins/charness/shared/scripts/reviewer_worker_capability.py, plugins/charness/shared/scripts/reviewer_worker_carrier_support.py, plugins/charness/shared/scripts/reviewer_worker_report.py, plugins/charness/shared/scripts/reviewer_worker_runtime.py, plugins/charness/shared/scripts/run_reviewer_worker.py, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/scripts/goal_artifact_hollow_sections.py, plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/goal_artifact_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_artifact_markdown.py, plugins/charness/skills/achieve/scripts/goal_artifact_pursue.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/verify_packet.py, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/quality/references/attention-state-visibility.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- rca-ledger-metrics: Committed RCA conversion ledger events and the validator/aggregator that keep the JSONL metric well-formed.
  source matches: charness-artifacts/metrics/rca-ledger.jsonl
  verify: python3 scripts/validate_rca_ledger.py --repo-root ., python3 scripts/aggregate_rca_ledger.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-24-consumer-friction-file-backed-work.md, charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.md, charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview.md, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-round2-resolution.md, charness-artifacts/critique/2026-08-24-issue-689-resolution-critique.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation.md, charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-issue-714-round2-packet.md, charness-artifacts/critique/2026-08-24-issue-714-round2-resolution.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-round2-resolution.md, charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-r1-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-r2-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-resolution-critique.md, charness-artifacts/critique/2026-08-25-artifact-referent-uuid-identity-resolution.md, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r1-packet.md, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.md, charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-25-debug-seam-index-round2-resolution.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-counterweight-retry.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-jackson.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-weinberg.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r2.md, charness-artifacts/debug/2026-08-24-gh-auth-network-misclassification.md, charness-artifacts/debug/2026-08-24-issue-689-node-tap-accounting.md, charness-artifacts/debug/2026-08-24-issue-714.md, charness-artifacts/debug/2026-08-24-issues-690-691-goal-readiness.md, charness-artifacts/debug/2026-08-24-worker-boundary-identity-pattern.md, charness-artifacts/debug/latest.md, charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md, charness-artifacts/ideation/2026-08-24-open-issue-consumer-friction-matrix.md, charness-artifacts/impl/2026-08-24-external-worker-capability-envelope-first-slice.md, charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.md, charness-artifacts/release/latest.md, charness-artifacts/retro/2026-08-23-v6-4-0-release-auto-retro.md, charness-artifacts/retro/2026-08-24-151441-packet.md, charness-artifacts/retro/2026-08-25-consumer-friction-session-retro.md, charness-artifacts/retro/2026-08-25-initial-consumer-friction-session-disposition.md, charness-artifacts/retro/lesson-session-receipts/2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d99824.md, charness-artifacts/retro/lesson-session-receipts/27605bc2-5cff-4ca0-a1e9-563dee69e9ba.md, charness-artifacts/retro/recent-lessons.md, charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md, charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md, charness-artifacts/spec/2026-08-24-issue-689-node-tap-accounting.md, charness-artifacts/spec/2026-08-24-issue-713-ceal-consumer-friction-p0.md, charness-artifacts/spec/2026-08-24-issue-714-run-window.md, charness-artifacts/spec/2026-08-24-issues-690-691-goal-readiness.md, charness-artifacts/spec/2026-08-24-worker-boundary-identity-pattern.md, skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/impl/SKILL.md
  derived matches: plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/impl/SKILL.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, python3 scripts/check_docs_graph.py --repo-root . || { [ "$?" -eq 3 ] && ! command -v awiki >/dev/null; }, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- quality-baseline-artifacts: Committed quality advisory and ratchet baselines must parse and match their owning inventories.
  source matches: charness-artifacts/quality/dup-ratchet-baseline.json, charness-artifacts/quality/dup-review.json
  verify: for quality_json in charness-artifacts/quality/nose-baseline.json charness-artifacts/quality/doc-nose-baseline.json charness-artifacts/quality/dup-ratchet-baseline.json charness-artifacts/quality/dup-review.json; do python3 -m json.tool "$quality_json" >/dev/null || exit $?; done, python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --detail >/dev/null, python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --detail >/dev/null, python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- operational-evidence-records: Durable issue, quality, and release evidence attachments produced by local planning and closeout workflows.
  source matches: charness-artifacts/quality/dup-ratchet-baseline.json, charness-artifacts/quality/dup-review.json, charness-artifacts/quality/sloc-inventory/latest.json, charness-artifacts/release/latest.md
  verify: python3 scripts/check_release_issue_ledger.py --repo-root . --ledger charness-artifacts/issues/2026-08-20-next-release-ledger.json, python3 scripts/validate_quality_artifact.py --repo-root ., ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- prompt-behavior-proof: Prompt-affecting instruction surfaces must follow deterministic Cautilus validation and on-demand proof policy.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/impl/SKILL.md, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bounded-review-result.schema.json
  verify: python3 scripts/validate_cautilus_proof.py --repo-root ., python3 scripts/validate_cautilus_diagnostics.py --repo-root .
- skill-packages: Public and support skill packages plus their helper scripts.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/scripts/goal_artifact_hollow_sections.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_lifecycle.py, skills/public/achieve/scripts/goal_artifact_markdown.py, skills/public/achieve/scripts/goal_artifact_pursue.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/verify_packet.py, skills/public/impl/SKILL.md, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_capability.py, skills/shared/scripts/reviewer_capability_preflight.py, skills/shared/scripts/reviewer_delivery.py, skills/shared/scripts/reviewer_delivery_attempt.py, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_schema.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_capability.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  derived matches: plugins/charness/shared/references/bounded-review-result.schema.json, plugins/charness/shared/scripts/reviewer_capability.py, plugins/charness/shared/scripts/reviewer_capability_preflight.py, plugins/charness/shared/scripts/reviewer_delivery.py, plugins/charness/shared/scripts/reviewer_delivery_attempt.py, plugins/charness/shared/scripts/reviewer_delivery_fields.py, plugins/charness/shared/scripts/reviewer_delivery_schema.py, plugins/charness/shared/scripts/reviewer_process.py, plugins/charness/shared/scripts/reviewer_worker.py, plugins/charness/shared/scripts/reviewer_worker_capability.py, plugins/charness/shared/scripts/reviewer_worker_carrier_support.py, plugins/charness/shared/scripts/reviewer_worker_report.py, plugins/charness/shared/scripts/reviewer_worker_runtime.py, plugins/charness/shared/scripts/run_reviewer_worker.py, plugins/charness/skills/achieve/SKILL.md, plugins/charness/skills/achieve/references/goal-artifact.md, plugins/charness/skills/achieve/references/lifecycle-before.md, plugins/charness/skills/achieve/scripts/goal_artifact_hollow_sections.py, plugins/charness/skills/achieve/scripts/goal_artifact_lib.py, plugins/charness/skills/achieve/scripts/goal_artifact_lifecycle.py, plugins/charness/skills/achieve/scripts/goal_artifact_markdown.py, plugins/charness/skills/achieve/scripts/goal_artifact_pursue.py, plugins/charness/skills/critique/SKILL.md, plugins/charness/skills/critique/references/prepare-packet.md, plugins/charness/skills/critique/scripts/prepare_packet.py, plugins/charness/skills/critique/scripts/verify_packet.py, plugins/charness/skills/impl/SKILL.md, plugins/charness/skills/quality/references/attention-state-visibility.json
  verify: python3 scripts/validate_skills.py --repo-root ., python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py skills/shared/scripts/*.py, python3 scripts/check_skill_ownership_overlap.py --repo-root ., python3 scripts/validate_skill_ergonomics.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary
- public-skill-policy: Public skill classification policy and validator that must stay aligned with the current public skill set.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/scripts/goal_artifact_hollow_sections.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_lifecycle.py, skills/public/achieve/scripts/goal_artifact_markdown.py, skills/public/achieve/scripts/goal_artifact_pursue.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/verify_packet.py, skills/public/impl/SKILL.md, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_capability.py, skills/shared/scripts/reviewer_capability_preflight.py, skills/shared/scripts/reviewer_delivery.py, skills/shared/scripts/reviewer_delivery_attempt.py, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_schema.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_capability.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  verify: python3 scripts/validate_public_skill_validation.py --repo-root .
- public-skill-dogfood: Checked-in consumer dogfood cases for public skills and the validator that keeps them aligned with current skill contracts.
  source matches: skills/public/achieve/SKILL.md, skills/public/achieve/references/goal-artifact.md, skills/public/achieve/references/lifecycle-before.md, skills/public/achieve/scripts/goal_artifact_hollow_sections.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_lifecycle.py, skills/public/achieve/scripts/goal_artifact_markdown.py, skills/public/achieve/scripts/goal_artifact_pursue.py, skills/public/critique/SKILL.md, skills/public/critique/references/prepare-packet.md, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/verify_packet.py, skills/public/impl/SKILL.md, skills/public/quality/references/attention-state-visibility.json, skills/shared/references/bounded-review-result.schema.json, skills/shared/scripts/reviewer_capability.py, skills/shared/scripts/reviewer_capability_preflight.py, skills/shared/scripts/reviewer_delivery.py, skills/shared/scripts/reviewer_delivery_attempt.py, skills/shared/scripts/reviewer_delivery_fields.py, skills/shared/scripts/reviewer_delivery_schema.py, skills/shared/scripts/reviewer_process.py, skills/shared/scripts/reviewer_worker.py, skills/shared/scripts/reviewer_worker_capability.py, skills/shared/scripts/reviewer_worker_carrier_support.py, skills/shared/scripts/reviewer_worker_report.py, skills/shared/scripts/reviewer_worker_runtime.py, skills/shared/scripts/run_reviewer_worker.py
  verify: python3 scripts/validate_public_skill_dogfood.py --repo-root .
- quality-inventory-artifacts: Checked-in quality inventory artifacts refreshed by local quality phases.
  source matches: charness-artifacts/quality/sloc-inventory/latest.json
  sync: python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- release-claims-review-evidence: Committed, machine-readable claims-review evidence that binds a prepared local release record before publication may resume.
  source matches: charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.json, charness-artifacts/release-review/2026-08-23-v6.4.0-round12-claims-review.md
  verify: for review_record in charness-artifacts/release-review/*.json; do [ -e "$review_record" ] && python3 -m json.tool "$review_record" >/dev/null || exit $?; done
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-24-consumer-friction-file-backed-work.md, charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.json, charness-artifacts/critique/2026-08-24-consumer-friction-lanes-premortem-packet.md, charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json, charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.json, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r2-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.json, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview-r4-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-envelope-rereview.md, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.json, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.json, charness-artifacts/critique/2026-08-24-external-worker-capability-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.json, charness-artifacts/critique/2026-08-24-external-worker-capability-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-external-worker-capability-round2-resolution.md, charness-artifacts/critique/2026-08-24-issue-689-resolution-critique.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.json, charness-artifacts/critique/2026-08-24-issue-713-implementation-final-cap-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-r1-packet.json, charness-artifacts/critique/2026-08-24-issue-713-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation-r2-packet.json, charness-artifacts/critique/2026-08-24-issue-713-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-issue-713-implementation.md, charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.json, charness-artifacts/critique/2026-08-24-issue-714-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.json, charness-artifacts/critique/2026-08-24-issue-714-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-issue-714-round2-packet.json, charness-artifacts/critique/2026-08-24-issue-714-round2-packet.md, charness-artifacts/critique/2026-08-24-issue-714-round2-resolution.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r1-packet.json, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r1-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.json, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.json, charness-artifacts/critique/2026-08-24-issues-690-691-implementation-r2-packet.md, charness-artifacts/critique/2026-08-24-issues-690-691-round2-resolution.md, charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.json, charness-artifacts/critique/2026-08-24-packet-verifier-final-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-r1-packet.json, charness-artifacts/critique/2026-08-24-packet-verifier-r1-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-r2-packet.json, charness-artifacts/critique/2026-08-24-packet-verifier-r2-packet.md, charness-artifacts/critique/2026-08-24-packet-verifier-resolution-critique.md, charness-artifacts/critique/2026-08-25-artifact-referent-uuid-identity-resolution.md, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r1-packet.json, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r1-packet.md, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.json, charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.md, charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.json, charness-artifacts/critique/2026-08-25-debug-seam-index-r2-cap-final-packet.md, charness-artifacts/critique/2026-08-25-debug-seam-index-round2-resolution.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-counterweight-retry.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-jackson.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r1-weinberg.md, charness-artifacts/critique/rounds/2026-08-24-issue713-r2.md, charness-artifacts/critique/workers/2026-08-24-counterweight-prompt.txt, charness-artifacts/critique/workers/2026-08-24-counterweight-result.json, charness-artifacts/critique/workers/2026-08-24-framing-prompt.txt, charness-artifacts/critique/workers/2026-08-24-framing-result.json, charness-artifacts/critique/workers/2026-08-24-integrity-prompt.txt, charness-artifacts/critique/workers/2026-08-24-integrity-result.json, charness-artifacts/critique/workers/2026-08-24-operator-prompt.txt, charness-artifacts/critique/workers/2026-08-24-operator-result.json, charness-artifacts/critique/workers/2026-08-24-post-repair-ledger.json, charness-artifacts/critique/workers/2026-08-24-post-repair-prompt.txt, charness-artifacts/critique/workers/2026-08-24-post-repair-receipt.json, charness-artifacts/critique/workers/2026-08-24-post-repair-report.yaml, charness-artifacts/critique/workers/2026-08-24-post-repair-result.json
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-23-v6.4.0-release-observer.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- debug-seam-risk-index: Generated source-linked index over debug artifact seam-risk fields.
  source matches: charness-artifacts/debug/2026-08-24-gh-auth-network-misclassification.md, charness-artifacts/debug/2026-08-24-issue-689-node-tap-accounting.md, charness-artifacts/debug/2026-08-24-issue-714.md, charness-artifacts/debug/2026-08-24-issues-690-691-goal-readiness.md, charness-artifacts/debug/2026-08-24-worker-boundary-identity-pattern.md, charness-artifacts/debug/latest.md, scripts/build_debug_seam_risk_index.py
  derived matches: charness-artifacts/debug/seam-risk-index.json
  sync: python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
  verify: python3 scripts/build_debug_seam_risk_index.py --repo-root . --check
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-23-v6-4-0-release-auto-retro.md, charness-artifacts/retro/2026-08-24-151441-packet.json, charness-artifacts/retro/2026-08-24-151441-packet.md, charness-artifacts/retro/2026-08-25-consumer-friction-session-retro.md, charness-artifacts/retro/2026-08-25-initial-consumer-friction-session-disposition.md, charness-artifacts/retro/lesson-session-receipts/2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d99824.md, charness-artifacts/retro/lesson-session-receipts/27605bc2-5cff-4ca0-a1e9-563dee69e9ba.md, charness-artifacts/retro/recent-lessons.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- lesson-ledger-and-contract-register: Local cited lesson state and the explicit pre-contract-mutation register probe.
  source matches: charness-artifacts/retro/lesson-ledger.json, charness-artifacts/retro/lesson-session-receipts/2026-08-24-01a032f5-c64c-7ad2-a838-8eb738d99824.json, charness-artifacts/retro/lesson-session-receipts/27605bc2-5cff-4ca0-a1e9-563dee69e9ba.json
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/check_lesson_ledger.py --repo-root ., python3 scripts/check_contract_register.py --repo-root ., python3 -m pytest -q tests/test_lesson_ledger.py tests/test_lesson_lifecycle.py tests/test_contract_register.py
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/artifact_referents.py, plugins/charness/scripts/build_debug_seam_risk_index.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/mutation_test_reporters.py, plugins/charness/scripts/risk_interrupt_lib.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_risk_interrupt.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root ., python3 scripts/update_tools.py --repo-root .
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/artifact_referents.py, scripts/build_debug_seam_risk_index.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/mutation_test_reporters.py, scripts/risk_interrupt_lib.py, scripts/run_slice_closeout.py, scripts/slice_closeout_risk_interrupt.py, tests/charness_cli/test_goal_helpers.py, tests/quality_gates/reviewer_capability_support.py, tests/quality_gates/test_artifact_referents.py, tests/quality_gates/test_debug_seam_risk_index.py, tests/quality_gates/test_goal_artifact_backlog.py, tests/quality_gates/test_goal_artifact_lifecycle.py, tests/quality_gates/test_goal_artifact_pursue.py, tests/quality_gates/test_goal_head_freshness.py, tests/quality_gates/test_goal_hollow_sections.py, tests/quality_gates/test_goal_superseded_status.py, tests/quality_gates/test_issue_worker_carrier.py, tests/quality_gates/test_mutation_test_reporters.py, tests/quality_gates/test_reviewer_capability.py, tests/quality_gates/test_reviewer_runner.py, tests/quality_gates/test_reviewer_worker.py, tests/quality_gates/test_reviewer_worker_capability.py, tests/quality_gates/test_reviewer_worker_report.py, tests/quality_gates/test_run_slice_closeout_review_obligations.py, tests/quality_gates/test_run_slice_closeout_surface_obligations.py, tests/quality_gates/test_skill_docs_contracts.py, tests/quality_gates/test_slice_closeout_artifact_citations.py, tests/test_critique_verify_packet.py, tests/test_risk_interrupt.py
  derived matches: plugins/charness/scripts/artifact_referents.py, plugins/charness/scripts/build_debug_seam_risk_index.py, plugins/charness/scripts/check_skill_contracts.py, plugins/charness/scripts/critique_packet_lib.py, plugins/charness/scripts/mutation_test_reporters.py, plugins/charness/scripts/risk_interrupt_lib.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_risk_interrupt.py
  verify: ./scripts/check-python-lint.sh, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/artifact_referents.py, scripts/build_debug_seam_risk_index.py, scripts/check_skill_contracts.py, scripts/critique_packet_lib.py, scripts/mutation_test_reporters.py, scripts/risk_interrupt_lib.py, scripts/run_slice_closeout.py, scripts/slice_closeout_risk_interrupt.py, skills/public/achieve/scripts/goal_artifact_hollow_sections.py, skills/public/achieve/scripts/goal_artifact_lib.py, skills/public/achieve/scripts/goal_artifact_lifecycle.py, skills/public/achieve/scripts/goal_artifact_markdown.py, skills/public/achieve/scripts/goal_artifact_pursue.py, skills/public/critique/scripts/prepare_packet.py, skills/public/critique/scripts/verify_packet.py
  verify: python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root . --require-empty --require-git-file-listing

Planned sync commands before validators:
- python3 scripts/sync_root_plugin_manifests.py --repo-root .
- python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . --output charness-artifacts/quality/sloc-inventory/latest.json
- python3 scripts/build_debug_seam_risk_index.py --repo-root . --write
- python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
```

## Non-Goals For This Contract

- **Section id**: `critique-prepare-non-goals`
- **Content kind**: `static`
- **Producer**: `static-config (inline)`
- **Section shape validation ok**: True

```text
- Charness does not classify section roles (source/derived/audit-only/rewrite). Roles stay consumer-defined.
- Charness does not enforce packet content correctness — the validator owns shape only.
- Retro owns its own prepare-packet slot through retro-adapter.yaml packet_sections; critique packets do not substitute for retro lesson judgment.
```

## Semantic Reviewer Question

- **Section id**: `reviewer-packet-semantic-question`
- **Content kind**: `static`
- **Producer**: `static-config (content_path: skills/shared/references/reviewer-packet-semantic-question.md)`
- **Section shape validation ok**: True

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
