"""The runner-agnostic accounting seam for `mutate_and_restore` (#689).

Three Node repositories could not use this harness because the way it READS a
test runner's counts was pytest-shaped and hardcoded. The three properties the
harness enforces are runner-independent; only the reading was not.

A separate module from `test_mutate_and_restore.py` because that file sits in the
advisory length warn band, and because this is its own concept: what a reporter
owns is "what counts did the runner report", and nothing about killed/survived/
refused. Classification stays where it was and is tested where it was.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT

pytestmark = pytest.mark.boundary_contract(
    reason="observe mutate_and_restore running a real Node test binary and classify its process output while restoring the tree"
)

reporters = import_repo_module(
    "scripts/mutation/mutation_test_reporters.py", "scripts.mutation.mutation_test_reporters"
)
mar = import_repo_module(
    "scripts/mutation/mutate_and_restore.py", "scripts.mutation.mutate_and_restore"
)

_NODE_PASS = """\
TAP version 13
ok 1 - t1
ok 2 - t2
1..2
# tests 2
# suites 0
# pass 2
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 67.239608
"""

_NODE_FAIL = (
    _NODE_PASS.replace("ok 1 - t1", "not ok 1 - t1")
    .replace("ok 2 - t2", "not ok 2 - t2")
    .replace("# pass 2", "# pass 0")
    .replace("# fail 0", "# fail 2")
)


# --------------------------------------------------------------------------- #
# The extraction must not have changed one pytest verdict.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "output, expected",
    [
        ("some runner said nothing useful", None),
        ("no tests ran in 0.01s", 0),
        ("3 passed in 0.10s", 3),
        ("1 failed, 2 passed in 0.10s", 2),
    ],
)
def test_the_pytest_reader_is_unchanged(output: str, expected) -> None:
    """The same four cases `test_mutate_and_restore` pins, read through the seam.
    A refactor of a proof surface that silently moved one of these would be the
    worst possible outcome of this change."""
    assert mar.parse_passed(output) == expected


def test_the_pytest_reader_still_refuses_the_whole_transcript() -> None:
    """The scoping rule, which was learned in BOTH directions here: a stray
    `no tests ran` in an echoed test body turned a real kill into a refusal, and a
    stray `N failed` could manufacture a kill from a run where nothing failed."""
    transcript = "assert 'no tests ran' in msg\nE  1 failed\n2 passed in 0.10s\n"

    counts = reporters.PytestReporter.read(transcript)

    assert counts.passed == 2
    assert counts.failed == 0, counts.evidence


# --------------------------------------------------------------------------- #
# node --test
# --------------------------------------------------------------------------- #


def test_the_node_reader_reads_a_green_tap_block() -> None:
    counts = reporters.NodeTestReporter.read(_NODE_PASS)

    assert (counts.passed, counts.failed, counts.errors) == (2, 0, 0)


def test_the_node_reader_reads_a_failing_tap_block() -> None:
    counts = reporters.NodeTestReporter.read(_NODE_FAIL)

    assert (counts.passed, counts.failed) == (0, 2)


def test_node_cancelled_counts_as_an_error_not_a_failure() -> None:
    """A cancelled test did not run to a verdict, so it is a BROKEN RUN and not a
    caught mutation. Mapping it to `failed` would manufacture kills out of a
    crashed runner -- the exact defect this harness exists to end, reintroduced
    through the new seam."""
    output = _NODE_PASS.replace("# pass 2", "# pass 0").replace("# cancelled 0", "# cancelled 2")

    counts = reporters.NodeTestReporter.read(output)

    assert counts.errors == 2
    assert counts.failed == 0


def test_node_skipped_and_todo_are_not_accounted() -> None:
    """Folding them into the total would let a mutant that turns tests into skips
    satisfy the harness's baseline-scope check and read as a survivor."""
    output = _NODE_PASS.replace("# pass 2", "# pass 0").replace("# skipped 0", "# skipped 2")

    counts = reporters.NodeTestReporter.read(output)

    assert counts.passed + counts.failed == 0


def test_an_echoed_count_line_cannot_supply_a_node_count() -> None:
    """The keys are `^`-anchored under MULTILINE. A test that prints the literal
    mid-line must not be able to feed the accounting -- this is the node-side form
    of the transcript-scanning defect the pytest reader already learned."""
    output = "ok 1 - prints '# pass 99' somewhere\n" + _NODE_PASS

    counts = reporters.NodeTestReporter.read(output)

    assert counts.passed == 2


def test_the_last_node_run_wins() -> None:
    """Matches the pytest reader's `reversed()` scan: a fixture that invokes the
    runner twice reports the final run, not the first."""
    output = _NODE_FAIL + _NODE_PASS

    assert reporters.NodeTestReporter.read(output).passed == 2


def test_a_block_without_a_total_is_unreadable() -> None:
    """`# tests` is what makes the block a REPORT. A duration with no total says
    nothing about how many tests there were, and guessing zero would be a
    fabricated baseline."""
    output = "# duration_ms 12.5\n"

    assert reporters.NodeTestReporter.read(output) is None


def test_no_tap_block_at_all_is_unreadable() -> None:
    assert reporters.NodeTestReporter.read("3 passed in 0.10s") is None


# --------------------------------------------------------------------------- #
# Resolution and the refusal that names a way out
# --------------------------------------------------------------------------- #


def test_an_absent_reporter_key_still_means_pytest() -> None:
    """Every existing plan names no reporter; none of them may change behavior."""
    assert reporters.resolve(None) is reporters.PytestReporter


def test_an_unknown_reporter_name_resolves_to_nothing() -> None:
    """Refused by the caller rather than silently defaulted: a plan asking for a
    reader this harness lacks, answered with pytest's, reports `baseline REFUSED`
    on a healthy tree and blames the tree."""
    assert reporters.resolve("node") is None


def test_the_refusal_names_the_reporter_that_can_read_it() -> None:
    """THE #689 discoverability half. The measured refusal said the summary was
    unreadable and stopped, so an operator on a green Node tree was told their
    baseline could not be trusted and given nothing to act on."""
    message = reporters.unreadable_refusal("pytest", _NODE_PASS)

    assert "`pytest` reporter found no readable count report" in message
    assert "`node-test`" in message
    assert 'set `"reporter"` in the plan' in message


def test_the_refusal_does_not_invent_a_reader_for_unreadable_bytes() -> None:
    """When nothing can read it, saying so is the honest answer; naming a
    reporter that also cannot read it would be a false lead on a proof surface."""
    message = reporters.unreadable_refusal("pytest", "total gibberish")

    assert "no registered reporter could read it either" in message


# --------------------------------------------------------------------------- #
# End to end against a REAL `node --test` run.
# --------------------------------------------------------------------------- #


def _seed_node_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "node-repo"
    (repo / "src").mkdir(parents=True)
    (repo / "test").mkdir(parents=True)
    (repo / "package.json").write_text(
        json.dumps({"name": "fixture", "type": "module", "private": True}), encoding="utf-8"
    )
    (repo / "src" / "calc.js").write_text(
        "export function add(a, b) {\n  return a + b;\n}\n", encoding="utf-8"
    )
    (repo / "test" / "calc.test.js").write_text(
        "import { test } from 'node:test';\n"
        "import assert from 'node:assert';\n"
        "import { add } from '../src/calc.js';\n\n"
        "test('add sums', () => { assert.strictEqual(add(2, 3), 5); });\n"
        "test('add zero', () => { assert.strictEqual(add(2, 0), 2); });\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return repo


def _run_harness(repo: Path, plan: dict, tmp_path: Path) -> subprocess.CompletedProcess:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "mutation" / "mutate_and_restore.py"),
            "--repo-root",
            str(repo),
            "--plan",
            str(plan_path),
        ],
        capture_output=True,
        text=True,
    )


_MUTANT = {
    "id": "add-to-mul",
    "path": "src/calc.js",
    "find": "return a + b;",
    "replace": "return a * b;",
}


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_a_node_repository_gets_a_real_verdict(tmp_path: Path) -> None:
    """The acceptance criterion, executed rather than mocked: a REAL `node --test`
    run, a real mutation applied to a real file, a real kill.

    Before this seam the same fixture answered `baseline REFUSED: baseline
    produced no readable passing count` with exit 2, on a tree whose baseline was
    green (`returncode: 0`)."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo,
        {"test_command": ["node", "--test"], "reporter": "node-test", "mutants": [_MUTANT]},
        tmp_path,
    )

    # The YAML payload on stdout is the machine-readable contract; the streamed
    # progress line goes to stderr. Assert the payload, because that is what a
    # consumer reads, and a progress line is not a verdict.
    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"] == {"earned": True, "passed": 2, "returncode": 0, "refusal": None}, (
        result.stdout + result.stderr
    )
    assert payload["killed"] == 1
    assert payload["mutants"][0]["verdict"] == "killed"
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_mutated_node_file_is_restored(tmp_path: Path) -> None:
    """Property 3 is runner-independent and must survive the new reporter path.
    A sweep that leaves a Node worktree mutated is worse than one that refuses."""
    repo = _seed_node_fixture(tmp_path)
    before = (repo / "src" / "calc.js").read_bytes()

    _run_harness(
        repo,
        {"test_command": ["node", "--test"], "reporter": "node-test", "mutants": [_MUTANT]},
        tmp_path,
    )

    assert (repo / "src" / "calc.js").read_bytes() == before


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_default_reporter_still_refuses_a_node_tree_but_says_why(tmp_path: Path) -> None:
    """The refusal is CORRECT -- pytest's reader genuinely cannot read this -- and
    it must now carry the way out rather than being a dead end."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo, {"test_command": ["node", "--test"], "mutants": [_MUTANT]}, tmp_path
    )

    assert result.returncode == 2
    # The structured `refusal`, not the streamed progress line: the payload is
    # what a consumer reads back, and it is where the way out has to be.
    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"]["earned"] is False
    assert payload["baseline"]["returncode"] == 0, (
        "the Node baseline is GREEN; only the READER failed"
    )
    assert "`node-test`" in payload["baseline"]["refusal"]


def test_an_unknown_reporter_refuses_before_running_anything(tmp_path: Path) -> None:
    """No baseline command is spawned at all: a misconfigured plan is the plan's
    problem, and running a suite to discover that wastes the run and risks
    reporting a verdict about the tree."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo,
        {"test_command": ["node", "--test"], "reporter": "node", "mutants": [_MUTANT]},
        tmp_path,
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert "which is not registered" in payload["baseline"]["refusal"]
    assert "`node-test`, `pytest`" in payload["baseline"]["refusal"]


# --------------------------------------------------------------------------- #
# Round-1 findings: the adversarial cases the first cut shipped without.
# --------------------------------------------------------------------------- #


_NODE_BROKEN = """\
TAP version 13
# Subtest: test/t1.test.js
not ok 1 - test/t1.test.js
  ---
  failureType: 'testCodeFailure'
  exitCode: 1
  error: 'test failed'
  code: 'ERR_TEST_FAILURE'
  ...
1..1
# tests 1
# suites 0
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 81.122046
"""

_NODE_ASSERTION_FAILURE = """\
TAP version 13
not ok 1 - t1
  ---
  code: 'ERR_ASSERTION'
  ...
1..1
# tests 1
# suites 0
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 42.0
"""

_NODE_COMPACT_FILE_FAILURE = """\
not ok 1 - file
  ---
  exitCode: 1
  ...
ok 2 - second
1..2
# tests 2
# pass 1
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 17.0
"""

_NODE_LATE_HEADER_FILE_FAILURE = """\
TAP version 13
# Subtest: file
not ok 1 - file
  ---
  exitCode: 1
  ...
TAP version 13
1..1
# tests 1
# pass 0
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 18.0
"""

_NODE_INCOMPLETE_SUMMARY = """\
TAP version 13
not ok 1 - incomplete
1..1
# tests 1
# fail 1
# duration_ms 19.0
"""

_NODE_PLAN_MISMATCH = """\
TAP version 13
ok 1 - only-one-result
1..2
# tests 1
# pass 1
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 20.0
"""

_NODE_INCOMPLETE_TAP_WRAPPER = """\
TAP version 13
ok 1 - wrapper-only
1..2
# tests 2
# pass 2
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 21.0
"""


def test_a_file_level_process_failure_is_an_error_not_a_failure() -> None:
    """THE false-kill guard. `node --test` has no error concept: a test FILE that
    fails to load is reported as a failing TEST, so a mutation that breaks the
    module reports counts BYTE-IDENTICAL to a real kill on the same fixture --
    measured both ways, `# tests 3 / # pass 0 / # fail 3` either way. No count-only
    rule can separate them; what separates them is that a broken module fails at
    FILE level and node prints that file process's `exitCode:`."""
    counts = reporters.NodeTestReporter.read(_NODE_BROKEN)

    assert counts.failed == 0, "a file that never ran its tests caught nothing"
    assert counts.errors == 1


def test_a_real_assertion_failure_stays_a_failure() -> None:
    """The other half: the guard must not turn genuine kills into refusals. A
    test-level failure carries `code: 'ERR_ASSERTION'` and no `exitCode`."""
    real = (
        _NODE_PASS.replace("ok 1 - t1", "not ok 1 - t1")
        .replace("# pass 2", "# pass 1")
        .replace("# fail 0", "# fail 1")
    )
    body = "not ok 1 - t1\n  ---\n  code: 'ERR_ASSERTION'\n  ...\n"

    counts = reporters.NodeTestReporter.read(body + real)

    assert (counts.failed, counts.errors) == (1, 0)


@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [
        (_NODE_PASS + "wrapper chatter\n  exitCode: 1\n", ""),
        (_NODE_BROKEN.split("# duration_ms", 1)[0] + "wrapper chatter\n  exitCode: 1\n", ""),
        ("", "wrapper chatter\n# duration_ms 99\n"),
    ],
    ids=["inter-run-wrapper", "incomplete-earlier-run", "trailing-duration-wrapper"],
)
def test_the_selected_run_owns_counts_and_process_diagnostics(prefix: str, suffix: str) -> None:
    """The selected summary and its process diagnostics share one run window.

    The final TAP run is byte-identical across each axis. Earlier complete or
    incomplete output, wrapper diagnostics, and a misleading trailing duration
    must not change its assertion-failure result.
    """
    counts = reporters.NodeTestReporter.read(prefix + _NODE_ASSERTION_FAILURE + suffix)

    assert (counts.passed, counts.failed, counts.errors) == (0, 1, 0)


def test_compact_run_retains_all_owned_results_for_process_diagnostics() -> None:
    counts = reporters.NodeTestReporter.read(_NODE_COMPACT_FILE_FAILURE)

    assert (counts.passed, counts.failed, counts.errors) == (1, 0, 1)


def test_an_inner_tap_header_cannot_erase_the_outer_run_diagnostic() -> None:
    counts = reporters.NodeTestReporter.read(_NODE_LATE_HEADER_FILE_FAILURE)

    assert (counts.passed, counts.failed, counts.errors) == (0, 0, 1)


def test_summary_stops_at_an_earlier_duration_after_owning_the_trailing_block() -> None:
    trailing = "# duration_ms 1\n# tests 1\n# pass 1\n# fail 0\n# cancelled 0\n# duration_ms 2\n"

    summary = reporters.NodeTestReporter._summary_block(trailing)

    assert summary is not None
    assert summary.startswith("# tests 1")
    assert "# duration_ms 1" not in summary


@pytest.mark.parametrize(
    "output",
    [
        _NODE_PASS.replace("# pass 2", "# pass 2\n# pass 2"),
        _NODE_PASS.replace("# pass 2", "# pass -1").replace("# fail 0", "# fail 3"),
        _NODE_PASS.replace("# pass 2", "# pass 1"),
    ],
    ids=["duplicate-count", "negative-count", "count-total-mismatch"],
)
def test_duplicate_negative_or_inconsistent_counts_are_unreadable(output: str) -> None:
    assert reporters.NodeTestReporter.read(output) is None


def test_a_plan_first_compact_run_owns_the_results_after_its_plan() -> None:
    output = """\
1..1
ok 1 - plan-first
# tests 1
# pass 1
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 3
"""

    counts = reporters.NodeTestReporter.read(output)

    assert (counts.passed, counts.failed, counts.errors) == (1, 0, 0)


def test_summary_returns_only_a_complete_selected_run() -> None:
    assert reporters.NodeTestReporter.summary(_NODE_PASS) is not None
    assert reporters.NodeTestReporter.summary("# tests 1\n# pass 1\n") is None


@pytest.mark.parametrize("output", [_NODE_INCOMPLETE_SUMMARY, _NODE_PLAN_MISMATCH])
def test_an_incomplete_or_inconsistent_tap_summary_is_unreadable(output: str) -> None:
    assert reporters.NodeTestReporter.read(output) is None


def test_a_complete_tap_shaped_wrapper_cannot_supersede_a_real_run() -> None:
    counts = reporters.NodeTestReporter.read(_NODE_ASSERTION_FAILURE + _NODE_INCOMPLETE_TAP_WRAPPER)

    assert (counts.passed, counts.failed, counts.errors) == (0, 1, 0)


@pytest.mark.parametrize(
    "output",
    [_NODE_COMPACT_FILE_FAILURE, _NODE_LATE_HEADER_FILE_FAILURE],
    ids=["compact-all-results", "explicit-first-header"],
)
def test_classification_refuses_file_failures_preserved_by_the_selected_run(output: str) -> None:
    completed = subprocess.CompletedProcess([], 1, output, "")
    baseline = mar.Baseline(returncode=0, passed=2, output="")

    verdict, _detail = mar.classify_mutant_run(completed, baseline, reporters.NodeTestReporter)

    assert verdict == mar.REFUSED


@pytest.mark.parametrize("output", [_NODE_INCOMPLETE_SUMMARY, _NODE_PLAN_MISMATCH])
def test_classification_refuses_an_incomplete_or_mismatched_tap_summary(output: str) -> None:
    completed = subprocess.CompletedProcess([], 1, output, "")
    baseline = mar.Baseline(returncode=0, passed=1, output="")

    verdict, detail = mar.classify_mutant_run(completed, baseline, reporters.NodeTestReporter)

    assert verdict == mar.REFUSED
    assert "no readable summary" in detail


def test_process_failures_cannot_exceed_the_reported_failures() -> None:
    """Direction of error is what makes reading outside the summary acceptable
    here: over-counting turns a kill into a refusal (a false stop) and can never
    manufacture one. The cap keeps `failed` from going negative."""
    noisy = "  exitCode: 1\n" * 9 + _NODE_BROKEN

    counts = reporters.NodeTestReporter.read(noisy)

    assert counts.failed == 0
    assert counts.errors == 1


def test_the_spec_marker_is_deliberately_NOT_read_as_counts() -> None:
    """REVERSED by round 2, and the reversal is the point.

    Round 1 asked for `spec` to be read so a consumer whose node emits it would
    not meet a dead end. Round 2 measured what that bought: `spec` omits the
    file-level failure detail the false-kill guard needs, so reading its counts
    reinstated a KILLED verdict on a run where no test caught anything. The
    counts are refused; the FORMAT is still recognised, so the refusal can name
    `--test-reporter=tap`. See the three tests at the end of this file."""
    spec = _NODE_PASS.replace("# ", "ℹ ")

    assert reporters.NodeTestReporter.read(spec) is None


def test_the_node_summary_shape_names_the_tap_escape_hatch() -> None:
    assert "--test-reporter=tap" in reporters.NodeTestReporter.summary_shape


@pytest.mark.parametrize("value", ["", [], 0, False, 5, ["node-test"], {}])
def test_an_unusable_reporter_value_is_refused_not_defaulted(value) -> None:
    """`REPORTERS.get(name or DEFAULT)` short-circuited on every FALSY value, so
    `{"reporter": ""}` -- what a templated plan with an unset variable emits --
    silently selected pytest and defeated the refusal on the input most likely to
    produce it. A truthy unhashable value was worse: `dict.get` raised and crashed
    the sweep. Only an ABSENT key means default."""
    assert reporters.resolve(value) is None


def test_only_an_absent_key_means_default() -> None:
    assert reporters.resolve(None) is reporters.PytestReporter


def test_the_refusal_survives_an_unregistered_reporter_name() -> None:
    """`REPORTERS[configured]` was an unguarded subscript on the path that exists
    to EXPLAIN a failure, so the first duck-typed out-of-tree reporter would turn
    "no readable summary, here is why" into a KeyError mid-sweep."""
    message = reporters.unreadable_refusal("some-out-of-tree-reporter", "gibberish")

    assert "some-out-of-tree-reporter" in message


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_a_module_breaking_mutant_is_refused_not_killed(tmp_path: Path) -> None:
    """End to end, against real `node --test`: the node analogue of the pytest
    suite's strongest property-2 test. Before the guard this returned
    `killed: 1` -- a kill reported when no test caught anything, which is exactly
    what the module docstring forbids."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo,
        {
            "test_command": ["node", "--test"],
            "reporter": "node-test",
            "mutants": [
                {
                    "id": "syntax-break",
                    "path": "src/calc.js",
                    "find": "return a + b;",
                    "replace": "return a +",
                }
            ],
        },
        tmp_path,
    )

    payload = yaml.safe_load(result.stdout)
    assert payload["killed"] == 0, result.stdout
    assert payload["mutants"][0]["verdict"] == "refused"


def test_an_unmeasured_baseline_reports_no_returncode(tmp_path: Path) -> None:
    """A plan refused for its OWN misconfiguration never spawned a baseline
    command. Reporting `returncode: 0` there let a consumer read "the tree is
    green" out of a run that established nothing -- and this suite itself draws
    that inference one test away."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo, {"test_command": ["node", "--test"], "reporter": "node", "mutants": []}, tmp_path
    )

    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"]["returncode"] is None


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_call_site_non_claim_says_the_check_was_inapplicable(tmp_path: Path) -> None:
    """`removed_calls` parses a PYTHON ast, so a `.js` target yields `None` and the
    whole call-site mechanism is inert: no Node mutant can ever count, so the
    non-claim fires on EVERY Node sweep regardless of the plan, and a false
    `"call_site": true` cannot be refused either. A message that is always printed
    carries no information; naming the cause is what keeps it informative."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo,
        {"test_command": ["node", "--test"], "reporter": "node-test", "mutants": [_MUTANT]},
        tmp_path,
    )

    payload = yaml.safe_load(result.stdout)
    assert "could not be APPLIED to src/calc.js" in payload["call_site_non_claim"]


# --------------------------------------------------------------------------- #
# Round-2: the spec reporter is refused, not half-read.
# --------------------------------------------------------------------------- #


_NODE_SPEC = _NODE_PASS.replace("# ", "ℹ ")


def test_the_spec_reporter_is_refused_rather_than_half_read() -> None:
    """THE round-2 blocker. An earlier cut accepted both markers so a consumer
    whose node emits `spec` would not meet a dead end -- and that widening
    silently reintroduced the false kill the same slice had just repaired,
    because the file-level/test-level distinction the guard needs EXISTS ONLY IN
    TAP. Measured: `node --test --test-reporter=spec` over a module-breaking
    mutant emits no `exitCode` line in any form."""
    assert reporters.NodeTestReporter.read(_NODE_SPEC) is None


def test_spec_output_is_recognised_so_the_refusal_can_be_specific() -> None:
    """A dead end that names its own fix is strictly better than a false kill --
    but a GENERIC dead end over output that is obviously node's is the thing this
    seam exists to end."""
    assert reporters.NodeTestReporter.looks_like_spec(_NODE_SPEC) is True
    assert reporters.NodeTestReporter.looks_like_spec(_NODE_PASS) is False


def test_the_spec_refusal_names_the_one_flag_that_fixes_it() -> None:
    message = reporters.unreadable_refusal("node-test", _NODE_SPEC)

    assert "`spec` reporter" in message
    assert "--test-reporter=tap" in message


def test_a_green_run_zeroes_the_process_failure_mechanism() -> None:
    """The cap means `reported_failures == 0` disables the subtraction entirely,
    so a SURVIVED verdict cannot be perturbed by transcript noise."""
    noisy = "  exitCode: 1\n" * 5 + _NODE_PASS

    counts = reporters.NodeTestReporter.read(noisy)

    assert (counts.passed, counts.failed, counts.errors) == (2, 0, 0)
