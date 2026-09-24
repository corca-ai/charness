from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.task_run import task_run, task_run_dag, task_run_lane_runner
from tests.charness_cli.test_task_run_dag import _provider, _raw_plan
from tests.charness_cli.test_task_run_fixtures import _codex, _commit, _git, _repo


def _dry_run(repo: Path, tmp_path: Path, *, lane: str, prompt: str, base: str | None = None):
    return task_run.run_task(
        repo,
        lane=lane,
        base=base,
        scopes=["module.py"],
        prompt=prompt,
        codex=str(_codex(tmp_path, "exit 0")),
        effort="medium",
        dry_run=True,
    )


def test_stale_base_is_reported_in_standalone_preflight_without_dag(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    stale_base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    (repo / "later.py").write_text("LATER = 1\n", encoding="utf-8")
    dependency_tip = _commit(repo, "advance dependency tip", "later.py")

    payload = _dry_run(
        repo,
        tmp_path,
        lane="stale-base",
        base=stale_base,
        prompt="Lane size: 45 minutes; 3 commit units\nInspect the selected base.",
    )

    hygiene = payload["prelaunch_plan"]["launch_hygiene"]
    assert payload["dry_run"] is True
    assert hygiene["base_freshness"] == {
        "status": "stale",
        "base_sha": stale_base,
        "dependency_tip_sha": dependency_tip,
        "warning": hygiene["base_freshness"]["warning"],
    }
    assert "no automatic rebase" in hygiene["base_freshness"]["warning"]
    assert hygiene["warnings"] == [hygiene["base_freshness"]["warning"]]


@pytest.mark.parametrize(
    "estimate",
    ["61 minutes; 3 commit units", "45 minutes; 5 commit units"],
)
def test_oversize_lane_preflight_suggests_a_split(tmp_path: Path, estimate: str) -> None:
    repo = _repo(tmp_path)
    payload = _dry_run(
        repo,
        tmp_path,
        lane="oversize",
        prompt=f"Lane size: {estimate}\nImplement the requested slice.",
    )

    lane_size = payload["prelaunch_plan"]["launch_hygiene"]["lane_size"]
    assert lane_size["status"] == "oversize"
    assert lane_size["limits"] == {"minutes": 60, "commit_units": 4}
    assert "split it into smaller lanes" in lane_size["warning"]
    assert "hard-dependency lane" in lane_size["warning"]


def test_lane_brief_requires_size_and_shared_primitive_candidate_report() -> None:
    prompt = task_run_lane_runner.build_lane_prompt(
        "Add the requested helper.", require_change=True, scopes=["scripts/example.py"]
    )

    assert "Lane size: <minutes> minutes; <commit_units> commit units" in prompt
    assert "search the repository with `rg`" in prompt
    assert "reuse it when suitable" in prompt
    assert "Shared-primitive candidates:" in prompt
    assert "candidate's name, path, and purpose, or `none`" in prompt
    assert "hard `depends_on`" in prompt


def _stacked_plan(tmp_path: Path) -> dict[str, Any]:
    raw = _raw_plan(tmp_path)
    raw["lanes"][1]["stacked_on"] = "base"
    path = tmp_path / "dag.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return task_run_dag.load_plan(path)


def test_stacked_on_must_name_a_hard_dependency(tmp_path: Path) -> None:
    raw = _raw_plan(tmp_path)
    raw["lanes"][1]["stacked_on"] = "base"
    raw["lanes"][1]["dependency_kinds"] = {"base": "soft"}
    path = tmp_path / "dag.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(task_run_dag.DagError, match="must be a hard dependency"):
        task_run_dag.load_plan(path)


def test_stacked_lane_launches_from_predecessor_candidate_sha(tmp_path: Path) -> None:
    plan = _stacked_plan(tmp_path)
    states = {853: "OPEN", 854: "OPEN"}
    predecessor_sha = "a" * 40
    launches: list[dict[str, Any]] = []

    def launch(_repo_root: Path, lane: dict[str, Any]) -> dict[str, Any]:
        launches.append(lane)
        if lane["key"] == "base":
            states[853] = "CLOSED"
            return {"task_id": "base", "status": "completed", "target_sha": predecessor_sha}
        return {"task_id": "dependent", "status": "completed"}

    payload = task_run_dag.pull_once(
        plan,
        provider_reader=_provider(states),
        task_reader=lambda _repo_root: {},
        launcher=launch,
    )

    assert [lane["key"] for lane in launches] == ["base", "dependent"]
    assert launches[1]["base"] == predecessor_sha
    assert payload["launched"][0]["candidate_sha"] == predecessor_sha


def test_lane_launcher_forwards_explicit_base_to_task_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = _stacked_plan(tmp_path)
    lane = dict(plan["lanes"][1], base="b" * 40, stacked_on=None)
    captured: dict[str, Any] = {}

    monkeypatch.setattr(task_run, "run_task", lambda _root, **kwargs: captured.update(kwargs) or {})
    task_run_dag._launch_lane(plan["repo_root"], lane)

    assert captured["base"] == "b" * 40
