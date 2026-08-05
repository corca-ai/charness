# Critique Prepare Packet — charness

- **Kind**: `charness.critique_prepare_packet` (v1)
- **Generated**: 2026-08-05T00:25:42Z
- **Prepared for**: 2026-08-05-proof-claims-final-claims-review
- **Changed ref**: `origin/main..480dc537`
- **Adapter**: `.agents/critique-adapter.yaml`
- **Reviewed input identity**: `6b6b56a0dcf52401b07d7b720adbbb69058c01af9ca7e09adc865c7f71092dd2`
- **Reviewed paths**: 5
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
Changed paths for ref `origin/main..480dc537`:
- charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md
- charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-boundary-receipt.json
- charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-critique.md
- charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-packet.json
- charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-packet.md
- charness-artifacts/critique/2026-08-05-proof-claims-final-claims-review.md
- charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-boundary-receipt.json
- charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.json
- charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.md
- charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md
- charness-artifacts/critique/2026-08-05-slice-b-proof-receipt.md
- charness-artifacts/critique/broader-proof-claims-goal-packet.json
- charness-artifacts/critique/broader-proof-claims-goal-packet.md
- charness-artifacts/critique/proof-claims-final-packet.json
- charness-artifacts/critique/proof-claims-final-packet.md
- charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md
- charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md
- charness-artifacts/issue/2026-08-05-issue-506-local-disposition.md
- charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json
- charness-artifacts/probe/2026-08-01-inventory-marker-rule.json
- charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json
- charness-artifacts/quality/2026-08-05-proof-claims.md
- charness-artifacts/quality/latest.md
- charness-artifacts/retro/2026-08-04-235906-packet.json
- charness-artifacts/retro/2026-08-04-235906-packet.md
- charness-artifacts/retro/2026-08-05-proof-claims-goal-retro.md
- charness-artifacts/retro/lesson-selection-index.json
- docs/deferred-decisions.md
- docs/handoff.md
- plugins/charness/scripts/proof_receipt.py
- plugins/charness/scripts/run-quality.sh
- plugins/charness/scripts/run_slice_closeout.py
- plugins/charness/scripts/slice_closeout_reporting.py
- plugins/charness/scripts/validate_inventory_consumption.py
- scripts/proof_receipt.py
- scripts/run-quality.sh
- scripts/run_slice_closeout.py
- scripts/slice_closeout_reporting.py
- scripts/validate_inventory_consumption.py
- tests/quality_gates/support.py
- tests/quality_gates/test_proof_receipt.py
- tests/quality_gates/test_quality_runner.py
- tests/quality_gates/test_quality_runner_runtime_aggregate.py
- tests/quality_gates/test_run_slice_closeout_surface_obligations.py
- tests/quality_gates/test_slice_closeout_broad_gate.py

Owning surfaces:
- checked-in-plugin-export: Checked-in plugin install surface and root marketplace artifacts derived from repo-owned source paths.
  source matches: scripts/proof_receipt.py, scripts/run-quality.sh, scripts/run_slice_closeout.py, scripts/slice_closeout_reporting.py, scripts/validate_inventory_consumption.py
  derived matches: plugins/charness/scripts/proof_receipt.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_reporting.py, plugins/charness/scripts/validate_inventory_consumption.py
  sync: python3 scripts/sync_root_plugin_manifests.py --repo-root .
  verify: python3 scripts/validate_packaging.py --repo-root ., python3 scripts/validate_packaging_committed.py --repo-root .
- repo-markdown: Repo-owned markdown docs and generated markdown copies that need link, lint, and secret checks.
  source matches: charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-critique.md, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-packet.md, charness-artifacts/critique/2026-08-05-proof-claims-final-claims-review.md, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.md, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md, charness-artifacts/critique/2026-08-05-slice-b-proof-receipt.md, charness-artifacts/critique/broader-proof-claims-goal-packet.md, charness-artifacts/critique/proof-claims-final-packet.md, charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md, charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md, charness-artifacts/issue/2026-08-05-issue-506-local-disposition.md, charness-artifacts/quality/2026-08-05-proof-claims.md, charness-artifacts/quality/latest.md, charness-artifacts/retro/2026-08-04-235906-packet.md, charness-artifacts/retro/2026-08-05-proof-claims-goal-retro.md, docs/deferred-decisions.md, docs/handoff.md
  verify: python3 scripts/check_doc_links.py --repo-root ., python3 scripts/check_command_docs.py --repo-root ., python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing, ./scripts/check-markdown.sh, ./scripts/check-secrets.sh
- critique-artifacts: Checked-in critique records and prepare packets for task-completing repo work.
  source matches: charness-artifacts/critique/2026-08-05-broader-proof-claims-goal-pre-mortem.md, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-boundary-receipt.json, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-critique.md, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-packet.json, charness-artifacts/critique/2026-08-05-handoff-proof-verdict-goal-packet.md, charness-artifacts/critique/2026-08-05-proof-claims-final-claims-review.md, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-boundary-receipt.json, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.json, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.md, charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique.md, charness-artifacts/critique/2026-08-05-slice-b-proof-receipt.md, charness-artifacts/critique/broader-proof-claims-goal-packet.json, charness-artifacts/critique/broader-proof-claims-goal-packet.md, charness-artifacts/critique/proof-claims-final-packet.json, charness-artifacts/critique/proof-claims-final-packet.md
  verify: python3 scripts/validate_critique_artifacts.py --repo-root . --all
- probe-artifacts: Checked-in host/runtime probe JSON artifacts used as closeout evidence.
  source matches: charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json, charness-artifacts/probe/2026-08-01-inventory-marker-rule.json, charness-artifacts/probe/2026-08-05-f29009bd-remote-check-readback.json
  verify: for path in charness-artifacts/probe/*.json; do python3 -m json.tool "$path" >/dev/null || exit $?; done
- retro-lesson-selection-index: Durable retro prepare packets and generated advisory index for source-linked retro lesson digest selection.
  source matches: charness-artifacts/retro/2026-08-04-235906-packet.json, charness-artifacts/retro/2026-08-04-235906-packet.md, charness-artifacts/retro/2026-08-05-proof-claims-goal-retro.md
  derived matches: charness-artifacts/retro/lesson-selection-index.json
  sync: python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write
  verify: for retro_packet_json in charness-artifacts/retro/*-packet.json; do if [ -e "$retro_packet_json" ]; then python3 -m json.tool "$retro_packet_json" >/dev/null || exit $?; fi; done, python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check
- integrations-and-control-plane: Integration manifests and control-plane helper scripts.
  derived matches: plugins/charness/scripts/proof_receipt.py, plugins/charness/scripts/run-quality.sh, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_reporting.py, plugins/charness/scripts/validate_inventory_consumption.py
  verify: python3 scripts/validate_integrations.py --repo-root ., python3 scripts/sync_support.py --repo-root . --json, python3 scripts/update_tools.py --repo-root . --json
- repo-python: Repo-owned Python code and tests.
  source matches: scripts/proof_receipt.py, scripts/run_slice_closeout.py, scripts/slice_closeout_reporting.py, scripts/validate_inventory_consumption.py, tests/quality_gates/support.py, tests/quality_gates/test_proof_receipt.py, tests/quality_gates/test_quality_runner.py, tests/quality_gates/test_quality_runner_runtime_aggregate.py, tests/quality_gates/test_run_slice_closeout_surface_obligations.py, tests/quality_gates/test_slice_closeout_broad_gate.py
  derived matches: plugins/charness/scripts/proof_receipt.py, plugins/charness/scripts/run_slice_closeout.py, plugins/charness/scripts/slice_closeout_reporting.py, plugins/charness/scripts/validate_inventory_consumption.py
  verify: ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts, python3 scripts/check_python_lengths.py --repo-root . --require-git-file-listing, python3 scripts/validate_attention_state_visibility.py --repo-root . --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support, python3 scripts/check_test_repo_copy_invariants.py --repo-root ., python3 scripts/check_boundary_bypass_ratchet.py --repo-root ., python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary, ./scripts/check-shell.sh, python3 scripts/run_standing_pytest.py --repo-root . --mode read-only
- python-scan-hygiene: Repo and skill Python that traverses the filesystem must stay gitignore-aware, so a committed non-gitignore-aware scanner does not ship latent until the next push.
  source matches: scripts/proof_receipt.py, scripts/run_slice_closeout.py, scripts/slice_closeout_reporting.py, scripts/validate_inventory_consumption.py
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
