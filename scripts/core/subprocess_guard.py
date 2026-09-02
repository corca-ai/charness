"""The repo's child-process primitive, with an EXPLICIT caller choice of visibility.

A runner has exactly two honest reasons to spawn a child, and they want opposite
defaults:

- ``run_process`` — a SHORT probe whose body only matters if it fails
  (``git rev-parse``, a ``--json`` query, a ``--help`` render). Quiet is correct:
  a lifecycle around a 40ms query is noise, and buffering costs an operator
  nothing because there was nothing to watch.
- ``run_monitored_phase`` — a LONG phase an operator may be sitting in front of.
  The child's body stays isolated (buffered, replayed by the caller on failure) so
  concurrent phases cannot interleave into unreadable output, but the PARENT
  immediately emits start, a bounded heartbeat while work remains, and a terminal
  status with elapsed time.

Collapsing the two is what the repo measured going wrong: the release publish
helper ran the standing quality runner — a child that streams its own per-check
lifecycle — through a ``capture_output=True`` call bounded at 1800s, so an
observable runner produced a 30-minute silence. An observable child cannot defend
itself from a silent parent, and picking the wrong shape is invisible until
someone is waiting.

The third caller choice, which this scope note used to defer (S6, 2026-08-15):
``run_monitored_phase(capture=False)`` — a long phase whose child ALREADY streams
a readable lifecycle of its own, where buffering the body is the harm rather than
the protection. The standing pytest runner is the case that earned it: it renders
live progress across a run measured in minutes, and capturing it would trade a
watchable suite for a silent one. The child inherits the parent's stdout and
stderr, so nothing interleaves it and nothing buffers it; ``PhaseOutcome.stdout``
and ``.stderr`` are then EMPTY by construction, and a caller that needs the body
back must not ask for this mode. Everything else the monitored shape provides —
its own session, the whole-group kill, the heartbeat, the timeout-as-result — is
unchanged, and those are what a caller in this mode is actually buying.

This stays one primitive rather than two because the alternative was measured:
the previous attempt at this shape began as a separate ``monitored_run.py`` whose
capture helper near-duplicated this module's, and two owners for "how this repo
spawns a child" is the concept-integrity failure the quality lens exists to
catch. Teeing — capturing the body AND streaming it — remains unsolved and
deliberately so; no caller should assume it.

Both shapes report a timeout the same way: as a RESULT, not an exception. The
caller receives ``TIMEOUT_EXIT_CODE`` and a stderr message naming the bound, so
one failure path handles both "the command failed" and "the command never
finished". Three differences between the shapes are real and deliberate:

- WHAT GETS KILLED. ``run_process`` is ``subprocess.run``, which signals only the
  DIRECT child, so a shell's backgrounded grandchildren are orphaned and keep
  running. ``run_monitored_phase`` spawns into its own session and terminates the
  whole GROUP, SIGTERM before SIGKILL.
- ENFORCEMENT GRANULARITY. ``run_process`` returns at exactly ``timeout_seconds``.
  ``run_monitored_phase`` evaluates the budget only on the heartbeat beat, so it
  kills at the first beat at or after the bound and then spends up to
  ``TERMINATE_GRACE_SECONDS`` + ``POST_KILL_DRAIN_SECONDS`` collecting the body.
  ``elapsed_seconds`` can therefore exceed the bound by roughly one interval plus
  those two, and a record honestly reading ``elapsed_seconds=1836`` beside a
  marker naming 1800s is not a contradiction.
- TIMEOUT STDERR. ``run_process`` REPLACES stderr with the marker.
  ``run_monitored_phase`` keeps whatever partial stderr it collected and appends
  the marker — EXCEPT when a descendant holds the pipes past the drain, where the
  body is unreachable and stderr becomes ``DRAIN_UNAVAILABLE`` instead.

One bound this module does NOT promise: a child wedged in uninterruptible sleep
(D state on a hung mount) does not die on SIGKILL, and ``Popen.__exit__``'s own
``wait()`` is unbounded. Nothing in userspace fixes that; it is disclosed rather
than claimed away.
"""

from __future__ import annotations

import contextlib
import math
import os
import shlex
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import NamedTuple, TextIO

TIMEOUT_EXIT_CODE = 124
DEFAULT_COMMAND_TIMEOUT_SECONDS = 30
DEFAULT_HEARTBEAT_SECONDS = 30.0
MINIMUM_HEARTBEAT_SECONDS = 0.1
DISPLAY_LIMIT = 120
ELLIPSIS = "..."
#: How long to keep reading the pipes after killing a phase's process group. A
#: bound is required: `communicate()` waits for EOF on the PIPES, not for the
#: child to exit, so any descendant still holding a write end can block the
#: "timeout" path forever. See `_kill_tree`.
POST_KILL_DRAIN_SECONDS = 5.0
#: Grace between SIGTERM and SIGKILL, so a child's EXIT trap can still run.
TERMINATE_GRACE_SECONDS = 0.5
DRAIN_UNAVAILABLE = (
    f"output unavailable: a surviving descendant held the pipes open past the "
    f"{POST_KILL_DRAIN_SECONDS:g}s post-kill drain"
)


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def timeout_message(command: Sequence[str] | str, *, timeout_seconds: float) -> str:
    rendered = command if isinstance(command, str) else shlex.join(command)
    seconds_text = f"{timeout_seconds:g}"
    return f"timed out after {seconds_text}s while running `{rendered}`"


def run_process(
    command: Sequence[str] | str,
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: float | None = DEFAULT_COMMAND_TIMEOUT_SECONDS,
    shell: bool = False,
    executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a short probe quietly and return its buffered result.

    Never raises for a non-zero exit or a timeout: refusal policy belongs to the
    caller, which is the only layer that knows whether this probe is advisory.
    """
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            # A child's bytes are not always UTF-8 (git prints raw paths); a
            # strict decode would turn one odd filename into a crashed probe.
            # surrogateescape keeps every byte recoverable by the caller.
            errors="surrogateescape",
            env=env,
            timeout=timeout_seconds,
            shell=shell,
            executable=executable,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            command,
            TIMEOUT_EXIT_CODE,
            _coerce_text(exc.stdout),
            timeout_message(command, timeout_seconds=timeout_seconds),
        )


def run_processes_in_order(
    commands: Sequence[Sequence[str] | str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: float | None = DEFAULT_COMMAND_TIMEOUT_SECONDS,
    shell: bool = False,
    executable: str | None = None,
) -> list[subprocess.CompletedProcess[str]]:
    if not commands:
        return []
    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        futures = [
            executor.submit(
                run_process,
                command,
                cwd=cwd,
                env=env,
                timeout_seconds=timeout_seconds,
                shell=shell,
                executable=executable,
            )
            for command in commands
        ]
        return [future.result() for future in futures]


def render_display(command: Sequence[str] | str, *, limit: int = DISPLAY_LIMIT) -> str:
    """A single-line, bounded rendering of ``command`` for lifecycle events.

    Lifecycle lines are read under time pressure and repeat once per heartbeat, so
    an unbounded multi-line command would bury the elapsed time and phase name
    that make the line worth printing at all.
    """
    text = command if isinstance(command, str) else shlex.join(command)
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    if limit < len(ELLIPSIS):
        # `collapsed[: limit - 3]` goes NEGATIVE below a 3-char limit and returns a
        # string LONGER than the limit — the one thing this function promises.
        return collapsed[: max(limit, 0)]
    return f"{collapsed[: limit - len(ELLIPSIS)]}{ELLIPSIS}"


def heartbeat_interval_from_env(name: str, default: float = DEFAULT_HEARTBEAT_SECONDS) -> float:
    """Resolve a caller-owned heartbeat override, falling back on unusable input.

    The env var NAME stays with the caller: one shared name would let a debugging
    override on one runner silence another. Only the parsing rule is shared, and a
    malformed value falls back rather than raising — an operator mistyping an
    interval must not turn an otherwise-healthy phase into a crash.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    # `float("inf")` and `float("nan")` parse cleanly and are NOT ValueError, so a
    # bare `except ValueError` let `inf` through as a heartbeat interval — which is
    # "never beat again", permanently, from a documented operator knob.
    if not math.isfinite(value):
        return default
    return max(MINIMUM_HEARTBEAT_SECONDS, value)


class PhaseOutcome(NamedTuple):
    """The result of one monitored phase, including what its lifecycle reported."""

    args: Sequence[str] | str
    phase: str
    display: str
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def completed_process(self) -> subprocess.CompletedProcess[str]:
        """Adapt to ``CompletedProcess`` for callers already shaped around it.

        DROPS ``timed_out``. ``TIMEOUT_EXIT_CODE`` is 124, which a child can also
        exit with on its own (GNU ``timeout`` does exactly that), so a caller that
        needs to tell a guard timeout from a real 124 must keep the ``PhaseOutcome``
        rather than this adapter.
        """
        return subprocess.CompletedProcess(self.args, self.returncode, self.stdout, self.stderr)


# `Popen` can fork the child before its constructor returns the object that owns
# the pid. If one of these signals raises in that gap, the caller has no object
# through which it can kill the new process group. A temporary non-raising
# handler lets the constructor finish without masking the child it launches.
_SPAWN_INTERRUPTION_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")


def _install_spawn_interruptions(pending: list[int]) -> dict[int, object]:
    """Record interrupt-like signals until the new ``Popen`` is bound.

    The handler intentionally does not raise: a Python signal exception during
    construction would arrive before the caller owns the returned process object.
    Signals that cannot be installed (for example, a non-main thread) keep the
    caller's existing signal policy rather than making launch fail for an
    unrelated reason.
    """

    def record(signum: int, _frame: object) -> None:
        pending.append(signum)

    previous: dict[int, object] = {}
    for name in _SPAWN_INTERRUPTION_NAMES:
        number = getattr(signal, name, None)
        if number is None:
            continue
        try:
            previous[number] = signal.signal(number, record)
        except (OSError, ValueError):
            continue
    return previous


def _restore_spawn_interruptions(previous: dict[int, object]) -> None:
    """Restore the caller's signal handlers after ``Popen`` is available."""
    for number, handler in previous.items():
        with contextlib.suppress(OSError, TypeError, ValueError):
            signal.signal(number, handler)


def _replay_spawn_interruptions(pending: list[int]) -> None:
    """Deliver recorded signals after the process tree has been cleaned up."""
    raise_signal = getattr(signal, "raise_signal", None)
    for number in pending:
        if raise_signal is not None:
            raise_signal(number)
        else:
            os.kill(os.getpid(), number)


def run_monitored_phase(
    command: Sequence[str] | str,
    *,
    cwd: Path,
    phase: str,
    timeout_seconds: float | None,
    display: str | None = None,
    heartbeat_seconds: float = DEFAULT_HEARTBEAT_SECONDS,
    env: dict[str, str] | None = None,
    shell: bool = False,
    executable: str | None = None,
    stream: TextIO | None = None,
    capture: bool = True,
) -> PhaseOutcome:
    """Run a long phase with an isolated body and a streamed lifecycle.

    Emits, unbuffered, to ``stream`` (default ``sys.stderr``):

    - ``RUN [phase] command`` before the child starts,
    - ``HEARTBEAT [phase] elapsed=Ns command`` every ``heartbeat_seconds``,
    - ``PASS|FAIL [phase] Ns command`` once the child is actually done.

    stderr by default so a caller whose stdout carries a machine-readable payload
    stays observable without corrupting it.

    ``timeout_seconds=None`` runs unbounded, matching ``run_process``.

    ``capture=False`` hands the child the parent's own stdout and stderr instead
    of pipes. Use it only for a child that already renders its own readable
    progress; the returned ``stdout``/``stderr`` are then empty strings, because
    the body went straight to the terminal and this function never held it.
    """
    events = sys.stderr if stream is None else stream
    rendered = display if display is not None else render_display(command)
    interval = _resolve_interval(heartbeat_seconds, timeout_seconds)
    _emit(events, f"RUN [{phase}] {rendered}")
    started_at = time.monotonic()
    pending_interruptions: list[int] = []
    previous_spawn_handlers = _install_spawn_interruptions(pending_interruptions)
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            # `None` INHERITS the parent's handles -- it does not discard the output.
            # The distinction matters: `subprocess.DEVNULL` here would silence the one
            # kind of child this mode exists for.
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            text=True,
            env=env,
            shell=shell,
            executable=executable,
            # Makes the child's whole descendant tree addressable as one process group.
            # Without it a timeout can only signal the direct child, and both callers
            # run a SHELL whose grandchildren outlive it. See `_kill_tree`.
            start_new_session=True,
        )
    except BaseException:
        # `Popen` owns its own partial-construction cleanup. If construction itself
        # failed, there is no process object we can safely address here.
        _restore_spawn_interruptions(previous_spawn_handlers)
        _replay_spawn_interruptions(pending_interruptions)
        raise
    with process:
        spawn_cleanup_done = False
        try:
            # Restore inside the cleanup envelope: a signal recorded by the
            # temporary handler can now be replayed only after its tree is dead.
            _restore_spawn_interruptions(previous_spawn_handlers)
            if pending_interruptions:
                _kill_tree(process)
                _drain(process, timeout=POST_KILL_DRAIN_SECONDS)
                spawn_cleanup_done = True
                _replay_spawn_interruptions(pending_interruptions)
            stdout, stderr, timed_out = _await_child(
                process,
                events=events,
                phase=phase,
                rendered=rendered,
                started_at=started_at,
                interval=interval,
                timeout_seconds=timeout_seconds,
            )
        except BaseException:
            # `subprocess.run` — the shape `run_process` uses — kills its child on
            # ANY exception, KeyboardInterrupt included. A bare Popen does not, so
            # an interrupted publish would leave the quality runner alive and still
            # mutating the worktree while the release lane ran its rollback against
            # that same worktree, and recorded the rollback as clean.
            if not spawn_cleanup_done:
                _kill_tree(process)
                _drain(process, timeout=POST_KILL_DRAIN_SECONDS)
            raise
    elapsed = time.monotonic() - started_at
    returncode = TIMEOUT_EXIT_CODE if timed_out else process.returncode
    if timed_out and timeout_seconds is not None:
        # `rendered`, not `command`: the bounded display is what the operator has
        # been reading in every lifecycle line, and a phase command can be a whole
        # wrapped shell body that would bury the timeout it is supposed to report.
        marker = timeout_message(rendered, timeout_seconds=timeout_seconds)
        stderr = f"{stderr}\n{marker}".strip() if stderr else marker
    status = "PASS" if returncode == 0 else "FAIL"
    _emit(events, f"{status} [{phase}] {elapsed:.1f}s {rendered}")
    return PhaseOutcome(
        args=command,
        phase=phase,
        display=rendered,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=round(elapsed, 2),
        timed_out=timed_out,
    )


def _resolve_interval(heartbeat_seconds: float, timeout_seconds: float | None) -> float:
    """Clamp the beat to the budget it is responsible for checking.

    The budget is only evaluated ON the beat, so an interval WIDER than the budget
    silences the heartbeat and defers the kill past its own bound at the same time
    — an operator who widened the interval to quiet the output would have
    reintroduced the exact silent window this primitive exists to close.
    """
    interval = max(MINIMUM_HEARTBEAT_SECONDS, heartbeat_seconds)
    if timeout_seconds is None:
        return interval
    return max(MINIMUM_HEARTBEAT_SECONDS, min(interval, timeout_seconds))


def _kill_tree(process: subprocess.Popen) -> None:
    """Terminate the child's whole process GROUP, not just the direct child.

    `process.kill()` alone signals the direct child, and `communicate()` waits for
    EOF on the PIPES rather than for that child to exit — so a surviving grandchild
    holding a write end blocks the "timeout" path indefinitely. Measured on this
    repo before the group kill: a 1-second budget against
    `bash -c 'sleep 25 & sleep 25'` returned after 25.0 seconds. Not a bound.

    SIGTERM first, then SIGKILL. A bash EXIT trap runs on SIGTERM and never on
    SIGKILL, and `run-quality.sh`'s trap is what removes its temp dir and leaves
    the failure-log receipt this repo names as the operator recovery channel.
    """
    if process.returncode is not None:
        # ALREADY REAPED. `Popen.send_signal` self-guards on exactly this (bpo-38630)
        # because a raw pid may already have been RECYCLED by the kernel — and unlike
        # `os.kill`, `os.killpg` would then destroy an unrelated process's whole
        # group, plausibly this process's own.
        return
    pgid = _process_group(process)
    if pgid is None:
        with contextlib.suppress(OSError):
            process.kill()
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except OSError:
            return
        if _wait_briefly(process):
            return


def _process_group(process: subprocess.Popen) -> int | None:
    """The child's own group, or ``None`` when killing it would kill us too."""
    try:
        pgid = os.getpgid(process.pid)
    except (OSError, AttributeError):
        return None
    if pgid == os.getpgrp():
        # `start_new_session=True` did not take effect, so the child shares OUR
        # group and a group kill would take down the caller — a release publish, or
        # the test runner. This guard is why that spawn flag cannot be silently
        # dropped: without it the failure is "the runner died", not a red test.
        return None
    return pgid


def _wait_briefly(process: subprocess.Popen) -> bool:
    try:
        process.wait(timeout=TERMINATE_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        return False
    return True


def _drain(process: subprocess.Popen, *, timeout: float) -> tuple[str, str, bool]:
    """Collect whatever the pipes still hold, bounded. Third value is `drained`."""
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return _coerce_text(stdout), _coerce_text(stderr), True
    except subprocess.TimeoutExpired:
        return "", "", False


def _await_child(
    process: subprocess.Popen,
    *,
    events: TextIO,
    phase: str,
    rendered: str,
    started_at: float,
    interval: float,
    timeout_seconds: float | None,
) -> tuple[str, str, bool]:
    """Drain the child on a heartbeat cadence, killing it once the budget is spent.

    ``communicate`` keeps draining both pipes across retries, so the heartbeat
    cadence cannot deadlock a child that fills a pipe buffer while the parent
    sleeps between beats.
    """
    while True:
        try:
            stdout, stderr = process.communicate(timeout=interval)
            return _coerce_text(stdout), _coerce_text(stderr), False
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - started_at
            _emit(events, f"HEARTBEAT [{phase}] elapsed={elapsed:.1f}s {rendered}")
        # Beat BEFORE the budget check, not after. A child that blows the whole
        # budget inside its first interval (a slow shell start against a short
        # timeout) would otherwise be killed having emitted nothing between `RUN`
        # and `FAIL`, which is exactly the silent window this function exists to
        # close.
        if timeout_seconds is None or time.monotonic() - started_at <= timeout_seconds:
            continue
        # `finished` is decided ONCE, BEFORE any kill, and it alone decides
        # `timed_out`. The child may have finished in the gap between the beat and
        # this check, in which case its real exit status is already reaped and
        # relabelling it a timeout would fail a phase that PASSED — on the release
        # lane, aborting a publish whose quality gate had just gone green. Letting
        # a failed drain flip that verdict makes the outcome depend on whether some
        # unrelated descendant closed a pipe in time.
        finished = process.poll() is not None
        if not finished:
            _kill_tree(process)
        stdout, stderr, drained = _drain(process, timeout=POST_KILL_DRAIN_SECONDS)
        if drained:
            return stdout, stderr, not finished
        return "", DRAIN_UNAVAILABLE, not finished


def _emit(stream: TextIO, line: str) -> None:
    print(line, file=stream, flush=True)
