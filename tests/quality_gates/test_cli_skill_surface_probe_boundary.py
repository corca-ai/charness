"""The probe's process boundary: deadline, group kill, drain, and what survives them.

Split from `test_cli_skill_surface.py` (#780): the adapter and classification
tests stay there; every test here spawns the check in its own session and
proves how it treats a probe's descendants.
"""

from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, run_script, write_executable
from .test_cli_skill_surface import seed_repo


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


def _write_controlled_pipe_holder(repo: Path) -> Path:
    holder = repo / "scripts" / "pipe_holder.py"
    write_executable(
        holder,
        "#!/usr/bin/env python3\n"
        "import os, signal, sys, time\n"
        "from pathlib import Path\n"
        "stop_path, exit_dir = map(Path, sys.argv[1:])\n"
        "pid = os.getpid()\n"
        "def finish(*_args):\n"
        "    exit_dir.mkdir(parents=True, exist_ok=True)\n"
        "    (exit_dir / str(pid)).write_text('exited\\n', encoding='utf-8')\n"
        "    raise SystemExit(0)\n"
        "signal.signal(signal.SIGTERM, finish)\n"
        "deadline = time.monotonic() + 5.0\n"
        "while not stop_path.exists() and time.monotonic() < deadline:\n"
        "    time.sleep(0.01)\n"
        "finish()\n",
    )
    return holder


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
    tmp_path: Path,
) -> None:
    """The drain deadline must bind when killing the group cannot reach the holder.

    Killing the probe's process group reaps the ordinary grandchild, which makes
    the drain return instantly and leaves the guard's post-kill drain unexercised --
    a mutation sweep confirmed the deadline could be deleted with the suite
    green. A grandchild that calls `setsid()` escapes the group, still holds the
    inherited pipe, and is the input that makes the deadline load-bearing.
    """
    pid_log = tmp_path / "escapee-pids.txt"
    stop_path = tmp_path / "stop-escapees"
    exit_dir = tmp_path / "escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/escapee.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        # start_new_session puts the grandchild in its OWN session, so killpg on
        # the probe's group never reaches it; it keeps the pipe open regardless.
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
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
    finally:
        escaped_pids, exited_pids, survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)

    assert result is not None, (
        "the drain was unbounded; the escaped grandchild held the pipe open forever"
    )
    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result)
    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    # The claim is that the drain BINDS with an escaped holder on the pipe, and
    # `_run_bounded_in_own_session` is that bound: `result is not None` above is the
    # whole of it. It used to also require one escapee per attempt and an elapsed
    # time under fifteen seconds; both are wall-clock claims (the second attempt is
    # killed 0.5 s after it starts, before a loaded runner has spawned its escapee),
    # and they failed six scheduled runs in a row without saying anything about the
    # drain (#764, #779). One established escapee is the input that makes the
    # deadline load-bearing; `assert escaped_pids` keeps that precondition.


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
    tmp_path: Path,
) -> None:
    """Partial evidence must survive the DRAIN deadline, not just the probe deadline.

    Round 2 found the two existing fixtures each covered one half: the orphan
    probe prints but its grandchild is reaped, so the drain succeeds and never
    exercises the discard; the escapee probe defeats the drain but prints
    nothing. Crossing them -- a probe that prints AND leaves an escaped
    grandchild holding the pipe -- is the input that reaches the discard, which
    is where the original defect had been reintroduced one call deeper.
    """
    pid_log = tmp_path / "loud-escapee-pids.txt"
    stop_path = tmp_path / "stop-loud-escapees"
    exit_dir = tmp_path / "loud-escapee-exits"
    repo = _probe_repo(tmp_path, "python3 scripts/loud_escapee.py doctor --json")
    holder = _write_controlled_pipe_holder(repo)
    write_executable(
        repo / "scripts" / "loud_escapee.py",
        "#!/usr/bin/env python3\n"
        "import subprocess, sys, time\n"
        f"child = subprocess.Popen([sys.executable, {str(holder)!r}, {str(stop_path)!r}, {str(exit_dir)!r}], start_new_session=True)\n"
        f"with open({str(pid_log)!r}, 'a', encoding='utf-8') as stream: stream.write(str(child.pid) + '\\n')\n"
        "print('partial verdict that must survive the drain')\n"
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
    finally:
        escaped_pids, exited_pids, survivors = _stop_recorded_children(pid_log, stop_path, exit_dir)
    assert result is not None, "the check hung instead of bounding its drain"
    assert escaped_pids, "the fixture never established an escaped pipe holder"
    assert exited_pids == escaped_pids, "the fixture failed to stop every escaped pipe holder"
    assert not survivors
    payload = yaml.safe_load(result)

    assert payload["status"] == "unobserved"
    assert payload["probe_results"][0]["timed_out"] is True
    # Not `len(escaped_pids) == attempts`: see the sibling test above (#779).
    assert (
        "partial verdict that must survive the drain"
        in payload["probe_results"][0]["stdout_preview"]
    )


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
