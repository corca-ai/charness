# Lane brief U1: source and test universes (#769, Goal Run #765)

Follow `charness-artifacts/goal-runs/765/briefs/brief-769-u-common.md` first.

Your labels and the universes key each reads:

- `pytest`, `pytest-release`, `check-test-completeness`: `pytest_targets`.
  `scripts/run_standing_pytest.py:78-91` `STANDING_PYTEST_TARGETS` becomes the
  default; the runner keeps calling `--print-expanded-targets`, which now
  expands the resolved universe, so `check-test-completeness` follows for free.
- `check-python-lengths` (`scripts/check_code_lengths.py:183-207` `GATED_GLOBS`),
  `check-python-runtime-inheritance` (`scripts/check_python_runtime_inheritance.py:14-23`),
  `ruff` (`scripts/check-python-lint.sh:66-72` literal roots), and the
  py-compile array (`scripts/run-quality.sh:1157-1166`, R2 applies your row):
  `python_sources`. `GATED_GLOBS` also carries Rust and test globs; keep those
  under their own sub-keys only if U0 defined them, otherwise leave the
  non-Python globs literal and say so.
- `check-shell` (`scripts/check-shell.sh:52-61`, the unguarded `find scripts`):
  `shell_sources`.
- `check-test-production-ratio` (`scripts/check_test_production_ratio.py:20-34`
  literal `tests`): `test_roots`.
- `release-changed-line-coverage` (`scripts/sample_mutation_files.py:53-69`
  `MUTATION_POOLS`, reached via `mutation_changed_files_lib.py:316-318`):
  `mutation_pool`. The existing `changed_line_mutation_gate.eligible_globs`
  stays the eligibility filter; the pool is the universe.

Scope: the files above, `tests/quality_gates/test_standing_pytest_runner.py`,
`test_check_test_completeness.py`, `test_shell_gate_root_resolution.py`,
`test_python_and_security_gates.py`, `test_shared_script_gate_scope.py`,
`test_code_length_gates.py`, `test_code_length_interpretation.py`,
`test_empty_scope_refusals.py`, `test_test_production_ratio.py`,
`test_release_changed_line_coverage.py`, `test_quality_mutation_sampling.py`,
`test_mutation_changed_line_targets.py`, `tests/conftest.py` (only if it pins
the targets), and new tests.

Commit subject:
`quality: read source, shell, test, and mutation-pool universes from the adapter (#769 U1 lane candidate)`
