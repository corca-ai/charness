# Quality Review
Date: 2026-08-05
Title: Issue 511 Nose Inventory Scope

## Scope

Target boundary: `inventory_nose_clones.py` scope validity, adapter-owned roots,
and `run-quality.sh` receipt semantics.

Ambient repo findings: broad quality, changed-line mutation, and remote CI are
separate closeout evidence; no Cautilus evaluation was run under its ask-before-run contract.

## Current Gates

Focused producer/consumer tests, adapter resolution, inventory declarations,
source/plugin parity, lint, shellcheck, the D47 probe refresh, and the locked
closeout packet are the current deterministic gates. Broad pytest and fresh
mutation coverage are green, but the first committed-range changed-line producer
found three uncovered changed surfaces; targeted coverage repairs are now in the
worktree and the final producer must be rerun. Remote CI remains required before
issue close.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`; no fresh timing capture was required for this focused scope slice. <!-- reproduction-source -->
- runtime hot spots: not measured; focused proof is subprocess and test-suite output.
- coverage gate: focused tests and locked broad pytest passed; the first committed-range mutation consumer identified concrete uncovered lines, and the repair suite is green while the final changed-line proof remains pending.
- evaluator depth: deterministic-gates-only; Cautilus was not invoked under its ask-before-run contract.

## Healthy

- Existing Charness roots remain the default fallback, while absent roots are
  disclosed and never passed to `nose`.
- JSON and summary carry `scope_status`, requested/scanned/missing paths, query
  diagnostics, and the wrapper exit code.
- Only `PASS` phases enter measured receipt scope; unproven inventory states are
  rendered `UNPROVEN`.
- Source and checked-in plugin mirrors were regenerated together.
- Pre-lock closeout completed after the scope library and adapter-validator splits;
  the duplicate-ratchet gate is clean with the seven initial and eight split-family
  classifications recorded in `charness-artifacts/quality/dup-review.json`.
- Locked closeout completed: broad pytest passed in the mutation-instrumented run,
  and all structural, packaging, probe, and inference gates passed.
- The inventory-marker and companion consumption-floor probes were refreshed after
  the #511 declaration change; the dedicated D47 pinning suite passed 60 tests.
- The post-commit mutation consumer named three changed quality surfaces and their
  exact uncovered lines; the repair adds in-process scope/receipt coverage and
  adapter-validator edge assertions without changing the gate.

## Weak

- Private consumer repositories, installed caches, and provider roundtrips are
  not observable here; fixtures prove the reconstructed contract only.

## Missing

- Final changed-line mutation coverage is pending the repair producer; the first
  committed-range run correctly blocked three files instead of accepting a false
  green.
- Remote CI and an independent GitHub readback remain pending.

## Deferred

- Generalizing scope fields across every quality inventory is deferred.
- A broader `dup_ratchet_scan.py` redesign is deferred; its configured scope is
  a separate contract.

## Advisory

- structural review result: command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .`; the target needs explicit scope/completion signals, not a new duplication floor.
- prose review result: `inventory-dispatch.md` and `adapter-contract.md` now own the progressive disclosure for alternate roots and partial scans.
- inventory evidence: `inventory_nose_clones.py --summary` exposes `scope_status`, `requested_paths`, `scanned_paths`, `missing_paths`, `cli_exit_code`, and `stderr`; consumers must answer the scope fields before treating clone counts as evidence.
- proof-surface disposition: `skills/public/quality/scripts/nose_inventory_scope_lib.py` is a verdict-producing scope/receipt helper; its path-specific fresh-eye disposition is recorded in the resolution critique.

## Public-skill Review

- Dogfood case reviewed: `docs/public-skill-dogfood.json` quality row. Its maintained slow-gate prompt and `quality` artifact contract are unchanged by this producer/receipt repair; the issue-specific scope matrix is deterministic evidence for the new behavior.
- Decision: no Cautilus run and no scenario-registry mutation. The planner reports `run_mode: ask`, `status: not-required`, with no next action; deterministic validators, focused tests, and the bounded fresh-eye packet own this slice.

## Delegated Review

- Delegated Review: executed — causal review `019fd10a`, contract critique `019fd112`, implementation round 1 `019fd11e`, and repaired-surface round 2 `019fd122` were unnamed bounded fresh-eye reviews; boundaries were verified clean. Round 2 found one Windows-root repair, fixed afterward and recorded accepted-unreviewed under the two-round cap. The required length-gate refactors were owner-verified afterward; no third review is claimed.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not re-delegated; this slice targeted a focused producer/receipt proof surface.

## Commands Run

- python3 -m pytest tests/quality_gates/test_quality_nose_advisory.py tests/test_nose_inprocess_coverage.py tests/quality_gates/test_quality_adapter_block_rejections.py tests/quality_gates/test_quality_runner.py tests/quality_gates/test_quality_runner_nose_scope.py tests/quality_gates/test_quality_runner_runtime_aggregate.py — 174 passed.
- `ruff check` on changed Python files; `shellcheck` on source/plugin runners.
- `python3 scripts/validate_inventory_consumption_declaration.py --repo-root .` and `python3 scripts/check_inventory_declaration_coverage.py --repo-root .` — passed.
- `python3 scripts/export_plugin.py --repo-root . --host codex --output-root . --with-marketplace`; plugin imports, references, and links — passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review` — pre-lock completed; all deterministic checks passed, broad pytest intentionally deferred to the locked run.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary` — clean after bounded intentional-family review.
- python3 -m pytest tests/quality_gates/test_a_declaration_is_not_its_own_corroboration.py tests/test_inventory_marker_rule_measurement.py — 60 passed after refreshing both pinned probes and D47.
- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock --produce-mutation-coverage --ack-cautilus-skill-review` — completed; broad pytest, fresh mutation coverage, and deterministic gates passed.
- `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha origin/main --reuse-coverage --require-fresh-coverage --allow-dirty` — exit 3, explicitly unverified because five mutation-pool files remain uncommitted; no changed-line claim made.
- `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha origin/main --reuse-coverage --require-fresh-coverage` — first committed-range run blocked `adapter_validators.py`, `inventory_nose_clones.py`, and `nose_inventory_scope_lib.py` at the exact lines recorded in its JSON payload.
- python3 -m pytest tests/quality_gates/test_quality_nose_scope_inprocess.py tests/quality_gates/test_quality_adapter_block_rejections.py tests/quality_gates/test_quality_nose_advisory.py tests/test_nose_inprocess_coverage.py tests/quality_gates/test_quality_runner_nose_scope.py — 136 passed after the coverage repair.
- Targeted mutant proof: inverted `nose_inventory_scope_lib.py:232` from `return 1` to `return 0`; `test_quality_nose_scope_inprocess.py::test_error_exit_code_is_nonzero` failed (`assert 0 == 1`), then the exact line was restored. No gate was weakened.

## Recommended Next Quality Moves

- active — capability_needed=final changed-line proof after the coverage repair; next_center=closeout verification; transformation=run the committed-range producer, commit the repair bundle, rerun the consumer, push through the pre-push gate, and read back remote CI; proof_boundary=remote CI plus GitHub issue readback; enforcement_posture=existing-gate-reuse.
- passive — capability_needed=private consumer roundtrip because the repository is unavailable; next_center=consumer fixture; transformation=repeat the scope matrix when available; proof_boundary=consumer readback; enforcement_posture=no-gate because local evidence cannot claim private behavior.

## History

- [Previous quality review](history/2026-07-19-portable-proof-path-learning-review.md)
