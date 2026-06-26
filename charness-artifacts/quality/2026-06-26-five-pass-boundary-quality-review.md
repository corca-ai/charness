# Quality Review
Date: 2026-06-26

## Scope

Target boundary: follow-up quality slice covering boundary-bypass reduction,
mixed test-file decomposition, duplicate advisory drift cleanup, and pre-push
runtime triage.

Ambient repo findings: full pre-push runtime, broad nested-CLI backlog, and
large intentional adapter/bootstrap duplicate families are not fully fixed here.

## Current Gates

- Focused pytest passed 42 tests across the split docs/misc files and
  boundary-bypass inventory/ratchet coverage.
- Boundary-bypass ratchet passed with effective candidate keys reduced from 116
  to 115 and no new candidate keys after one explicit CLI-smoke exemption.
- Code and doc duplicate inventories report clean drift after reviewed baseline
  refresh; dup-ratchet reports no new fixable-eligible families.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 21.4s latest / 25.0s median, budget 140.0s;
  `check-coverage` 5.7s latest / 12.0s median; `check-markdown` 4.8s latest /
  median.
- coverage gate: focused tests, boundary ratchet, duplicate inventories, and
  dup-ratchet passed; broad closeout pending at artifact draft time.
- evaluator depth: deterministic gates only; no Cautilus run was requested or
  allowed for this structural test/runtime slice.

## Healthy

- `tests/quality_gates/test_docs_and_misc.py` is now a small real-boundary smoke
  file for narrative and release bump scripts, down to 118 Python code lines.
- `tests/quality_gates/test_script_inprocess_behaviors.py` owns in-process
  script behavior tests plus one thin setup CLI wrapper smoke.
- `tests/quality_gates/test_skill_docs_contracts.py` owns the moved docs and
  skill contract assertions with 414 lines of file headroom remaining.
- `synthesize_operator_acceptance` behavior moved below the subprocess boundary,
  while a single CLI smoke preserves argparse/bootstrap/stdout JSON proof.
- Duplicate inventories are quiet after accepting reviewed baseline drift for
  intentional portable boilerplate/template families.

## Weak

- `tests/quality_gates/test_skill_docs_contracts.py` is still a broad docs and
  skill-contract assertion file at 386 code lines; it is smaller than the old
  mixed file but still mixed by theme.
- The duplicate baseline refresh accepts ID churn rather than removing the
  underlying adapter/bootstrap duplication; that is intentional portability
  boilerplate, not a code simplification.
- Pre-push runtime remains dominated by `run-quality-read-only` and `pytest`;
  only `check-markdown` is CI-backed and it is not a large enough safe win to
  justify weakening the local proof bar here.

## Missing

- Missing before this slice: the mixed docs/misc test file made focused review
  noisy, the setup operator-acceptance behavior assertion still lived behind a
  subprocess boundary, and duplicate advisory drift repeated at pre-push.

## Deferred

- Tokenizer-specific prompt measurement remains deferred; this slice targets
  script execution fanout, test surface shape, duplicate advisory noise, and
  pre-push runtime triage.

## Advisory

- structural review result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` reports ok with 115
  effective candidate keys and 34 clean-convertible files after exemptions.
- prose review result: `testability-and-selection.md` supports keeping one
  real-boundary CLI smoke while moving ordinary operator-acceptance behavior
  assertions in-process.
- duplicate review result: code advisory families `fe221babe2ef45c0`,
  `a70c088815bc4d2c`, and `5e1af1bcc0506d04` are intentional
  adapter/bootstrap/path-normalization boilerplate; doc family `e89e772efc0ba634`
  is an already-classified HITL/Narrative shared-template family. Baselines were
  refreshed to align advisory drift with that reviewed state.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=343`, `nested_cli_file_count=149`, and
  `nested_cli_standing_or_mixed_file_count=145` keep broad test runtime and
  boundary-bypass cleanup in scope, but this slice only removes one clean
  candidate instead of claiming the nested-CLI backlog is solved.
- runtime review result: `inventory_ci_recoverable_gates.py --repo-root . --json`
  found only `check-markdown` as a CI-backed candidate, so no safe large
  move-off-local change shipped.
- fresh-eye result: artifact:
  `charness-artifacts/critique/2026-06-26-boundary-docs-runtime-quality-slice.md`
  records the CLI-smoke and baseline-explanation findings fixed before closeout.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f03ad-fa93-7e62-9cec-2b47400ca2d6` found one CLI-boundary gap and one
  duplicate-baseline explanation gap; both were fixed before closeout.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through runtime summary, CI-recoverable-gate
  inventory, standing-test economics, focused pytest, and duplicate inventories.

## Commands Run

- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_ci_recoverable_gates.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json --top 20`
- `python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --write-baseline`
- `python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root . --write-baseline`
- focused pytest over docs/misc split files plus boundary-bypass inventory and ratchet tests (42 passed)
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root .`

## Recommended Next Gates

- active none — the requested 1-4 slice has deterministic proof and no
  uncovered local gate change.
- passive split `test_skill_docs_contracts.py` further because it is still a
  broad docs/skill assertion file even though it is no longer near the file cap.
- passive revisit local `check-markdown` placement because the current
  CI-backed candidate saves about 4.8s but does not address the dominant
  `pytest` and full-gate costs.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
