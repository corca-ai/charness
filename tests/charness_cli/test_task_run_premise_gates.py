"""Prelaunch premise gates and critical-lane acceptance skeletons."""

from __future__ import annotations

import shlex
from typing import Any

from tests.charness_cli.support import CLI, load_cli_module
from tests.charness_cli.test_task_run_fixtures import _codex, _repo, _run
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_main import run_loaded_script_main
from scripts.task_run import task_run_completion, task_run_plan, task_run_state


def _resolved(checks: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "prelaunch": {
            "enabled": bool(checks),
            "critical_lane": False,
            "acceptance_skeleton": None,
            "premise_checks": checks,
        }
    }


def _review(checks: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "status": "completed",
        "premise_failure": False,
        "findings": [],
        "premise_checks": checks,
    }


def test_one_blocked_premise_item_does_not_stop_the_lane() -> None:
    payload: dict[str, Any] = {}
    declaration = [
        {
            "id": "provider-order",
            "premise": "stable order",
            "decision_needed": "confirm or choose another API",
        }
    ]
    reviewer_calls: list[dict[str, Any]] = []

    def critic(**kwargs: Any) -> dict[str, Any]:
        reviewer_calls.append(kwargs)
        return _review(
            [
                {
                    "id": "provider-order",
                    "kind": "premise-blocked",
                    "evidence": "no ordering guarantee",
                }
            ]
        )

    blocker = task_run_plan.run_prelaunch_gates(
        payload, _resolved(declaration), "brief", brief_critic=critic
    )

    assert blocker is None
    assert len(reviewer_calls) == 1
    assert isinstance(payload["prelaunch"]["brief_critique"]["duration_ms"], int)
    assert payload["prelaunch"]["premise_checks"] == [
        {
            "id": "provider-order",
            "kind": task_run_state.ResultKind.PREMISE_BLOCKED.value,
            "evidence": "no ordering guarantee",
            "decision_needed": "confirm or choose another API",
        }
    ]


def test_run_task_launches_after_a_single_blocked_item(tmp_path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    events = tmp_path / "events.txt"
    executable = _codex(
        tmp_path,
        f"printf 'lane\\n' >> {shlex.quote(str(events))}",
    )

    def critic(**_kwargs: Any) -> dict[str, Any]:
        events.write_text("review\n", encoding="utf-8")
        return _review(
            [{"id": "provider-order", "kind": "premise-blocked", "evidence": "unknown"}]
        )

    monkeypatch.setattr(task_run_plan, "_run_brief_critique", critic)
    payload = _run(
        repo,
        tmp_path,
        executable,
        require_change=False,
        prelaunch={
            "premise_checks": [
                ["provider-order", "provider preserves order", "confirm or change API"]
            ]
        },
    )

    assert events.read_text(encoding="utf-8").splitlines() == ["review", "lane"]
    assert payload["prelaunch"]["premise_checks"][0]["kind"] == "premise-blocked"
    assert payload["execution"]["status"] == "completed"


def test_run_task_blocks_before_launch_on_a_false_brief_premise(tmp_path, monkeypatch) -> None:
    repo = _repo(tmp_path)
    marker = tmp_path / "lane-started"
    executable = _codex(tmp_path, f"touch {shlex.quote(str(marker))}")
    monkeypatch.setattr(
        task_run_plan,
        "_run_brief_critique",
        lambda **_kwargs: {
            "status": "completed",
            "premise_failure": True,
            "premise_failure_reason": "the requested API has no active consumer",
            "findings": [],
            "premise_checks": [],
        },
    )

    payload = _run(
        repo,
        tmp_path,
        executable,
        require_change=False,
        prelaunch={"brief_critique": True},
    )

    assert not marker.exists()
    assert payload["status"] == "premise-blocked"
    assert payload["result_kind"] == task_run_state.ResultKind.PREMISE_BLOCKED.value
    assert payload["blocker"] == "the requested API has no active consumer"


def test_partial_premise_success_keeps_blocked_decisions_in_receipt() -> None:
    payload: dict[str, Any] = {}
    declarations = [
        {
            "id": "consumer",
            "premise": "a CLI invokes this",
            "decision_needed": "none",
        },
        {
            "id": "ordering",
            "premise": "provider guarantees order",
            "decision_needed": "confirm or choose another API",
        },
    ]

    blocker = task_run_plan.run_prelaunch_gates(
        payload,
        _resolved(declarations),
        "brief",
        brief_critic=lambda **_kwargs: _review(
            [
                {"id": "consumer", "kind": "success", "evidence": "cmd_task_run forwards it"},
                {"id": "ordering", "kind": "premise-blocked", "evidence": "no ordering guarantee"},
            ]
        ),
    )

    assert blocker is None
    assert [item["kind"] for item in payload["prelaunch"]["premise_checks"]] == [
        task_run_state.ResultKind.SUCCESS.value,
        task_run_state.ResultKind.PREMISE_BLOCKED.value,
    ]
    assert payload["prelaunch"]["premise_checks"][1]["decision_needed"] == (
        "confirm or choose another API"
    )


def test_style_findings_are_advisory_but_false_brief_premise_blocks() -> None:
    resolved = _resolved([])
    resolved["prelaunch"]["enabled"] = True
    advisory = task_run_plan.run_prelaunch_gates(
        {},
        resolved,
        "brief",
        brief_critic=lambda **_kwargs: {
            "status": "completed",
            "premise_failure": False,
            "findings": ["consider a clearer variable name"],
        },
    )
    blocked = task_run_plan.run_prelaunch_gates(
        {},
        resolved,
        "brief",
        brief_critic=lambda **_kwargs: {
            "status": "completed",
            "premise_failure": True,
            "premise_failure_reason": "no active consumer exists",
        },
    )

    assert advisory is None
    assert blocked == "no active consumer exists"


def test_brief_critic_uses_read_only_bounded_fresh_process(tmp_path, monkeypatch) -> None:
    from scripts.runtime_bootstrap import import_repo_module
    from scripts.task_run import task_run_execution, task_run_runtime, task_run_support

    exec_lib = import_repo_module(task_run_plan.__file__, "scripts.worktree.worktree_exec_lib")
    observed: dict[str, Any] = {}
    monkeypatch.setattr(task_run_runtime, "_resolve_codex", lambda _name: "/usr/bin/codex")
    monkeypatch.setattr(
        task_run_runtime,
        "build_codex_command",
        lambda executable, *, effort: [executable, "exec", "--sandbox", "workspace-write", "-"],
    )
    monkeypatch.setattr(
        exec_lib,
        "prepare_exec_environment",
        lambda *_args, **_kwargs: {"PATH": "/usr/bin"},
    )
    monkeypatch.setattr(task_run_support, "scrubbed_lane_env", lambda _p, env, _e: env)

    def execute(command: list[str], **kwargs: Any) -> dict[str, Any]:
        observed["command"] = command
        observed["timeout_seconds"] = kwargs["timeout_seconds"]
        kwargs["stdout_log"].write_text(
            '{"premise_failure": false, "findings": [], "premise_checks": []}',
            encoding="utf-8",
        )
        return {"exit_code": 0, "timed_out": False}

    monkeypatch.setattr(task_run_execution, "_execute_codex", execute)
    review = task_run_plan._run_brief_critique(
        payload={"task_id": "lane", "execution_runtime_root": str(tmp_path / "execution")},
        resolved={"runtime_path": tmp_path / "runtime", "target_path": tmp_path, "executor": "muse"},
        prompt="implement the lane",
        premise_checks=[],
    )

    assert observed["command"][observed["command"].index("--sandbox") + 1] == "read-only"
    assert observed["timeout_seconds"] == 120
    assert review["status"] == "completed"


def test_critical_acceptance_skeleton_must_be_green_for_completion(tmp_path) -> None:
    target = install_committed_repo(
        tmp_path / "lane",
        {"tests/test_acceptance.py": "def test_acceptance():\n    assert False\n"},
    )
    payload: dict[str, Any] = {}
    resolved = _resolved([])
    resolved["target_path"] = target
    resolved["prelaunch"] = {
        "enabled": True,
        "critical_lane": True,
        "acceptance_skeleton": "tests/test_acceptance.py",
        "premise_checks": [],
    }
    blocker = task_run_plan.run_prelaunch_gates(
        payload,
        resolved,
        "brief",
        brief_critic=lambda **_kwargs: _review([]),
    )
    assert blocker is None
    assert payload["prelaunch"]["acceptance_skeleton"]["baseline"]["status"] == "red"
    assert "tests/test_acceptance.py" in task_run_plan.acceptance_skeleton_prompt(
        "brief", payload
    )

    skeleton = target / "tests/test_acceptance.py"
    skeleton.write_text("def test_acceptance():\n    assert True\n", encoding="utf-8")
    acceptance = task_run_plan.finish_acceptance_skeleton(payload, target)
    assert acceptance is not None and acceptance["status"] == "green"
    assert task_run_completion._acceptance_result_state("completed", acceptance) == "completed"

    skeleton.write_text("def test_acceptance():\n    assert False\n", encoding="utf-8")
    acceptance = task_run_plan.finish_acceptance_skeleton(payload, target)
    blockers = task_run_completion._completion_blockers(
        execution_status="completed",
        scope={"verdict": "pass", "reason": ""},
        parent_progress={"blocking": False},
        pass_value="pass",
        delivery={"status": "delivered", "text": "done"},
        acceptance_skeleton=acceptance,
    )

    assert acceptance is not None and acceptance["status"] == "red"
    assert "acceptance skeleton did not turn green" in blockers
    assert task_run_completion._acceptance_result_state("completed", acceptance) == (
        "completed-needs-review"
    )


def test_cli_forwards_prelaunch_declarations_to_task_runner(
    tmp_path, monkeypatch
) -> None:
    module = load_cli_module("charness_task_run_premise_gates", CLI)
    observed: dict[str, Any] = {}

    class FakeTaskRun:
        @staticmethod
        def run_task(*_args: Any, **kwargs: Any) -> dict[str, Any]:
            observed.update(kwargs)
            return {"status": "completed", "result_kind": "success"}

    monkeypatch.setattr(module, "_load_task_run_lib", lambda _args: FakeTaskRun)
    result = run_loaded_script_main(
        str(CLI),
        module,
        "task",
        "run",
        "--repo-root",
        str(tmp_path),
        "--lane",
        "fixture-lane",
        "--scope",
        "module.py",
        "--prompt",
        "fixture",
        "--effort",
        "medium",
        "--critical-lane",
        "--acceptance-skeleton",
        "tests/test_acceptance.py",
        "--premise-check",
        "ordering",
        "provider preserves order",
        "verify or choose another API",
    )

    assert result.returncode == 0
    assert observed["prelaunch"] == {
        "brief_critique": True,
        "critical_lane": True,
        "acceptance_skeleton": "tests/test_acceptance.py",
        "premise_checks": [
            ["ordering", "provider preserves order", "verify or choose another API"]
        ],
    }
