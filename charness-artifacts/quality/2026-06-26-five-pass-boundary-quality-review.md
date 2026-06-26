# Quality Review
Date: 2026-06-26

## Scope

Target boundary: five-plus repeated subprocess/script execution assertions in
find-skills, integration validation, and docs/misc quality tests.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, Python
warn-band files, and the larger nested-CLI backlog are not fully fixed here.

## Current Gates

- Focused pytest passed 50 tests across find-skills, control-plane validation,
  and docs/misc quality coverage.
- Boundary-bypass ratchet passed after the conversion and after restoring two
  operator-facing CLI proofs that fresh-eye found were unique.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 29.0s latest / 25.6s median, budget 140.0s;
  `check-coverage` 18.4s latest / 18.9s median, budget 55.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout pending at draft time.
- evaluator depth: deterministic gates only; `plan_cautilus_proof.py` returned
  `next_action: none`, so no Cautilus run was allowed or needed.

## Healthy

- `tests/test_find_skills_shadowing.py` now drives `list_capabilities.main()`
  in-process for local-vs-trusted shadowing and duplicate trusted-id behavior.
- `tests/test_find_skills_synced_support.py` now drives
  `list_capabilities.main()` in-process for synced support and discovery-stub
  cross-link behavior.
- `tests/control_plane/test_integrations_validation.py` now tests four
  integration manifest validation failures through direct validator functions
  instead of launching `validate_integrations.py` four times.
- `tests/quality_gates/test_docs_and_misc.py` now uses in-process script main
  calls for list-capabilities trusted-root behavior and impl verification
  survey JSON behavior.
- Fresh-eye found two over-conversions; the final slice restored the only known
  real CLI proofs for setup operator-acceptance synthesis and quality closeout
  contract validation.
- Raw boundary-bypass inventory improved from 86 candidates / 148 keys / 49
  convertible files to 84 / 144 / 47; ratchet-effective counts improved from
  82 candidates / 45 clean-convertible files to 80 / 43.

## Weak

- `tests/control_plane/test_integrations_validation.py` still has clean
  boundary-bypass targets because doctor, install, sync, and update flows keep
  real process coverage in the same broad file.
- The new path loaders for find-skills scripts are duplicated across three test
  modules; they are small but could become a shared test helper if this pattern
  repeats.
- `tests/quality_gates/test_docs_and_misc.py` remains near the test-file warn
  band with 660 Python code lines.

## Missing

- Missing before this slice: several routine validation and inventory behavior
  assertions were only reachable through subprocess execution despite callable
  seams already existing.

## Deferred

- Tokenizer-specific prompt measurement remains deferred; this slice targets
  script execution fanout and boundary-bypass ratchet/token noise.

## Advisory

- structural review result: command: `check_boundary_bypass_ratchet.py --repo-root .`
  reports 80 effective candidates and 43 clean-convertible files after
  exemptions; raw inventory reports 84 candidates, 144 keys, and 47 convertible
  files.
- prose review result: `testability-and-selection.md` supports keeping thin
  real-boundary smokes while moving ordinary behavior assertions below the
  boundary; the restored CLI proofs follow that rule.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333`, `nested_cli_file_count=149`, and
  `nested_cli_standing_or_mixed_file_count=145` still justify continuing this
  cleanup pattern.
- fresh-eye result: artifact:
  `charness-artifacts/critique/2026-06-26-five-pass-boundary.md` records two
  high findings that were fixed before closeout.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f014f-0f66-7582-a917-7bfb3b576989` found two high over-conversions; both
  were restored before final verification.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass inventory, standing-test
  economics, and focused-test evidence; no unique CLI boundary proof remains
  removed in the final diff.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 scripts/check_python_lengths.py --headroom --paths tests/test_find_skills_shadowing.py tests/test_find_skills_synced_support.py tests/control_plane/test_integrations_validation.py tests/quality_gates/test_docs_and_misc.py`
- command: python3 -m pytest -q tests/test_find_skills_shadowing.py tests/test_find_skills_synced_support.py tests/control_plane/test_integrations_validation.py tests/quality_gates/test_docs_and_misc.py
- command: python3 -m ruff check tests/test_find_skills_shadowing.py tests/test_find_skills_synced_support.py tests/control_plane/test_integrations_validation.py tests/quality_gates/test_docs_and_misc.py

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet already guards new growth
  in this class.
- passive convert another clean candidate because the remaining effective
  clean-convertible backlog is still 43 files.
- passive extract a shared script-loader test helper because three files now
  need dataclass-safe path loading for hyphenated skill script paths.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
