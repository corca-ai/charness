from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from scripts.task_run import task_run_dag as dag
from scripts.task_run.task_run_state import ResultKind


def _raw_plan(repo: Path, *, max_parallel: int = 1) -> dict[str, Any]:
    (repo / "briefs").mkdir(parents=True, exist_ok=True)
    (repo / "briefs" / "base.md").write_text("base brief\n", encoding="utf-8")
    (repo / "briefs" / "dependent.md").write_text("dependent brief\n", encoding="utf-8")
    return {
        "schema": dag.PLAN_SCHEMA,
        "repo_root": ".",
        "provider": {"repo": "corca-ai/charness", "parent_issue": 844},
        "max_parallel": max_parallel,
        "lanes": [
            {
                "key": "base",
                "issue_number": 853,
                "depends_on": [],
                "carrier": "codex",
                "brief_path": "briefs/base.md",
                "scopes": ["scripts/example.py"],
                "effort": "medium",
            },
            {
                "key": "dependent",
                "issue_number": 854,
                "depends_on": ["base"],
                "carrier": "muse",
                "brief_path": "briefs/dependent.md",
                "scopes": ["tests/example.py"],
                "effort": "high",
            },
        ],
    }


def _load_plan(tmp_path: Path, *, max_parallel: int = 1) -> dict[str, Any]:
    plan_path = tmp_path / "dag.json"
    plan_path.write_text(json.dumps(_raw_plan(tmp_path, max_parallel=max_parallel)), encoding="utf-8")
    return dag.load_plan(plan_path)


def _provider(states: dict[int, str]):
    def read(_repo_root: Path, _repo: str, _parent_issue: int) -> dict[int, str]:
        return dict(states)

    return read


def test_runtime_bootstrap_adds_the_script_repository_to_import_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "path", [])

    dag._load_repo_runtime_bootstrap()

    assert str(Path(dag.__file__).resolve().parents[2]) in sys.path


def test_plan_is_one_static_source_and_ready_derivation_uses_provider_states(
    tmp_path: Path,
) -> None:
    plan = _load_plan(tmp_path)
    assert [lane["key"] for lane in plan["lanes"]] == ["base", "dependent"]
    assert "state" not in plan["lanes"][0]
    assert dag.derive_ready(plan, {"base": "OPEN", "dependent": "OPEN"}) == ["base"]
    assert dag.derive_ready(plan, {"base": "CLOSED", "dependent": "OPEN"}) == [
        "dependent"
    ]


def test_soft_dependency_does_not_block_launch(tmp_path: Path) -> None:
    plan = _load_plan(tmp_path)
    dependent = plan["lanes"][1]
    dependent["dependency_kinds"] = {"base": "soft"}

    assert dag.derive_ready(plan, {"base": "OPEN", "dependent": "OPEN"}) == [
        "base",
        "dependent",
    ]


def test_status_reads_child_state_and_reports_blocker_without_persisting(tmp_path: Path) -> None:
    plan = _load_plan(tmp_path)
    source_before = (tmp_path / "dag.json").read_bytes()
    payload = dag.status_once(
        plan,
        provider_reader=_provider({853: "OPEN", 854: "OPEN"}),
    )

    assert payload["status"] == dag.PASS
    assert payload["lanes"] == [
        {
            "key": "base",
            "issue_number": 853,
            "provider_state": "OPEN",
            "ready": True,
            "blocked_by": [],
        },
        {
            "key": "dependent",
            "issue_number": 854,
            "provider_state": "OPEN",
            "ready": False,
            "blocked_by": ["base"],
        },
    ]
    assert (tmp_path / "dag.json").read_bytes() == source_before


def test_pull_launches_newly_ready_dependent_after_provider_closes_dependency(
    tmp_path: Path,
) -> None:
    plan = _load_plan(tmp_path)
    states = {853: "OPEN", 854: "OPEN"}
    launches: list[str] = []

    def launch(_repo_root: Path, lane: dict[str, Any]) -> dict[str, Any]:
        launches.append(lane["key"])
        if lane["key"] == "base":
            states[853] = "CLOSED"
        return {
            "task_id": lane["key"],
            "status": "validated-partial-result" if lane["key"] == "dependent" else "completed",
        }

    payload = dag.pull_once(
        plan,
        provider_reader=_provider(states),
        task_reader=lambda _repo_root: {},
        launcher=launch,
    )

    assert launches == ["base", "dependent"]
    assert [row["key"] for row in payload["launched"]] == launches
    assert payload["launched"][1]["result_kind"] == ResultKind.VALIDATED_PARTIAL.value
    assert payload["launched"][1]["exit_code"] == 3
    assert payload["result_kind"] == ResultKind.VALIDATED_PARTIAL.value
    assert payload["exit_code"] == 3
    assert payload["provider_states"][0]["provider_state"] == "CLOSED"


def test_pull_does_not_start_ready_lane_when_every_slot_is_occupied(tmp_path: Path) -> None:
    plan = _load_plan(tmp_path)
    launches: list[str] = []
    payload = dag.pull_once(
        plan,
        provider_reader=_provider({853: "CLOSED", 854: "OPEN"}),
        task_reader=lambda _repo_root: {
            "other-task": {
                "task_id": "other-task",
                "status": "running",
                "liveness": {"alive": True},
            }
        },
        launcher=lambda _root, lane: launches.append(lane["key"]),
    )

    assert launches == []
    assert payload["launched"] == []
    assert payload["status"] == dag.PASS
    assert payload["result_kind"] == ResultKind.SUCCESS.value


def test_plan_rejects_dependency_cycles_and_provider_graph_mismatch(tmp_path: Path) -> None:
    plan_path = tmp_path / "dag.json"
    raw = _raw_plan(tmp_path)
    raw["lanes"][0]["depends_on"] = ["dependent"]
    plan_path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(dag.DagError, match="cycle"):
        dag.load_plan(plan_path)

    plan = _load_plan(tmp_path / "valid")
    with pytest.raises(dag.DagError, match="exactly match"):
        dag.status_once(plan, provider_reader=_provider({853: "OPEN"}))


def test_plan_file_read_failure_is_typed(tmp_path: Path) -> None:
    plan_path = tmp_path / "bad.json"
    plan_path.write_text("{", encoding="utf-8")

    with pytest.raises(dag.DagError, match="could not read plan"):
        dag.load_plan(plan_path)


def test_provider_reader_uses_issue_tool_and_returns_only_provider_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(
            command,
            0,
            "ok: true\nchildren:\n  - number: 853\n    state: OPEN\n  - number: 854\n    state: CLOSED\n",
            "",
        )

    monkeypatch.setattr(dag._guard, "run_process", run)
    states = dag.read_provider_children(tmp_path, "corca-ai/charness", 844)

    assert states == {853: "OPEN", 854: "CLOSED"}
    assert calls[0][1].endswith("skills/public/issue/scripts/issue_tool.py")
    assert calls[0][2:4] == ["list-sub-issues", "--repo"]


def test_module_command_reads_one_plan_and_emits_structured_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    plan_path = tmp_path / "dag.json"
    plan_path.write_text(json.dumps(_raw_plan(tmp_path)), encoding="utf-8")
    expected = {"status": dag.PASS, "result_kind": ResultKind.SUCCESS.value, "exit_code": 0}
    monkeypatch.setattr(dag, "configure_runtime_environment", lambda _repo_root: {})
    monkeypatch.setattr(dag, "status_once", lambda _plan: expected)

    assert dag.main(["status", "--plan-file", str(plan_path)]) == 0
    assert json.loads(capsys.readouterr().out) == expected


def test_lane_launcher_delegates_to_task_run_with_static_brief(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = _load_plan(tmp_path)
    lane = plan["lanes"][1]
    captured: dict[str, Any] = {}

    def run(repo_root: Path, **kwargs: Any) -> dict[str, Any]:
        captured.update(repo_root=repo_root, **kwargs)
        return {"status": "completed", "task_id": "dependent"}

    from scripts.task_run import task_run

    monkeypatch.setattr(task_run, "run_task", run)
    result = dag._launch_lane(plan["repo_root"], lane)

    assert result["task_id"] == "dependent"
    assert captured["prompt"] == "dependent brief\n"
    assert captured["executor"] == "muse"
    assert captured["effort"] == "high"
    assert captured["lane"] == "dependent"


def test_pull_records_launcher_exception_as_failed_result(tmp_path: Path) -> None:
    plan = _load_plan(tmp_path)

    def fail(_repo_root: Path, _lane: dict[str, Any]) -> object:
        raise RuntimeError("executor launch failed")

    payload = dag.pull_once(
        plan,
        provider_reader=_provider({853: "OPEN", 854: "CLOSED"}),
        task_reader=lambda _repo_root: {},
        launcher=fail,
    )

    assert payload["status"] == dag.FAIL
    assert payload["result_kind"] == ResultKind.FAILED.value
    assert payload["exit_code"] == 1
    assert payload["launched"] == [
        {
            "key": "base",
            "task_id": "base",
            "result_kind": ResultKind.FAILED.value,
            "exit_code": 1,
            "blocker": "executor launch failed",
        }
    ]


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("root-type", "root must be a mapping"),
        ("unknown-root-key", "unknown keys"),
        ("schema", "plan.schema"),
        ("repo-empty", "repo_root must"),
        ("repo-missing", "not a directory"),
        ("provider-shape", "exactly repo and parent_issue"),
        ("provider-repo", "owner/repository"),
        ("parent-issue", "positive integer"),
        ("max-parallel", "positive integer"),
        ("lanes-empty", "non-empty list"),
        ("lane-shape", "known fields"),
        ("lane-key", "key is invalid"),
        ("issue-number", "issue_number must be positive"),
        ("dependencies", "unique string list"),
        ("dependency-keys", "name declared dependencies"),
        ("dependency-kind", "hard, soft, or integration-gate"),
        ("carrier", "carrier must"),
        ("effort", "effort is invalid"),
        ("brief-empty", "brief_path"),
        ("brief-escape", "escapes plan.repo_root"),
        ("brief-missing", "does not exist"),
        ("scopes", "scopes must"),
        ("duplicate-key", "keys must be unique"),
        ("duplicate-issue", "issue numbers must be unique"),
        ("unknown-dependency", "unknown dependencies"),
    ],
)
def test_plan_validation_refuses_malformed_inputs(
    tmp_path: Path, case: str, message: str
) -> None:
    raw = _raw_plan(tmp_path)
    def set_value(plan: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
        plan[key] = value
        return plan

    def set_provider(plan: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
        plan["provider"][key] = value
        return plan

    def set_lane(
        plan: dict[str, Any], key: str, value: Any, index: int = 0
    ) -> dict[str, Any]:
        plan["lanes"][index][key] = value
        return plan

    mutations = {
        "root-type": lambda _plan: [],
        "unknown-root-key": lambda plan: set_value(plan, "status", "OPEN"),
        "schema": lambda plan: set_value(plan, "schema", "other"),
        "repo-empty": lambda plan: set_value(plan, "repo_root", " "),
        "repo-missing": lambda plan: set_value(plan, "repo_root", "missing-repo"),
        "provider-shape": lambda plan: set_value(plan, "provider", {"repo": "corca-ai/charness"}),
        "provider-repo": lambda plan: set_provider(plan, "repo", "charness"),
        "parent-issue": lambda plan: set_provider(plan, "parent_issue", "844"),
        "max-parallel": lambda plan: set_value(plan, "max_parallel", 0),
        "lanes-empty": lambda plan: set_value(plan, "lanes", []),
        "lane-shape": lambda plan: set_lane(plan, "unknown", True),
        "lane-key": lambda plan: set_lane(plan, "key", "contains space"),
        "issue-number": lambda plan: set_lane(plan, "issue_number", 0),
        "dependencies": lambda plan: set_lane(plan, "depends_on", [1]),
        "dependency-keys": lambda plan: set_lane(plan, "dependency_kinds", {"ghost": "hard"}),
        "dependency-kind": lambda plan: set_lane(
            plan, "dependency_kinds", {"base": "invalid"}, index=1
        ),
        "carrier": lambda plan: set_lane(plan, "carrier", "unknown"),
        "effort": lambda plan: set_lane(plan, "effort", "high"),
        "brief-empty": lambda plan: set_lane(plan, "brief_path", ""),
        "brief-escape": lambda plan: set_lane(plan, "brief_path", "../outside.md"),
        "brief-missing": lambda plan: set_lane(plan, "brief_path", "briefs/missing.md"),
        "scopes": lambda plan: set_lane(plan, "scopes", []),
        "duplicate-key": lambda plan: set_lane(plan, "key", "base", index=1),
        "duplicate-issue": lambda plan: set_lane(plan, "issue_number", 853, index=1),
        "unknown-dependency": lambda plan: set_lane(plan, "depends_on", ["ghost"]),
    }
    raw = mutations[case](raw)

    with pytest.raises(dag.DagError, match=message):
        dag.validate_plan(raw, plan_path=tmp_path / "dag.json")


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr", "message"),
    [
        (1, "", "provider unavailable", "provider unavailable"),
        (0, "[", "", "unreadable"),
        (0, "[]", "", "did not verify"),
        (0, "ok: false\n", "", "did not verify"),
        (0, "ok: true\n", "", "no children list"),
        (0, "ok: true\nchildren:\n  - nope\n", "", "not a mapping"),
        (
            0,
            "ok: true\nchildren:\n  - number: 0\n    state: OPEN\n",
            "",
            "invalid issue number or state",
        ),
        (
            0,
            "ok: true\nchildren:\n  - number: 853\n    state: OPEN\n"
            "  - number: 853\n    state: CLOSED\n",
            "",
            "repeated child",
        ),
    ],
)
def test_provider_reader_rejects_invalid_provider_observations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    stdout: str,
    stderr: str,
    message: str,
) -> None:
    def run(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, returncode, stdout, stderr)

    monkeypatch.setattr(dag._guard, "run_process", run)
    with pytest.raises(dag.DagError, match=message):
        dag.read_provider_children(tmp_path, "corca-ai/charness", 844)


def test_provider_reader_requires_the_canonical_issue_tool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    is_file = Path.is_file
    monkeypatch.setattr(
        Path,
        "is_file",
        lambda path: False if path.name == "issue_tool.py" else is_file(path),
    )

    with pytest.raises(dag.DagError, match="issue provider command is missing"):
        dag.read_provider_children(tmp_path, "corca-ai/charness", 844)


def test_lane_state_reader_requires_a_complete_known_provider_mapping(tmp_path: Path) -> None:
    plan = _load_plan(tmp_path)
    with pytest.raises(dag.DagError, match="issue-number to state mappings"):
        dag.status_once(plan, provider_reader=lambda *_args: [])
    with pytest.raises(dag.DagError, match="state.*invalid"):
        dag.status_once(plan, provider_reader=lambda *_args: {853: "OPEN", 854: "BLOCKED"})


def test_task_record_reader_and_liveness_use_the_existing_task_run_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dag._runtime, "task_status", lambda _root: {"tasks": "invalid"})
    assert dag._task_records(tmp_path) == {}
    monkeypatch.setattr(
        dag._runtime,
        "task_status",
        lambda _root: {"tasks": [{"task_id": "base", "status": "running"}]},
    )
    records = dag._task_records(tmp_path)

    assert records["base"]["status"] == "running"
    assert dag._record_is_active(records["base"])
    assert not dag._record_is_active({"status": "completed"})


def test_main_reports_a_typed_failure_and_direct_execution_reaches_entrypoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(dag, "load_plan", lambda _path: (_ for _ in ()).throw(dag.DagError("bad plan")))

    assert dag.main(["status", "--plan-file", str(tmp_path / "dag.json")]) == 1
    failure = json.loads(capsys.readouterr().out)
    assert failure["result_kind"] == ResultKind.FAILED.value
    assert failure["exit_code"] == 1
    assert failure["error"] == "bad plan"

    monkeypatch.setattr(sys, "argv", ["task_run_dag.py", "--help"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(Path(dag.__file__)), run_name="__main__")
    assert exit_info.value.code == 0
