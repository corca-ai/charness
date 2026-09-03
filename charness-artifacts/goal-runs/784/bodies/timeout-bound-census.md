<!-- charness-work-item-key: timeout-bound-census -->

## Objective

The wall-clock census sees a claim whose verdict rides on a `*_TIMEOUT_SECONDS` knob or a subprocess deadline, not only a `time.*` call. Hosted run 33701977188 tripped on that shape (`test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out`, no `time.*` call).

## Owned scope

- `scripts/gates/check_wall_clock_form.py` or a sibling form check: a closed AST predicate pinned before the slice starts: within one test `FunctionDef`, a `*_TIMEOUT_SECONDS` name assigned or `setenv`'d to a value under 5 s together with an `assert` that reads `.stdout`, `.stderr`, `.returncode`, or a `communicate()` result; or a `communicate(timeout=)` or `run(timeout=)` under 1 s whose `except TimeoutExpired` branch holds the assertion; the docstring names the shapes still outside the rule (`detector-blind-class-unstated`).
- Census recorded under `charness-artifacts/goal-runs/<parent>/timeout-census.md`: today's 12 files reading a knob, 9 setting one, 8 passing a sub-second or `communicate` timeout; each entry rewritten (controlled clock plus `tests/fifo_witness.py`), deleted, or kept with the written reason that its claim is not a deadline (`test_cli_skill_surface_reports_probe_timeout` is the known case).
- Baseline record starts empty or names each kept site with its reason, in the same shape as `wall-clock-baseline.json`; `--write-baseline` refuses to raise a count.

## Acceptance

- Seeded timeout-bound test is red under the form check; the rewritten drain test and the census entries are green.
- The census list is empty or every remaining entry carries a reason in the baseline.
- `docs/development.md` testing paragraph names the extended rule in one sentence.

## Focused verification

Standing lane on `tests/quality_gates/test_check_wall_clock_form*.py` and the census files, then the standing runner.

## Dependencies

none

## Non-claims

Does not retry, widen, or deselect any test. Does not change the #358 recovery rule or #764's path.
