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

reporters = import_repo_module("scripts/mutation_test_reporters.py", "scripts.mutation_test_reporters")
mar = import_repo_module("scripts/mutate_and_restore.py", "scripts.mutate_and_restore")

_NODE_PASS = """\
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

_NODE_FAIL = _NODE_PASS.replace("# pass 2", "# pass 0").replace("# fail 0", "# fail 2")


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
    output = _NODE_PASS.replace("# skipped 0", "# skipped 7").replace("# todo 0", "# todo 5")

    counts = reporters.NodeTestReporter.read(output)

    assert counts.passed + counts.failed == 2


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
    assert "set `\"reporter\"` in the plan" in message


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
        cwd=repo, check=True, capture_output=True,
    )
    return repo


def _run_harness(repo: Path, plan: dict, tmp_path: Path) -> subprocess.CompletedProcess:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return subprocess.run(
        ["python3", str(ROOT / "scripts" / "mutate_and_restore.py"),
         "--repo-root", str(repo), "--plan", str(plan_path)],
        capture_output=True, text=True,
    )


_MUTANT = {"id": "add-to-mul", "path": "src/calc.js",
           "find": "return a + b;", "replace": "return a * b;"}


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_a_node_repository_gets_a_real_verdict(tmp_path: Path) -> None:
    """The acceptance criterion, executed rather than mocked: a REAL `node --test`
    run, a real mutation applied to a real file, a real kill.

    Before this seam the same fixture answered `baseline REFUSED: baseline
    produced no readable passing count` with exit 2, on a tree whose baseline was
    green (`returncode: 0`)."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo, {"test_command": ["node", "--test"], "reporter": "node-test", "mutants": [_MUTANT]}, tmp_path
    )

    # The YAML payload on stdout is the machine-readable contract; the streamed
    # progress line goes to stderr. Assert the payload, because that is what a
    # consumer reads, and a progress line is not a verdict.
    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"] == {
        "earned": True, "passed": 2, "returncode": 0, "refusal": None
    }, result.stdout + result.stderr
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
        repo, {"test_command": ["node", "--test"], "reporter": "node-test", "mutants": [_MUTANT]}, tmp_path
    )

    assert (repo / "src" / "calc.js").read_bytes() == before


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_default_reporter_still_refuses_a_node_tree_but_says_why(tmp_path: Path) -> None:
    """The refusal is CORRECT -- pytest's reader genuinely cannot read this -- and
    it must now carry the way out rather than being a dead end."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(repo, {"test_command": ["node", "--test"], "mutants": [_MUTANT]}, tmp_path)

    assert result.returncode == 2
    # The structured `refusal`, not the streamed progress line: the payload is
    # what a consumer reads back, and it is where the way out has to be.
    payload = yaml.safe_load(result.stdout)
    assert payload["baseline"]["earned"] is False
    assert payload["baseline"]["returncode"] == 0, "the Node baseline is GREEN; only the READER failed"
    assert "`node-test`" in payload["baseline"]["refusal"]


def test_an_unknown_reporter_refuses_before_running_anything(tmp_path: Path) -> None:
    """No baseline command is spawned at all: a misconfigured plan is the plan's
    problem, and running a suite to discover that wastes the run and risks
    reporting a verdict about the tree."""
    repo = _seed_node_fixture(tmp_path)

    result = _run_harness(
        repo, {"test_command": ["node", "--test"], "reporter": "node", "mutants": [_MUTANT]}, tmp_path
    )

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert "which is not registered" in payload["baseline"]["refusal"]
    assert "`node-test`, `pytest`" in payload["baseline"]["refusal"]
