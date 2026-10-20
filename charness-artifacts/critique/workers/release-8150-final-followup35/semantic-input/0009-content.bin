"""The lane progress rule: the one stop condition a task-run lane has.

A wall-clock timeout killed productive lanes mid-edit and let a looping lane
burn its whole budget. This rule replaces it with progress. Progress since the
last check is any of: a new commit, a file change, or a new command outcome
(a completed command whose (command text, worktree fingerprint) pair this lane
has not completed before; rerunning a command on an unchanged tree is not
new, and a completion without command text always is). Every progress window the rule checks. A window without progress earns
a checkpoint request; a second one in a row, with the request unanswered,
stops the lane. A command the rule has seen start since the previous check,
still running, defers the request, and so the stop, by one check, or by two
when the rule first sees it start while a check is probing the tree (a start
the event reader has not delivered yet is unseen). Windows are
nominal: the watch runs a due check at its next poll. A hung command, a silent model and a dead executor are the
same case, so there is no second timer.

Loops are judged at each command completion: the third completion of the
same test, lint or typecheck command on an unchanged worktree asks the lane
to switch to the debug skill, the fourth asks it to checkpoint and stop, and
the fifth stops it.

The rule is pure over its inputs: the clock is the caller's `now`, the
worktree is read through an injected fingerprint. An unobservable worktree
(`None`) shows neither progress nor its absence: the window check falls back
to the executor's own events, so a silent lane is still stopped, and no loop
is claimed without seeing the tree. The watch (`task_run_progress`) applies its actions.
"""

from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_process  # noqa: E402
from scripts.task_run import task_run_event_timing as _timing  # noqa: E402

#: Muse task kinds that change files (seen in ceal lane logs, 2026-10-20);
#: reads, searches, todo lists and bash input are activity, not outcomes.
MUSE_EDIT_TOOL_KINDS = frozenset({"tool.edit", "tool.edit_file", "tool.write_file"})
PROGRESS_WINDOW_ENV = "CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS"
_NO_PROBE = object()  # sentinel: no tree probe was taken before the lock
DEFAULT_PROGRESS_WINDOW_SECONDS = 1200.0
LOOP_FAMILIES = frozenset({"test", "lint", "typecheck"})
_FINGERPRINT_PROBE_SECONDS = 60.0

CHECKPOINT_REQUEST = (
    "charness progress check: no commit, file change, or new command result in the "
    "last {window}. If your work has a coherent state, commit it now (hooks must "
    "pass; never --no-verify) and write your final report naming what remains. If "
    "you are blocked, reply on its own line: BLOCKED: <reason>. If you are still "
    "making progress, continue; charness stops this lane if the next {window} also "
    "shows no commit, file change, or new command result."
)
LOOP_DEBUG_REQUEST = (
    "charness loop check: `{command}` has now completed {count} times with no file "
    "change between runs{exit}. Running it again will not change the result. Switch "
    "to the debug skill: read the failure output, state one falsifiable hypothesis, "
    "and change code, test, or approach before you run it again."
)
LOOP_CHECKPOINT_REQUEST = (
    "charness loop check: `{command}` ran a {count}th time on an unchanged worktree. "
    "Checkpoint now: commit the coherent part of your work if there is one (hooks "
    "must pass; never --no-verify), write your final report naming what is "
    "unresolved, and stop. One more identical run stops this lane."
)


@dataclass(frozen=True)
class Action:
    """What the watch must do now: send `message` (preempting) or `stop`."""

    kind: str
    text: str
    reason_code: str


def worktree_fingerprint(worktree: Path) -> str | None:
    """One hash of HEAD, the tracked diff, and untracked files, or None if unobservable.

    Ignored files (build output, caches) do not count. Untracked files are
    read by size and modification time, not content, so a rewrite counts as a
    change; the error is toward progress, never toward a false stop.
    """
    digest = hashlib.sha256()
    for args in (
        ("rev-parse", "HEAD"),
        ("diff", "HEAD", "--no-ext-diff", "--no-color", "--binary"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        try:
            result = run_process(
                ["git", *args], cwd=worktree, timeout_seconds=_FINGERPRINT_PROBE_SECONDS
            )
        except OSError:
            return None
        if result.returncode != 0:
            return None
        digest.update(result.stdout.encode("utf-8", "surrogateescape") + b"\0")
        if args[0] == "ls-files":
            for name in sorted(filter(None, result.stdout.split("\0"))):
                try:
                    stat = os.stat(worktree / name, follow_symlinks=False)
                except OSError:
                    continue
                digest.update(f"{name}\0{stat.st_size}\0{stat.st_mtime_ns}\0".encode(
                    "utf-8", "surrogateescape"
                ))
    return digest.hexdigest()


def _duration(seconds: float) -> str:
    return f"{seconds / 60:g} minutes" if seconds >= 60 else f"{seconds:g} seconds"


class ProgressRule:
    """Window checks and loop detection for one lane; thread-safe.

    `on_event` runs on the event reader as each executor line arrives;
    `on_tick` runs on the watch's poll. Both return an `Action` or None.
    Request states: None, `deferred` (a command was in flight at an empty
    check; delivery waits for its completion or the next check),
    `delivered-between-checks` (delivered at a command completion; the next
    check starts the request's full window instead of stopping), and
    `delivered` (an empty check stops the lane, unless a command younger
    than one window is running, which defers the stop a check).
    """

    def __init__(
        self,
        *,
        window_seconds: float,
        fingerprint: Callable[[], str | None],
        window_source: str = "default",
    ) -> None:
        self.window_seconds = window_seconds
        self.window_source = window_source
        self._fingerprint = fingerprint
        self._lock = threading.Lock()
        self._completion_state: object = _NO_PROBE
        self._timeline = _timing._Timeline(on_complete=self._on_complete)
        self._muse_kinds: dict[str, str] = {}
        self._outcomes: dict[tuple[str, str], int] = {}
        self._pending: Action | None = None
        self._last_check_at: float | None = None
        self._last_state: str | None = None
        self._last_progress_at: float | None = None
        self._new_outcomes = 0
        self._request: str | None = None
        self._in_flight_at_check: set[str] = set()
        self._invocation = 0
        self.checks: list[dict[str, Any]] = []
        self.messages: list[dict[str, Any]] = []
        self.stop_reason: str | None = None

    def start(self, now: float) -> None:
        """Begin observing at `now`; a later call starts the next invocation.

        Window state carries over a preemption; command state does not: the
        previous executor process is dead, and a resumed Codex session reuses
        item ids, so each invocation gets a fresh timeline and its own keys.
        """
        with self._lock:
            if self._last_check_at is None:
                self._last_check_at = now
                self._last_progress_at = now
                self._last_state = self._fingerprint()
            else:
                self._invocation += 1
                self._timeline = _timing._Timeline(on_complete=self._on_complete)
                self._muse_kinds = {}

    def _in_flight(self) -> dict[str, str]:
        return {
            f"{self._invocation}:{key}": command
            for key, command in self._timeline.in_flight().items()
        }

    def on_event(self, event: Mapping[str, Any]) -> Action | None:
        # A command completion keys its outcome to the tree; probe it before
        # taking the lock, so a window check is never held behind it. The
        # event reader itself still waits for the probe before it reads the
        # next line, so a start arriving during it is seen only afterwards.
        state = self._fingerprint() if self._is_command_completion(event) else _NO_PROBE
        with self._lock:
            if self.stop_reason is not None or self.window_seconds <= 0:
                return None  # stopped, or the rule is off: no message reaches the lane
            self._count_edit_outcome(event)
            self._completion_state = state
            self._timeline.feed(None, event)
            action, self._pending = self._pending, None
            return self._record(action)

    def _is_command_completion(self, event: Mapping[str, Any]) -> bool:
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, Mapping):
            return item.get("type") == "command_execution"
        payload = event.get("payload")
        return (
            event.get("payload_type") == "task.lifecycle.completed"
            and isinstance(payload, Mapping)
            and str(payload.get("task_id")) in self._timeline.bash_tasks()
        )

    def _count_edit_outcome(self, event: Mapping[str, Any]) -> None:
        """File edits the executor reports are outcomes even when git cannot be read."""
        item = event.get("item")
        if (
            event.get("type") == "item.completed"
            and isinstance(item, Mapping)
            and item.get("type") == "file_change"
        ):
            self._new_outcomes += 1
            return
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            return
        task_id = str(payload.get("task_id"))
        inner = payload.get("event")
        if event.get("payload_type") == "task.lifecycle.proposed" and isinstance(inner, Mapping):
            self._muse_kinds[task_id] = str(inner.get("task_kind") or "")
        elif event.get("payload_type") == "task.lifecycle.completed":
            if self._muse_kinds.get(task_id, "") in MUSE_EDIT_TOOL_KINDS:
                self._new_outcomes += 1

    def _on_complete(self, command: str | None, exit_code: object) -> None:
        if not command:
            self._new_outcomes += 1  # an unnamed command cannot be proven a repeat
            return
        state = self._completion_state
        if state is _NO_PROBE:
            state = self._fingerprint()
        # An unreadable tree is one unknown state: a new command is still new,
        # a rerun is not, and no loop is claimed without seeing the tree.
        key = (command.strip(), state or "unobservable")
        count = self._outcomes.get(key, 0) + 1
        self._outcomes[key] = count
        if count == 1:
            self._new_outcomes += 1
        if count > 1 and self._request == "deferred" and not self._in_flight():
            # The deferred request waited for this boundary, and the command
            # produced nothing new: deliver it now. It arrives between checks,
            # so the next check opens its full window rather than stopping.
            self._request = "delivered-between-checks"
            self._pending = self._checkpoint_request(interrupted=[])
            return
        if state is None:
            return
        if count < 3 or not LOOP_FAMILIES & set(_timing.command_families(command)):
            return
        shown = command.strip()[:200]
        if count == 3:
            ending = f" (last exit code {exit_code})" if isinstance(exit_code, int) else ""
            self._pending = Action(
                "message",
                LOOP_DEBUG_REQUEST.format(command=shown, count=count, exit=ending),
                "loop-debug",
            )
        elif count == 4:
            self._pending = Action(
                "message",
                LOOP_CHECKPOINT_REQUEST.format(command=shown, count=count),
                "loop-checkpoint",
            )
        elif count == 5:
            self._pending = Action(
                "stop",
                f"loop: `{shown}` completed {count} times on an unchanged worktree; "
                "the debug and checkpoint requests went unanswered",
                "loop-stop",
            )

    def _checkpoint_request(self, *, interrupted: list[str]) -> Action:
        text = CHECKPOINT_REQUEST.format(window=_duration(self.window_seconds))
        if interrupted:
            # The kill takes the executor's whole process group, so every
            # running command is interrupted, not only the oldest one.
            named = [f"`{command[:200]}`" for command in interrupted if command]
            unnamed = len(interrupted) - len(named)
            if unnamed:  # e.g. a Muse bash task killed before its first output
                named.append(f"{unnamed} command(s) whose text was not yet seen")
            text += (
                f" Every command still running was interrupted ({', '.join(named)}), "
                "each after "
                f"running for at least {_duration(self.window_seconds)}; they may have "
                "left partial output or files. Do not simply rerun them: run a narrower "
                "or faster variant, or report that one needs longer."
            )
        return Action("message", text, "no-progress")

    def on_tick(self, now: float) -> Action | None:
        with self._lock:
            if self.window_seconds <= 0 or self._last_check_at is None:
                return None
            if now - self._last_check_at < self.window_seconds:
                return None
            # Only commands already running before this probe count as seen at
            # this check: one that starts mid-probe stays young at the next
            # check too, so no seen command is killed before it has run a full
            # window (a start not yet delivered by the event reader is unseen).
            seen_before_probe = set(self._in_flight())
        # Probe the tree without the lock, so executor events keep arriving: a
        # command that starts during a slow probe is in flight (and young) below
        # instead of waiting on the lock while the check decides to preempt.
        state = self._fingerprint()
        with self._lock:
            tree_changed = state is not None and state != self._last_state
            progressed = tree_changed or self._new_outcomes > 0
            in_flight = self._in_flight()
            young = set(in_flight) - self._in_flight_at_check
            self._in_flight_at_check = seen_before_probe & set(in_flight)
            check = {
                "elapsed_s": round(now - self._last_check_at, 3),
                "progress": progressed,
                "new_outcomes": self._new_outcomes,
                "tree_changed": tree_changed,
                "tree_observable": state is not None,
                "commands_in_flight": len(in_flight),
                "commands_started_since_check": len(young),
                "request_before": self._request,
            }
            self.checks.append(check)
            self._last_check_at = now
            self._last_state = state if state is not None else self._last_state
            self._new_outcomes = 0
            if progressed:
                self._last_progress_at = now
                if self._request in ("delivered", "delivered-between-checks"):
                    self._mark_answered(True, "progress")
                self._request = None
                return None
            if young:
                # A command started after the last check has run less than one
                # window, and preemption never kills a command that young: the
                # request (or stop) waits for its completion or the next check.
                check["deferred_for_young_command"] = True
                if self._request is None:
                    self._request = "deferred"
                return None
            if self._request == "delivered-between-checks":
                # Less than a window has passed since delivery: start it now.
                self._request = "delivered"
                check["request_window_started"] = True
                return None
            if self._request in (None, "deferred"):
                self._request = "delivered"
                return self._record(self._checkpoint_request(interrupted=list(in_flight.values())))
            self._mark_answered(False, "unanswered")
            window = _duration(self.window_seconds)
            running = [f"`{command[:200]}`" if command else "an unnamed command"
                       for command in in_flight.values()]
            killed = f"; interrupted: {', '.join(running)}" if running else ""
            return self._record(
                Action(
                    "stop",
                    f"no commit, file change, or new command result in two consecutive "
                    f"{window} windows; the checkpoint request went unanswered{killed}",
                    "no-progress-stop",
                )
            )

    def _mark_answered(self, answered: bool, by: str) -> None:
        for message in reversed(self.messages):
            if message["reason_code"] == "no-progress":
                if "answered" not in message:
                    message.update(answered=answered, answered_by=by)
                return

    def finish(self, *, ended_normally: bool) -> None:
        """The executor stopped running; a clean end answers a delivered request.

        A clean end is the executor's own exit 0 (its final report or a
        `BLOCKED:` line ends the turn); a timeout, interruption, or failure
        leaves the request unanswered.
        """
        with self._lock:
            if self._request in ("delivered", "delivered-between-checks"):
                if ended_normally:
                    self._mark_answered(True, "lane-ended")
                else:
                    self._mark_answered(False, "lane-failed")
            self._request = None

    def _record(self, action: Action | None) -> Action | None:
        if action is None:
            return None
        if action.kind == "stop":
            self.stop_reason = action.text
        else:
            self.messages.append({"reason_code": action.reason_code, "text": action.text})
        return action

    def snapshot(self, now: float) -> dict[str, Any]:
        with self._lock:
            since = None if self._last_progress_at is None else now - self._last_progress_at
            return {
                "window_seconds": self.window_seconds,
                "seconds_since_progress_seen": (
                    None if since is None else round(max(0.0, since), 3)
                ),
                "checkpoint_request": self._request,
            }

    def receipt(self) -> dict[str, Any]:
        with self._lock:
            return {
                "window_seconds": self.window_seconds,
                "window_source": self.window_source,
                "stop_enabled": self.window_seconds > 0,
                "checks": list(self.checks),
                "messages": [dict(message) for message in self.messages],
                "stop_reason": self.stop_reason,
            }
