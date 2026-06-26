# Quality Review
Date: 2026-06-26

## Scope

Target boundary: public-skill validation and dogfood tests that were using
script subprocesses for ordinary policy, registry, and matrix assertions.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, Python
warn-band files, and the larger nested-CLI backlog are not fully fixed here.

## Current Gates

- Focused pytest passed 15 tests for public-skill validation/dogfood behavior
  and dogfood wrapper parity.
- Boundary-bypass ratchet passed after preserving four intentional CLI smokes
  with explicit exemption rationales.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.3s latest / 25.6s median, budget 140.0s;
  `check-coverage` 18.4s latest / 18.9s median, budget 55.0s.
- coverage gate: focused pytest, ruff, packaging validation, and
  boundary-bypass ratchet passed; broad read-only closeout pending at draft
  time.
- evaluator depth: deterministic gates only; `plan_cautilus_proof.py` returned
  `next_action: none`, so no Cautilus run was allowed or needed.

## Healthy

- `tests/test_public_skill_validation.py` now asserts policy partition,
  adapter requirement, suggestion payload, and human-format behavior through
  `validate_policy()`, `validate_adapter_requirement()`, `build_report()`, and
  `_format_human()`.
- `tests/test_public_skill_dogfood.py` now checks registry drift and required
  review failures through `validate_registry()` and scaffolds demo cases through
  `build_matrix()`.
- `tests/quality_gates/test_public_skill_dogfood.py` now validates root matrix
  content through `build_matrix()` instead of launching the root CLI.
- One real CLI smoke remains for each public-skill validation/dogfood command,
  preserving `__main__`, argument parsing, exit status, stdout/stderr shape, and
  operator guidance.
- Boundary-bypass ratchet now reports 82 candidates, 45 clean-convertible files,
  33 internally-spawning files, and 23 likely keep-boundary files after
  exemptions are applied.

## Weak

- `build_matrix()` can still spawn adapter resolver subprocesses internally for
  adapter-backed skills; this slice removes the outer CLI boundary, not every
  dogfood matrix process.
- The wrapper parity test intentionally still launches root, source-wrapper, and
  plugin-wrapper dogfood suggestion scripts; fresh-eye flagged this as a low
  duplicate CLI-smoke risk, but it proves exported wrapper parity rather than
  ordinary matrix behavior.
- The standing suite still has 145 standing/mixed nested-CLI files in the
  standing-test-economics advisory.

## Missing

- Missing before this slice: public-skill policy and dogfood failure behavior
  was mostly verified through subprocesses even though import-safe library seams
  existed.

## Deferred

- Tokenizer-specific prompt measurement remains deferred; this slice targets
  script execution fanout and boundary-bypass ratchet/token noise.

## Advisory

- structural review result: command: `check_boundary_bypass_ratchet.py --repo-root .`
  reports 82 effective candidates and 45 clean-convertible files after
  exemptions; raw inventory remains 86 candidates, 148 keys, and 49 convertible
  files.
- prose review result: `boundary-bypass-ratchet.md` allows exemptions only for
  intentional real-boundary tests; the four new entries include `# why:`, owner,
  and revisit conditions.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333`, `nested_cli_file_count=149`, and
  `nested_cli_standing_or_mixed_file_count=145` support reducing repeated
  subprocess fanout while keeping thin real-boundary smokes.
- fresh-eye result: artifact:
  `charness-artifacts/critique/2026-06-26-public-skill-validation-boundary.md`
  records no blockers and one low wrapper-parity duplication caveat.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f0140-1e5f-7382-a451-82e7428e8abe` found no blockers, confirmed meaningful
  CLI proof remains for all four scripts, and identified the wrapper-parity
  subprocess as residual low risk.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass inventory, standing-test
  economics, and focused-test evidence; no real-boundary wrapper proof was
  removed.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 scripts/check_python_lengths.py --headroom --paths tests/test_public_skill_validation.py tests/test_public_skill_dogfood.py tests/quality_gates/test_public_skill_dogfood.py`
- command: python3 -m pytest -q tests/test_public_skill_validation.py tests/test_public_skill_dogfood.py tests/quality_gates/test_public_skill_dogfood.py
- command: python3 -m ruff check tests/test_public_skill_validation.py tests/test_public_skill_dogfood.py tests/quality_gates/test_public_skill_dogfood.py

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet and exemption rationale
  rule already cover new growth in this class.
- passive convert the next clean candidate because the remaining effective
  clean-convertible backlog is still 45 files.
- passive review dogfood adapter artifact resolution because `build_matrix()`
  still pays internal resolver subprocesses until a cleaner artifact seam exists.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
