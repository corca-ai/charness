"""Completion behavior for deletions and persistence boundary cases."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts.task_run import task_run_completion_proof, task_run_git
from scripts.task_run.task_run_contract import TaskRunError
from tests.charness_cli.task_run_completion_support import _complete


def test_snapshot_acknowledgement_does_not_hide_candidate_disappearance(tmp_path: Path) -> None:
    def git(cwd: Path, *args: str) -> Any:
        result = task_run_git._git(cwd, *args)
        if "commit" in args and result.returncode == 0:
            (cwd / "module.py").unlink()
        return result

    def gate(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise AssertionError("incomplete preserved work must not invoke proof")

    payload = _complete(tmp_path, candidate_kind="dirty", changed_line_gate=gate, git=git)

    assert payload["candidate"]["persist"]["status"] == "committed"
    assert payload["candidate"]["dirty_paths"] == ["module.py"]
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["status"] == "skipped"
    assert "incomplete after persistence" in payload["changed_line_gate"]["reason"]
    assert payload["keep_worktree"] is True
    assert not (tmp_path / "worktree" / "module.py").exists()


def test_carrier_refresh_failure_after_persistence_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def boom(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise TaskRunError("carrier refresh failed")

    monkeypatch.setattr(task_run_completion_proof, "_candidate_carrier", boom)
    calls: list[str] = []

    def gate(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        calls.append("gate")
        return {"status": "clean", "blocking": False}

    payload = _complete(tmp_path, candidate_kind="dirty", changed_line_gate=gate)

    assert calls == []
    assert payload["candidate"]["persist"]["status"] == "committed"
    assert payload["candidate"]["carrier_observation"]["status"] == "unreadable"
    assert payload["candidate"]["carrier_kind"] == "unknown"
    assert payload["candidate"]["head_is_complete"] is False
    assert payload["keep_worktree"] is True
    assert payload["approval_eligibility"] == "ineligible"
    assert "carrier could not be observed after persistence" in payload["changed_line_gate"]["reason"]
    capsys.readouterr()

def test_completion_accepts_an_intentional_exact_scope_file_deletion(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path="module.py",
        scope_specs_override=[{"path": "module.py", "kind": "exact"}],
        changed_line_gate=lambda *_args, **_kwargs: {
            "status": "clean",
            "blocking": False,
            "summary": "gate clean",
        },
    )

    assert payload["status"] == "completed"
    assert payload["approval_eligibility"] == "eligible"
    capsys.readouterr()


def test_completion_still_blocks_a_missing_promised_exact_scope_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _complete(
        tmp_path,
        candidate_kind="clean",
        scope_specs_override=[{"path": "new-output.py", "kind": "exact"}],
        prelaunch_plan_override={
            "scope_preflight": {"required_scope_paths": ["new-output.py"]},
            "scope_verifiers": {
                "status": "configured",
                "bundle_status": "repo-owned-bundle",
                "scope_paths": ["module.py"],
                "unmatched_paths": [],
                "mapped_suites": ["tests/test_completion_scope.py"],
            },
        },
        changed_line_gate=lambda *_args, **_kwargs: {
            "status": "clean",
            "blocking": False,
            "summary": "gate clean",
        },
    )

    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["blocker"].startswith("in-scope file deficit:")
    assert "new-output.py" in payload["blocker"]
    capsys.readouterr()


def test_completion_accepts_committed_deletion_of_entire_scoped_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    suite = "tests/test_completion_scope.py"
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "completion-fixture",
                    "description": "Fixture verifier mapping for task completion tests.",
                    "source_paths": ["module.py", "pkg/**"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": [f"python3 -m pytest -q {suite}"],
                    "notes": [],
                }
            ],
        }
    )
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path="pkg/only.py",
        scope_specs_override=[{"path": "pkg", "kind": "directory"}],
        extra_files={"pkg/only.py": "VALUE = 1\n", ".agents/surfaces.json": surfaces},
        changed_line_gate=lambda *_args, **_kwargs: {
            "status": "clean",
            "blocking": False,
            "summary": "gate clean",
        },
    )

    assert payload["candidate"]["changed_paths"] == ["pkg/only.py"]
    assert not (tmp_path / "worktree" / "pkg").exists()
    assert payload["status"] == "completed"
    assert payload["approval_eligibility"] == "eligible"
    capsys.readouterr()


@pytest.mark.parametrize(
    ("include_deleted_path_in_scope", "expected_eligibility"),
    [(False, "ineligible"), (True, "eligible")],
)
def test_persisted_mixed_merge_deletion_is_reclassified_before_proof(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    include_deleted_path_in_scope: bool,
    expected_eligibility: str,
) -> None:
    suite = "tests/test_completion_scope.py"
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "completion-fixture",
                    "description": "Fixture verifier mapping for task completion tests.",
                    "source_paths": ["module.py", "pkg/**"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": [f"python3 -m pytest -q {suite}"],
                    "notes": [],
                }
            ],
        }
    )
    scope_specs = [{"path": "module.py", "kind": "exact"}]
    if include_deleted_path_in_scope:
        scope_specs.append({"path": "pkg", "kind": "directory"})
    gate_calls: list[str] = []

    def gate(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        gate_calls.append("gate")
        return {"status": "clean", "blocking": False, "summary": "gate clean"}

    payload = _complete(
        tmp_path,
        candidate_kind="mixed-merge-delete",
        scope_specs_override=scope_specs,
        extra_files={".agents/surfaces.json": surfaces},
        changed_line_gate=gate,
    )

    assert payload["candidate"]["changed_paths"] == ["module.py", "pkg/item.py"]
    if include_deleted_path_in_scope:
        assert payload["candidate"]["disallowed_paths"] == []
        assert payload["approval_eligibility"] == expected_eligibility
        assert payload["status"] == "completed"
        assert gate_calls == ["gate"]
    else:
        assert payload["candidate"]["disallowed_paths"] == ["pkg/item.py"]
        assert payload["approval_eligibility"] == expected_eligibility
        assert payload["status"] == "validated-partial-result"
        assert any("outside the declared scope: pkg/item.py" in item for item in payload["blockers"])
        assert gate_calls == []
    capsys.readouterr()


def test_completion_blocks_a_mapped_suite_dropped_from_the_candidate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    suite = "tests/test_mapped.py"
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "repo-python",
                    "description": "Repo Python tests.",
                    "source_paths": ["module.py", "tests/**"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": [f"python3 -m pytest -q {suite}"],
                    "notes": [],
                }
            ],
        }
    )
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path=suite,
        extra_files={suite: "def test_mapped():\n    assert True\n", ".agents/surfaces.json": surfaces},
        prelaunch_plan_override={
            "scope_preflight": {"required_scope_paths": []},
            "scope_verifiers": {
                "status": "configured",
                "bundle_status": "repo-owned-bundle",
                "scope_paths": ["module.py"],
                "unmatched_paths": [],
                "mapped_suites": [suite],
            },
        },
        changed_line_gate=lambda *_args, **_kwargs: {
            "status": "clean",
            "blocking": False,
            "summary": "gate clean",
        },
    )

    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["blocker"].startswith("mapped suite deficit:")
    assert suite in payload["blocker"]
    capsys.readouterr()

def test_gate_deletion_is_ineligible_but_clean_candidate_can_be_released(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def gate(worktree: Path, *, base_sha: str, log_dir: Path) -> dict[str, Any]:
        (worktree / "module.py").unlink()
        task_run_git._commit_lane_snapshot(worktree, message="gate deletion")
        return {"status": "clean", "blocking": False, "summary": "gate clean"}

    def allow_release(cwd: Path, *args: str) -> Any:
        if args[:2] == ("worktree", "remove"):
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        return task_run_git._git(cwd, *args)

    payload = _complete(tmp_path, changed_line_gate=gate, git=allow_release)

    assert payload["status"] == "validated-partial-result"
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["candidate"]["carrier_kind"] == "commit-only"
    assert payload["candidate"]["head_is_complete"] is True
    assert not (tmp_path / "worktree" / "module.py").exists()
    assert payload["retention"]["worktree"] == "removed"
    assert payload["keep_worktree"] is False
    capsys.readouterr()
