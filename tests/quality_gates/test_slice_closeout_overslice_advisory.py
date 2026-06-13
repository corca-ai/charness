"""Over-slicing advisory (spec achieve-efficiency-improvements, direction B).

A run of consecutive charness-artifacts/-only commits is process churn. The
advisory is non-blocking and enabled by default; the threshold is env-tunable.
The `Current slice intent:` frame field must stay non-blocking (C5): it is a
frame bullet, never a required closeout section.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts import slice_closeout_advisories as adv
from scripts.slice_closeout_advisories import (
    DEFAULT_OVERSLICE_ARTIFACT_RUN,
    advise_over_slicing,
    resolve_overslice_artifact_run_threshold,
    trailing_artifact_only_run,
)


def test_trailing_run_counts_consecutive_artifact_only_commits() -> None:
    commits = [
        ["charness-artifacts/goals/g.md"],
        ["charness-artifacts/retro/r.md", "charness-artifacts/handoff.md"],
        ["charness-artifacts/critique/c.md"],
    ]
    assert trailing_artifact_only_run(commits) == 3


def test_run_breaks_at_first_substantive_commit() -> None:
    commits = [
        ["charness-artifacts/goals/g.md"],
        ["scripts/run_slice_closeout.py"],  # substantive — breaks the run
        ["charness-artifacts/retro/r.md"],
    ]
    assert trailing_artifact_only_run(commits) == 1


def test_mixed_commit_is_not_artifact_only() -> None:
    # A commit touching both an artifact and code is NOT artifact-only.
    commits = [["charness-artifacts/goals/g.md", "skills/public/achieve/SKILL.md"]]
    assert trailing_artifact_only_run(commits) == 0


def test_empty_commit_paths_do_not_count() -> None:
    assert trailing_artifact_only_run([[], ["charness-artifacts/x.md"]]) == 0


def test_threshold_env_override_and_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHARNESS_OVERSLICE_ARTIFACT_RUN", raising=False)
    assert resolve_overslice_artifact_run_threshold() == DEFAULT_OVERSLICE_ARTIFACT_RUN
    monkeypatch.setenv("CHARNESS_OVERSLICE_ARTIFACT_RUN", "5")
    assert resolve_overslice_artifact_run_threshold() == 5
    # Floor of 2: a single artifact-only commit is never churn.
    monkeypatch.setenv("CHARNESS_OVERSLICE_ARTIFACT_RUN", "1")
    assert resolve_overslice_artifact_run_threshold() == 2
    monkeypatch.setenv("CHARNESS_OVERSLICE_ARTIFACT_RUN", "nope")
    assert resolve_overslice_artifact_run_threshold() == DEFAULT_OVERSLICE_ARTIFACT_RUN


def test_advise_fires_at_threshold(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    monkeypatch.setattr(
        adv,
        "_recent_commit_path_lists",
        lambda repo_root, max_commits: [["charness-artifacts/a.md"]] * 3,
    )
    advise_over_slicing(tmp_path)
    err = capsys.readouterr().err
    assert "consecutive charness-artifacts/-only commits" in err
    assert "Current slice intent" in err


def test_advise_silent_below_threshold(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    monkeypatch.setattr(
        adv,
        "_recent_commit_path_lists",
        lambda repo_root, max_commits: [["charness-artifacts/a.md"], ["scripts/x.py"]],
    )
    advise_over_slicing(tmp_path)
    assert capsys.readouterr().err == ""


def test_recent_commit_path_lists_breaks_when_show_fails(monkeypatch, tmp_path) -> None:
    # log returns a sha, git show fails -> break before appending (degrade path).
    def fake_run(cmd, **_kw):
        if "log" in cmd:
            return SimpleNamespace(returncode=0, stdout="abc123\n")
        if "show" in cmd:
            return SimpleNamespace(returncode=1, stdout="")
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(adv.subprocess, "run", fake_run)
    assert adv._recent_commit_path_lists(tmp_path, max_commits=3) == []


def test_current_slice_intent_is_non_blocking() -> None:
    # C5: the frame field must never gate the complete flip. It lives in
    # `## Active Operating Frame` (a frame bullet), never in REQUIRED_SECTIONS.
    import importlib.util
    from pathlib import Path

    path = Path("skills/public/achieve/scripts/goal_artifact_lib.py")
    spec = importlib.util.spec_from_file_location("goal_artifact_lib_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert "Current slice intent" not in module.REQUIRED_SECTIONS
    assert "Active Operating Frame" not in module.REQUIRED_SECTIONS
