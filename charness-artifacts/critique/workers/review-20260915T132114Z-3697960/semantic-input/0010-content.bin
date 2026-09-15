"""Implementation-lane shaping for require-change task runs (#815).

A require-change lane once spent a full model run in analysis without a
scoped edit. The carrier now marks implementation lanes, demands prompt
entry into the edit loop, and records phase/blocker signals on the receipt.
"""

from __future__ import annotations

from pathlib import Path

from scripts.task_run import task_run_lane_runner as lane_runner
from tests.charness_cli.test_task_run_fixtures import _repo, _run


def test_implementation_prompt_names_scope_and_blocker_protocol() -> None:
    shaped = lane_runner.build_lane_prompt(
        "Fix the lease delta.",
        require_change=True,
        scopes=["gateway/lease.py"],
    )
    assert "implementation lane" in shaped
    assert "gateway/lease.py" in shaped
    assert "EDITING" in shaped
    assert "BLOCKED:" in shaped
    assert shaped.rstrip().endswith("Fix the lease delta.")


def test_non_require_change_prompt_passes_through_untouched() -> None:
    assert (
        lane_runner.build_lane_prompt(
            "Review this.", require_change=False, scopes=["a.py"]
        )
        == "Review this."
    )


def test_lane_progress_parses_phases_and_blocker() -> None:
    progress = lane_runner.lane_progress(
        "thinking\nCONTRACT-READ\nmore\nEDITING\nBLOCKED: no lease event\n"
    )
    assert progress["phases"] == ["CONTRACT-READ", "EDITING"]
    assert progress["blocker"] == "no lease event"


def test_lane_progress_without_markers_is_empty() -> None:
    assert lane_runner.lane_progress("analysis only\n") == {
        "phases": [],
        "blocker": None,
    }


def _stub(tmp_path: Path, body: str) -> Path:
    executable = tmp_path / "codex"
    executable.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    executable.chmod(0o755)
    return executable


def test_blocked_lane_records_typed_blocker(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        'echo "CONTRACT-READ"\necho "BLOCKED: lease event never fires"\nexit 0',
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert payload["lane_progress"]["blocker"] == "lease event never fires"
    assert "lane reported blocker" in payload["next_step"]


def test_stalled_lane_names_missing_editing(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(tmp_path, 'echo "CONTRACT-READ"\nexit 0')
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["gateway/lease.py"],
        require_change=True,
    )
    assert payload["status"] == "failed", payload
    assert payload["lane_progress"]["phases"] == ["CONTRACT-READ"]
    assert payload["lane_progress"]["blocker"] is None
    assert "without EDITING" in payload["next_step"]


def test_editing_lane_records_phases_and_completes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    executable = _stub(
        tmp_path,
        "echo CONTRACT-READ\necho EDITING\n"
        "echo delta > worktree-file.txt\n"
        "echo TESTING\nexit 0",
    )
    payload = _run(
        repo,
        tmp_path,
        executable,
        scopes=["worktree-file.txt"],
        require_change=True,
    )
    assert payload["status"] == "completed", payload
    assert payload["lane_progress"]["phases"] == [
        "CONTRACT-READ",
        "EDITING",
        "TESTING",
    ]
    assert payload["lane_progress"]["blocker"] is None
