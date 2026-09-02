#!/usr/bin/env python3
"""How a standing pytest run OUTLIVES the caller that started it.

SPLIT FROM `run_standing_pytest` (S6, 2026-08-15) when the round-2 repairs pushed
that file back over its length cap. One concept, not a spill: both halves here
exist for the same failure -- an agent's wrapper dies mid-suite and takes its own
transcript with it.

- `_terminate_reaps_the_child` makes SIGTERM raise, so the monitored guard kills
  the pytest process tree instead of leaving it orphaned. Without it the RUN does
  not outlive its caller correctly.
- `write_run_record` / `run_record_path` leave the outcome on disk, so the RESULT
  outlives the caller and a later session can read it back rather than saying
  "unknown".

The heartbeat interval lives here too because it answers the third form of the
same question: is this run still alive right now.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import signal
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, runtime_root

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
heartbeat_interval_from_env = _subprocess_guard.heartbeat_interval_from_env


RUN_RECORD_DIR = Path("standing-pytest")
HEARTBEAT_INTERVAL_ENV = "CHARNESS_STANDING_PYTEST_HEARTBEAT_SECONDS"


def _heartbeat_seconds() -> float:
    return heartbeat_interval_from_env(
        HEARTBEAT_INTERVAL_ENV, _subprocess_guard.DEFAULT_HEARTBEAT_SECONDS
    )


@contextlib.contextmanager
def _terminate_reaps_the_child():
    """Make SIGTERM raise, so the monitored guard kills the pytest tree first.

    SIGINT already raises `KeyboardInterrupt`; SIGTERM's default disposition is
    immediate death with no unwinding, so no `finally` and no `except
    BaseException` runs -- including the guard's `_kill_tree`. Since the child
    lives in its OWN session, that combination orphans the whole xdist tree
    exactly when an enclosing guard times out, which is the case this runner is
    most often in.

    Restores the previous handlers on the way out, and tolerates not being on the
    main thread (`signal.signal` raises `ValueError` there) rather than making
    thread context a reason the suite cannot start.

    WHAT IT DOES NOT COVER, said plainly rather than left to be discovered:
    SIGKILL. An outer guard escalates to `os.killpg(..., SIGKILL)` after its
    grace window, and `kill -9` and the OOM killer do the same; none of them can
    be handled, so in those cases the pytest tree IS orphaned. This handler
    covers the SIGTERM that arrives first, which is the path an enclosing
    monitored phase actually takes.

    A swallowed install is REPORTED, not silent: off the main thread the
    tolerated outcome is not a degraded feature, it is the orphan-the-tree
    behaviour this exists to remove, and an operator reading a log deserves to
    know which one they got.
    """

    def _raise(signum, _frame):
        raise KeyboardInterrupt(f"standing-pytest terminated by signal {signum}")

    # Built with `getattr`, because `signal.SIGHUP` does not exist on Windows and
    # evaluating it in a tuple literal would raise OUTSIDE the try below -- an
    # `except AttributeError` that can never fire while the case it names kills
    # the runner one line earlier.
    numbers = [
        number
        for number in (getattr(signal, name, None) for name in ("SIGTERM", "SIGHUP"))
        if number is not None
    ]
    previous: dict[int, Any] = {}
    for number in numbers:
        try:
            previous[number] = signal.signal(number, _raise)
        except (ValueError, OSError) as exc:
            print(
                f"standing-pytest: could not install a {number} handler ({exc}); a wrapper "
                "timeout will orphan this run's pytest process tree",
                file=sys.stderr,
            )
    try:
        yield
    finally:
        for number, handler in previous.items():
            # `signal.signal` returns None when the previous handler was not
            # installed from Python, and passing None back raises TypeError --
            # which, on the interrupt path, unwinds INSTEAD of the
            # KeyboardInterrupt and replaces the real cause with a traceback
            # naming this line.
            if handler is None:
                continue
            try:
                signal.signal(number, handler)
            except (ValueError, OSError, TypeError):
                pass


def run_record_path(repo_root: Path) -> Path:
    # The record is runtime telemetry, not repository evidence. Keeping it under
    # `.charness/` made every canonical run create an ignored worktree artifact,
    # so a clean checkout became dirty after the very gate meant to protect it.
    # An explicitly supplied runtime root can be shared by an outer quality run
    # and its synthetic repos, so keep each repo's record separate as well. The
    # record is useful only if concurrent runs cannot overwrite or concatenate it.
    repo_key = hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:16]
    return runtime_root(repo_root) / RUN_RECORD_DIR / repo_key / "last-run.json"


def write_run_record(repo_root: Path, record: dict[str, object]) -> None:
    """Leave the run's outcome somewhere a LATER session can read it.

    The heartbeat proves liveness to whoever is watching; this proves the result
    to whoever was not. That is the half SC11 asks for that monitoring alone does
    not give: when an agent's wrapper dies mid-suite, the wrapper's own transcript
    is gone, and without a record the only honest thing a next session can say is
    "unknown" -- which is what made the recorded losses cost a full re-run each.

    Best-effort by construction. A runner that fails because it could not write
    its own telemetry would be a worse runner, so an unwritable record degrades
    to no record rather than to a failed suite.
    """
    path = run_record_path(repo_root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        pass
