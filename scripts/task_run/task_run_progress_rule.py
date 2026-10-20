"""The lane progress rule: the one stop condition a task-run lane has.

A wall-clock timeout killed productive lanes mid-edit and let a looping lane
burn its whole budget. This rule replaces it with progress. Progress since the
last check is any of: a new commit, a file change, or a new command outcome
(a completed command whose (command text, worktree fingerprint) pair this lane
has not completed before; rerunning a command on an unchanged tree is not
new). Every progress window the rule checks. A window without progress earns
a checkpoint request; a second one in a row, with the request unanswered,
stops the lane. A hung command, a silent model and a dead executor are the
same case, so there is no second timer.

Loops are judged at each command completion: the third completion of the
same test, lint or typecheck command on an unchanged worktree asks the lane
to switch to the debug skill, the fourth asks it to checkpoint and stop, and
the fifth stops it.

The rule is pure over its inputs: the clock is the caller's `now`, the
worktree is read through an injected fingerprint, and an unobservable
worktree (`None`) counts as progress, so the rule never stops a lane it
cannot see. The watch (`task_run_progress`) applies its actions.
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

PROGRESS_WINDOW_ENV = "CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS"
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
    check; delivery waits for its completion or the next check), and
    `delivered` (the next empty check stops the lane).
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
        self.checks: list[dict[str, Any]] = []
        self.messages: list[dict[str, Any]] = []
        self.stop_reason: str | None = None

    def start(self, now: float) -> None:
        """Begin observing at `now`; a later call (after a preemption) continues."""
        with self._lock:
            if self._last_check_at is None:
                self._last_check_at = now
                self._last_progress_at = now
                self._last_state = self._fingerprint()

    def on_event(self, event: Mapping[str, Any]) -> Action | None:
        with self._lock:
            self._count_edit_outcome(event)
            self._timeline.feed(None, event)
            action, self._pending = self._pending, None
            return self._record(action)

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
            kind = self._muse_kinds.get(task_id, "")
            if kind.startswith("tool.") and kind != "tool.bash":
                self._new_outcomes += 1

    def _on_complete(self, command: str | None, exit_code: object) -> None:
        if not command:
            self._new_outcomes += 1  # an unnamed command cannot be proven a repeat
            return
        state = self._fingerprint()
        # An unreadable tree is one unknown state: a new command is still new,
        # a rerun is not, and no loop is claimed without seeing the tree.
        key = (command.strip(), state or "unobservable")
        count = self._outcomes.get(key, 0) + 1
        self._outcomes[key] = count
        if count == 1:
            self._new_outcomes += 1
        if state is None:
            return
        if count > 1 and self._request == "deferred" and not self._timeline.in_flight():
            # The deferred request waited for this boundary, and the command
            # produced nothing new: deliver it now.
            self._request = "delivered"
            self._pending = self._checkpoint_request(interrupted=None)
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

    def _checkpoint_request(self, *, interrupted: str | None) -> Action:
        text = CHECKPOINT_REQUEST.format(window=_duration(self.window_seconds))
        if interrupted:
            text += (
                f" Your running command `{interrupted[:200]}` was interrupted after "
                f"running for at least {_duration(self.window_seconds)}; it may have "
                "left partial output or files."
            )
        return Action("message", text, "no-progress")

    def on_tick(self, now: float) -> Action | None:
        with self._lock:
            if self.window_seconds <= 0 or self._last_check_at is None:
                return None
            if now - self._last_check_at < self.window_seconds:
                return None
            state = self._fingerprint()
            tree_changed = state is not None and state != self._last_state
            progressed = tree_changed or self._new_outcomes > 0
            in_flight = self._timeline.in_flight()
            young = set(in_flight) - self._in_flight_at_check
            self._in_flight_at_check = set(in_flight)
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
                if self._request == "delivered":
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
            if self._request in (None, "deferred"):
                self._request = "delivered"
                interrupted = list(in_flight.values())[-1] if in_flight else None
                return self._record(self._checkpoint_request(interrupted=interrupted))
            self._mark_answered(False, "unanswered")
            window = _duration(self.window_seconds)
            return self._record(
                Action(
                    "stop",
                    f"no commit, file change, or new command result in two consecutive "
                    f"{window} windows; the checkpoint request went unanswered",
                    "no-progress-stop",
                )
            )

    def _mark_answered(self, answered: bool, by: str) -> None:
        for message in reversed(self.messages):
            if message["reason_code"] == "no-progress":
                if "answered" not in message:
                    message.update(answered=answered, answered_by=by)
                return

    def finish(self) -> None:
        """The lane ended on its own: a delivered request was answered by that end."""
        with self._lock:
            if self._request == "delivered":
                self._mark_answered(True, "lane-ended")
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
