"""The lane progress rule, driven on an injected clock and worktree fingerprint.

No test here reads wall time: `now` is passed in and the worktree state is a
value the test sets, so every verdict follows from the inputs alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.task_run import task_run_progress_rule as rule_owner

from .test_task_run_fixtures import _repo

TEST = "/usr/bin/zsh -lc 'pnpm run test:changed'"


class _Tree:
    def __init__(self) -> None:
        self.state: str | None = "tree-0"

    def __call__(self) -> str | None:
        return self.state


def _rule(window: float = 100.0) -> tuple[rule_owner.ProgressRule, _Tree]:
    tree = _Tree()
    rule = rule_owner.ProgressRule(window_seconds=window, fingerprint=tree)
    rule.start(0.0)
    return rule, tree


def _completed(command: str, item_id: str, exit_code: int = 1) -> dict[str, object]:
    return {
        "type": "item.completed",
        "item": {
            "id": item_id,
            "type": "command_execution",
            "command": command,
            "exit_code": exit_code,
        },
    }


def test_a_window_with_progress_asks_nothing() -> None:
    rule, tree = _rule()
    tree.state = "tree-1"  # a file changed

    assert rule.on_tick(99.0) is None  # inside the window: no check yet
    assert rule.on_tick(100.0) is None
    assert rule.receipt()["checks"][-1]["progress"] is True


def test_an_empty_window_requests_a_checkpoint_and_the_next_one_stops() -> None:
    rule, _tree = _rule()

    request = rule.on_tick(100.0)
    assert request is not None and request.kind == "message"
    assert request.reason_code == "no-progress"
    assert "commit it now" in request.text and "never --no-verify" in request.text
    assert rule.snapshot(150.0)["checkpoint_request"] == "delivered"

    stop = rule.on_tick(200.0)
    assert stop is not None and stop.kind == "stop"
    assert "checkpoint request went unanswered" in stop.text
    assert rule.receipt()["stop_reason"] == stop.text


def test_answering_the_request_with_any_progress_clears_it() -> None:
    rule, tree = _rule()
    assert rule.on_tick(100.0) is not None

    tree.state = "tree-after-commit"  # the lane committed
    assert rule.on_tick(200.0) is None
    assert rule.snapshot(200.0)["checkpoint_request"] is None
    assert rule.receipt()["messages"][0]["answered"] is True
    # A later empty window starts the sequence over with a request, not a stop.
    request = rule.on_tick(300.0)
    assert request is not None and request.kind == "message"


def test_a_new_command_outcome_is_progress_but_a_repeat_is_not() -> None:
    rule, _tree = _rule()
    rule.on_event(_completed("cat a.py", "c1"))
    assert rule.on_tick(100.0) is None  # one new outcome

    rule.on_event(_completed("cat a.py", "c2"))  # same command, same tree
    assert rule.on_tick(200.0) is not None  # no new outcome: request


def test_an_unobservable_worktree_falls_back_to_the_executors_own_events() -> None:
    rule, tree = _rule()
    tree.state = None
    edit = {"type": "item.completed", "item": {"id": "f1", "type": "file_change"}}

    rule.on_event(edit)
    assert rule.on_tick(100.0) is None  # the executor reported an edit
    assert rule.receipt()["checks"][-1]["tree_observable"] is False
    # Silence with an unreadable tree is still silence: request, then stop.
    assert rule.on_tick(200.0).kind == "message"
    assert rule.on_tick(300.0).kind == "stop"


def test_a_command_in_flight_defers_the_request_instead_of_killing_it() -> None:
    rule, _tree = _rule()
    started = {"type": "item.started",
               "item": {"id": "c1", "type": "command_execution", "command": TEST}}
    rule.on_event(started)

    assert rule.on_tick(100.0) is None  # deferred: the command may be long
    assert rule.snapshot(100.0)["checkpoint_request"] == "deferred"
    # Still running at the next check: now it is interrupted with the request.
    request = rule.on_tick(200.0)
    assert request is not None and request.kind == "message"
    assert "was interrupted after running for at least" in request.text
    assert rule.on_tick(300.0).kind == "stop"


def test_a_deferred_request_is_withdrawn_when_the_long_command_finishes() -> None:
    rule, _tree = _rule()
    rule.on_event({"type": "item.started",
                   "item": {"id": "c1", "type": "command_execution", "command": TEST}})
    assert rule.on_tick(100.0) is None
    rule.on_event(_completed(TEST, "c1"))  # a new outcome

    assert rule.on_tick(200.0) is None
    assert rule.snapshot(200.0)["checkpoint_request"] is None


def test_a_deferred_request_is_delivered_at_a_repeat_completion() -> None:
    rule, _tree = _rule()
    rule.on_event(_completed("cat a.py", "c0"))
    assert rule.on_tick(100.0) is None  # that outcome was progress
    rule.on_event({"type": "item.started",
                   "item": {"id": "c1", "type": "command_execution", "command": "cat a.py"}})
    assert rule.on_tick(200.0) is None  # deferred
    request = rule.on_event(_completed("cat a.py", "c1"))  # nothing new

    assert request is not None and request.reason_code == "no-progress"
    assert "interrupted" not in request.text


def test_the_third_identical_test_run_asks_for_debug_then_checkpoint_then_stops() -> None:
    rule, _tree = _rule()

    assert rule.on_event(_completed(TEST, "c1")) is None
    assert rule.on_event(_completed(TEST, "c2")) is None
    debug = rule.on_event(_completed(TEST, "c3", exit_code=1))
    assert debug is not None and debug.reason_code == "loop-debug"
    assert "debug skill" in debug.text and "last exit code 1" in debug.text
    checkpoint = rule.on_event(_completed(TEST, "c4"))
    assert checkpoint is not None and checkpoint.reason_code == "loop-checkpoint"
    stop = rule.on_event(_completed(TEST, "c5"))
    assert stop is not None and stop.kind == "stop" and stop.reason_code == "loop-stop"


def test_a_file_change_between_runs_resets_the_loop_count() -> None:
    rule, tree = _rule()
    for index in range(6):
        tree.state = f"tree-{index}"  # an edit before every run
        assert rule.on_event(_completed(TEST, f"c{index}")) is None


def test_repeats_outside_the_loop_families_never_message() -> None:
    rule, _tree = _rule()
    for index in range(6):
        assert rule.on_event(_completed("cat a.py", f"c{index}")) is None


def test_muse_bash_completions_feed_the_same_rule() -> None:
    rule, _tree = _rule()

    def bash(task_id: str) -> list[dict[str, object]]:
        chunk = json.dumps({"command": "python3 -m pytest tests/a.py", "exit_code": 1})
        return [
            {"payload_type": "task.lifecycle.proposed",
             "payload": {"task_id": task_id, "event": {"task_kind": "tool.bash"}}},
            {"payload_type": "task.lifecycle.started", "payload": {"task_id": task_id}},
            {"payload_type": "task.lifecycle.output",
             "payload": {"task_id": task_id, "event": {"chunk": chunk}}},
            {"payload_type": "task.lifecycle.completed", "payload": {"task_id": task_id}},
        ]

    actions = [rule.on_event(event) for task in ("t1", "t2", "t3") for event in bash(task)]
    assert [action.reason_code for action in actions if action] == ["loop-debug"]


def test_a_non_positive_window_turns_the_stop_off() -> None:
    rule, _tree = _rule(window=0)

    assert rule.on_tick(10_000.0) is None
    assert rule.receipt()["stop_enabled"] is False


def test_worktree_fingerprint_sees_edits_commits_and_untracked_but_not_ignored(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path, ignored=True)
    first = rule_owner.worktree_fingerprint(repo)
    assert first is not None and rule_owner.worktree_fingerprint(repo) == first

    (repo / "ignored-output.txt").write_text("cache\n", encoding="utf-8")
    assert rule_owner.worktree_fingerprint(repo) == first

    (repo / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    edited = rule_owner.worktree_fingerprint(repo)
    assert edited != first

    (repo / "new.py").write_text("NEW = 1\n", encoding="utf-8")
    untracked = rule_owner.worktree_fingerprint(repo)
    assert untracked != edited

    for args in (("add", "-A"), ("-c", "user.email=t@e", "-c", "user.name=t", "commit", "-qm", "x")):
        subprocess.run(["git", *args], cwd=repo, check=True)
    assert rule_owner.worktree_fingerprint(repo) not in {first, edited, untracked}
    assert rule_owner.worktree_fingerprint(tmp_path / "missing") is None
