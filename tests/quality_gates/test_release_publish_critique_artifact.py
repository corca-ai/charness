from __future__ import annotations

import os
import subprocess
from pathlib import Path

from tests.quality_gates.test_release_publish import _seed_publish_release_repo


def _run_publish(repo: Path, tmp_path: Path, bin_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    return subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            *extra,
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_publish_release_rejects_untracked_critique_artifact(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique_artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    critique_artifact.write_text("# Demo critique\n", encoding="utf-8")

    result = _run_publish(
        repo, tmp_path, bin_dir,
        "--critique-artifact", "charness-artifacts/critique/demo.md",
    )

    assert result.returncode != 0
    assert "--critique-artifact must be tracked before release" in result.stderr


def test_publish_release_refuses_without_any_critique_flag(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    result = _run_publish(repo, tmp_path, bin_dir)
    assert result.returncode != 0
    assert "release publish gate refused: standalone critique not satisfied" in result.stderr
    assert "standalone_critique" in result.stderr


def test_publish_release_refuses_when_blocked_signal_too_terse(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    result = _run_publish(repo, tmp_path, bin_dir, "--critique-blocked", "host-down")
    assert result.returncode != 0
    assert "release publish gate refused" in result.stderr


def test_publish_release_refuses_both_critique_flags_at_once(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique_artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    critique_artifact.write_text("# Demo critique\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "charness-artifacts/critique/demo.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "add critique"], check=True, capture_output=True)
    result = _run_publish(
        repo, tmp_path, bin_dir,
        "--critique-artifact", "charness-artifacts/critique/demo.md",
        "--critique-blocked", "synthetic-host-signal that is long enough",
    )
    assert result.returncode != 0
    assert "pass exactly one of" in result.stderr
