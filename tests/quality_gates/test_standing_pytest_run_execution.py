"""How the standing runner RUNS its child, as opposed to what command it builds.

SPLIT FROM `test_standing_pytest_runner` (S6, 2026-08-15) when that file crossed
its length cap. This file owns what S6 ADDED to the run: the monitored child, the
run record that outlives its caller, the signal handling that lets an enclosing
guard reap the process tree, and the read-back path.

Stated narrowly on purpose. A first draft of this docstring claimed the sibling
"owns command CONSTRUCTION" while this file "owns EXECUTION", and a round-2
reviewer falsified it from the sibling itself: `test_standing_pytest_runner.py`
still holds four execution tests that patch `run_monitored_phase`, and retention
behaviour lives in `test_retention_refusal_coverage.py` besides. The split is
real but PARTIAL, and describing a partial split as a clean seam is the same
over-claim this slice keeps catching in its own prose.
"""

from __future__ import annotations

import json
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.fifo_witness import FifoWitness, shell_holder_snippet

ROOT = Path(__file__).resolve().parents[2]


def _runner_args(repo: Path, **overrides: object) -> SimpleNamespace:
    defaults = dict(
        repo_root=repo,
        mode="read-only",
        basetemp=repo / "basetemp",
        include_release_only=False,
        keep_basetemp=True,
        pytest_target=[],
        extra_pytest_target=[],
        print_command=False,
        timeout_seconds=None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_standing_pytest_runs_its_child_monitored_and_streamed(tmp_path: Path, monkeypatch) -> None:
    """SC11. The repo's longest child was a bare `subprocess.run`.

    Two properties, and both are load-bearing in opposite directions. It must go
    through the monitored primitive -- otherwise the process tree is untracked and
    a wrapper timeout orphans every xdist worker, which is the recorded loss. And
    it must pass `capture=False` -- otherwise a multi-minute suite that renders
    live progress goes silent, which is the regression a naive conversion makes
    and which no exit code would reveal.
    """
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    seen: dict[str, object] = {}

    def fake_phase(command, **kwargs):
        seen["command"] = command
        seen.update(kwargs)
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.5, stdout="", stderr=""
        )

    monkeypatch.setattr(runner, "run_monitored_phase", fake_phase)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *a, **k: ["pytest", "-q"])
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda *a, **k: None)

    assert runner.run_standing_pytest(_runner_args(repo)) == 0

    assert seen["capture"] is False, "capturing the body would silence a live suite"
    assert seen["phase"] == "standing-pytest"
    # Unbounded BY DEFAULT: a bound short enough to catch a hang is short enough
    # to kill a healthy 20-minute run, and the loss this repairs was an untracked
    # tree rather than a missing bound.
    assert seen["timeout_seconds"] is None


def test_standing_pytest_leaves_a_readable_record_of_a_run_that_finished(
    tmp_path: Path, monkeypatch
) -> None:
    import json

    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    monkeypatch.setattr(
        runner,
        "run_monitored_phase",
        lambda command, **kwargs: SimpleNamespace(
            returncode=2, timed_out=True, elapsed_seconds=9.0, stdout="", stderr="timed out"
        ),
    )
    monkeypatch.setattr(runner, "build_pytest_command", lambda *a, **k: ["pytest", "-q"])
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda *a, **k: None)

    assert runner.run_standing_pytest(_runner_args(repo)) == 2

    # The half monitoring alone does not give: when the CALLER dies mid-suite its
    # transcript dies with it, so the outcome has to outlive the caller on disk.
    record = json.loads(runner.run_record_path(repo).read_text(encoding="utf-8"))
    assert record["state"] == "timed-out"
    assert record["returncode"] == 2
    assert record["timed_out"] is True
    # The basetemp is kept on failure, so naming it is what makes the run
    # diagnosable rather than merely known to have failed.
    assert record["basetemp"] == str(repo / "basetemp")


def test_standing_pytest_run_record_survives_an_unwritable_state_dir(
    tmp_path: Path, monkeypatch
) -> None:
    # Telemetry must never be why a suite fails. A runner that refused to run
    # because it could not write its own record would be strictly worse than one
    # with no record at all.
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)
    monkeypatch.setattr(Path, "mkdir", lambda *a, **k: (_ for _ in ()).throw(OSError("read-only")))

    runner.write_run_record(repo, {"state": "finished"})

    assert not runner.run_record_path(repo).exists()


def test_standing_pytest_run_record_is_external_runtime_telemetry(tmp_path: Path) -> None:
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    path = runner.run_record_path(repo)

    assert repo not in path.parents
    assert path.name == "last-run.json"
    assert path.parent.parent.name == "standing-pytest"


def test_standing_pytest_records_are_repo_scoped_under_a_shared_runtime_root(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts.gates_support import run_standing_pytest as runner

    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)

    first_record = runner.run_record_path(first)
    second_record = runner.run_record_path(second)

    assert first_record != second_record
    assert first_record.name == second_record.name == "last-run.json"
    assert first_record.parent.parent.name == second_record.parent.parent.name == "standing-pytest"


def test_runtime_root_keeps_auto_identity_across_repeated_calls(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import runtime_bootstrap

    repo = tmp_path / "repo"
    other = tmp_path / "other"
    repo.mkdir()
    other.mkdir()
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)

    first = runtime_bootstrap.configure_runtime_environment(repo)
    second = runtime_bootstrap.configure_runtime_environment(repo)

    assert second["CHARNESS_RUNTIME_ROOT_AUTO"] == "1"
    assert second["CHARNESS_RUNTIME_REPO_KEY"] == first["CHARNESS_RUNTIME_REPO_KEY"]
    assert runtime_bootstrap.runtime_root(other) != runtime_bootstrap.runtime_root(repo)


def test_print_last_run_reads_back_a_record_and_refuses_when_absent(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    """The READ-BACK half of "its result retrievable", which had no test at all.

    The write side was pinned and the read side was not -- and the read side is
    the entire point of the record, because it is what a session reaches for
    after the run's own caller died.
    """
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)

    # Absent: refuse loudly rather than printing nothing and exiting 0, which
    # would read as "the last run had no result".
    assert runner.main(["--repo-root", str(repo), "--print-last-run"]) == 1
    assert "no standing-pytest run record" in capsys.readouterr().err

    runner.write_run_record(repo, {"state": "timed-out", "returncode": 124})

    assert runner.main(["--repo-root", str(repo), "--print-last-run"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"state": "timed-out", "returncode": 124}


def test_a_supplied_timeout_reaches_the_monitored_phase(tmp_path: Path, monkeypatch) -> None:
    # Only the None default was asserted; nothing proved a supplied value was
    # threaded through rather than dropped.
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    seen: dict[str, object] = {}

    def fake_phase(command, **kwargs):
        seen.update(kwargs)
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        )

    monkeypatch.setattr(runner, "run_monitored_phase", fake_phase)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *a, **k: ["pytest", "-q"])
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda *a, **k: None)

    runner.run_standing_pytest(_runner_args(repo, timeout_seconds=42.5))

    assert seen["timeout_seconds"] == 42.5


def test_the_heartbeat_interval_is_operator_overridable_and_refuses_nonsense(
    monkeypatch,
) -> None:
    from scripts.gates_support import run_standing_pytest as runner

    monkeypatch.delenv(runner.HEARTBEAT_INTERVAL_ENV, raising=False)
    default = runner._heartbeat_seconds()
    assert default > 0

    monkeypatch.setenv(runner.HEARTBEAT_INTERVAL_ENV, "3")
    assert runner._heartbeat_seconds() == 3

    # A malformed value must fall back rather than crash the suite: a tuning knob
    # is never allowed to be why the standing gate cannot start.
    monkeypatch.setenv(runner.HEARTBEAT_INTERVAL_ENV, "not-a-number")
    assert runner._heartbeat_seconds() == default


def test_an_interrupted_run_records_a_terminal_state_and_marks_its_basetemp(
    tmp_path: Path, monkeypatch
) -> None:
    """A record stuck at `running` is worse than no record.

    It is indistinguishable from a live run, which is the ambiguity the record
    exists to remove. And an unmarked basetemp is never pruned, so every
    interrupted run would leak one permanently. Both were true until round 1.
    """
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    # A RUNNER-OWNED basetemp (`--basetemp` unset), because marking and pruning
    # only ever apply to roots the runner owns -- an explicitly supplied one
    # belongs to the caller and is left alone on every path, interrupt included.
    basetemp = tmp_path / "pytest-of-user" / "charness-run-1"
    basetemp.mkdir(parents=True)

    def interrupted(command, **kwargs):
        raise KeyboardInterrupt("terminated by signal 15")

    monkeypatch.setattr(runner, "run_monitored_phase", interrupted)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *a, **k: ["pytest", "-q"])
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda *a, **k: None)
    monkeypatch.setattr(runner, "default_basetemp", lambda _repo_root: basetemp)

    with pytest.raises(KeyboardInterrupt):
        runner.run_standing_pytest(_runner_args(repo, basetemp=None))

    record = json.loads(runner.run_record_path(repo).read_text(encoding="utf-8"))
    assert record["state"] == "interrupted"
    assert record["returncode"] is None
    assert (basetemp / runner._FAILED_BASETEMP_MARKER).is_file()


@pytest.mark.boundary_contract(
    reason="prove the standing runner's SIGTERM path reaps the real child process tree"
)
def test_sigterm_is_converted_so_the_guard_can_reap_the_child(monkeypatch) -> None:
    """SIGTERM's default disposition runs no cleanup at all.

    That matters because this runner is usually NESTED inside another monitored
    phase, and its child lives in its own session: without this, an outer guard's
    kill takes the runner down and leaves the xdist tree running. The handler is
    what lets the guard's `except BaseException: _kill_tree` run first.
    """
    from scripts.gates_support import run_standing_pytest as runner

    before = signal.getsignal(signal.SIGTERM)
    with runner._terminate_reaps_the_child():
        installed = signal.getsignal(signal.SIGTERM)
        assert installed is not before
        with pytest.raises(KeyboardInterrupt):
            installed(signal.SIGTERM, None)

    # And it puts the previous disposition back, so importing this runner does
    # not silently change signal behaviour for whatever called it.
    assert signal.getsignal(signal.SIGTERM) is before


@pytest.mark.boundary_contract(
    reason="prove the standing runner's SIGTERM path reaps the real child process tree"
)
def test_a_wrapper_sigterm_reaps_the_real_child_tree(tmp_path: Path) -> None:
    """The end-to-end proof the round-1 blocker's fix had been missing.

    Everything else here tests the handler in isolation from the child and the
    child in isolation from the handler. Round 2's point: the composition -- a
    SIGTERM to the runner actually reaping the pytest tree -- was asserted only
    by the shape of the code. This runs the real thing.

    A fake `pytest` that backgrounds a grandchild stands in for xdist workers,
    because the property under test is that the whole SESSION dies, not that one
    process does. The FIFO line forces the fake pytest to have started, and EOF
    proves that the shell, its background child, and both sleeping processes all
    died with it.

    The FIFO is also the ordering boundary: no assertion runs until the fake
    pytest has opened fd 3 and published its start line.
    """
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    with FifoWitness(tmp_path / "witness") as witness:
        fake_pytest = tmp_path / "fake_pytest.sh"
        fake_pytest.write_text(
            f"#!/bin/bash\n{shell_holder_snippet(witness.path, 'started')}\n(sleep 3600) &\nsleep 3600\n",
            encoding="utf-8",
        )
        fake_pytest.chmod(0o755)

        driver = tmp_path / "driver.py"
        driver.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ROOT)!r})\n"
            f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
            "from scripts.gates_support import run_standing_pytest as runner\n"
            "from types import SimpleNamespace\n"
            f"runner.build_pytest_command = lambda *a, **k: [{str(fake_pytest)!r}]\n"
            "runner.ensure_external_temp_root = lambda *a, **k: None\n"
            "runner.run_standing_pytest(SimpleNamespace(\n"
            f"    repo_root=__import__('pathlib').Path({str(repo)!r}),\n"
            f"    mode='read-only', basetemp=__import__('pathlib').Path({str(tmp_path / 'bt')!r}),\n"
            "    include_release_only=False, keep_basetemp=True, pytest_target=[],\n"
            "    extra_pytest_target=[], print_command=False, timeout_seconds=None,\n"
            "))\n",
            encoding="utf-8",
        )

        proc = subprocess.Popen([sys.executable, str(driver)], cwd=tmp_path)
        try:
            assert witness.wait_line() == "started"

            # Exactly what an enclosing `run_monitored_phase` does at its budget.
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=15)
        finally:
            if proc.poll() is None:  # pragma: no cover - only on a failed reap
                proc.kill()
                proc.wait(timeout=10)

        # EOF is the proof that the whole tree released fd 3. With
        # `_terminate_reaps_the_child` disabled, this read blocks until the
        # runner's budget ends it; with the handler in place, it completes here.
        witness.wait_eof()
