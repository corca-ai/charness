"""The lane progress rule, driven on an injected clock and worktree fingerprint.

No test here reads wall time: `now` is passed in and the worktree state is a
value the test sets, so every verdict follows from the inputs alone.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

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


def test_the_checkpoint_names_every_command_the_kill_interrupts() -> None:
    """The kill takes the whole process group, so the message names every
    running command, not only the last one (follow-up review 24)."""
    rule, _tree = _rule()
    for item_id, command in (("c1", TEST), ("c2", "sleep 900")):
        rule.on_event({"type": "item.started",
                       "item": {"id": item_id, "type": "command_execution", "command": command}})
    assert rule.on_tick(100.0) is None  # both young: deferred
    request = rule.on_tick(200.0)
    assert request is not None and f"`{TEST}`" in request.text and "`sleep 900`" in request.text


def test_an_interrupted_muse_command_without_text_is_still_counted() -> None:
    """A Muse bash task has no command text until its first output; the
    checkpoint still says it was interrupted (follow-up review 25)."""
    rule, _tree = _rule()
    rule.on_event({"payload_type": "task.lifecycle.proposed",
                   "payload": {"task_id": "m1", "event": {"task_kind": "tool.bash"}}})
    rule.on_event({"payload_type": "task.lifecycle.started", "payload": {"task_id": "m1"}})
    assert rule.on_tick(100.0) is None  # young: deferred
    request = rule.on_tick(200.0)
    assert request is not None
    assert "1 command(s) whose text was not yet seen" in request.text
    assert "``" not in request.text


def test_a_loop_repeat_that_resolves_a_deferred_request_delivers_the_checkpoint() -> None:
    """A third identical test run arriving while a request is deferred sends the
    checkpoint request, not the loop message, so the state the next check reads
    matches what the lane received (follow-up review 24)."""
    rule, _tree = _rule()
    rule.on_event(_completed(TEST, "c1"))
    rule.on_event(_completed(TEST, "c2"))
    assert rule.on_tick(100.0) is None  # the first run was a new outcome
    rule.on_event({"type": "item.started",
                   "item": {"id": "c3", "type": "command_execution", "command": TEST}})
    assert rule.on_tick(200.0) is None  # deferred for the young third run
    action = rule.on_event(_completed(TEST, "c3"))
    assert action is not None and action.reason_code == "no-progress"
    assert rule.snapshot(200.0)["checkpoint_request"] == "delivered-between-checks"


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
    assert "Every command still running was interrupted" in request.text
    assert TEST in request.text
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
    # Delivered between checks: the next check opens the request's full
    # window instead of stopping seconds after delivery (claims review C-B1).
    assert rule.on_tick(300.0) is None
    assert rule.checks[-1]["request_window_started"] is True
    stop = rule.on_tick(400.0)
    assert stop is not None and stop.kind == "stop"


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
    # `0` turns the whole rule off, loop check included (claims review B1).
    assert [rule.on_event(_completed(TEST, f"c{n}")) for n in range(1, 6)] == [None] * 5


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


def test_reruns_on_an_unreadable_tree_are_not_progress_and_never_claim_a_loop() -> None:
    rule, tree = _rule()
    tree.state = None
    assert rule.on_event(_completed(TEST, "c0")) is None  # new: progress
    assert rule.on_tick(100.0) is None
    for index in range(1, 6):
        assert rule.on_event(_completed(TEST, f"c{index}")) is None
    assert rule.on_tick(200.0).kind == "message"


def test_a_repeat_on_an_unreadable_tree_still_delivers_a_deferred_request() -> None:
    """Delivery at a completion does not need the tree: a known repeat with
    nothing else running delivers the deferred request (follow-up review 26)."""
    rule, tree = _rule()
    tree.state = None
    rule.on_event(_completed("cat a.py", "c0"))
    assert rule.on_tick(100.0) is None  # new outcome: progress
    rule.on_event({"type": "item.started",
                   "item": {"id": "c1", "type": "command_execution", "command": "cat a.py"}})
    assert rule.on_tick(200.0) is None  # deferred
    request = rule.on_event(_completed("cat a.py", "c1"))
    assert request is not None and request.reason_code == "no-progress"


def test_a_command_started_during_a_slow_tree_probe_is_young_not_killed() -> None:
    """The check probes the tree without the rule lock, so a command start that
    arrives mid-probe is seen as young and defers the request (review 28)."""
    import threading

    rule: rule_owner.ProgressRule
    ticking = threading.Event()

    def fingerprint() -> str:
        if ticking.is_set():
            start = {"type": "item.started",
                     "item": {"id": "mid", "type": "command_execution", "command": TEST}}
            feeder = threading.Thread(target=rule.on_event, args=(start,))
            feeder.start()
            feeder.join(timeout=2)
            assert not feeder.is_alive(), "on_event blocked behind the tree probe"
        return "same"

    rule = rule_owner.ProgressRule(window_seconds=100.0, fingerprint=fingerprint)
    rule.start(0.0)
    ticking.set()
    assert rule.on_tick(100.0) is None  # deferred for the command started mid-probe
    assert rule.checks[-1]["deferred_for_young_command"] is True


def test_a_command_started_after_the_request_is_not_killed_until_it_is_a_window_old() -> None:
    rule, _tree = _rule()
    assert rule.on_tick(100.0).kind == "message"  # delivered
    rule.on_event({"type": "item.started",
                   "item": {"id": "late", "type": "command_execution", "command": TEST}})

    assert rule.on_tick(200.0) is None  # the command is younger than a window
    assert rule.receipt()["checks"][-1]["deferred_for_young_command"] is True
    stop = rule.on_tick(300.0)  # still running a window later, nothing moved
    assert stop is not None and stop.kind == "stop"
    assert f"interrupted: `{TEST}`" in stop.text  # the stop names what it kills


@pytest.mark.parametrize(
    ("ended_normally", "answer"), [(True, (True, "lane-ended")), (False, (False, "lane-failed"))]
)
def test_only_a_clean_end_answers_a_checkpoint_request(
    ended_normally: bool, answer: tuple[bool, str]
) -> None:
    rule, _tree = _rule()
    assert rule.on_tick(100.0).kind == "message"
    rule.finish(ended_normally=ended_normally)

    message = rule.receipt()["messages"][0]
    assert (message["answered"], message["answered_by"]) == answer
    assert rule.snapshot(100.0)["checkpoint_request"] is None


def test_a_resumed_session_reusing_an_item_id_is_a_new_young_command() -> None:
    """Codex numbers items per turn, so `item_1` after a resume is a new command."""
    rule, _tree = _rule()
    started = {"type": "item.started",
               "item": {"id": "item_1", "type": "command_execution", "command": "sleep 300"}}
    rule.on_event(started)
    assert rule.on_tick(100.0) is None  # young: deferred
    assert rule.on_tick(200.0).kind == "message"  # a window old: request, killing it
    rule.start(210.0)  # the resumed invocation
    rule.on_event(started)  # the lane restarts it under the same item id

    assert rule.on_tick(300.0) is None
    assert rule.receipt()["checks"][-1]["deferred_for_young_command"] is True
    assert rule.on_tick(400.0).kind == "stop"


def test_a_stopped_rule_raises_no_more_messages() -> None:
    rule, _tree = _rule()
    assert rule.on_tick(100.0).kind == "message"
    assert rule.on_tick(200.0).kind == "stop"
    for index in range(3):
        assert rule.on_event(_completed(TEST, f"c{index}")) is None


def test_muse_edit_tools_are_outcomes_but_model_responses_are_not() -> None:
    rule, _tree = _rule()

    def task(task_id: str, kind: str) -> list[dict[str, object]]:
        return [
            {"payload_type": "task.lifecycle.proposed",
             "payload": {"task_id": task_id, "event": {"task_kind": kind}}},
            {"payload_type": "task.lifecycle.completed", "payload": {"task_id": task_id}},
        ]

    for kind in ("model.meta.response", "tool.read_file", "tool.search", "tool.write_todos"):
        for event in task(f"r-{kind}", kind):
            rule.on_event(event)
    assert rule.on_tick(100.0) is not None  # reading and planning alone are not progress
    for event in task("e1", "tool.edit_file"):
        rule.on_event(event)
    assert rule.on_tick(200.0) is None


def test_worktree_fingerprint_is_none_outside_git_and_skips_vanished_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    assert rule_owner.worktree_fingerprint(plain) is None

    repo = _repo(tmp_path)
    (repo / "gone.txt").write_text("x\n", encoding="utf-8")
    import os as real_os

    def vanished(path: object, **kwargs: object) -> object:
        if str(path).endswith("gone.txt"):
            raise FileNotFoundError(path)
        return real_os.stat(path, **kwargs)

    # Rebinds only this module's `os`; the file vanishes between listing and stat.
    monkeypatch.setattr(rule_owner, "os", type("Os", (), {"stat": staticmethod(vanished)}))
    assert rule_owner.worktree_fingerprint(repo) is not None


def test_bootstrap_shims_insert_the_repo_root_when_it_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sys

    from scripts.task_run import task_run_lane_signals

    root = Path(__file__).resolve().parents[2]
    for module in (rule_owner, task_run_lane_signals):
        stripped = [entry for entry in sys.path if entry and Path(entry).resolve() != root]
        monkeypatch.setattr(sys, "path", stripped)
        module._load_repo_runtime_bootstrap()
        assert str(root) in sys.path
