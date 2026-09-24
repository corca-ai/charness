"""Live phase relay and no-progress guard for require-change lanes (#815)."""

from __future__ import annotations

import json
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

_env_seconds = _execution._env_seconds
_tail_text = _execution._tail_text
_lane_stderr_text = _execution._lane_stderr_text
_guard_phases = _execution._guard_phases
_guard_stop_reason = _execution._guard_stop_reason

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
        for line in _transcript_lines(text):
            stripped = line.strip()
            if stripped in LANE_PHASES and stripped not in phases:
                phases.append(stripped)
            elif blocker is None and stripped.startswith("BLOCKED:"):
                blocker = stripped[len("BLOCKED:"):].strip() or None
            elif blocker is None and stripped.startswith(NO_PROGRESS_STOP_PREFIX):
                blocker = stripped[len(NO_PROGRESS_STOP_PREFIX):].strip() or None
    return {"phases": phases, "blocker": blocker}


def _transcript_lines(text: str):
    """Expose phase text inside JSONL executor events as transcript lines."""
    for line in text.splitlines():
        yield line
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        yield from _event_texts(event)


def _event_texts(value: Any):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in {"text", "message", "content", "last_agent_message"} and isinstance(
                nested, str
            ):
                yield from nested.splitlines()
            else:
                yield from _event_texts(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _event_texts(nested)


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


def _worktree_liveliness(worktree: Path, base_sha: str) -> dict[str, Any] | None:
    """Changed files, lane-branch commits, and the last subject, or None when unobservable."""
    try:
        changed = _support._candidate_carrier(worktree, base_sha)["changed_paths"]
        log = _support._git(worktree, "log", f"{base_sha}..HEAD", "--format=%s")
        subjects = (
            [line.strip() for line in log.stdout.splitlines() if line.strip()]
            if log.returncode == 0
            else []
        )
    except Exception:  # noqa: BLE001 - an unobservable tree reads as unknown
        return None
    return {
        "files_changed": len(changed),
        "commits": len(subjects),
        "last_commit_subject": subjects[0][:120] if subjects else None,
    }


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
        observe: Callable[[dict[str, Any]], None] | None = None,
        budget_source: str = "env",
    ) -> None:
        self._stdout_log = stdout_log
        self._stderr_log = stderr_log
        self._worktree = worktree
        self._base_sha = base_sha
        self._scope_specs = list(scope_specs)
        self._budget_seconds = budget_seconds
        self._budget_source = budget_source
        self._poll_seconds = max(poll_seconds, 0.05)
        self._blocked_grace_seconds = blocked_grace_seconds
        self._clock = clock
        self._observe = observe
        self._last_log_sizes: tuple[int, int] = (-1, -1)
        self._last_growth_at: float | None = None
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
        self._first_scoped_paths: list[str] | None = None
        self._first_scoped_diff: str | None = None
        self._first_scoped_truncated: bool = False
        self._first_scoped_elapsed: float | None = None
        self._steer_queue = stdout_log.parent / "steer.queue.jsonl"
        self._steer_seen: set[str] = set()
        self._steer_messages: list[dict[str, Any]] = []

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
        self._stopped.clear()
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
            "budget_source": self._budget_source,
            "blocked_grace_seconds": self._blocked_grace_seconds,
            "poll_seconds": self._poll_seconds,
            "stop_reason": self.stop_reason,
            "last_phases": list(self._last_phases),
            "first_scoped_diff": {
                "observed": self._first_scoped_paths is not None,
                "changed_paths": list(self._first_scoped_paths or []),
                "diff": self._first_scoped_diff,
                "truncated": self._first_scoped_truncated,
                "observed_elapsed_s": self._first_scoped_elapsed,
            },
        }

    def tick(self, now: float) -> str | None:
        """One poll: relay new phases, publish a live snapshot, report a stop reason."""
        self._poll_steer_queue()
        self._track_log_growth(now)
        reason = self._poll(now)
        if self._observe is not None:
            try:
                self._observe(self.snapshot(now))
            except Exception:  # noqa: BLE001 - a failed snapshot must not kill the watch
                pass
        return reason

    def pending_steers(self) -> list[dict[str, Any]]:
        """Read the queue once more at the turn boundary and return undelivered entries."""
        self._poll_steer_queue()
        return [message for message in self._steer_messages if message.get("delivered_at") is None]

    def record_steer_delivery(
        self, messages: Sequence[Mapping[str, Any]], *, resume_path: str
    ) -> None:
        """Record the typed delivery disposition after the next invocation starts."""
        by_id = {item.get("message_id"): item for item in self._steer_messages}
        stamp = _support.utc_now_iso()
        from scripts.task_run import task_run_lane_runner as _lane_runner

        for message in messages:
            current = by_id.get(message.get("message_id"))
            if current is not None:
                current.update(
                    delivered_at=stamp,
                    disposition="accepted",
                    reason=None,
                    resume_path=resume_path,
                )
                _lane_runner.update_steer_queue(self._steer_queue, current)

    def _poll_steer_queue(self) -> None:
        from scripts.task_run import task_run_lane_runner as _lane_runner

        for message in _lane_runner.read_steer_queue(self._steer_queue):
            message_id = message.get("message_id")
            if not isinstance(message_id, str) or message_id in self._steer_seen:
                continue
            self._steer_seen.add(message_id)
            self._steer_messages.append(dict(message))

    def snapshot(self, now: float) -> dict[str, Any]:
        """Cheap live lane signal for result.json pollers (#829).

        Phase plus worktree truth the orchestrator previously re-derived by
        hand: changed-file count, lane-branch commit count, and the last
        commit subject. Tool-call counts are executor-private and stay out;
        log silence is reported as seconds since the logs last grew.
        """
        lively = _worktree_liveliness(self._worktree, self._base_sha)
        lively = lively if isinstance(lively, dict) else {}
        age = None if self._last_growth_at is None else max(0.0, now - self._last_growth_at)
        return {
            "phase": self._last_phases[-1] if self._last_phases else None,
            "phases": list(self._last_phases),
            "files_changed": lively.get("files_changed"),
            "commits": lively.get("commits"),
            "last_commit_subject": lively.get("last_commit_subject"),
            "seconds_since_log_growth": age,
        }

    def _track_log_growth(self, now: float) -> None:
        try:
            sizes = (
                self._stdout_log.stat().st_size if self._stdout_log.is_file() else 0,
                self._stderr_log.stat().st_size if self._stderr_log.is_file() else 0,
            )
        except OSError:
            return
        if sizes != self._last_log_sizes:
            self._last_log_sizes = sizes
            self._last_growth_at = now

    def _poll(self, now: float) -> str | None:
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
        diff_present = scoped_diff_present(
            self._worktree, self._base_sha, self._scope_specs
        )
        if diff_present:
            self._maybe_snapshot_scoped_diff(now)
        return no_progress_stop_due(
            phases=phases,
            contract_read_at=self._contract_read_at,
            now=now,
            budget_seconds=self._budget_seconds,
            diff_present=diff_present,
        )

    def _maybe_snapshot_scoped_diff(self, now: float) -> None:
        """Keep the first observed scoped diff so a self-revert stays recoverable (#834).

        Best-effort and once-only: the guard must never fail a lane it is
        watching, so any unobservable worktree simply leaves the snapshot
        empty for the receipt backstop to report as unobserved.
        """
        if self._first_scoped_paths is not None:
            return
        try:
            refreshed = _support._refresh_scope_specs(self._worktree, list(self._scope_specs))
            changed = _support._candidate_carrier(self._worktree, self._base_sha)[
                "changed_paths"
            ]
            scoped = _support._paths_in_scopes(changed, refreshed)
            if not scoped:
                return
            self._first_scoped_paths = list(scoped)
            elapsed = None
            if self._started_at is not None:
                elapsed = max(0.0, now - self._started_at)
            self._first_scoped_elapsed = elapsed
            # The diff covers the first 50 paths; a longer scoped set is a
            # second truncation source beside the byte cap below.
            self._first_scoped_truncated = len(scoped) > 50
            result = _support._git(
                self._worktree, "diff", self._base_sha, "--", *scoped[:50]
            )
            text = result.stdout if result.returncode == 0 else ""
        except Exception:  # noqa: BLE001 - an unobservable tree reads as unknown
            return
        limit = 64 * 1024
        if len(text.encode("utf-8", errors="replace")) > limit:
            raw = text.encode("utf-8", errors="replace")[:limit]
            self._first_scoped_diff = raw.decode("utf-8", errors="replace")
            self._first_scoped_truncated = True
        else:
            self._first_scoped_diff = text

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
    observe: Callable[[dict[str, Any]], None] | None = None,
    budget_override: float | None = None,
) -> LaneProgressWatch | None:
    """The live guard for a require-change lane, or None when it is off.

    The guard owns queue polling for watched lanes. Execution checks the same
    queue at every natural executor boundary when this guard is absent. An
    explicit ``budget_override`` (``--no-progress-seconds``) wins over the
    environment so a contract-heavy lane records its budget as a deliberate
    per-lane choice (#835).
    """
    if not require_change:
        return None
    if budget_override is None:
        budget_seconds = (
            _env_seconds(NO_PROGRESS_BUDGET_ENV, DEFAULT_NO_PROGRESS_BUDGET_SECONDS)
        )
        budget_source = (
            "env" if require_change and NO_PROGRESS_BUDGET_ENV in os.environ
            else "default" if require_change else "disabled"
        )
    else:
        budget_seconds = budget_override
        budget_source = "flag"
    return LaneProgressWatch(
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=worktree,
        base_sha=base_sha,
        scope_specs=scope_specs,
        budget_seconds=budget_seconds,
        poll_seconds=_env_seconds(PROGRESS_POLL_ENV, DEFAULT_PROGRESS_POLL_SECONDS),
        blocked_grace_seconds=(
            _env_seconds(BLOCKED_GRACE_ENV, DEFAULT_BLOCKED_GRACE_SECONDS)
            if require_change else 0.0
        ),
        observe=observe,
        budget_source=budget_source,
    )

def _execute_watched_lane(payload: dict[str, Any], command: list[str], **kwargs: Any) -> dict[str, Any]:
    """Run the lane executor; the attempt loop owns retries (see task_run_attempts)."""
    from scripts.task_run import task_run_attempts as _attempts

    return _attempts._execute_watched_lane(payload, command, **kwargs)
