from __future__ import annotations

import os
import subprocess
from pathlib import Path

from tests.quality_gates.test_release_publish import _seed_publish_release_repo


def test_publish_release_rejects_untracked_critique_artifact(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    critique_artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    critique_artifact.parent.mkdir(parents=True)
    critique_artifact.write_text("# Demo critique\n", encoding="utf-8")

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--critique-artifact",
            "charness-artifacts/critique/demo.md",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode != 0
    assert "--critique-artifact must be tracked before release" in result.stderr
