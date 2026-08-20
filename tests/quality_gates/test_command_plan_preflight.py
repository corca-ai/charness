from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .support import ROOT, run_script

SCRIPT = ROOT / "scripts" / "command_plan_preflight.py"


def _write_plan(repo: Path, payload: dict) -> Path:
    plan = repo / "plan.json"
    plan.write_text(json.dumps(payload), encoding="utf-8")
    return plan


def _demo(repo: Path) -> None:
    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "demo.py").write_text(
        """import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--repo-root')
parser.add_argument('--detail', action='store_true')
parser.add_argument('-v', action='store_true')
parser.parse_args()
""",
        encoding="utf-8",
    )


def _base_plan() -> dict:
    return {
        "schema_version": 1,
        "targets": [
            {"id": "demo", "query": "demo.py", "expected_path": "scripts/demo.py"},
        ],
        "refs": [],
        "commands": [
            {
                "id": "demo-command",
                "argv": ["python3", "{target:demo}", "--repo-root", ".", "--detail", "-v"],
            }
        ],
    }


def _run(repo: Path, plan: Path):
    return run_script(str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan))


def test_command_plan_preflight_resolves_target_and_owner_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    result = _run(repo, _write_plan(repo, _base_plan()))
    assert result.returncode == 0, result.stderr
    assert "status: pass" in result.stdout
    assert "scripts/demo.py" in result.stdout
    assert "--detail" in result.stdout


def test_wrong_path_stops_help_fanout_and_reports_candidates(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["targets"][0] = {"id": "demo", "query": "scripts/missing_demo.py"}
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "target-not-found" in result.stdout
    assert "fanout-stopped" in result.stdout
    assert "commands: []" in result.stdout


def test_ambiguous_basename_requires_explicit_expected_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "one").mkdir(parents=True)
    (repo / "two").mkdir()
    (repo / "one" / "demo.py").write_text("", encoding="utf-8")
    (repo / "two" / "demo.py").write_text("", encoding="utf-8")
    plan = _base_plan()
    plan["targets"][0] = {"id": "demo", "query": "demo.py"}
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "target-ambiguous" in result.stdout


def test_owner_help_rejects_planned_flag_that_was_removed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "--gone"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "flag-unresolved" in result.stdout
    assert "--gone" in result.stdout


def test_owner_help_rejects_unknown_short_flag(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "-x"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "flag-unresolved" in result.stdout
    assert "-x" in result.stdout


def test_owner_or_flag_failure_stops_later_help_probes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    plan = _base_plan()
    plan["commands"].extend(
        [{"id": "later-command", "argv": ["python3", "{target:demo}", "--detail"]}]
    )
    plan["commands"][0]["argv"] = ["python3", "{target:demo}", "--gone"]
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "fanout-stopped" in result.stdout
    assert "id: later-command" not in result.stdout


def test_ref_resolution_is_verified_before_help_probe(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _demo(repo)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Command Plan Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "seed command plan"], cwd=repo, check=True)
    plan = _base_plan()
    plan["refs"] = [{"id": "missing", "ref": "does-not-exist"}]
    plan["commands"].append(
        {"id": "later-command", "argv": ["python3", "{target:demo}", "--detail"]}
    )
    result = _run(repo, _write_plan(repo, plan))
    assert result.returncode == 2
    assert "ref-unresolved" in result.stdout
    assert "commands: []" in result.stdout
    assert "demo-command" not in result.stdout
    assert "later-command" not in result.stdout
