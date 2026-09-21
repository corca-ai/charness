"""Live phase relay and no-progress guard for require-change lanes (#815)."""

from __future__ import annotations

import math
import os
import threading
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

LANE_PHASES = ("CONTRACT-READ", "EDITING", "TESTING")

#: Typed stop marker the progress guard appends to the executor transcript
#: before killing a stalled lane. Parsed like `BLOCKED:` on the receipt.
NO_PROGRESS_STOP_PREFIX = "NO-PROGRESS-STOP:"

#: Wall-clock budget between `CONTRACT-READ` and the first scoped signal
#: (`EDITING` or a real scoped diff) before a require-change lane is stopped
#: as a typed no-progress blocker. `<= 0` turns the stop off.
NO_PROGRESS_BUDGET_ENV = "CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS"
PROGRESS_POLL_ENV = "CHARNESS_TASK_RUN_PROGRESS_POLL_SECONDS"
BLOCKED_GRACE_ENV = "CHARNESS_TASK_RUN_BLOCKED_GRACE_SECONDS"
DEFAULT_NO_PROGRESS_BUDGET_SECONDS = 300.0
DEFAULT_PROGRESS_POLL_SECONDS = 15.0
#: Grace after a declared `BLOCKED:` marker before a still-running lane is
#: stopped. Compliant executors exit promptly on their own; only a lane that
#: lingers past the grace is killed, so a block declaration cannot become a
#: full-timeout consumption.
DEFAULT_BLOCKED_GRACE_SECONDS = 60.0

#: Phase-marker scan window for the executor transcript. Stderr can grow
#: without bound on long lanes; markers are emitted throughout the run, so the
#: tail carries the phases that matter for the receipt.
_MAX_LANE_STDERR_SCAN_BYTES = 256 * 1024


def lane_progress(stdout_text: str, stderr_text: str = "") -> dict[str, Any]:
    """Parse phase markers and the typed blocker from lane output (#815).

    Executors render progress on stderr while stdout carries the machine
    delivery: a lane whose stdout stayed empty still emitted CONTRACT-READ
    on stderr, so both streams are parsed (stdout first, stderr second).
    A guard-issued `NO-PROGRESS-STOP:` line parses as the blocker, like an
    executor-issued `BLOCKED:` line.
    """
    phases: list[str] = []
    blocker: str | None = None
    for text in (stdout_text, stderr_text):
        for line in text.splitlines():
            stripped = line.strip()
            if stripped in LANE_PHASES and stripped not in phases:
                phases.append(stripped)
            elif blocker is None and stripped.startswith("BLOCKED:"):
                blocker = stripped[len("BLOCKED:"):].strip() or None
            elif blocker is None and stripped.startswith(NO_PROGRESS_STOP_PREFIX):
                blocker = stripped[len(NO_PROGRESS_STOP_PREFIX):].strip() or None
    return {"phases": phases, "blocker": blocker}


def no_progress_stop_due(
    *,
    phases: Sequence[str],
    contract_read_at: float | None,
    now: float,
    budget_seconds: float,
    diff_present: bool | None,
) -> str | None:
    """Whether the no-progress guard must stop the lane now (#815).

    Pure in its inputs (including `now`) so tests drive it on a controlled
    clock: a require-change lane that announced `CONTRACT-READ` but shows no
    `EDITING` and no real scoped diff once the budget is spent is a typed
    stall, not a lane still worth its remaining timeout. An unobservable
    diff (`None`) suppresses the stop: the guard may only kill on an
    affirmative observed-absent worktree, never on a failed observation.
    """
    if budget_seconds <= 0:
        return None
    if "EDITING" in phases or diff_present:
        return None
    if diff_present is None:
        return None
    if "CONTRACT-READ" not in phases or contract_read_at is None:
        return None
    if now - contract_read_at < budget_seconds:
        return None
    return (
        "require-change lane produced no EDITING and no scoped diff within "
        f"{budget_seconds:g}s after CONTRACT-READ"
    )


def scoped_diff_present(
    worktree: Path, base_sha: str, scope_specs: Sequence[Mapping[str, Any]]
) -> bool | None:
    """Whether the worktree currently holds a real scoped diff.

    Reuses the checkpoint's own classification (refreshed specs plus the
    carrier's changed paths), so the live guard and the terminal checkpoint
    agree on what counts as progress. Three-valued: True/False for an
    observed worktree, None when the worktree cannot be observed — the guard
    must not kill a lane it cannot see.
    """
    try:
        refreshed = _support._refresh_scope_specs(worktree, list(scope_specs))
        changed = _support._candidate_carrier(worktree, base_sha)["changed_paths"]
        return bool(_support._paths_in_scopes(changed, refreshed))
    except Exception:  # noqa: BLE001 - an unobservable tree reads as unknown
        return None


def _lane_stderr_text(stdout_log: Path, stderr_log: Path | None) -> str:
    """Executor stderr for phase-marker parsing (#815).

    Executors render progress (CONTRACT-READ / EDITING / TESTING / BLOCKED)
    on stderr while stdout carries the machine delivery, so a lane whose
    delivery stayed empty can still have emitted its phases. An explicit log
    wins; otherwise the conventional `<executor>.stderr.log` sibling of the
    stdout log is tried. Anything unreadable parses as no markers.
    """
    candidate = stderr_log
    if candidate is None and stdout_log.name.endswith(".stdout.log"):
        candidate = stdout_log.with_name(
            stdout_log.name[: -len(".stdout.log")] + ".stderr.log"
        )
    if candidate is None:
        return ""
    try:
        if not candidate.is_file():
            return ""
        raw = candidate.read_bytes()
        return raw[-_MAX_LANE_STDERR_SCAN_BYTES:].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _guard_phases(payload: Mapping[str, Any]) -> list[str]:
    """Phases the live guard observed, for the terminal receipt merge (#815)."""
    guard = payload.get("progress_guard")
    if not isinstance(guard, Mapping):
        return []
    phases = guard.get("last_phases")
    if not isinstance(phases, list):
        return []
    return [phase for phase in phases if isinstance(phase, str)]


def _guard_stop_reason(payload: Mapping[str, Any]) -> str:
    """The live guard stop reason, for when the transcript marker is lost (#815)."""
    guard = payload.get("progress_guard")
    if not isinstance(guard, Mapping):
        return ""
    reason = guard.get("stop_reason")
    return reason if isinstance(reason, str) else ""


def _env_seconds(name: str, default: float) -> float:
    """A tuned duration from the environment, falling back to the default.

    Non-finite values (NaN/inf) parse but break every comparison the guard
    and the receipt predicates rely on, so they fall back like unparsable
    ones instead of arming a stop the receipt reports as disabled.
    """
    try:
        value = float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default
    if not math.isfinite(value):
        return default
    return value


def _tail_text(path: Path, limit: int = 64 * 1024) -> str:
    try:
        if not path.is_file():
            return ""
        return path.read_bytes()[-limit:].decode("utf-8", errors="replace")
    except OSError:
        return ""


class LaneProgressWatch:
    """Live phase relay and no-progress guard for one require-change lane.

    The carrier cannot stream the executor's own pipes (they are redirected
    into the lane logs), so the watch tails those logs on a poll cadence and
    relays phase changes as `PROGRESS` lines on the carrier's own stderr —
    the parent observes "alive and editing" versus "alive but exploring"
    without tailing private executor logs (#815). When the lane announced
    `CONTRACT-READ` but shows no `EDITING` and no real scoped diff once the
    budget is spent, the watch records a typed `NO-PROGRESS-STOP` marker on
    the transcript and kills the lane instead of letting it consume its full
    timeout in analysis.

    The clock is injectable so tests drive `tick` deterministically; only the
    thin `_run` loop touches wall-clock time.
    """

    def __init__(
        self,
        *,
        stdout_log: Path,
        stderr_log: Path,
        worktree: Path,
        base_sha: str,
        scope_specs: Sequence[Mapping[str, Any]],
        budget_seconds: float,
        poll_seconds: float,
        blocked_grace_seconds: float = DEFAULT_BLOCKED_GRACE_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._stdout_log = stdout_log
        self._stderr_log = stderr_log
        self._worktree = worktree
        self._base_sha = base_sha
        self._scope_specs = list(scope_specs)
        self._budget_seconds = budget_seconds
        self._poll_seconds = max(poll_seconds, 0.05)
        self._blocked_grace_seconds = blocked_grace_seconds
        self._clock = clock
        self._contract_read_at: float | None = None
        self._blocker_at: float | None = None
        self._blocker: str | None = None
        self._last_phases: list[str] = []
        self._started_at: float | None = None
        self._emit: Callable[[list[str], float], None] | None = None
        self._kill: Callable[[], None] | None = None
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None
        self.stop_reason: str | None = None

    def start(
        self,
        *,
        emit: Callable[[list[str], float], None],
        kill: Callable[[], None],
    ) -> None:
        """Begin polling beside the running lane; `kill` stops its process group."""
        self._emit = emit
        self._kill = kill
        self._started_at = self._clock()
        self._thread = threading.Thread(
            target=self._run, name="charness-lane-progress", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Halt polling; safe to call when the lane already exited."""
        self._stopped.set()
        if self._thread is not None:
            self._thread.join(timeout=self._poll_seconds + 5)

    def receipt(self) -> dict[str, Any]:
        """The guard configuration and outcome for the lane receipt."""
        return {
            "enabled": True,
            "stop_enabled": self._budget_seconds > 0,
            "linger_stop_enabled": self._blocked_grace_seconds > 0,
            "budget_seconds": self._budget_seconds,
            "blocked_grace_seconds": self._blocked_grace_seconds,
            "poll_seconds": self._poll_seconds,
            "stop_reason": self.stop_reason,
            "last_phases": list(self._last_phases),
        }

    def tick(self, now: float) -> str | None:
        """One poll: relay new phases and report a stop reason, if due.

        Cumulative: markers are one-line events the executor need not
        repeat, so phases union into the watched set and the first
        `CONTRACT-READ` observation time is kept. A marker that aged out of
        the tail window still counts (#815).
        """
        progress = lane_progress(
            _tail_text(self._stdout_log), _tail_text(self._stderr_log)
        )
        fresh = [phase for phase in progress["phases"]]
        new = [phase for phase in LANE_PHASES if phase in fresh and phase not in self._last_phases]
        if new:
            self._last_phases = [
                phase
                for phase in LANE_PHASES
                if phase in self._last_phases or phase in fresh
            ]
            if self._emit is not None and self._started_at is not None:
                self._emit(list(self._last_phases), now - self._started_at)
        phases = list(self._last_phases)
        # The declared blocker is cumulative like phases: a marker that ages
        # out of the tail window still counts, so a lingering lane cannot
        # evade the grace by emitting enough output after declaring BLOCKED.
        observed = progress["blocker"]
        if observed is not None and self._blocker is None:
            self._blocker = observed
        blocker = observed if observed is not None else self._blocker
        if blocker is not None:
            # A declared block is terminal semantics, not a stall to watch:
            # a lane that lingers past the grace after declaring BLOCKED is
            # stopped, so the declaration cannot burn the full timeout. A
            # non-positive grace turns the linger stop off independently of
            # the no-progress budget.
            if self._blocked_grace_seconds <= 0:
                return None
            if self._blocker_at is None:
                self._blocker_at = now
                return None
            if now - self._blocker_at < self._blocked_grace_seconds:
                return None
            return (
                f"lane declared BLOCKED ({blocker}) but kept running; "
                f"stopped after {self._blocked_grace_seconds:g}s"
            )
        if "CONTRACT-READ" not in phases:
            return None
        if self._contract_read_at is None:
            self._contract_read_at = now
        return no_progress_stop_due(
            phases=phases,
            contract_read_at=self._contract_read_at,
            now=now,
            budget_seconds=self._budget_seconds,
            diff_present=scoped_diff_present(
                self._worktree, self._base_sha, self._scope_specs
            ),
        )

    def fire(self, reason: str) -> None:
        """Record the typed stop on the transcript and kill the stalled lane."""
        try:
            with self._stderr_log.open("a", encoding="utf-8") as handle:
                handle.write(f"{NO_PROGRESS_STOP_PREFIX} {reason}\n")
        except OSError:
            pass
        finally:
            if self._kill is not None:
                self._kill()

    def _run(self) -> None:
        while not self._stopped.wait(self._poll_seconds):
            try:
                reason = self.tick(self._clock())
            except Exception:  # noqa: BLE001 - a failed poll must not kill the watch
                continue
            if reason is None:
                continue
            self.stop_reason = reason
            try:
                self.fire(reason)
            except Exception:  # noqa: BLE001 - a failed stop must not kill the watch
                pass
            return


def build_progress_watch(
    *,
    require_change: bool,
    stdout_log: Path,
    stderr_log: Path,
    worktree: Path,
    base_sha: str,
    scope_specs: Sequence[Mapping[str, Any]],
) -> LaneProgressWatch | None:
    """The live guard for a require-change lane, or None when it is off.

    Only require-change lanes are watched, and a non-positive budget turns
    the stop off (the phase relay still runs while the lane does).
    """
    if not require_change:
        return None
    return LaneProgressWatch(
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=worktree,
        base_sha=base_sha,
        scope_specs=scope_specs,
        budget_seconds=_env_seconds(
            NO_PROGRESS_BUDGET_ENV, DEFAULT_NO_PROGRESS_BUDGET_SECONDS
        ),
        poll_seconds=_env_seconds(PROGRESS_POLL_ENV, DEFAULT_PROGRESS_POLL_SECONDS),
        blocked_grace_seconds=_env_seconds(
            BLOCKED_GRACE_ENV, DEFAULT_BLOCKED_GRACE_SECONDS
        ),
    )


def _execute_watched_lane(
    payload: dict[str, Any],
    command: list[str],
    *,
    lane_prompt: str,
    resolved_target: Path,
    configured_env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
    require_change: bool,
    base_sha: str,
    scope_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run the lane executor under its live progress guard (#815).

    Require-change lanes tail their logs for phase markers (relayed as
    `PROGRESS` lines) and are stopped early once the no-progress budget is
    spent with no `EDITING` and no scoped diff. The guard configuration and
    outcome are recorded on the receipt beside the execution.
    """
    lane_watch = build_progress_watch(
        require_change=require_change,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=resolved_target,
        base_sha=base_sha,
        scope_specs=scope_specs,
    )
    execution = _execution._execute_codex(
        command,
        prompt=lane_prompt,
        target_path=resolved_target,
        configured_env=configured_env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=timeout_seconds,
        lane_watch=lane_watch,
    )
    if lane_watch is not None:
        payload["progress_guard"] = lane_watch.receipt()
    return execution
