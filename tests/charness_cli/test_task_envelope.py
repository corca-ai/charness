from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from .support import run_cli_in_repo


def test_task_claim_submit_and_status_are_structured(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    env = os.environ.copy()
    env["CHARNESS_AGENT_ID"] = "agent-a"

    claim = run_cli_in_repo(
        Path(__file__).resolve().parents[2],
        "task",
        "--repo-root",
        str(repo_root),
        "claim",
        "slice-1",
        "--summary",
        "Implement the first slice",
        env=env,
    )
    assert claim.returncode == 0, claim.stderr
    claim_payload = yaml.safe_load(claim.stdout)
    assert claim_payload["event"] == "claimed"
    assert claim_payload["task_path"] == ".charness/tasks/slice-1.json"
    assert claim_payload["task"]["status"] == "claimed"
    assert claim_payload["task"]["agent_id"] == "agent-a"

    submit = run_cli_in_repo(
        Path(__file__).resolve().parents[2],
        "task",
        "--repo-root",
        str(repo_root),
        "submit",
        "slice-1",
        "--summary",
        "Finished with tests",
        "--artifact",
        "tests/charness_cli/test_task_envelope.py",
        env=env,
    )
    assert submit.returncode == 0, submit.stderr
    submit_payload = yaml.safe_load(submit.stdout)
    assert submit_payload["event"] == "submitted"
    assert submit_payload["task"]["status"] == "submitted"
    assert submit_payload["task"]["submission"]["artifacts"] == ["tests/charness_cli/test_task_envelope.py"]

    status = run_cli_in_repo(
        Path(__file__).resolve().parents[2],
        "task",
        "--repo-root",
        str(repo_root),
        "status",
        "slice-1",
        env=env,
    )
    assert status.returncode == 0, status.stderr
    status_payload = yaml.safe_load(status.stdout)
    assert status_payload["task"]["status"] == "submitted"
    assert json.loads((repo_root / ".charness" / "tasks" / "slice-1.json").read_text())["status"] == "submitted"


def test_task_claim_conflict_and_abort_reason_are_structured(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    env_a = {**os.environ, "CHARNESS_AGENT_ID": "agent-a"}
    env_b = {**os.environ, "CHARNESS_AGENT_ID": "agent-b"}
    root = Path(__file__).resolve().parents[2]

    first = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "claim", "slice-2", env=env_a)
    assert first.returncode == 0, first.stderr
    conflict = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "claim", "slice-2", env=env_b)
    assert conflict.returncode == 1
    conflict_payload = yaml.safe_load(conflict.stdout)
    assert conflict_payload["event"] == "rejected"
    assert conflict_payload["status"] == "already-owned"
    assert conflict_payload["task"]["agent_id"] == "agent-a"

    abort = run_cli_in_repo(
        root,
        "task",
        "--repo-root",
        str(repo_root),
        "abort",
        "slice-2",
        "--reason",
        "blocked by missing fixture",
        env=env_a,
    )
    assert abort.returncode == 0, abort.stderr
    abort_payload = yaml.safe_load(abort.stdout)
    assert abort_payload["event"] == "aborted"
    assert abort_payload["task"]["status"] == "aborted"
    assert abort_payload["task"]["abort"]["reason"] == "blocked by missing fixture"


def test_task_legacy_json_flag_is_ignored_and_hidden(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    root = Path(__file__).resolve().parents[2]

    default = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "status")
    legacy = run_cli_in_repo(root, "task", "--json", "--repo-root", str(repo_root), "status")
    help_result = run_cli_in_repo(root, "task", "--help")

    assert default.returncode == legacy.returncode == 0
    assert legacy.stdout == default.stdout
    assert yaml.safe_load(legacy.stdout)["event"] == "status-list"
    assert "--json" not in help_result.stdout
