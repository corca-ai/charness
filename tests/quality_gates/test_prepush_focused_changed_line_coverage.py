"""The incremental pre-push changed-line teeth (D40).

The lane this replaces exited 0 by construction, which is how a gate that fired
eight times still let eight regressions land. Its replacement is only worth having
if it cannot be read as a pass when it did not judge — so most of what these tests
pin is the SHAPE OF NOT KNOWING: producer death, an unresolvable base, a consumer
refusal, and a mapping that reached nothing all have to be distinguishable from a
clean run, on the exit code and in the payload.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from .support import ROOT, run_script

SCRIPT = "scripts/prepush_focused_changed_line_coverage.py"


@pytest.fixture()
def gate():
    from tests.script_loader import load_script_module

    return load_script_module("prepush_focused_under_test", ROOT / SCRIPT)


def _recommendation(**overrides) -> dict:
    payload = {
        "status": "partial",
        "base_sha": "b" * 40,
        "changed_pool_files": ["scripts/mapped.py", "scripts/unmapped.py"],
        "mapped_tests_by_file": {"scripts/mapped.py": ["tests/test_mapped.py"]},
        "unmapped_changed_pool_files": ["scripts/unmapped.py"],
    }
    payload.update(overrides)
    return payload


def test_no_base_sha_is_a_no_verdict_not_a_pass(gate, monkeypatch, capsys) -> None:
    """Exit 0 here is what the old lane did, and it is the whole bug: a range that
    could not be resolved was reported the same way as a range with nothing wrong."""
    monkeypatch.setattr(gate._producer, "default_mutation_base_sha", lambda _root: "")

    assert gate.main(["--repo-root", str(ROOT), "--json"]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "no-verdict"
    assert "It is NOT a pass" in captured.err


def test_a_dead_producer_is_a_no_verdict_not_a_pass(gate, monkeypatch, capsys) -> None:
    import subprocess

    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())

    def _boom(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, "pytest")

    monkeypatch.setattr(gate._producer, "produce_command_coverage", _boom)

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json"]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "no-verdict"
    assert payload["reason"] == "focused producer failed"
    assert "This is NOT a pass" in captured.err


def test_nothing_mapped_warns_loudly_and_does_not_block(gate, monkeypatch, capsys) -> None:
    """Policy (a), chosen 2026-07-29: an unmapped file is a MAPPER gap, not a coverage
    gap, so blocking on it would stop a push over the tool's blind spot. It is named
    instead — loudly enough for `run-quality.sh` to surface it on a passing gate."""
    monkeypatch.setattr(
        gate._suggest,
        "build_recommendation",
        lambda *_a, **_k: _recommendation(status="missing", mapped_tests_by_file={}),
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json"]) == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "unproven"
    assert payload["unmapped_changed_pool_files"] == ["scripts/unmapped.py"]
    assert captured.err.startswith("WARNING")
    assert "nothing could be proven before this push" in captured.err


def test_noop_is_quiet(gate, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation(status="noop")
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json"]) == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "noop"
    assert "WARNING" not in captured.err


def test_warning_lines_use_the_head_run_quality_actually_surfaces(gate, capsys) -> None:
    """`run-quality.sh::print_phase_output` only shows a PASSING gate's output when a
    line matches `^(WARNING|WARN|WEAK|ADVISORY)`. A warning that does not start that
    way is invisible on exactly the runs it exists for, which is the failure mode the
    previous lane already had."""
    gate._warn("something unproven")

    assert capsys.readouterr().err.startswith("WARNING (incremental changed-line coverage):")


def test_focused_command_is_instrumentable_pytest(gate) -> None:
    """The suggester emits a `run_standing_pytest.py` wrapper for operator use, which
    coverage cannot instrument. Rebuilding from the same mapping keeps ONE source of
    truth for which tests run while changing how they are launched."""
    command = gate._focused_pytest_command(
        _recommendation(mapped_tests_by_file={"a.py": ["tests/test_b.py"], "c.py": ["tests/test_a.py", "tests/test_b.py"]})
    )

    assert command.startswith("python3 -m pytest -q ")
    # Deduplicated and ordered, so two files sharing a test do not run it twice.
    assert command.endswith("tests/test_a.py tests/test_b.py")
    assert gate._producer.is_instrumentable_pytest_command(command)


def test_focused_command_is_none_when_no_test_is_mapped(gate) -> None:
    assert gate._focused_pytest_command(_recommendation(mapped_tests_by_file={})) is None


def test_run_command_surfaces_stdout_on_failure(gate, tmp_path, capsys) -> None:
    """pytest reports failures on STDOUT. Surfacing only stderr left the operator with
    `the producer failed (exit 1)` and no failing test name — and a gate whose failure
    cannot be diagnosed is a gate that gets disabled."""
    import subprocess

    with pytest.raises(subprocess.CalledProcessError):
        gate._run_command(tmp_path, "echo FAILED_TEST_MARKER_ON_STDOUT; exit 1", "verify")

    assert "FAILED_TEST_MARKER_ON_STDOUT" in capsys.readouterr().err


def test_cli_help_names_the_repo_root_and_base(monkeypatch) -> None:
    result = run_script(SCRIPT, "--help")

    assert result.returncode == 0
    assert "--base-sha" in result.stdout
    assert "--repo-root" in result.stdout


# --------------------------------------------------------------------------- #
# Round-1 review repairs. Each of these was exit 0 reported as `clean` while the
# consumer's own payload said it had established nothing — the exit-0-means-proven
# equivalence this lane exists to break, reintroduced at the surface reporting the
# lane's verdict.
# --------------------------------------------------------------------------- #
def _consumer(stdout: str, returncode: int = 0):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")


def test_a_dirty_pool_is_unestablished_not_clean(gate) -> None:
    """The focused coverage is produced by running pytest against the LIVE worktree
    while the changed-line mapping is computed against HEAD. Line numbers can skew
    between the two trees, so an executed worktree line can be attributed to a
    different HEAD statement — a false PASS, and outside the subset-of-full-coverage
    safety argument, which covers test-subsetting only."""
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": True, "blocking": [], "dirty_pool_unverified": True}))
    )

    assert status == gate.UNESTABLISHED_STATUS
    assert "different tree" in reason


def test_a_limit_that_analyzed_nothing_is_unestablished_not_clean(gate) -> None:
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({
            "ok": True, "blocking": [],
            "reason": "every changed mutation-pool file (2) fell OUTSIDE --limit-to-file; "
                      "this run analyzed nothing and proves nothing about them",
        }))
    )

    assert status == gate.UNESTABLISHED_STATUS
    assert "proves nothing" in reason


def test_an_unreadable_consumer_payload_is_a_no_verdict(gate) -> None:
    """Exit 0 with no readable payload means the exit code stands for nothing."""
    status, reason = gate._verdict_from_consumer(_consumer("not json"))

    assert status == "no-verdict"
    assert "stands for nothing" in reason


def test_a_real_clean_verdict_is_still_clean(gate) -> None:
    """The discriminating control: the repairs narrowed `clean`, they did not delete it.
    Without this, every test above would pass on a surface that never reports clean."""
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": True, "blocking": [], "changed_pool_files": ["scripts/a.py"]}))
    )

    assert status == "clean"
    assert "covered" in reason


def test_blocking_is_read_from_the_exit_code_not_the_payload(gate) -> None:
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": False, "blocking": ["scripts/a.py"]}), returncode=1)
    )

    assert status == "blocked"
    assert "uncovered changed lines" in reason


def test_the_focused_coverage_path_is_not_the_canonical_closeout_artifact(gate) -> None:
    """Writing subset coverage to `reports/mutation/test-coverage.json` would leave it
    at the path the BROAD closeout producer owns, carrying a valid freshness marker, so
    every `--require-fresh-coverage` consumer would read freshness as breadth."""
    default = gate.parse_args(["--repo-root", "."]).coverage_json

    assert default.name == "prepush-focused-coverage.json"
    assert default.as_posix() != "reports/mutation/test-coverage.json"


# --------------------------------------------------------------------------- #
# Round-2 review repair. Round 1 made the lane NAME an unestablished result; round 2
# found that naming it changed nothing, because it still exited 0 -- so one
# uncommitted pool file disarmed the whole lane, and `run-quality.sh` states that a
# live dirty worktree is the normal condition. Exit 0 plus prose is exactly what the
# predecessor did and exactly why it was walked past eight times.
# --------------------------------------------------------------------------- #
def _blocking_consumer_stub(gate, monkeypatch, consumer_payload: dict, returncode: int = 0):
    import subprocess

    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())
    monkeypatch.setattr(gate._producer, "produce_command_coverage", lambda *_a, **_k: {"returncode": 0})
    monkeypatch.setattr(Path, "is_file", lambda _self: True)
    monkeypatch.setattr(
        gate.subprocess,
        "run",
        lambda *_a, **_k: subprocess.CompletedProcess(
            [], returncode, json.dumps(consumer_payload), ""
        ),
    )


def test_an_unestablished_result_refuses_at_push_time(gate, monkeypatch, capsys) -> None:
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": [], "dirty_pool_unverified": True})

    code = gate.main(
        ["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json", "--refuse-unestablished"]
    )

    assert code == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == gate.UNESTABLISHED_STATUS
    assert "an unestablished changed-line result is not a pass" in captured.err


def test_the_same_result_stays_non_blocking_mid_work(gate, monkeypatch, capsys) -> None:
    """The discriminating control. A dirty worktree IS the normal state during the
    verify phase, which runs before commit, so refusing unconditionally would hard-fail
    every ordinary run and get the lane disabled — the failure mode being repaired."""
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": [], "dirty_pool_unverified": True})

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json"])

    assert code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == gate.UNESTABLISHED_STATUS
    assert "established no changed-line verdict" in captured.err


def test_policy_a_stays_non_blocking_even_at_push_time(gate, monkeypatch, capsys) -> None:
    """`--refuse-unestablished` must NOT govern policy (a). An unmapped file is a mapper
    gap, and the repo owner's decision is that a push is never stopped over the tool's
    blind spot. Conflating the two would silently overturn that decision."""
    monkeypatch.setattr(
        gate._suggest,
        "build_recommendation",
        lambda *_a, **_k: _recommendation(status="missing", mapped_tests_by_file={}),
    )

    code = gate.main(
        ["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json", "--refuse-unestablished"]
    )

    assert code == 0
    assert json.loads(capsys.readouterr().out)["status"] == "unproven"


def test_missing_focused_coverage_refuses_instead_of_stalling(gate, monkeypatch, capsys) -> None:
    """The consumer runs with `--reuse-coverage`; a missing file makes it fall through
    to the BROAD probe, turning a ~24s lane into an 11-15 minute stall with no
    explanation. A gate that hangs is a gate that gets disabled."""
    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())
    monkeypatch.setattr(gate._producer, "produce_command_coverage", lambda *_a, **_k: {"returncode": 0})
    monkeypatch.setattr(Path, "is_file", lambda _self: False)

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--json"])

    assert code == gate.NO_VERDICT_EXIT
    captured = capsys.readouterr()
    assert json.loads(captured.out)["reason"] == "focused coverage missing after produce"
    assert "wrote no coverage" in captured.err
