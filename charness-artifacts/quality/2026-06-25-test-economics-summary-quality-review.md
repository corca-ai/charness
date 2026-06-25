# Quality Review
Date: 2026-06-25

## Scope

Target boundary: repo-wide quality slice for test-economics inventory token
efficiency; no single public skill target.

Ambient repo findings: existing `hitl` / `narrative` doc duplicate advisory and
Python near-limit warnings are not caused by this slice. The prior pytest xdist
worker cap from `19899869` remains in place and is not re-claimed here.

## Current Gates

- `./scripts/run-quality.sh --read-only` passed 79/79 after the slice.
- `pytest -q tests/quality_gates/test_standing_test_economics.py`
  passed 9 tests in 3.03s.
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
  passed after replacing the new `_pick` helper clone with inline selection.
- `python3 scripts/doctor.py --repo-root . --json --tool-id nose` reported
  `nose` observed/latest `0.15.0`, status `current`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  `pytest` 27.7s latest / 26.4s median, `check-coverage` 18.7s latest /
  19.0s median, and legacy `check-duplicates` 10.0s latest / 11.9s median.
- coverage gate: `./scripts/run-quality.sh --read-only` passed 79/79; changed-line
  mutation coverage still warns until the producer refresh runs for the committed
  range.
- evaluator depth: deterministic gates only. No Cautilus run was in scope
  because this slice changed helper output shape, not a prompt behavior claim
  needing evaluator-backed proof.

## Healthy

- `inventory_standing_test_economics.py --summary` now emits compact triage JSON:
  `test_file_count`, `nested_cli_file_count`, `runner_snippets`,
  `nested_cli_files_sample`, `pytest_temp_footprint`, `findings`, and
  `interpretation`.
- Token payload probe on this repo: summary output 4,531 bytes versus 11,763
  bytes for full `--json`.
- Full attribution remains available through `--json`; summary carries an
  explicit note that it is triage output and points reviewers to `--json` for
  full `nested_cli_files`.
- The focused test asserts that advisory `findings` survive summary mode, so
  compact output does not hide the key Weak/Advisory-like signal.

## Weak

- Summary mode is a triage surface, not a full attribution source. A reviewer
  using only summary can see a 10-file nested CLI sample and counts, but not the
  full `nested_cli_files` tail.
- Runtime and payload-size gains were measured on this checkout and this
  repository state; other repos with fewer nested CLI files will see a smaller
  absolute token reduction.

## Missing

- No missing deterministic gate is justified by this slice. Existing
  `validate-inventory-consumption*`, `validate-inference-interpretation`, and
  `dup-ratchet` covered the changed contract.

## Deferred

- Existing nested CLI fanout remains a real test-economics advisory; this slice
  made the inventory cheaper to consume and did not convert subprocess tests to
  in-process seams.
- The ambient `hitl` / `narrative` doc duplicate advisory remains a separate
  quality follow-up.

## Advisory

- structural review result: command:
  `plan_quality_run.py --repo-root . --json`; the next structural move was a
  helper-owned compact packet, not another broad test change.
- prose review result: command:
  `inventory_standing_test_economics.py --repo-root . --summary`; summary engages
  `test_file_count`, `nested_cli_file_count`, and `runner_snippets`, while the
  full path remains `--json`.
- runtime interpretation: command: `render_runtime_summary.py --repo-root . --json`;
  `pytest` is still a hot spot, but this loop selected the cheaper agent-token
  waste because prior xdist work already moved the main pytest runtime.
- dup-ratchet interpretation: the initial helper shape created a new `_pick`
  clone family; it was removed instead of accepted into baseline.
- dogfood decision: command:
  `suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`;
  `quality` remains `hitl-recommended`, the checked-in dogfood case already
  covers artifact behavior, and Cautilus planner did not request evaluator
  execution.
- fresh-eye review result: bounded reviewers `019efe2e-956e-7352-8c4b-31ddcf5af38f`,
  `019efe2e-a795-7ff3-af71-238dfc5588be`, and
  `019efe2e-b986-7093-82f5-c89132969458` found no blockers. Non-blocking notes
  drove the explicit summary note and findings-preservation assertion.

## Delegated Review

- Delegated Review: executed — token-efficiency/output-contract reviewer
  `019efe2e-956e-7352-8c4b-31ddcf5af38f`, validation/packaging reviewer
  `019efe2e-a795-7ff3-af71-238dfc5588be`, and counterweight reviewer
  `019efe2e-b986-7093-82f5-c89132969458`.
- Reviewer-tier evidence: requested bounded fresh-eye review under repo
  `Subagent Delegation`; host exposed `multi_agent_v1.spawn_agent`, requested
  fields sent as host-default reviewer tasks, applied model details hidden.

## Commands Run

- `python3 skills/public/quality/scripts/resolve_adapter.py --repo-root .`
- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --summary`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 scripts/doctor.py --repo-root . --json --tool-id nose`
- `pytest -q tests/quality_gates/test_standing_test_economics.py`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_inference_interpretation.py --repo-root . --require-git-file-listing`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- `./scripts/run-quality.sh --read-only`

## Recommended Next Gates

- active none — the compact summary contract is covered by focused tests and the
  existing broad quality gate.
- passive keep converting nested CLI fanout to in-process seams because the
  inventory still reports 150 nested CLI files.
- passive keep the ambient doc duplicate advisory until a docs/skill prose
  cleanup slice can classify or remove that family.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
