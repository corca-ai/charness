from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

blind_workspace = load_script_module(
    "prepare_prompt_mutation_blind_workspace_under_test",
    ROOT / "scripts" / "prepare_prompt_mutation_blind_workspace.py",
)


def _git(repo: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
        env=env,
    )


def _commit_env(offset: int = 0) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "tester",
            "GIT_AUTHOR_EMAIL": "tester@example.invalid",
            "GIT_COMMITTER_NAME": "tester",
            "GIT_COMMITTER_EMAIL": "tester@example.invalid",
            "GIT_AUTHOR_DATE": f"170000000{offset} +0000",
            "GIT_COMMITTER_DATE": f"170000000{offset} +0000",
        }
    )
    return env


def _make_source_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "source"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "secret.txt").write_text("old experiment blueprint\n", encoding="utf-8")
    (repo / "visible.txt").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "historical clue", env=_commit_env(0))
    (repo / "secret.txt").unlink()
    (repo / "visible.txt").write_text("capture tree\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "snapshot source", env=_commit_env(1))
    snapshot_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, snapshot_sha


def _make_poison_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "poison"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "poison.txt").write_text("wrong repo\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "poison", env=_commit_env(9))
    return repo


def test_prepare_workspace_exports_tree_without_source_history_or_remotes(tmp_path: Path) -> None:
    source, snapshot_sha = _make_source_repo(tmp_path)
    workspace = tmp_path / "blind"
    metadata = tmp_path / "blind-metadata.json"

    rc = blind_workspace.main(
        [
            "--repo-root",
            str(source),
            "--snapshot-ref",
            snapshot_sha,
            "--out-dir",
            str(workspace),
            "--metadata-out",
            str(metadata),
        ]
    )

    assert rc == 0
    report = json.loads(metadata.read_text(encoding="utf-8"))
    assert report["source_snapshot_sha"] == snapshot_sha
    assert report["visible_history_commit_count"] == 1
    assert report["workspace_head_parents"] == []
    assert report["workspace_remote_count"] == 0
    assert (workspace / "visible.txt").read_text(encoding="utf-8") == "capture tree\n"
    assert not (workspace / "secret.txt").exists()
    assert not (workspace / "blind-metadata.json").exists()

    assert _git(workspace, "rev-list", "--count", "HEAD").stdout.strip() == "1"
    assert _git(workspace, "show", "HEAD~1:secret.txt", check=False).returncode != 0
    assert _git(workspace, "remote", "-v").stdout == ""


def test_metadata_out_inside_workspace_is_refused(tmp_path: Path, capsys) -> None:
    source, snapshot_sha = _make_source_repo(tmp_path)
    workspace = tmp_path / "blind"

    rc = blind_workspace.main(
        [
            "--repo-root",
            str(source),
            "--snapshot-ref",
            snapshot_sha,
            "--out-dir",
            str(workspace),
            "--metadata-out",
            str(workspace / "metadata.json"),
        ]
    )

    assert rc == 1
    assert "metadata-out must live outside" in capsys.readouterr().err
    assert not workspace.exists()


def test_prepare_workspace_scrubs_ambient_git_routing_env(tmp_path: Path, monkeypatch) -> None:
    source, snapshot_sha = _make_source_repo(tmp_path)
    poison = _make_poison_repo(tmp_path)
    source_head_before = _git(source, "rev-parse", "HEAD").stdout.strip()
    source_count_before = _git(source, "rev-list", "--count", "HEAD").stdout.strip()
    poison_head_before = _git(poison, "rev-parse", "HEAD").stdout.strip()
    workspace = tmp_path / "blind"

    monkeypatch.setenv("GIT_DIR", str(poison / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(poison))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "poison-index"))

    report = blind_workspace.prepare_workspace(source, snapshot_sha, workspace)
    clean_env = blind_workspace.scrub_git_env()

    assert report["visible_history_commit_count"] == 1
    assert report["workspace_head_parents"] == []
    assert _git(workspace, "rev-list", "--count", "HEAD", env=clean_env).stdout.strip() == "1"
    assert _git(source, "rev-parse", "HEAD", env=clean_env).stdout.strip() == source_head_before
    assert _git(source, "rev-list", "--count", "HEAD", env=clean_env).stdout.strip() == source_count_before
    assert _git(poison, "rev-parse", "HEAD", env=clean_env).stdout.strip() == poison_head_before
