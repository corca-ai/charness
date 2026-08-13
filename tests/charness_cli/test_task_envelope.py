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
    assert "charness task submit slice-1" in claim_payload["next_step"]
    claimed_state = json.loads((repo_root / ".charness" / "tasks" / "slice-1.json").read_text())
    assert "charness task submit slice-1" in claimed_state["next_step"]

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
    submitted_state = json.loads((repo_root / ".charness" / "tasks" / "slice-1.json").read_text())
    assert submitted_state["status"] == "submitted"
    assert ".charness/tasks/slice-1.json" in submitted_state["next_step"]
    assert status_payload["task"]["next_step"] == submitted_state["next_step"]


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
    assert "charness task status slice-2" in conflict_payload["next_step"]

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


def test_task_rejections_carry_recovering_next_step(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    env = {**os.environ, "CHARNESS_AGENT_ID": "agent-a"}
    root = Path(__file__).resolve().parents[2]

    missing = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "submit", "slice-3", "--summary", "x", env=env)
    assert missing.returncode == 1
    missing_payload = yaml.safe_load(missing.stdout)
    assert missing_payload["status"] == "missing"
    assert "charness task claim slice-3" in missing_payload["next_step"]

    missing_abort = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "abort", "slice-3", "--reason", "x", env=env)
    assert missing_abort.returncode == 1
    assert "charness task claim slice-3" in yaml.safe_load(missing_abort.stdout)["next_step"]

    missing_status = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "status", "slice-3", env=env)
    assert missing_status.returncode == 1
    assert "charness task claim slice-3" in yaml.safe_load(missing_status.stdout)["next_step"]

    claim = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "claim", "slice-3", env=env)
    assert claim.returncode == 0, claim.stderr

    reclaim = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "claim", "slice-3", env=env)
    assert reclaim.returncode == 0, reclaim.stderr
    reclaim_payload = yaml.safe_load(reclaim.stdout)
    assert reclaim_payload["event"] == "claim-existing"
    persisted = json.loads((repo_root / ".charness" / "tasks" / "slice-3.json").read_text())
    assert reclaim_payload["next_step"] == persisted["next_step"]
    empty_submit = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "submit", "slice-3", env=env)
    assert empty_submit.returncode == 1
    empty_payload = yaml.safe_load(empty_submit.stdout)
    assert empty_payload["status"] == "missing-result"
    assert "charness task submit slice-3" in empty_payload["next_step"]

    abort = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "abort", "slice-3", "--reason", "blocked", env=env)
    assert abort.returncode == 0, abort.stderr
    abort_payload = yaml.safe_load(abort.stdout)
    assert ".charness/tasks/slice-3.json" in abort_payload["next_step"]
    aborted_state = json.loads((repo_root / ".charness" / "tasks" / "slice-3.json").read_text())
    assert abort_payload["next_step"] == aborted_state["next_step"]

    closed = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "submit", "slice-3", "--summary", "late", env=env)
    assert closed.returncode == 1
    closed_payload = yaml.safe_load(closed.stdout)
    assert closed_payload["status"] == "closed"
    assert ".charness/tasks/slice-3.json" in closed_payload["next_step"]

    closed_abort = run_cli_in_repo(root, "task", "--repo-root", str(repo_root), "abort", "slice-3", "--reason", "again", env=env)
    assert closed_abort.returncode == 1
    closed_abort_payload = yaml.safe_load(closed_abort.stdout)
    assert closed_abort_payload["status"] == "closed"
    assert ".charness/tasks/slice-3.json" in closed_abort_payload["next_step"]
