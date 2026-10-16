"""Task completion deletion verdicts using the existing committed Git fixture."""

from __future__ import annotations

import json
from pathlib import Path

from tests.charness_cli.test_task_run_completion import _complete


def test_completion_allows_a_missing_exact_scope_file_without_claiming_approval(
    tmp_path: Path,
) -> None:
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path="module.py",
        scope_specs_override=[{"path": "module.py", "kind": "exact"}],
    )

    assert not any(
        item.startswith("in-scope file deficit:") for item in payload["blockers"]
    )
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["status"] == "not-run"


def test_completion_allows_a_missing_glob_scope_file_without_claiming_approval(
    tmp_path: Path,
) -> None:
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path="module.py",
        scope_specs_override=[
            {"path": "**", "kind": "glob", "matches": ["module.py"]}
        ],
    )

    assert payload["candidate"]["changed_paths"] == ["module.py"]
    assert not any(
        item.startswith("in-scope file deficit:") for item in payload["blockers"]
    )
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["status"] == "not-run"


def test_completion_allows_git_delete_add_rename_within_directory_scope(
    tmp_path: Path,
) -> None:
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "rename-fixture",
                    "description": "Fixture verifier mapping for a Git D+A rename.",
                    "source_paths": ["pkg/module.py", "pkg/module2.py"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": ["python3 -m pytest -q tests/test_completion_scope.py"],
                    "notes": [],
                }
            ],
        }
    )
    payload = _complete(
        tmp_path,
        candidate_kind="rename",
        rename_from="pkg/module.py",
        rename_to="pkg/module2.py",
        extra_files={
            "pkg/module.py": "VALUE = 1\n",
            ".agents/surfaces.json": surfaces,
        },
        scope_specs_override=[{"path": "pkg", "kind": "directory"}],
    )

    assert set(payload["candidate"]["changed_paths"]) == {
        "pkg/module.py",
        "pkg/module2.py",
    }
    assert not any(
        item.startswith("in-scope file deficit:") for item in payload["blockers"]
    )
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["status"] == "not-run"


def test_completion_allows_deleting_the_last_child_of_a_scoped_directory(
    tmp_path: Path,
) -> None:
    surfaces = json.dumps(
        {
            "version": 1,
            "surfaces": [
                {
                    "surface_id": "directory-delete-fixture",
                    "description": "Fixture verifier mapping for deleting a directory child.",
                    "source_paths": ["adir/child.py"],
                    "derived_paths": [],
                    "sync_commands": [],
                    "verify_commands": ["python3 -m pytest -q tests/test_completion_scope.py"],
                    "notes": [],
                }
            ],
        }
    )
    payload = _complete(
        tmp_path,
        candidate_kind="delete",
        delete_path="adir/child.py",
        extra_files={
            "adir/child.py": "VALUE = 1\n",
            ".agents/surfaces.json": surfaces,
        },
        scope_specs_override=[{"path": "adir", "kind": "directory"}],
    )

    assert payload["candidate"]["changed_paths"] == ["adir/child.py"]
    assert not (tmp_path / "worktree" / "adir").exists()
    assert not any(
        item.startswith("in-scope file deficit:") for item in payload["blockers"]
    )
    assert payload["approval_eligibility"] == "ineligible"
    assert payload["changed_line_gate"]["status"] == "not-run"
