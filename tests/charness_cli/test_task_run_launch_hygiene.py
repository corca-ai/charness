from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any

import pytest

from scripts.task_run import (
    task_run,
    task_run_dag,
    task_run_lane_runner,
    task_run_plan,
    task_run_prelaunch,
)
from tests.charness_cli.test_task_run_dag import _provider, _raw_plan
from tests.charness_cli.test_task_run_fixtures import _codex, _commit, _git, _repo


def _dry_run(
    repo: Path,
    tmp_path: Path,
    *,
    lane: str,
    prompt: str,
    base: str | None = None,
    scopes: list[str] | None = None,
):
    return task_run.run_task(
        repo,
        lane=lane,
        base=base,
        scopes=scopes or ["module.py"],
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


def test_scope_preflight_names_an_evidence_path_outside_scope_before_exec(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "temp-producers.yaml").write_text("version: 1\n", encoding="utf-8")
    _commit(repo, "add named evidence path", ".agents/temp-producers.yaml")

    payload = _dry_run(
        repo,
        tmp_path,
        lane="scope-omission",
        scopes=["module.py"],
        prompt=(
            "Lane size: 45 minutes; 3 commit units\n"
            "The failure evidence names `.agents/temp-producers.yaml` as a required owner."
        ),
    )

    findings = payload["prelaunch_plan"]["scope_preflight"]["would_touch_outside_declared"]
    assert findings == [
        {
            "code": "would-touch-outside-declared",
            "path": ".agents/temp-producers.yaml",
            "basis": "the brief/task evidence names this repository path",
        }
    ]
    assert payload["dry_run"] is True
    assert "execution" not in payload


def test_scope_omission_blocks_before_executor_launch(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "temp-producers.yaml").write_text("version: 1\n", encoding="utf-8")
    _commit(repo, "add named evidence path", ".agents/temp-producers.yaml")
    marker = tmp_path / "executor-started"
    executable = _codex(tmp_path, f"touch {shlex.quote(str(marker))}")

    payload = task_run.run_task(
        repo,
        lane="scope-omission-blocked",
        scopes=["module.py"],
        prompt=(
            "Lane size: 30 minutes; 1 commit unit\n"
            "The failure evidence names `.agents/temp-producers.yaml` as a required owner."
        ),
        codex=str(executable),
        effort="medium",
        prepare=False,
        require_change=False,
    )

    assert payload["status"] == "premise-blocked"
    assert payload["prelaunch"]["status"] == "blocked"
    assert ".agents/temp-producers.yaml" in payload["next_step"]
    assert not marker.exists()


def test_task_run_scope_precomputes_its_gate_and_verifier_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / "scripts" / "task_run").mkdir(parents=True)
    (repo / "scripts" / "mutation").mkdir(parents=True)
    (repo / "tests").mkdir()
    source = "scripts/task_run/task_run_plan.py"
    suite = "tests/test_task_run_plan.py"
    (repo / source).write_text("VALUE = 1\n", encoding="utf-8")
    (repo / suite).write_text("def test_scope():\n    assert True\n", encoding="utf-8")
    (repo / "scripts/mutation/release_changed_line_coverage.py").write_text(
        "# release gate\n", encoding="utf-8"
    )
    command = f"python3 -m pytest -q {suite}"
    manifest = {
        "version": 1,
        "surfaces": [
            {
                "surface_id": "task-run-python",
                "description": "Task-run Python source and its focused test.",
                "source_paths": ["scripts/**"],
                "derived_paths": [],
                "sync_commands": [],
                "verify_commands": [command],
                "notes": [],
            }
        ],
    }
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    _commit(
        repo,
        "seed verifier surfaces",
        source,
        suite,
        "scripts/mutation/release_changed_line_coverage.py",
        ".agents/surfaces.json",
    )
    monkeypatch.setattr(task_run_plan, "_list_eligible", lambda _root: [source])

    payload = _dry_run(
        repo,
        tmp_path,
        lane="task-run-verifiers",
        scopes=[source],
        prompt="Lane size: 45 minutes; 3 commit units\nUpdate task-run planning.",
    )

    verifiers = payload["prelaunch_plan"]["scope_verifiers"]
    assert verifiers["completion_gates"] == ["release-changed-line-coverage"]
    assert verifiers["matched_surface_ids"] == ["task-run-python"]
    assert verifiers["verify_commands"] == [command]
    assert verifiers["mapped_suites"] == [suite]
    brief = task_run_prelaunch.acceptance_skeleton_prompt(
        "Lane brief", {"prelaunch_plan": payload["prelaunch_plan"]}
    )
    assert "release-changed-line-coverage" in brief
    assert command in brief


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
