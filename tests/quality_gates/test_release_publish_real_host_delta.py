from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.quality_gates.test_release_publish import _seed_publish_release_repo


def _write_real_host_release_config(repo: Path) -> None:
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_required_path_globs:\n- README.md\nreal_host_checklist:\n- Verify on a clean host.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "operator-docs",
                        "description": "Operator docs.",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _publish_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    return env


def _assert_real_host_required(repo: Path, result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(
        encoding="utf-8"
    )
    assert payload["real_host_required"] is True
    assert "Release-time real-host proof is required for this slice." in artifact_text
    assert "Verify on a clean host." in artifact_text
    return payload


def test_publish_release_records_real_host_proof_for_already_pushed_tag_delta(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    _write_real_host_release_config(repo)
    (repo / "README.md").write_text("# Demo\n\nChanged after the previous release.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Change release surface"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    _assert_real_host_required(repo, result)


def test_publish_release_fetches_missing_previous_tag_for_real_host_proof(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "tag", "-d", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    _write_real_host_release_config(repo)
    (repo / "README.md").write_text("# Demo\n\nChanged after the previous release.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Change release surface"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)

    env = _publish_env(tmp_path, bin_dir)
    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    _assert_real_host_required(repo, result)
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"] in git_log


def test_publish_current_uses_previous_release_tag_for_real_host_proof(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "origin", "v0.0.0"], cwd=repo, check=True, capture_output=True, text=True)
    _write_real_host_release_config(repo)
    (repo / "README.md").write_text("# Demo\n\nChanged before publish-current.\n", encoding="utf-8")
    subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/bump_version.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Prepare current release"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--publish-current",
            "--execute",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    payload = _assert_real_host_required(repo, result)
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.1"
