"""Live phase relay and no-progress guard for require-change lanes (#815)."""

from __future__ import annotations

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

from scripts.task_run import task_run_evidence as _evidence  # noqa: E402
from scripts.task_run import task_run_execution as _execution  # noqa: E402
from scripts.task_run import task_run_lane_signals as _signals  # noqa: E402
from scripts.task_run import task_run_progress_rule as _rule  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

_env_seconds = _execution._env_seconds
_guard_phases = _execution._guard_phases
_guard_stop_reason = _execution._guard_stop_reason

LANE_PHASES = _signals.LANE_PHASES
NO_PROGRESS_STOP_PREFIX = _signals.NO_PROGRESS_STOP_PREFIX
lane_progress = _signals.lane_progress
_transcript_lines = _signals._transcript_lines
_event_texts = _signals._event_texts
no_progress_stop_due = _signals.no_progress_stop_due
scoped_diff_present = _signals.scoped_diff_present
_worktree_liveliness = _signals._worktree_liveliness


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
#: Consecutive failed progress checks before the watch stops the lane: with
#: no wall clock, a watch that cannot check must not leave a lane unbounded.
MAX_RULE_FAILURES = 8


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
        budget_raw: str | None = None,
        progress_rule: _rule.ProgressRule | None = None,
    ) -> None:
        self._stdout_log = stdout_log
        self._stderr_log = stderr_log
        self._worktree = worktree
        self._base_sha = base_sha
        self._scope_specs = list(scope_specs)
        self._budget_seconds = budget_seconds
        self._budget_source = budget_source
        self._budget_raw = budget_raw
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
        from scripts.task_run import task_run_lane_runner as _lane_runner

        self._steer_queue = _lane_runner.steer_queue_path(stdout_log.parent)
        self._steer_seen: set[str] = set()
        self._steer_messages: list[dict[str, Any]] = []
        self._progress_rule = progress_rule
        self._action_lock = threading.Lock()
        self._preempted = False
        self.preemptions = 0
        self._rule_failures = 0
        self.suppressed_actions = 0
        self._undelivered: list[dict[str, Any]] = []

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
        if self._progress_rule is not None:
            self._progress_rule.start(self._started_at)
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
            "budget_raw": self._budget_raw,
            "blocked_grace_seconds": self._blocked_grace_seconds,
            "poll_seconds": self._poll_seconds,
            "stop_reason": self.stop_reason,
            "preemptions": self.preemptions,
            "suppressed_actions": self.suppressed_actions,
            "progress_rule": (
                None if self._progress_rule is None else self._progress_rule.receipt()
            ),
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
        try:
            self._poll_steer_queue()
            self._track_log_growth(now)
            reason = self._poll(now)
        except Exception:  # noqa: BLE001 - the progress rule below must still run
            reason = None
        # The progress rule is the lane's only bound, so it runs even when the
        # phase or queue poll above fails.
        reason = reason or self._tick_rule(now)
        if self._observe is not None:
            try:
                self._observe(self.snapshot(now))
            except Exception:  # noqa: BLE001 - a failed snapshot must not kill the watch
                pass
        return reason

    def _tick_rule(self, now: float) -> str | None:
        if self._progress_rule is None:
            return None
        checks_before = len(self._progress_rule.checks)
        try:
            action = self._progress_rule.on_tick(now)
        except Exception as exc:  # noqa: BLE001 - counted; repeated failure stops the lane
            self._rule_failures += 1
            if self._rule_failures < MAX_RULE_FAILURES:
                return None
            return (
                f"progress watch failed {self._rule_failures} consecutive checks "
                f"({type(exc).__name__}: {exc}); the lane cannot be bounded"
            )
        if len(self._progress_rule.checks) > checks_before:
            # Only a completed due check proves the rule works; a no-op poll
            # between failing checks must not reset the count.
            self._rule_failures = 0
        if action is not None and action.kind == "stop":
            return action.text
        self._apply(action)
        return None

    def finish_lane(self, *, ended_normally: bool) -> None:
        """The executor stopped running; resolve an outstanding checkpoint request."""
        if self._progress_rule is not None:
            self._progress_rule.finish(ended_normally=ended_normally)

    def observe_event(self, event: Mapping[str, Any]) -> None:
        """Feed one executor event to the progress rule (runs on the event reader)."""
        if self._progress_rule is None or self.stop_reason is not None:
            return
        action = self._progress_rule.on_event(event)
        if action is not None and action.kind == "stop":
            self._stop_now(action.text)
        else:
            self._apply(action)

    def _apply(self, action: _rule.Action | None) -> None:
        """Deliver the rule's message now: queue it as a steer, then preempt.

        The kill ends this executor invocation; the execution loop sees the
        preemption and resumes the same session with the queued message.
        """
        if action is None or self._kill is None:
            return
        from scripts.task_run import task_run_lane_runner as _lane_runner

        with self._action_lock:
            # First wins: once the lane is stopping (here or in the rule), a
            # message would never be delivered, so it is suppressed and counted.
            rule = self._progress_rule
            if self.stop_reason is not None or (rule is not None and rule.stop_reason):
                self.suppressed_actions += 1
                return
            self._undelivered.append(
                _lane_runner.enqueue_steer(
                    self._steer_queue,
                    self._stdout_log.parent.name,
                    action.text,
                    reason=action.reason_code,
                    actor="charness-progress-rule",
                )
            )
            if not self._preempted:
                # One preemption per invocation; later messages ride along.
                self._preempted = True
                self.preemptions += 1
                self._kill()

    def take_preempted(self) -> bool:
        """Whether the last invocation ended because the watch preempted it."""
        preempted, self._preempted = self._preempted, False
        return preempted

    def _stop_now(self, reason: str) -> None:
        from scripts.task_run import task_run_lane_runner as _lane_runner

        with self._action_lock:
            if self.stop_reason is not None:
                return
            self.stop_reason = reason
            # A message queued in this invocation will never be delivered: the
            # stop supersedes it, and its preemption did not happen as one.
            for record in self._undelivered:
                _lane_runner.update_steer_queue(
                    self._steer_queue,
                    {**record, "disposition": "nacked", "reason_code": "superseded-by-stop"},
                )
                self.suppressed_actions += 1
            self._undelivered = []
            if self._preempted:
                self._preempted = False
                self.preemptions -= 1
        try:
            self.fire(reason)
        except Exception:  # noqa: BLE001 - a failed stop must not kill the reader
            pass

    def pending_steers(self) -> list[dict[str, Any]]:
        """Read the queue once more at the turn boundary and return undelivered entries."""
        self._poll_steer_queue()
        return [message for message in self._steer_messages if message.get("delivered_at") is None]

    def record_steer_delivery(
        self, messages: Sequence[Mapping[str, Any]], *, resume_path: str
    ) -> None:
        """Record the typed delivery disposition after the next invocation starts."""
        by_id = {item.get("message_id"): item for item in self._steer_messages}
        delivered = {message.get("message_id") for message in messages}
        with self._action_lock:
            self._undelivered = [
                item for item in self._undelivered if item.get("message_id") not in delivered
            ]
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
        progress = None if self._progress_rule is None else self._progress_rule.snapshot(now)
        return {
            "progress_rule": progress,
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
            _evidence._tail_text(self._stdout_log),
            _evidence._tail_text(self._stderr_log),
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
        snapshot = _signals.scoped_diff_snapshot(self._worktree, self._base_sha, self._scope_specs)
        if snapshot is None:
            return
        self._first_scoped_paths, self._first_scoped_diff, self._first_scoped_truncated = snapshot
        if self._started_at is not None:
            self._first_scoped_elapsed = max(0.0, now - self._started_at)

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
            if self.stop_reason is not None:
                return
            try:
                reason = self.tick(self._clock())
            except Exception:  # noqa: BLE001 - a failed poll must not kill the watch
                continue
            if reason is None:
                continue
            self._stop_now(reason)
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
    """The live watch for a lane, or None when nothing would be watched.

    Every lane gets the progress rule (`task_run_progress_rule`), the one
    stop a lane has once no wall clock bounds it; `CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS`
    sets its window and `0` turns it off. A require-change lane also gets the
    first-edit budget and the BLOCKED linger grace. The guard owns queue
    polling for watched lanes. Execution checks the same queue at every
    natural executor boundary when this guard is absent. An explicit
    ``budget_override`` (``--no-progress-seconds``) wins over the environment
    so a contract-heavy lane records its budget as a deliberate per-lane
    choice (#835).
    """
    window_seconds, window_parsed = _env_seconds(
        _rule.PROGRESS_WINDOW_ENV, _rule.DEFAULT_PROGRESS_WINDOW_SECONDS
    )
    if not require_change and window_seconds <= 0:
        return None
    progress_rule = _rule.ProgressRule(
        window_seconds=window_seconds,
        fingerprint=lambda: _rule.worktree_fingerprint(worktree),
        window_source="env" if window_parsed else "default",
    )
    budget_raw = os.environ.get(NO_PROGRESS_BUDGET_ENV)
    if not require_change:
        budget_seconds, budget_source = 0.0, "disabled"
    elif budget_override is None:
        budget_seconds, budget_parsed = _env_seconds(
            NO_PROGRESS_BUDGET_ENV, DEFAULT_NO_PROGRESS_BUDGET_SECONDS
        )
        budget_source = "env" if budget_parsed else "default"
    else:
        budget_seconds = budget_override
        budget_source = "flag"
    poll_seconds, _ = _env_seconds(PROGRESS_POLL_ENV, DEFAULT_PROGRESS_POLL_SECONDS)
    grace_seconds, _ = _env_seconds(BLOCKED_GRACE_ENV, DEFAULT_BLOCKED_GRACE_SECONDS)
    return LaneProgressWatch(
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        worktree=worktree,
        base_sha=base_sha,
        scope_specs=scope_specs,
        budget_seconds=budget_seconds,
        poll_seconds=poll_seconds,
        blocked_grace_seconds=grace_seconds if require_change else 0.0,
        observe=observe,
        budget_source=budget_source,
        budget_raw=budget_raw,
        progress_rule=progress_rule,
    )


def _execute_watched_lane(payload: dict[str, Any], command: list[str], **kwargs: Any) -> dict[str, Any]:
    """Run the lane executor; the attempt loop owns retries (see task_run_attempts)."""
    from scripts.task_run import task_run_attempts as _attempts

    return _attempts._execute_watched_lane(payload, command, **kwargs)
