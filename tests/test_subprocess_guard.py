from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

import scripts.core.subprocess_guard as subprocess_guard
from scripts.core.subprocess_guard import (
    DEFAULT_HEARTBEAT_SECONDS,
    DRAIN_UNAVAILABLE,
    MINIMUM_HEARTBEAT_SECONDS,
    TIMEOUT_EXIT_CODE,
    heartbeat_interval_from_env,
    render_display,
    run_monitored_phase,
    run_process,
    run_processes_in_order,
)
from tests.fifo_witness import FifoWitness, shell_holder_snippet

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.boundary_contract(
    reason="these tests assert child exit, signal, timeout, and process-group behavior"
)


def test_run_process_returns_timeout_completed_process(tmp_path: Path) -> None:
    result = run_process(
        ["python3", "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=0.1,
    )

    assert result.returncode == TIMEOUT_EXIT_CODE
    assert "timed out after 0.1s" in result.stderr


def test_run_processes_in_order_preserves_input_order(tmp_path: Path) -> None:
    results = run_processes_in_order(
        [
            ["python3", "-c", "import time; time.sleep(0.2); print('slow')"],
            ["python3", "-c", "print('fast')"],
        ],
        cwd=tmp_path,
        timeout_seconds=None,
    )

    assert [result.stdout.strip() for result in results] == ["slow", "fast"]


def test_monitored_phase_streams_lifecycle_while_isolating_the_body(tmp_path: Path, capsys) -> None:
    outcome = run_monitored_phase(
        # The tokens are ASSEMBLED in the child so they cannot appear in the command
        # text the lifecycle lines legitimately echo back.
        ["python3", "-c", "import sys; print('body' + '-out'); print('body' + '-err', file=sys.stderr)"],
        cwd=tmp_path,
        phase="probe",
        timeout_seconds=30,
    )

    assert outcome.ok
    assert outcome.stdout.strip() == "body-out"
    assert outcome.stderr.strip() == "body-err"
    events = capsys.readouterr().err
    assert events.startswith("RUN [probe] ")
    assert "PASS [probe] " in events
    # The child's own output must NOT leak into the parent's lifecycle stream:
    # isolated bodies are what keeps concurrent phases readable.
    assert "body-out" not in events
    assert "body-err" not in events


def test_monitored_phase_can_stream_the_body_instead_of_capturing_it(tmp_path: Path) -> None:
    """SC11's enabling half: the third caller choice the module docstring deferred.

    Run through a real subprocess rather than in-process, because the property
    under test is that the CHILD writes to the parent's OWN file descriptors --
    `capsys` replaces `sys.stdout` at the Python level and would not see a
    descriptor a grandchild inherited, so an in-process assertion here could pass
    for a mode that actually discarded the output.
    """
    script = tmp_path / "driver.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from scripts.core.subprocess_guard import run_monitored_phase\n"
        "outcome = run_monitored_phase(\n"
        "    [sys.executable, '-c', \"import sys; print('body' + '-out'); \"\n"
        "     \"print('body' + '-err', file=sys.stderr)\"],\n"
        f"    cwd={str(tmp_path)!r}, phase='streamed', timeout_seconds=30, capture=False,\n"
        ")\n"
        "print('RC', outcome.returncode)\n"
        "print('CAPTURED', repr(outcome.stdout), repr(outcome.stderr))\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, check=False, cwd=tmp_path
    )

    assert completed.returncode == 0, completed.stderr
    # The body reached the operator's terminal, on the stream the child chose.
    assert "body-out" in completed.stdout
    assert "body-err" in completed.stderr
    # The lifecycle is still emitted, so a silent stretch is still distinguishable
    # from a dead one.
    assert "RUN [streamed] " in completed.stderr
    assert "PASS [streamed] " in completed.stderr
    assert "RC 0" in completed.stdout
    # And the outcome reports EMPTY bodies rather than pretending it holds them.
    # A caller that reads `outcome.stdout` in this mode must find nothing, not a
    # partial or stale capture.
    assert "CAPTURED '' ''" in completed.stdout


def test_monitored_phase_streaming_still_kills_the_whole_group_on_timeout(
    monkeypatch, tmp_path: Path
) -> None:
    """Streaming must not cost the group kill; both observations are forced.

    The property the standing runner actually buys: an untracked xdist tree is
    what turned two wrapper timeouts into two lost runs.

    The budget is spent on a CONTROLLED clock rather than on the wall. The guard's
    `time.monotonic` reads 0 until the shell has opened the witness and published
    its line, and 100 from then on, so the budget is judged spent only once the
    tree has PROVABLY formed. The previous version slept and then checked a marker
    file, which passed vacuously whenever the kill landed before the backgrounded
    grandchild had started at all. `_await_child` still calls
    `communicate(timeout=interval)` in real time, so it beats every
    `heartbeat_seconds` and re-reads the fake clock on each beat.

    The kill itself is then proved by EOF on the witness: the shell, the
    backgrounded subshell that inherited descriptor 3, and both sleeps have all
    gone. A survivor would still hold the write end and the read would not return.
    """
    with FifoWitness(tmp_path / "witness") as witness:
        budget_spent = False

        def fake_monotonic() -> float:
            nonlocal budget_spent
            if not budget_spent and witness.has_line():
                budget_spent = True
            return 100.0 if budget_spent else 0.0

        monkeypatch.setattr("scripts.core.subprocess_guard.time.monotonic", fake_monotonic)
        outcome = run_monitored_phase(
            [
                "/bin/bash",
                "-c",
                # The holder runs BEFORE the fork, so the background job inherits
                # descriptor 3 and EOF covers the whole tree rather than the shell.
                #
                # The sleeps outlast any plausible run ON PURPOSE. A survivor that
                # could reach its own end would let `wait_eof()` return for the
                # wrong reason, and the test would read "killed" off a tree that
                # merely died of old age.
                f"{shell_holder_snippet(witness.path, 'tree-up')}; (sleep 3600) & sleep 3600",
            ],
            cwd=tmp_path,
            phase="streamed-timeout",
            timeout_seconds=1.0,
            heartbeat_seconds=0.2,
            capture=False,
        )

        assert outcome.timed_out
        assert outcome.returncode == TIMEOUT_EXIT_CODE
        # The kill proof, and it is the RETURN of this read rather than its value:
        # EOF arrives exactly when no process holds the write end. A backgrounded
        # grandchild that outlived the group kill would still hold it, and this
        # would not return. (The unread `tree-up` line is what it hands back; the
        # controlled clock peeked at it without consuming it.)
        witness.wait_eof()


def test_monitored_phase_reports_failure_status_and_returncode(tmp_path: Path, capsys) -> None:
    outcome = run_monitored_phase(
        ["python3", "-c", "raise SystemExit(3)"],
        cwd=tmp_path,
        phase="failing",
        timeout_seconds=30,
    )

    assert outcome.returncode == 3
    assert not outcome.ok
    assert not outcome.timed_out
    assert "FAIL [failing] " in capsys.readouterr().err


def test_monitored_phase_beats_before_it_kills_an_over_budget_child(tmp_path: Path, capsys) -> None:
    """A child that blows the whole budget in its first interval still reports."""
    outcome = run_monitored_phase(
        ["python3", "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        phase="over-budget",
        timeout_seconds=0.05,
        heartbeat_seconds=0.1,
    )

    assert outcome.returncode == TIMEOUT_EXIT_CODE
    assert outcome.timed_out
    assert "timed out after 0.05s" in outcome.stderr
    events = capsys.readouterr().err
    assert "HEARTBEAT [over-budget] elapsed=" in events
    assert "FAIL [over-budget] " in events


def test_monitored_phase_repeats_bounded_heartbeats_on_a_supplied_display(monkeypatch, tmp_path: Path, capsys) -> None:
    class FakeProcess:
        returncode = 0

        def __init__(self) -> None:
            self.calls = 0

        def communicate(self, timeout=None):
            self.calls += 1
            if self.calls <= 2:
                raise subprocess.TimeoutExpired(["fake"], timeout)
            return "", ""

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    monkeypatch.setattr(subprocess, "Popen", lambda *_args, **_kwargs: FakeProcess())
    monkeypatch.setattr("scripts.core.subprocess_guard.time.monotonic", lambda: 0.0)

    outcome = run_monitored_phase(
        ["/bin/bash", "-lc", "export PATH=/wrapper; pytest -q"],
        cwd=tmp_path,
        phase="verify",
        timeout_seconds=1800,
        heartbeat_seconds=0.01,
        display="pytest -q",
    )

    events = capsys.readouterr().err
    assert events.count("HEARTBEAT [verify] elapsed=0.0s pytest -q") == 2
    assert "PASS [verify] 0.0s pytest -q" in events
    # The supplied display is what the operator reads; the wrapped shell body must
    # not reach any lifecycle line.
    assert "export PATH=/wrapper" not in events
    assert outcome.display == "pytest -q"


def test_monitored_phase_bound_holds_when_a_grandchild_outlives_the_kill(tmp_path: Path) -> None:
    """The kill must reach the process GROUP, or the bound is not a bound.

    `process.kill()` signals only the direct child, and `communicate()` waits for
    EOF on the PIPES — which a surviving grandchild still holds. Measured before
    the group kill: a 1s budget against this command returned after 25.0s.
    """
    outcome = run_monitored_phase(
        "python3 -c 'import time; time.sleep(25)' & sleep 25",
        cwd=tmp_path,
        phase="grandchild",
        timeout_seconds=1.0,
        heartbeat_seconds=0.3,
        shell=True,
        executable="/bin/bash",
    )

    assert outcome.timed_out
    assert outcome.returncode == TIMEOUT_EXIT_CODE
    # The load-bearing assertion, and the only one that can tell the two outcomes
    # apart. Measured elapsed time cannot: the drain bound caps it either way, so
    # "the group kill worked" and "only the direct child died and the bounded
    # drain gave up" produce the same number. The grandchild is in the child's
    # group, so a group kill reaches it and the pipes close; with a
    # direct-child-only kill it survives and the drain fails.
    assert DRAIN_UNAVAILABLE not in outcome.stderr


def test_monitored_phase_clamps_a_heartbeat_wider_than_its_own_budget(tmp_path: Path, capsys) -> None:
    """A wide interval must not silence the beat AND defer the kill past the bound.

    The budget is only checked ON the beat, so an unclamped interval turns an
    operator's "quiet the output" knob back into the silent window this primitive
    exists to close.
    """
    outcome = run_monitored_phase(
        ["python3", "-c", "import time; time.sleep(20)"],
        cwd=tmp_path,
        phase="wide-beat",
        timeout_seconds=0.5,
        heartbeat_seconds=3600.0,
    )

    # A 3600s interval that was NOT clamped could produce neither of these: the
    # phase would still be waiting on its first beat, silent, well past the bound.
    assert outcome.timed_out
    assert "HEARTBEAT [wide-beat] elapsed=" in capsys.readouterr().err


def test_resolve_interval_clamps_the_beat_to_the_budget() -> None:
    """The clamp itself, with no child and no clock: the arithmetic the phase relies on."""
    # Wider than the budget: the beat becomes the budget, so the budget is checked.
    assert subprocess_guard._resolve_interval(3600.0, 0.5) == 0.5
    # Narrower than the floor, from either side: the floor wins, so a beat can
    # never become a busy loop.
    assert subprocess_guard._resolve_interval(0.01, 0.5) == MINIMUM_HEARTBEAT_SECONDS
    assert subprocess_guard._resolve_interval(3600.0, 0.01) == MINIMUM_HEARTBEAT_SECONDS
    # No budget, nothing to clamp against: the caller's interval stands.
    assert subprocess_guard._resolve_interval(3600.0, None) == 3600.0


#: A grandchild that ESCAPES the group kill: its own session, inheriting the pipes.
#: This is what forces the post-kill drain to hit its bound.
_ESCAPING_GRANDCHILD = (
    "import os, subprocess, sys, time\n"
    "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],\n"
    "                 start_new_session=True)\n"
    "time.sleep({child_sleep})\n"
    "raise SystemExit({exit_code})\n"
)


def test_monitored_phase_bounds_the_drain_when_a_descendant_escapes_the_kill(tmp_path: Path) -> None:
    """A timeout must not become a second, unbounded hang.

    The grandchild starts its OWN session, so the group kill cannot reach it, and it
    inherits the pipes — exactly the shape that made `communicate()` wait forever.
    """
    outcome = run_monitored_phase(
        ["python3", "-c", _ESCAPING_GRANDCHILD.format(child_sleep=30, exit_code=0)],
        cwd=tmp_path,
        phase="escaped",
        timeout_seconds=0.5,
        heartbeat_seconds=0.2,
    )

    assert outcome.timed_out
    assert outcome.returncode == TIMEOUT_EXIT_CODE
    # By construction this IS the proof the drain bound fired: the guard only ever
    # substitutes DRAIN_UNAVAILABLE for the body on the `TimeoutExpired` branch of
    # `_drain`, so the phase reaching this line at all means `communicate()`
    # stopped at POST_KILL_DRAIN_SECONDS instead of waiting on the escaped
    # grandchild's pipes forever. No measured elapsed time can add to that.
    assert outcome.stderr.startswith(DRAIN_UNAVAILABLE)


def test_monitored_phase_does_not_relabel_a_child_that_finished_before_the_kill(tmp_path: Path) -> None:
    """A phase that PASSED past its budget keeps its real exit status.

    The child exits 0 just after the budget, leaving a pipe-holding grandchild that
    escapes the group kill. `timed_out` must follow whether the CHILD finished, not
    whether an unrelated descendant happened to close a pipe in time — otherwise a
    green quality gate aborts the publish it just passed.
    """
    # Beats land at 0.9s and 1.8s; the budget is only CHECKED on a beat, so the
    # first check is at 1.8s. The child exits at 1.4s — after the 1.0s budget, well
    # before the check — which is the gap this branch exists for.
    outcome = run_monitored_phase(
        ["python3", "-c", _ESCAPING_GRANDCHILD.format(child_sleep=1.4, exit_code=0)],
        cwd=tmp_path,
        phase="late-pass",
        timeout_seconds=1.0,
        heartbeat_seconds=0.9,
    )

    assert not outcome.timed_out, "a child that exited on its own is not a timeout"
    assert outcome.returncode == 0
    assert "timed out after" not in outcome.stderr


def test_monitored_phase_kills_the_child_when_the_wait_raises(monkeypatch, tmp_path: Path) -> None:
    """`subprocess.run` kills its child on ANY exception; a bare Popen does not.

    Without this, an interrupted release publish leaves the quality runner alive and
    mutating the worktree that the rollback path then restores and reports clean.
    """
    seen: dict[str, subprocess.Popen] = {}

    def exploding_await(process, **_kwargs):
        seen["process"] = process
        raise KeyboardInterrupt

    monkeypatch.setattr("scripts.core.subprocess_guard._await_child", exploding_await)

    with pytest.raises(KeyboardInterrupt):
        run_monitored_phase(
            ["python3", "-c", "import time; time.sleep(30)"],
            cwd=tmp_path,
            phase="interrupted",
            timeout_seconds=30,
        )

    # A REAPED child is a dead child, and the cleanup path this test exists for --
    # `_kill_tree`, then `_drain`'s `communicate`, with `Popen.__exit__` behind it
    # -- reaps it before `run_monitored_phase` re-raises. So `returncode` is set by
    # the time control returns here, with no waiting to do. Probing the raw pid
    # with `os.kill(pid, 0)` was the wrong question as well as a timed one: a
    # reaped pid may already have been recycled, and the probe would then be
    # asking about whoever holds it now.
    assert seen["process"].returncode is not None
    # Killed, not exited: the child was sleeping 30s and had nothing to exit 0 for.
    assert seen["process"].returncode != 0


def test_monitored_phase_kills_the_tree_when_sigterm_interrupts_popen(monkeypatch, tmp_path: Path) -> None:
    """A signal between fork/exec and Popen binding must not orphan the tree.

    The GRANDCHILD holds one FIFO open for its whole life, which turns both halves
    of this test into observations it forces rather than deadlines it polls:

    - `wait_line()` blocks until the grandchild is running AND holding the witness,
      so the SIGTERM is injected against a fully formed tree. The marker-file poll
      it replaces could time out, and worse, could win its race against a tree that
      had not been built yet.
    - `wait_eof()` blocks until the grandchild -- the only writer -- is gone, which
      is exactly the claim. The `os.killpg(pgid, 0)` and `os.kill(pid, 0)` loops it
      replaces asked a question a recycled pid can answer wrongly.
    """
    if not hasattr(os, "killpg"):
        pytest.skip("constructor interruption tree proof requires process groups")

    with FifoWitness(tmp_path / "witness") as witness:
        # Built by hand rather than with `holder_snippet`: the line is the pair
        # (parent pid, own pid), which only the grandchild can compute, at runtime.
        # Both sleeps outlast any plausible run ON PURPOSE: a grandchild that could
        # reach its own end would let `wait_eof()` return for the wrong reason.
        grandchild_code = (
            "import os, time\n"
            f"_witness = open({str(witness.path)!r}, 'w')\n"
            "_witness.write(f'{os.getppid()} {os.getpid()}\\n')\n"
            "_witness.flush()\n"
            "time.sleep(3600)\n"
        )
        child_code = (
            "import subprocess, sys, time\n"
            f"subprocess.Popen([sys.executable, '-c', {grandchild_code!r}])\n"
            "time.sleep(3600)\n"
        )
        observed: dict[str, object] = {}
        original_popen = subprocess_guard.subprocess.Popen
        original_kill_tree = subprocess_guard._kill_tree
        kill_calls: list[int] = []

        def injected_popen(command, **kwargs):
            process = original_popen(command, **kwargs)
            observed["process"] = process
            observed["pids"] = tuple(int(value) for value in witness.wait_line().split())
            observed["injection"] = "after-real-Popen-before-return"
            os.kill(os.getpid(), signal.SIGTERM)
            return process

        def record_kill(process):
            kill_calls.append(process.pid)
            original_kill_tree(process)

        def raise_sigterm(_signum, _frame):
            raise KeyboardInterrupt("SIGTERM injected before Popen binding")

        previous_handler = signal.signal(signal.SIGTERM, raise_sigterm)
        monkeypatch.setattr(subprocess_guard.subprocess, "Popen", injected_popen)
        monkeypatch.setattr(subprocess_guard, "_kill_tree", record_kill)
        process = None
        try:
            with pytest.raises(KeyboardInterrupt, match="before Popen binding"):
                run_monitored_phase(
                    [sys.executable, "-c", child_code],
                    cwd=tmp_path,
                    phase="popen-constructor-interrupted",
                    timeout_seconds=30,
                )
            process = observed["process"]
        finally:
            signal.signal(signal.SIGTERM, previous_handler)
            process = observed.get("process", process)
            if process is not None and process.poll() is None:
                original_kill_tree(process)
                process.communicate(timeout=2)

        assert observed["injection"] == "after-real-Popen-before-return"
        assert len(kill_calls) == 1
        assert process.returncode is not None
        # The witness line names the holder's parent, so this pins the SHAPE the
        # test claims to have built: the writer really is a grandchild of the guard,
        # one level below the process the guard itself holds.
        assert observed["pids"][0] == process.pid
        assert witness.wait_eof() == b"", "a grandchild outlived the constructor cleanup"


def test_monitored_phase_keeps_partial_output_across_a_timeout(tmp_path: Path) -> None:
    """`whatever output was collected` is a docstring promise; pin it."""
    outcome = run_monitored_phase(
        ["python3", "-c", "import sys, time; print('partial' + '-body'); sys.stdout.flush(); time.sleep(20)"],
        cwd=tmp_path,
        phase="partial",
        timeout_seconds=0.5,
        heartbeat_seconds=0.2,
    )

    assert outcome.timed_out
    assert "partial-body" in outcome.stdout
    assert DRAIN_UNAVAILABLE not in outcome.stderr


def test_monitored_phase_names_the_supplied_display_in_the_timeout_marker(tmp_path: Path) -> None:
    """The marker uses the bounded display, not the wrapped body it stands for."""
    outcome = run_monitored_phase(
        ["/bin/bash", "-lc", "export PATH=/a/very/long/wrapper/dir:$PATH; sleep 20"],
        cwd=tmp_path,
        phase="wrapped",
        timeout_seconds=0.4,
        heartbeat_seconds=0.2,
        display="pytest -q",
    )

    assert "timed out after 0.4s while running `pytest -q`" in outcome.stderr
    assert "export PATH=" not in outcome.stderr


def test_monitored_phase_forwards_env_and_pipe_configuration(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakeProcess:
        returncode = 0
        pid = -1

        def communicate(self, timeout=None):
            return "", ""

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    run_monitored_phase(
        ["true"],
        cwd=tmp_path,
        phase="forwarding",
        timeout_seconds=30,
        env={"CHARNESS_PROBE": "1"},
        shell=True,
        executable="/bin/bash",
    )

    assert captured["env"] == {"CHARNESS_PROBE": "1"}
    assert captured["cwd"] == tmp_path
    assert captured["shell"] is True
    assert captured["executable"] == "/bin/bash"
    assert captured["text"] is True
    assert captured["stdout"] is subprocess.PIPE
    assert captured["stderr"] is subprocess.PIPE
    # Without a new session the kill cannot reach a shell's grandchildren.
    assert captured["start_new_session"] is True


def test_monitored_phase_runs_unbounded_when_the_budget_is_none(tmp_path: Path, capsys) -> None:
    """`timeout_seconds=None` means the same thing it means for `run_process`."""
    outcome = run_monitored_phase(
        ["python3", "-c", "import time; time.sleep(0.35)"],
        cwd=tmp_path,
        phase="unbounded",
        timeout_seconds=None,
        heartbeat_seconds=0.1,
    )

    assert outcome.returncode == 0
    assert not outcome.timed_out
    assert "timed out after" not in outcome.stderr
    assert "HEARTBEAT [unbounded] elapsed=" in capsys.readouterr().err


class _FakeProcess:
    """Stands in for a Popen so the kill guards can be exercised without a real kill."""

    def __init__(self, *, pid: int, returncode: int | None = None, waits: list[bool] | None = None) -> None:
        self.pid = pid
        self.returncode = returncode
        self.killed = 0
        self._waits = list(waits or [])

    def kill(self) -> None:
        self.killed += 1

    def wait(self, timeout=None):
        if self._waits and not self._waits.pop(0):
            raise subprocess.TimeoutExpired(["fake"], timeout)
        return 0


def test_kill_tree_never_signals_an_already_reaped_pid(monkeypatch) -> None:
    """bpo-38630: a reaped pid may already belong to somebody else.

    `Popen.send_signal` self-guards on this. `os.killpg` is worse than `os.kill`
    here — it would destroy a recycled pid's whole GROUP, plausibly our own.
    """

    def forbidden(*_args, **_kwargs):
        raise AssertionError("killpg must not run against a reaped pid")

    monkeypatch.setattr(os, "killpg", forbidden)
    process = _FakeProcess(pid=-1, returncode=0)

    subprocess_guard._kill_tree(process)

    assert process.killed == 0


def test_kill_tree_falls_back_to_the_child_when_the_group_is_our_own(monkeypatch) -> None:
    """If `start_new_session` did not take effect, a group kill kills the caller."""

    def forbidden(*_args, **_kwargs):
        raise AssertionError("killpg must not run against the caller's own group")

    monkeypatch.setattr(os, "killpg", forbidden)
    monkeypatch.setattr(os, "getpgid", lambda _pid: os.getpgrp())
    process = _FakeProcess(pid=424242)

    subprocess_guard._kill_tree(process)

    assert process.killed == 1


def test_kill_tree_falls_back_to_the_child_when_no_group_is_addressable(monkeypatch) -> None:
    def missing(_pid):
        raise ProcessLookupError

    monkeypatch.setattr(os, "getpgid", missing)
    process = _FakeProcess(pid=424242)

    subprocess_guard._kill_tree(process)

    assert process.killed == 1


def test_kill_tree_escalates_to_sigkill_only_when_sigterm_is_ignored(monkeypatch) -> None:
    """SIGTERM first so a child's EXIT trap can still run; SIGKILL only if it does not."""
    sent: list[int] = []
    monkeypatch.setattr(os, "getpgid", lambda _pid: os.getpgrp() + 1)
    monkeypatch.setattr(os, "killpg", lambda _pgid, sig: sent.append(sig))

    polite = _FakeProcess(pid=424242, waits=[True])
    subprocess_guard._kill_tree(polite)
    assert sent == [signal.SIGTERM]

    sent.clear()
    stubborn = _FakeProcess(pid=424242, waits=[False, True])
    subprocess_guard._kill_tree(stubborn)
    assert sent == [signal.SIGTERM, signal.SIGKILL]


def test_kill_tree_stops_when_the_group_signal_is_refused(monkeypatch) -> None:
    def refused(_pgid, _sig):
        raise PermissionError

    monkeypatch.setattr(os, "getpgid", lambda _pid: os.getpgrp() + 1)
    monkeypatch.setattr(os, "killpg", refused)
    process = _FakeProcess(pid=424242)

    subprocess_guard._kill_tree(process)

    assert process.killed == 0


def test_render_display_collapses_and_bounds_a_command() -> None:
    assert render_display(["git", "status", "--short"]) == "git status --short"
    assert render_display("a\n  b\tc") == "a b c"
    bounded = render_display("x" * 400, limit=20)
    assert len(bounded) == 20
    assert bounded.endswith("...")
    # Below the ellipsis width the naive `[: limit - 3]` slice goes NEGATIVE and
    # returns MORE than the limit — the one thing this function promises.
    for limit in (0, 1, 2, 3):
        assert len(render_display("x" * 400, limit=limit)) <= limit


def test_heartbeat_interval_from_env_floors_and_falls_back(monkeypatch) -> None:
    monkeypatch.delenv("CHARNESS_PROBE_INTERVAL", raising=False)
    assert heartbeat_interval_from_env("CHARNESS_PROBE_INTERVAL") == DEFAULT_HEARTBEAT_SECONDS
    monkeypatch.setenv("CHARNESS_PROBE_INTERVAL", "not-a-number")
    assert heartbeat_interval_from_env("CHARNESS_PROBE_INTERVAL", 7.0) == 7.0
    monkeypatch.setenv("CHARNESS_PROBE_INTERVAL", "0.0001")
    assert heartbeat_interval_from_env("CHARNESS_PROBE_INTERVAL") == 0.1
    monkeypatch.setenv("CHARNESS_PROBE_INTERVAL", "5")
    assert heartbeat_interval_from_env("CHARNESS_PROBE_INTERVAL") == 5.0
    # `inf`/`nan` parse cleanly and are NOT ValueError; `inf` would mean "never beat
    # again", permanently, from a documented operator knob.
    for hostile in ("inf", "-inf", "nan"):
        monkeypatch.setenv("CHARNESS_PROBE_INTERVAL", hostile)
        assert heartbeat_interval_from_env("CHARNESS_PROBE_INTERVAL", 7.0) == 7.0
