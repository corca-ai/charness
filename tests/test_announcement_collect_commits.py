from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECT_COMMITS = ROOT / "skills" / "public" / "announcement" / "scripts" / "collect_commits.py"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def init_repo(repo: Path) -> None:
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Codex Test")
    git(repo, "config", "user.email", "codex-test@example.com")


def run_collect(repo: Path, *args: str) -> dict[str, object]:
    result = subprocess.run(
        ["python3", str(COLLECT_COMMITS), "--repo-root", str(repo), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_collect_commits_includes_body_trailers_and_closing_references(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(
        tmp_path,
        "commit",
        "-m",
        "announcement sees intent",
        "-m",
        "Explain the human-facing value before diff archaeology.\n\nResolves #150\n\nVerification: pytest",
    )

    payload = run_collect(tmp_path)

    commits = payload["commits"]
    assert len(commits) == 1
    commit = commits[0]
    assert commit["subject"] == "announcement sees intent"
    assert commit["has_body"] is True
    assert "human-facing value" in commit["body"]
    assert commit["trailers"] == [
        {"key": "Verification", "value": "pytest", "raw": "Verification: pytest", "truncated": False},
    ]
    assert commit["trailers_truncated"] is False
    assert commit["closing_references"] == ["Resolves #150"]
    assert commit["closing_references_truncated"] is False
    assert commit["is_merge"] is False
    assert set(commit).issuperset({"sha", "subject"})
    assert isinstance(commit["sha"], str)
    assert len(commit["sha"]) == 40


def test_collect_commits_marks_merge_commit_body(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "base.txt").write_text("base\n", encoding="utf-8")
    git(tmp_path, "add", "base.txt")
    git(tmp_path, "commit", "-m", "base")
    git(tmp_path, "checkout", "-b", "feature")
    (tmp_path / "feature.txt").write_text("feature\n", encoding="utf-8")
    git(tmp_path, "add", "feature.txt")
    git(tmp_path, "commit", "-m", "feature work")
    git(tmp_path, "checkout", "main")
    (tmp_path / "main.txt").write_text("main\n", encoding="utf-8")
    git(tmp_path, "add", "main.txt")
    git(tmp_path, "commit", "-m", "main work")
    git(
        tmp_path,
        "merge",
        "--no-ff",
        "feature",
        "-m",
        "merge announcement narrative",
        "-m",
        "Merge body carries final closeout context.\n\nCloses #150",
    )

    payload = run_collect(tmp_path, "--limit", "1")

    commit = payload["commits"][0]
    assert commit["subject"] == "merge announcement narrative"
    assert commit["is_merge"] is True
    assert len(commit["parents"]) == 2
    assert "final closeout context" in commit["body"]
    assert commit["closing_references"] == ["Closes #150"]


def test_collect_commits_trims_long_body(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "long body", "-m", "abcdef")

    payload = run_collect(tmp_path, "--body-limit", "3")

    commit = payload["commits"][0]
    assert commit["body"] == "abc\n[truncated]"
    assert commit["body_truncated"] is True


def test_collect_commits_preserves_subject_only_shape_and_closing_reference(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "Fixes #150")

    payload = run_collect(tmp_path)

    commit = payload["commits"][0]
    assert isinstance(commit["sha"], str)
    assert len(commit["sha"]) == 40
    assert commit["subject"] == "Fixes #150"
    assert commit["has_body"] is False
    assert commit["body"] == ""
    assert commit["closing_references"] == ["Fixes #150"]


def test_collect_commits_omits_fanout_hint_by_default(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "first")

    payload = run_collect(tmp_path)

    assert "fanout_hint" not in payload


def test_collect_commits_fanout_hint_small_window(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "first")

    payload = run_collect(tmp_path, "--fanout-hint")

    hint = payload["fanout_hint"]
    assert hint["commit_count"] == 1
    assert hint["recommended"] is False
    assert hint["signals"] == []
    assert "large-window-fanout.md" in hint["reference"]


def test_collect_commits_fanout_hint_large_window(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "seed").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "seed")
    git(tmp_path, "commit", "-m", "seed")
    for index in range(32):
        (tmp_path / f"file_{index}.txt").write_text(f"{index}\n", encoding="utf-8")
        git(tmp_path, "add", f"file_{index}.txt")
        git(tmp_path, "commit", "-m", f"commit {index}")

    payload = run_collect(tmp_path, "--fanout-hint", "--limit", "50")

    hint = payload["fanout_hint"]
    assert hint["commit_count"] == 33
    assert hint["recommended"] is True
    assert any("large_window" in signal for signal in hint["signals"])


def test_collect_commits_bounds_trailers_and_closing_references(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    closing_lines = "\n".join(f"Resolves #{150 + index}" for index in range(25))
    trailer_lines = "\n".join(f"Token-{index}: {'x' * 500}" for index in range(25))
    git(
        tmp_path,
        "commit",
        "-m",
        "bounded metadata",
        "-m",
        f"Human value.\n\n{closing_lines}\n\n{trailer_lines}",
    )

    payload = run_collect(tmp_path)

    commit = payload["commits"][0]
    assert len(commit["trailers"]) == 20
    assert commit["trailers_truncated"] is True
    assert commit["trailers"][0]["truncated"] is True
    assert len(commit["trailers"][0]["value"]) < 430
    assert len(commit["closing_references"]) == 20
    assert commit["closing_references_truncated"] is True
