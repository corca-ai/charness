"""The probe's process boundary: deadline, group kill, drain, and what survives them.

Split from `test_cli_skill_surface.py` (#780): the adapter and classification
tests stay there; every test here proves how the check treats a probe's
descendants.

Two shapes live here, and the difference is deliberate. A test whose claim is
only "the check refused to hang" runs the check in ITS OWN SESSION, so a
regression cannot take the suite with it. A test whose claim needs the guard's
budget to be spent by an OBSERVATION rather than by the wall runs the check
IN-PROCESS through `run_cli_skill_surface`, because a controlled
`time.monotonic` can only reach a probe that runs in this interpreter.
"""

from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from scripts.core.subprocess_guard import DRAIN_UNAVAILABLE
from tests.fifo_witness import FifoWitness

from .support import ROOT, run_script, write_executable
from .test_cli_skill_surface import run_cli_skill_surface, seed_repo


def _run_bounded_in_own_session(*args: str, env: dict[str, str], limit: float = 30.0) -> str | None:
    """Run the check under a bound that does NOT depend on the code under test.

    `subprocess.run(timeout=)` is not usable here: it kills only the direct child
    and then drains with no deadline, which is the exact defect this test exists
    to catch, so a regressed check would hang the SUITE instead of failing it.
    Returns stdout, or None when the check blew the bound.
    """
    process = subprocess.Popen(
        [sys.executable, *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=limit)
        assert stdout, (
            f"the check produced no stdout; rc={process.returncode} stderr={stderr[-400:]}"
        )
        return stdout
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return None


def _probe_repo(tmp_path: Path, command: str) -> Path:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                f"- {command}",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8"
    )
    return repo


def _recorded_pids(path: Path) -> list[int]:
    if not path.is_file():
        return []
    return [int(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_controlled_pipe_holder(
    repo: Path,
    *,
    witness_path: Path | None = None,
    pid_log: Path | None = None,
    release: str = "deadline",
) -> Path:
    """Seed the grandchild that holds a probe's inherited output pipe.

    `pid_log` and `witness_path` are what make this holder a CONTROLLED child.
    It records its own pid and THEN writes one FIFO line, before it does
    anything else, so a single line proves three things at once: the holder
    exists, it already holds the pipe it inherited at fork, and the test can name
    its pid for cleanup. A probe that recorded that pid itself could be killed in
    the gap between the spawn and the write, which a test reads as "the fixture
    never established a holder" -- a red with nothing to say about the check.

    `release` names what ends the hold:

    - `deadline` (unchanged, and what the in-group orphan fixture still uses):
      the stop file, or a five-second self-deadline.
    - `parent-death`: block on a pidfd for the spawning probe with no timeout and
      release the pipe the moment that probe dies. The group kill landing on the
      probe but NOT on this holder is then what closes the pipe, so the post-kill
      drain gets its EOF from a holder that provably outlived the kill.
    - `stop-file`: hold until the test says stop. The drain cannot finish on its
      own, so it must hit its own bound or never return at all.

    The polling below is the child's behaviour, not a test's claim, and the long
    deadline on `stop-file` is only a leak guard for a session that dies before
    its cleanup runs; no assertion depends on either.
    """
    holder = repo / "scripts" / "pipe_holder.py"
    lines = [
        "#!/usr/bin/env python3",
        "import os, select, signal, sys, time",
        "from pathlib import Path",
        "stop_path, exit_dir = map(Path, sys.argv[1:])",
        "pid = os.getpid()",
        "def finish(*_args):",
        "    exit_dir.mkdir(parents=True, exist_ok=True)",
        "    (exit_dir / str(pid)).write_text('exited\\n', encoding='utf-8')",
        "    raise SystemExit(0)",
        "signal.signal(signal.SIGTERM, finish)",
    ]
    if release == "parent-death":
        # Armed BEFORE the witness line, and the witness line is what lets the
        # kill fire: the probe cannot die in the window between this holder
        # reading its pid and this holder watching it.
        lines.append("_parent = os.pidfd_open(os.getppid())")
    if pid_log is not None:
        lines.append(
            f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as _log:"
            " _log.write(str(pid) + '\\n')"
        )
    if witness_path is not None:
        # Held open for this process's whole life, so the FIFO tracks the holder.
        lines += [
            f"_witness = open({str(witness_path)!r}, 'w')",
            "_witness.write('holding\\n')",
            "_witness.flush()",
        ]
    if release == "parent-death":
        # A blocking select with no timeout, and the end of this script: the stop
        # file below would be unreachable code, not a second chance.
        lines += ["select.select([_parent], [], [])", "finish()", ""]
    else:
        lines += [
            f"deadline = time.monotonic() + {600.0 if release == 'stop-file' else 5.0}",
            "while not stop_path.exists() and time.monotonic() < deadline:",
            "    time.sleep(0.01)",
            "finish()",
            "",
        ]
    write_executable(holder, "\n".join(lines))
    return holder


def _clock_spent_by_witness(witness: FifoWitness) -> Callable[[], float]:
    """A `time.monotonic` whose budget is spent by an OBSERVATION, not by the wall.

    Reads 0 until the attempt's controlled holder has written its line, and 100
    more for every line after that. The guard reads `started_at` once per attempt
    and compares it against this on every heartbeat, so each of the check's two
    probe attempts gets its own budget: attempt N starts at 100*(N-1) and crosses
    its bound only once THAT attempt's holder has signalled.

    Counting rather than latching one flag is what makes the second attempt
    honest. A sticky flag reads as already-spent the moment attempt 2 starts, so
    attempt 2 is killed before its child exists -- the vacuous pass this rewrite
    removes, in a new place.
    """
    lines = 0

    def monotonic() -> float:
        nonlocal lines
        if witness.has_line():
            # Consumed, not peeked: the next attempt must produce its own line.
            witness.wait_line()
            lines += 1
        return 100.0 * lines

    return monotonic


def _owned_process_is_running(pid: int, identity: str) -> bool:
    process = subprocess.run(
        ["ps", "-o", "stat=,args=", "-p", str(pid)],
        check=False,
        capture_output=True,
        text=True,
    )
    fields = process.stdout.strip().split(maxsplit=1)
    if process.returncode != 0 or len(fields) != 2:
        return False
    state, argv = fields
    return not state.startswith("Z") and identity in argv


def _wait_for_owned_child_exit(pid: int) -> None:
    """Block until `pid` has terminated. No deadline, no polling, no retry.

    `os.pidfd_open` returns a descriptor the kernel makes readable exactly when
    that process terminates, so a blocking `select` with no timeout IS the
    observation "this holder is gone": reported when it is true and never
    earlier. A terminated-but-unreaped process (a zombie) counts as gone, which
    is the same thing `_owned_process_is_running` reports -- it reads a `Z`
    state as not running. `ProcessLookupError` means the holder exited before
    the descriptor could be opened, which is the answer already.

    `pidfd_open` needs Linux >= 5.3 and Python >= 3.9. The repo has no non-Linux
    runner, so its absence is a broken assumption to name loudly, not a reason
    to skip the test.
    """
    if not hasattr(os, "pidfd_open"):
        raise AssertionError(
            f"os.pidfd_open is unavailable on platform {sys.platform!r}; this fixture "
            "observes child exit through a pidfd and the repo has no non-Linux runner"
        )
    try:
        descriptor = os.pidfd_open(pid)
    except ProcessLookupError:
        return
    try:
        select.select([descriptor], [], [])
    finally:
        os.close(descriptor)


def _stop_recorded_children(
    pid_log: Path, stop_path: Path, exit_dir: Path
) -> tuple[list[int], list[int], list[int]]:
    """Stop every recorded pipe holder; return `(recorded, exited, survivors)`.

    The stop file is the holders' exit signal: each one polls for it and writes
    its marker into `exit_dir` on the way out (or on SIGTERM). Waiting for that
    used to be a six-second `ps` poll, which is a guess about how loaded the
    runner is rather than a claim about the holders. It is now the kernel's own
    answer -- block on each live holder's pidfd until it terminates -- so
    `exited` and `survivors` below are single point-in-time reads taken once
    every holder has already gone.
    """
    stop_path.write_text("stop\n", encoding="utf-8")
    pids = _recorded_pids(pid_log)
    identity = str(stop_path)
    for pid in pids:
        # The identity check stays in front of the wait: a recorded pid the
        # kernel has already recycled belongs to a stranger, and blocking on
        # that stranger's lifetime would be a hang with no relation to this
        # fixture. It also keeps that stranger out of `survivors`.
        if _owned_process_is_running(pid, identity):
            _wait_for_owned_child_exit(pid)
    exited = [pid for pid in pids if (exit_dir / str(pid)).is_file()]
    survivors = [pid for pid in pids if _owned_process_is_running(pid, identity)]
    return pids, exited, survivors


def test_cli_skill_surface_separates_a_real_124_exit_from_an_unobserved_probe(
    tmp_path: Path,
) -> None:
    """A command that ANSWERS 124 is a blocker; only an unread verdict is unobserved.

    124 is the code this check synthesizes for its own deadline, so a probe that
    exits 124 on its own is the one input that tells a returncode-keyed
    implementation apart from a `timed_out`-keyed one.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/exits124.py doctor --json")
    write_executable(
        repo / "scripts" / "exits124.py", "#!/usr/bin/env python3\nraise SystemExit(124)\n"
    )

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes"
    )
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["unobserved"] == []
    assert payload["probe_results"][0]["returncode"] == 124
    assert payload["probe_results"][0]["timed_out"] is False
    assert payload["probe_results"][0]["attempts"] == 1
    assert any("exited 124" in blocker for blocker in payload["blockers"])


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: a real probe process and grandchild must be bounded and reaped"
)
def test_cli_skill_surface_survives_a_probe_whose_grandchild_holds_the_pipe(tmp_path: Path) -> None:
    """The deadline must bind even when a grandchild inherits the output pipe.

    `subprocess.run(timeout=)` kills only the direct child and then drains with
    NO deadline, so this shape hangs the check forever. Nothing above it -- not
    `run-quality.sh`, not the pre-push hook -- puts a wall clock around a label,
    so the gate would hang rather than refuse.
    """
    pid_log = tmp_path / "orphan-pids.txt"
    stop_path = tmp_path / "stop-orphans"
    exit_dir = tmp_path / "orphan-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/orphan.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "orphan.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        # The grandchild inherits stdout/stderr and outlives the parent.
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}])\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
        "print('partial verdict before the hang')\n"
        "sys.stdout.flush()\n"
        "time.sleep(600)\n",
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.5"

    try:
        result = _run_bounded_in_own_session(
            "scripts/gates/check_cli_skill_surface.py",
            "--repo-root",
            str(repo),
            "--run-probes",
            env=env,
        )
        recorded_pids = _recorded_pids(pid_log)
        production_survivors = [
            pid for pid in recorded_pids if _owned_process_is_running(pid, str(stop_path))
        ]
    finally:
        cleanup_pids, _, cleanup_survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)
    assert result is not None, (
        "the check did not bound its own probe deadline; it hung on the orphan-held pipe"
    )
    assert recorded_pids, "the fixture never established an inherited pipe holder"
    assert not production_survivors, "the production group kill left an ordinary descendant running"
    assert not cleanup_survivors, "the fixture failed to clean every recorded descendant"
    payload = yaml.safe_load(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    assert len(recorded_pids) == payload["probe_results"][0]["attempts"]
    # Partial output captured before the deadline is EVIDENCE, not noise: it is
    # what tells a reader the command was mid-verdict rather than never started.
    assert "partial verdict before the hang" in payload["probe_results"][0]["stdout_preview"]


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: an escaped grandchild must not defeat the process-group drain deadline"
)
def test_cli_skill_surface_bounds_the_drain_when_the_grandchild_escapes_the_group(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The drain deadline must bind when killing the group cannot reach the holder.

    Killing the probe's process group reaps an ordinary grandchild, which makes
    the drain return instantly and leaves the guard's post-kill drain unexercised --
    a mutation sweep confirmed the deadline could be deleted with the suite
    green. A grandchild that calls `setsid()` escapes the group and still holds
    the inherited pipe, and it is now the input that makes the deadline
    load-bearing rather than merely present:

    - the escaped holder releases the pipe for nothing the check can do, only for
      the stop file this test writes in its cleanup, so `communicate()` cannot
      reach EOF while the check runs. The bound is then the only thing that can
      end the drain: delete it and this test hangs, which is the whole claim;
    - the outcome that proves the bound fired is in the payload, not in a stopwatch.
      `DRAIN_UNAVAILABLE` with an EMPTY stdout preview is what the guard reports
      exactly when it killed the group, waited its full drain, and found the body
      still unreachable.

    The clock is controlled and the check runs in-process, so the budget is spent
    by the holder's FIFO line rather than by a 0.5 s wall deadline racing the
    child's start. The old shape asserted one escapee per attempt and an elapsed
    time under fifteen seconds, failed six scheduled runs in a row, and could
    still pass vacuously with the kill landing before the grandchild existed
    (#764, #779). The holder's earlier five-second self-deadline made this worse
    than vacuous once the kill became prompt: it raced POST_KILL_DRAIN_SECONDS
    from the other side, so the same test could bind or not bind by a margin the
    scheduler picked.
    """
    pid_log = tmp_path / "escapee-pids.txt"
    stop_path = tmp_path / "stop-escapees"
    exit_dir = tmp_path / "escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/escapee.py doctor --json")
    with FifoWitness(tmp_path / "escapee-witness") as witness:
        holder = _write_controlled_pipe_holder(
            repo, witness_path=witness.path, pid_log=pid_log, release="stop-file"
        )
        write_executable(
            repo / "scripts" / "escapee.py",
            "#!/usr/bin/env python3\n"
            "import subprocess, sys, time\n"
            # start_new_session puts the grandchild in its OWN session, so killpg on
            # the probe's group never reaches it; it keeps the pipe open regardless.
            # `Popen` returns only once that grandchild has exec'd, and the pipe was
            # inherited at fork, so the witness line it writes covers both.
            f"subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
            # Outlasts any plausible run ON PURPOSE: a probe that could reach its
            # own end would let the drain finish for the wrong reason.
            "time.sleep(600)\n",
        )
        # Not a deadline any more. The budget is judged on the fake clock below;
        # this knob only sets the beat at which the guard re-reads it, because
        # `_resolve_interval` clamps the heartbeat to the budget and
        # MINIMUM_HEARTBEAT_SECONDS is 0.1.
        monkeypatch.setenv("CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS", "0.1")
        monkeypatch.setattr(
            "scripts.core.subprocess_guard.time.monotonic", _clock_spent_by_witness(witness)
        )
        try:
            result = run_cli_skill_surface(
                monkeypatch, capsys, "--repo-root", str(repo), "--run-probes"
            )
        finally:
            escaped_pids, exited_pids, survivors = _stop_recorded_children(
                pid_log, stop_path, exit_dir
            )

    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result.stdout)
    probe = payload["probe_results"][0]
    assert payload["status"] == "unobserved"
    assert probe["timed_out"] is True
    assert DRAIN_UNAVAILABLE in probe["stderr_preview"], (
        "the drain did not bind against a holder that never releases the pipe"
    )
    assert probe["stdout_preview"] == ""


@pytest.mark.boundary_contract(
    reason="signal behavior: group cleanup must not signal a process group the probe does not own"
)
def test_kill_group_and_drain_never_signals_a_group_the_probe_does_not_own(tmp_path: Path) -> None:
    """Guard against the probe SIGKILLing the whole quality run.

    `os.getpgid(child)` returns the SHARED group when the child is not a group
    leader, so an unguarded `killpg` reaps every sibling check, the runner, and
    the shell. That is not hypothetical: a mutant flipping `start_new_session`
    to False did exactly that three times during this slice, killing the sweep
    mid-run and leaving the tree mutated.

    The scenario runs in its OWN session so a regression kills only that
    subprocess instead of this suite -- the containment is the point.
    """
    probe = tmp_path / "self_signal.py"
    probe.write_text(
        "import subprocess, sys, time\n"
        f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
        "from runtime_bootstrap import import_repo_module\n"
        f"m = import_repo_module({str(ROOT / 'scripts/core/subprocess_guard.py')!r}, 'scripts.core.subprocess_guard')\n"
        # No start_new_session: the child SHARES this process's group, so an
        # unguarded killpg would take this process down with it.
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(600)'],\n"
        "                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)\n"
        "m._kill_tree(child)\n"
        # One-sided otherwise: 'we were not killed' also holds when nothing
        # was killed at all, which leaks the child and proves half the property.
        "child.wait(timeout=5)\n"
        "assert child.poll() is not None, 'the child was never reaped'\n"
        "print('SURVIVED', flush=True)\n",
        encoding="utf-8",
    )

    process = subprocess.Popen(
        [sys.executable, str(probe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.communicate()
        raise AssertionError("kill-and-drain hung on a group it does not own")

    assert "SURVIVED" in stdout, (
        "kill-and-drain signalled a process group it does not own; "
        f"rc={process.returncode} stderr={stderr[-400:]}"
    )


@pytest.mark.boundary_contract(
    reason="child-exit-on-parent-death: escaped descendants must be cleaned while preserving partial output"
)
def test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Partial evidence must survive a group kill the pipe holder ESCAPED.

    Round 2 found the two existing fixtures each covered one half: the orphan
    probe prints but its grandchild is reaped, so the drain returns instantly and
    the body was never at risk; the escapee probe defeats the drain but prints
    nothing. Crossing them -- a probe that prints AND leaves an escaped
    grandchild holding the pipe -- is the input where the post-kill drain has to
    WAIT for a descendant it could not signal, and still hand back what the probe
    managed to say before it died. That is where the original defect had been
    reintroduced one call deeper.

    Every precondition is an observation this test forces, on a controlled clock:

    - the probe prints its verdict and flushes BEFORE it spawns the holder, and
      `Popen` returns only once that holder has exec'd, so the holder's existence
      proves the verdict is already in the pipe;
    - the holder records its pid and writes one FIFO line as its first actions,
      so one line proves an escaped holder is alive on the inherited pipe and
      nameable for cleanup;
    - `time.monotonic` in the guard reads 0 until that line arrives, so the budget
      is judged spent only once all of it is true. The knob below is a heartbeat
      cadence, not a deadline (see the sibling above);
    - the holder then blocks on a pidfd for the probe and releases the pipe when
      the probe dies. EOF therefore arrives from a holder that OUTLIVED the group
      kill, at the moment the kill landed, rather than whenever a self-deadline
      happened to expire.

    What it replaces: a real 0.5 s probe deadline racing the child's start. The
    probe spawned the holder -- a whole interpreter -- BEFORE printing, so on a
    loaded runner the deadline fired first, nothing was ever printed, and this
    test's own assertion read `'partial verdict...' in ''`. It failed the hosted
    mutation baseline on 2026-09-03 and once locally under three concurrent
    agents.

    On the name: when the drain TRULY times out, `_await_child` discards the body
    and reports `DRAIN_UNAVAILABLE`, so partial output surviving a FAILED drain is
    not behaviour this repo has. The sibling above owns the failed drain and
    asserts exactly that discard; this test owns the other half -- a drain that
    completes only because its holder escaped the kill -- and the payload check
    below pins which of the two it is.
    """
    pid_log = tmp_path / "loud-escapee-pids.txt"
    stop_path = tmp_path / "stop-loud-escapees"
    exit_dir = tmp_path / "loud-escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/loud_escapee.py doctor --json")
    with FifoWitness(tmp_path / "loud-escapee-witness") as witness:
        holder = _write_controlled_pipe_holder(
            repo, witness_path=witness.path, pid_log=pid_log, release="parent-death"
        )
        write_executable(
            repo / "scripts" / "loud_escapee.py",
            "#!/usr/bin/env python3\n"
            "import subprocess, sys, time\n"
            # The verdict enters the pipe FIRST. Everything the test waits for
            # happens after it, so no observation can precede it.
            "print('partial verdict that must survive the drain')\n"
            "sys.stdout.flush()\n"
            f"subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
            "time.sleep(600)\n",
        )
        monkeypatch.setenv("CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS", "0.1")
        monkeypatch.setattr(
            "scripts.core.subprocess_guard.time.monotonic", _clock_spent_by_witness(witness)
        )
        try:
            result = run_cli_skill_surface(
                monkeypatch, capsys, "--repo-root", str(repo), "--run-probes"
            )
        finally:
            escaped_pids, exited_pids, survivors = _stop_recorded_children(
                pid_log, stop_path, exit_dir
            )

    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result.stdout)
    probe = payload["probe_results"][0]

    assert payload["status"] == "unobserved"
    assert probe["timed_out"] is True
    # Not `len(escaped_pids) == attempts`: see the sibling test above (#779).
    assert "partial verdict that must survive the drain" in probe["stdout_preview"]
    # The half this test owns: the drain COMPLETED, so the body is real evidence
    # rather than the marker the sibling asserts.
    assert DRAIN_UNAVAILABLE not in probe["stderr_preview"]


def test_cli_skill_surface_names_the_unobserved_probe_in_its_only_output(tmp_path: Path) -> None:
    """The output must say UNOBSERVED, not look like a failure.

    `run-quality.sh` invokes this check with no format selector, and after the
    `--json` removal the YAML payload is the only thing an operator ever reads.
    The defect this pins misnamed a probe that never answered as one that
    failed; the distinction now has to live in the payload, because there is no
    second rendering left to carry it.
    """
    repo = _probe_repo(tmp_path, "python3 scripts/hang.py doctor --json")
    write_executable(
        repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n"
    )
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.2"

    result = run_script(
        "scripts/gates/check_cli_skill_surface.py",
        "--repo-root",
        str(repo),
        "--run-probes",
        env=env,
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "unobserved"
    assert any("verdict NOT OBSERVED" in item for item in payload["unobserved"])
    # The word that misled a whole session must not appear for a probe that
    # merely never answered -- in the payload or anywhere else on the surface.
    assert payload["blockers"] == []
    assert "probe failed" not in result.stdout
    assert "probe failed" not in result.stderr
