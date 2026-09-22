"""Persisted-data-loss lens for lane candidates (#830).

A lane that drops a persistence structure while every gate stays green
must not read as a success: the lens records a typed blocker, the
receipt carries `persistence`, and a finished lane with a blocking
finding reports `completed-needs-review`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.task_run import task_run_git
from scripts.task_run import task_run_persistence as persistence
from scripts.task_run import task_run_state as state
from tests.charness_cli.test_task_run_fixtures import _codex, _run
from tests.quality_gates.repo_shapes import install_committed_repo


def _lane_with_removed_line(tmp_path: Path, filename: str, removed_line: str) -> tuple[Path, str]:
    repo = install_committed_repo(
        tmp_path / "lane", {filename: f"keep\n{removed_line}\n", "other.py": "x = 1\n"}
    )
    base = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    lines = (repo / filename).read_text(encoding="utf-8").splitlines(keepends=True)
    (repo / filename).write_text("".join(line for line in lines if line.strip() != removed_line.strip()), encoding="utf-8")
    task_run_git._git(repo, "add", "--", filename)
    task_run_git._git(repo, "commit", "-m", "lane work", "--", filename)
    return repo, base


def _scan(repo: Path, base: str, paths: list[str]) -> dict[str, Any]:
    return persistence.scan_persistence_risks(repo, base, paths, git=task_run_git._git)


def test_dropped_table_blocks_the_lane(tmp_path: Path) -> None:
    repo, base = _lane_with_removed_line(tmp_path, "migration.sql", "DROP TABLE principals;")
    result = _scan(repo, base, ["migration.sql"])
    assert result["blocking"] is True
    assert result["findings"][0]["shape"] == "dropped-persistence-structure"
    assert persistence.persistence_blockers(result) != []
    assert persistence.persistence_blockers({"findings": [], "blocking": False}) == []
    assert persistence.persistence_blockers(None) == []


def test_unscoped_delete_blocks_the_lane(tmp_path: Path) -> None:
    repo, base = _lane_with_removed_line(tmp_path, "cleanup.sql", "DELETE FROM principals;")
    result = _scan(repo, base, ["cleanup.sql"])
    assert result["blocking"] is True
    assert result["findings"][0]["shape"] == "unscoped-delete"


def test_empty_substitution_is_advisory_only(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"store.py": "def load():\n    return read()\n"})
    base = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    (repo / "store.py").write_text(
        "def load():\n    # deferred until the replacement lands\n    return []\n",
        encoding="utf-8",
    )
    task_run_git._git(repo, "add", "--", "store.py")
    task_run_git._git(repo, "commit", "-m", "lane work", "--", "store.py")
    result = _scan(repo, base, ["store.py"])
    assert result["blocking"] is False
    assert [finding["shape"] for finding in result["findings"]] == [
        "deferred-replacement-note",
        "empty-substitution",
    ]


def test_unreadable_diff_blocks_fail_closed(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"module.py": "x = 1\n"})

    def _boom(_cwd: Path, *args: object) -> object:
        raise RuntimeError("git down")

    result = persistence.scan_persistence_risks(repo, "abc", ["module.py"], git=_boom)
    assert result["blocking"] is True
    assert result["error"] == "candidate diff unreadable"
    assert result["findings"][0]["shape"] == "candidate-diff-unreadable"


def test_added_destruction_and_truncate_block(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"migration.sql": "SELECT 1;\n"})
    base = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    (repo / "migration.sql").write_text(
        "SELECT 1;\nDROP TABLE principals;\nTRUNCATE TABLE sessions;\nDELETE FROM audit;\n",
        encoding="utf-8",
    )
    task_run_git._git(repo, "add", "--", "migration.sql")
    task_run_git._git(repo, "commit", "-m", "lane work", "--", "migration.sql")
    result = _scan(repo, base, ["migration.sql"])
    assert result["blocking"] is True
    assert sorted(finding["shape"] for finding in result["findings"]) == [
        "dropped-persistence-structure",
        "dropped-persistence-structure",
        "unscoped-delete",
    ]


def test_clean_change_and_unreadable_diff_stay_quiet(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "lane", {"module.py": "x = 1\n"})
    base = task_run_git._git_output(repo, "rev-parse", "HEAD").strip()
    (repo / "module.py").write_text("x = 2\n", encoding="utf-8")
    task_run_git._git(repo, "add", "--", "module.py")
    task_run_git._git(repo, "commit", "-m", "lane work", "--", "module.py")
    assert _scan(repo, base, ["module.py"]) == {"findings": [], "blocking": False}
    assert _scan(repo, base, []) == {"findings": [], "blocking": False}
    broken = _scan(repo, "0" * 40, ["module.py"])
    assert broken["blocking"] is True
    assert broken["error"] == "candidate diff unreadable"


def test_finished_lane_with_dropped_table_needs_review(tmp_path: Path) -> None:
    repo = install_committed_repo(
        tmp_path / "parent",
        {
            "module.py": "VALUE = 1\n",
            "schema.sql": "CREATE TABLE kept (id);\nDROP TABLE legacy;\n",
        },
    )
    executable = _codex(tmp_path, "sed -i '/DROP TABLE legacy;/d' schema.sql")
    payload = _run(repo, tmp_path, executable, scopes=["module.py", "schema.sql"])

    assert payload["status"] == "completed-needs-review"
    assert payload["persistence"]["blocking"] is True
    assert "persistence-risk" in payload["review_required"]
    assert payload["approval_eligibility"] == "ineligible"
    assert "persisted data path" in payload["next_step"]


def test_blocking_persistence_forces_needs_review() -> None:
    blocking = {"findings": [{"shape": "dropped-persistence-structure"}], "blocking": True}
    assert state.apply_persistence_state("completed", blocking) == "completed-needs-review"
    assert (
        state.apply_persistence_state("validated-partial-result", blocking)
        == "completed-needs-review"
    )
    assert state.apply_persistence_state("failed", blocking) == "failed"
    assert state.apply_persistence_state("completed", {"findings": [], "blocking": False}) == "completed"
    assert state.apply_persistence_state("completed", None) == "completed"
    assert state.review_reasons(
        scope={"disallowed_paths": []}, parent_progress={"blocking": False}, persistence=blocking
    ) == ["persistence-risk"]
