# Timeout-bound census, 2026-09-03 (#786)

The wall-clock form check (`scripts/gates/check_wall_clock_form.py`) refuses a
`time.sleep`, `time.monotonic`, or `time.perf_counter` call in `tests/`. Hosted
run 33701977188 tripped on a test with no such call: its verdict rode on a
`*_TIMEOUT_SECONDS` knob set to 0.5 s and an assertion that the child's stdout
held a line the child had to print before that deadline. This census names
every site of that shape in today's tree and settles each one.

## Pinned predicate (written before the code)

The predicate as pinned in the #786 body was blind to the hosted shape itself:
that test asserts on `probe["stdout_preview"]`, a subscript two assignments away
from `result.stdout`. Before writing the gate it was extended by one closed rule:
a name assigned, transitively within the function, from an expression that reads
`.stdout`, `.stderr`, `.returncode`, or a `.communicate()` call counts as a read
of the child's output. The rest is as pinned.

Within one `def test_*` function in a scanned test file, a **timeout-bound
verdict** is either:

1. **Knob-bound.** A `*_TIMEOUT_SECONDS` name set to a value under 5 s by any
   of: `env["X_TIMEOUT_SECONDS"] = "0.1"`, `monkeypatch.setenv("X_TIMEOUT_SECONDS", "0.1")`,
   `module.X_TIMEOUT_SECONDS = 0.25`, or `monkeypatch.setattr(module, "X_TIMEOUT_SECONDS", 0.25)`,
   together with an `assert` in the same function whose expression reads
   `.stdout`, `.stderr`, `.returncode`, or a name bound from a `.communicate()`
   call in that function.
2. **Deadline-bound.** A `.communicate(timeout=N)`, `.run(..., timeout=N)`, or
   `.wait(timeout=N)` with a literal `N` under 1 s, inside a `try` whose
   `except TimeoutExpired` handler contains an `assert` or `raise AssertionError`.

Exempt, and stated in the gate's docstring: a function that installs a
controlled clock (`monkeypatch.setattr("...time.monotonic", ...)`), because the
knob there is a heartbeat cadence and the budget is spent by an observation.

Outside the rule (the blind shapes the docstring names): a knob set in a
fixture, helper, or module constant rather than in the test function; a deadline
passed through a variable or a helper parameter rather than a literal; an
assertion on a value that reaches the test through a call or a tuple unpack
(`result = run_bounded(env=env)`, `returncode, output = run(...)`) rather than
through an attribute read; `capsys` output (`.out`); a fake that raises
`TimeoutExpired` (no clock is involved).

## Census of today's sites

Read 2026-09-03 from `grep -rln _TIMEOUT_SECONDS tests` (12 files) plus every
`communicate(timeout=`, `run(timeout=`, and `wait(timeout=` in `tests/`.

| File | Site | Shape | Disposition |
| --- | --- | --- | --- |
| `tests/quality_gates/test_cli_skill_surface.py` | `test_cli_skill_surface_reports_probe_timeout`: knob 0.1 s, child `sleep(2)`, asserts `result.returncode == 1` and the payload | knob-bound | **keep**: the child sleeps 20x the knob, so the deadline is certain to fire and load only widens the margin; the claim is the `unobserved` reporting shape. Baseline entry with this reason. |
| `tests/quality_gates/test_cli_skill_surface_probe_boundary.py` | `test_cli_skill_surface_survives_a_probe_whose_grandchild_holds_the_pipe`: knob 0.5 s, the probe spawns a holder interpreter, records its pid, prints, then `sleep(600)`; asserts `len(recorded_pids) == attempts` and that the partial line is in `stdout_preview` | knob-bound, unsafe direction twice (the holder spawn and the print must both beat the kill); blind to the gate because the output reaches the test through a helper's return value | **delete**: a real check process cannot be given a controlled clock, so neither claim can be forced; both are owned non-vacuously by the in-process siblings on a controlled clock (`..._bounds_the_drain_when_the_grandchild_escapes_the_group` for the drain bound with a real escaped holder, `..._keeps_partial_output_when_even_the_drain_times_out` for the partial output), and the real-process bound on a hanging probe is owned by `..._names_the_unobserved_probe_in_its_only_output`. The unused `_run_bounded_in_own_session` helper goes with it. |
| same file | `test_cli_skill_surface_bounds_the_drain_when_the_grandchild_escapes_the_group` and `..._keeps_partial_output_when_even_the_drain_times_out`: knob 0.1 s on a patched `time.monotonic` | exempt (controlled clock, #780) | keep, green under the exemption |
| same file | `test_cli_skill_surface_names_the_unobserved_probe_in_its_only_output`: knob 0.2 s, child `sleep(30)`, asserts `result.returncode == 1` | knob-bound | **keep**: certain-to-fire, 150x margin; the claim is the payload's `unobserved` word. Baseline entry. |
| same file | `communicate(timeout=60)` in the kill-tree probe with `raise AssertionError` in the handler (the deleted test's `_run_bounded_in_own_session(limit=30.0)` was the same shape) | deadline-bound, limit ≥ 1 s | outside the rule by the 1 s threshold; the bound is the suite's own hang guard, not the claim |
| `tests/test_markdown_preview_support.py` | `test_markdown_preview_marks_slow_glow_as_backend_error`: knob 0.1 s, fake glow `sleep(2)`, asserts `result.returncode == 0` | knob-bound | **keep**: certain-to-fire, 20x margin; the claim is the `backend-error` rendering. Baseline entry. |
| same file | `test_markdown_preview_glow_backend_check_exit_codes`: `setenv` knob 0.1 s, asserts `mod.main() == 1` and `capsys.readouterr().out` | knob-bound, blind (the output is `capsys` `.out`, not a child attribute) | keep: same fake, same margin. Named as a blind shape. |
| `tests/test_script_timeout.py` | `test_arm_cli_timeout_exits_in_subprocess`: knob 0.05 s, child `sleep(0.2)`, asserts `result.returncode == 1` and stderr | knob-bound | **keep**: certain-to-fire, 4x margin, and the alarm is armed before the sleep starts; the claim is the exit-code and stderr contract of the alarm handler. Baseline entry. |
| `tests/test_docs_graph_gate.py` | `test_a_hung_awiki_times_out_rather_than_hanging_the_whole_quality_run`: `setattr(_awiki, "AWIKI_TIMEOUT_SECONDS", 0.25)`, stub `sleep 30`, asserts `returncode == 124` (a name unpacked from the call) | knob-bound, blind under the strict predicate (assert on an unpacked name) | keep: certain-to-fire, 120x margin. Named as a blind shape; not in the baseline because the gate does not see it. |
| `tests/test_probe_stimulus_replay.py` | `test_a_resolver_that_never_answers_is_refused_rather_than_read_as_agreement`: `replay._RESOLVE_TIMEOUT_SECONDS = 0.001`, asserts `timed_out["data"] is None` | knob-bound, blind (assert on a subscript) | keep: a real resolver cannot answer in 1 ms; the claim is the fail-closed shape. Named as a blind shape. |
| `tests/test_announcement_delivery_verification.py`, `tests/test_doc_duplicates_inprocess_coverage.py`, `tests/test_nose_inprocess_coverage.py`, `tests/quality_gates/test_prepush_close_keyword_guard.py` | fakes that return or raise a timeout result; the knob is read as a value, never set | not a site | keep: no clock is involved |
| `tests/quality_gates/test_startup_probe_measure.py`, `tests/test_worktree_doctor_state.py` | assertions on the default knob values | not a site | keep: data, not a deadline |

## Gate read on the finished tree

`python3 scripts/gates/check_timeout_bound_form.py --repo-root . --require-git-file-listing`
with no record: 4 sites in 4 files, exactly the four **keep** rows above
(`test_cli_skill_surface_reports_probe_timeout`,
`test_cli_skill_surface_names_the_unobserved_probe_in_its_only_output`,
`test_markdown_preview_marks_slow_glow_as_backend_error`,
`test_arm_cli_timeout_exits_in_subprocess`). The two `#780` controlled-clock
tests are exempt as designed; the deleted boundary test and the three blind
rows were, as stated, invisible to it.

## Baseline

`charness-artifacts/quality/timeout-bound-baseline.json` names each of the
four kept sites with its reason in the wall-clock record's shape plus a
`reasons` map; a file above its count is red, `--write-baseline` refuses to
raise a count or to record a site without a reason. The label
`check-timeout-bound-form` runs in the standing lane beside
`check-wall-clock-form`.
