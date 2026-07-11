from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from .support import ROOT, run_script

STANDING_PYTEST = "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"


def test_broad_pytest_detector_matches_repo_python_closeout_command() -> None:
    from scripts.slice_closeout_broad_gate import is_broad_pytest_command

    assert is_broad_pytest_command(STANDING_PYTEST)
    assert is_broad_pytest_command("pytest -q -m 'not release_only' tests/quality_gates tests/control_plane")
    assert not is_broad_pytest_command("python3 scripts/run_standing_pytest.py --print-targets")
    assert not is_broad_pytest_command("python3 scripts/run_standing_pytest.py --print-expanded-targets")
    assert not is_broad_pytest_command("python3 scripts/run_standing_pytest.py --print-temp-root")
    assert not is_broad_pytest_command("pytest -q tests/quality_gates/test_goal_artifact_lib.py")


def test_run_slice_closeout_requires_lock_before_broad_pytest() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["verification_lock_required"] is True
    assert payload["broad_pytest_policy_mode"] == "lock-required"
    assert "Choose --skip-broad-pytest" in payload["broad_pytest_recommendation"]
    assert "ambiguous" in payload["broad_pytest_cost_warning"]
    assert payload["executed_commands"] == []
    assert "broad pytest closeout requires" in payload["error"]


def test_run_slice_closeout_requires_exclusive_broad_pytest_phase_flags() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--skip-broad-pytest",
        "--verification-lock",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["phase_conflict"] is True
    assert "mutually exclusive" in payload["error"]
    assert payload["executed_commands"] == []


def test_run_slice_closeout_skip_broad_pytest_rehearsal_filters_pytest() -> None:
    from scripts.slice_closeout_broad_gate import is_broad_pytest_command

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--skip-broad-pytest",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["broad_pytest_policy_mode"] == "pre-lock-rehearsal"
    assert "focused current-diff proof" in payload["broad_pytest_recommendation"]
    assert "stale after reviewer-driven changes" in payload["broad_pytest_cost_warning"]
    assert payload["skipped_broad_pytest_commands"]
    planned = [item["command"] for item in payload["planned_commands"]]
    assert not any(is_broad_pytest_command(command) for command in planned)


def test_run_slice_closeout_skip_broad_pytest_text_names_skipped_command() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--skip-broad-pytest",
        "--plan-only",
    )

    assert result.returncode == 0, result.stderr
    assert "Broad pytest policy:" in result.stdout
    assert "mode: pre-lock-rehearsal" in result.stdout
    assert "focused current-diff proof" in result.stdout
    assert "Skipped broad pytest commands:" in result.stdout
    assert STANDING_PYTEST in result.stdout


def test_run_slice_closeout_lock_required_text_names_policy() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
    )

    assert result.returncode == 1
    assert "Broad pytest policy:" in result.stdout
    assert "mode: lock-required" in result.stdout
    assert "cost/evidence boundary ambiguous" in result.stdout
    assert "Verification lock required before broad pytest." in result.stdout


def test_run_slice_closeout_verification_lock_keeps_broad_pytest_in_plan() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness",
        "--skip-sync",
        "--verification-lock",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "planned"
    assert payload["broad_pytest_policy_mode"] == "verification-lock"
    assert "final verification lock" in payload["broad_pytest_recommendation"]
    assert "broad_pytest_cost_warning" not in payload
    assert "verification_lock_required" not in payload
    planned = [item["command"] for item in payload["planned_commands"]]
    assert STANDING_PYTEST in planned


def test_broad_pytest_cache_reuses_matching_fingerprint(tmp_path) -> None:
    from scripts.slice_closeout_broad_gate import (
        broad_pytest_cache_report,
        broad_pytest_fingerprint,
        record_broad_pytest_proof,
    )

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "f.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "f.txt").write_text("two\n", encoding="utf-8")
    command = STANDING_PYTEST
    fingerprint = broad_pytest_fingerprint(tmp_path, ["f.txt"])

    assert broad_pytest_cache_report(tmp_path, command=command, fingerprint=fingerprint)["status"] == "missing"
    record_broad_pytest_proof(
        tmp_path,
        command=command,
        fingerprint=fingerprint,
        elapsed_seconds=1.23,
        changed_paths=["f.txt"],
    )

    assert broad_pytest_cache_report(tmp_path, command=command, fingerprint=fingerprint)["status"] == "reusable"
    (tmp_path / "f.txt").write_text("three\n", encoding="utf-8")
    changed = broad_pytest_fingerprint(tmp_path, ["f.txt"])
    assert broad_pytest_cache_report(tmp_path, command=command, fingerprint=changed)["status"] == "invalidated"
    record_broad_pytest_proof(
        tmp_path,
        command=command,
        fingerprint=changed,
        elapsed_seconds=1.24,
        changed_paths=["f.txt"],
    )
    (tmp_path / "f.txt").write_text("two\n", encoding="utf-8")

    stale_latest_report = broad_pytest_cache_report(tmp_path, command=command, fingerprint=fingerprint)
    assert stale_latest_report["status"] == "reusable"
    assert stale_latest_report["latest"]["fingerprint"] == changed
    assert stale_latest_report["match"]["fingerprint"] == fingerprint


def test_execute_plan_explains_invalidated_broad_cache_as_locked_diff(tmp_path: Path) -> None:
    from scripts.slice_closeout_broad_gate import (
        broad_pytest_fingerprint,
        record_broad_pytest_proof,
    )
    from scripts.slice_closeout_command_executor import execute_command_plan

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "f.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "f.txt").write_text("two\n", encoding="utf-8")
    command = STANDING_PYTEST
    record_broad_pytest_proof(
        tmp_path,
        command=command,
        fingerprint=broad_pytest_fingerprint(tmp_path, ["f.txt"]),
        elapsed_seconds=1.0,
        changed_paths=["f.txt"],
    )
    (tmp_path / "f.txt").write_text("three\n", encoding="utf-8")

    payload: dict[str, object] = {"executed_commands": []}

    stopped = execute_command_plan(
        tmp_path,
        [("verify", command)],
        payload,
        run_command=lambda *_args: {"returncode": 99},
        collect_changed_paths=lambda _repo_root: ["f.txt"],
        refresh_broad_pytest_proof=False,
    )

    assert stopped is True
    assert payload["status"] == "blocked"
    assert "different locked diff fingerprint" in str(payload["error"])
    assert "mutation fingerprint" not in str(payload["error"])
    assert payload["executed_commands"] == []
    invalidated = payload["invalidated_broad_pytest_proofs"][0]
    assert invalidated["status"] == "invalidated"
    assert invalidated["latest"]["changed_paths"] == ["f.txt"]


def _init_closeout_git_repo(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
    (repo / "untouched.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt", "untouched.txt"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=T", "commit", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def test_execute_plan_verification_lock_stops_after_sync_tracked_drift(tmp_path: Path) -> None:
    from scripts.slice_closeout_command_executor import execute_command_plan

    _init_closeout_git_repo(tmp_path)
    # The slice is already dirty before sync.  The sync command must still be
    # caught when it changes that same tracked path again.
    (tmp_path / "tracked.txt").write_text("slice edit\n", encoding="utf-8")
    (tmp_path / "untouched.txt").write_text("other slice edit\n", encoding="utf-8")
    executed: list[str] = []
    payload: dict[str, object] = {"executed_commands": []}

    def run_command(repo: Path, command: str, phase: str) -> dict[str, object]:
        executed.append(phase)
        if phase == "sync":
            (repo / "tracked.txt").write_text("generated sync output\n", encoding="utf-8")
            (repo / "untracked-cache.tmp").write_text("ignore me\n", encoding="utf-8")
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    stopped = execute_command_plan(
        tmp_path,
        [("sync", "sync"), ("verify", STANDING_PYTEST)],
        payload,
        run_command=run_command,
        collect_changed_paths=lambda repo: ["tracked.txt", "untracked-cache.tmp"],
        refresh_broad_pytest_proof=False,
        stop_on_sync_drift=True,
        broad_pytest_producer=lambda *_args: (_ for _ in ()).throw(
            AssertionError("broad producer must not run after sync drift")
        ),
    )

    assert stopped is True
    assert executed == ["sync"]
    assert payload["status"] == "blocked"
    assert payload["sync_drift_paths"] == ["tracked.txt"]
    assert payload["sync_drift"]["tracked_only"] is True
    assert "commit the generated sync output" in str(payload["error"])
    assert "rerun with --verification-lock" in str(payload["error"])
    assert len(payload["executed_commands"]) == 1


def test_execute_plan_verification_lock_continues_when_sync_is_clean(tmp_path: Path) -> None:
    from scripts.slice_closeout_command_executor import execute_command_plan

    _init_closeout_git_repo(tmp_path)
    payload: dict[str, object] = {"executed_commands": []}
    executed: list[str] = []

    def run_command(repo: Path, command: str, phase: str) -> dict[str, object]:
        executed.append(phase)
        return {"phase": phase, "command": command, "returncode": 0, "stdout": "", "stderr": ""}

    stopped = execute_command_plan(
        tmp_path,
        [("sync", "sync"), ("verify", "verify")],
        payload,
        run_command=run_command,
        collect_changed_paths=lambda _repo: [],
        refresh_broad_pytest_proof=False,
        stop_on_sync_drift=True,
    )

    assert stopped is False
    assert executed == ["sync", "verify"]


def test_execute_plan_verification_lock_preserves_sync_failure(tmp_path: Path) -> None:
    from scripts.slice_closeout_command_executor import execute_command_plan

    _init_closeout_git_repo(tmp_path)
    payload: dict[str, object] = {"executed_commands": []}
    executed: list[str] = []

    def run_command(repo: Path, command: str, phase: str) -> dict[str, object]:
        executed.append(phase)
        return {"phase": phase, "command": command, "returncode": 7, "stdout": "", "stderr": "sync failed"}

    stopped = execute_command_plan(
        tmp_path,
        [("sync", "sync"), ("verify", "verify")],
        payload,
        run_command=run_command,
        collect_changed_paths=lambda _repo: [],
        refresh_broad_pytest_proof=False,
        stop_on_sync_drift=True,
    )

    assert stopped is True
    assert payload["status"] == "failed"
    assert executed == ["sync"]


def test_tracked_state_reports_git_inspection_failure(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import slice_closeout_command_executor as executor

    class FailedGit:
        returncode = 1
        stdout = b""
        stderr = b"git inspection failed"

    monkeypatch.setattr(executor.subprocess, "run", lambda *_args, **_kwargs: FailedGit())
    with pytest.raises(RuntimeError, match="git inspection failed"):
        executor._tracked_state(tmp_path)
