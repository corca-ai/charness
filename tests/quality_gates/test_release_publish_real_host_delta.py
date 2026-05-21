from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
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


def _write_broken_real_host_release_config(repo: Path) -> None:
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_required_surfaces:\n- missing-release-surface\nreal_host_checklist:\n- Verify on a clean host.\n",
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


def _write_missing_surfaces_real_host_release_config(repo: Path) -> None:
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nreal_host_required_surfaces:\n- operator-docs\nreal_host_checklist:\n- Verify on a clean host.\n",
        encoding="utf-8",
    )


def _publish_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    return env


def _write_base_ref_failing_git(bin_dir: Path) -> None:
    real_git = shutil.which("git") or "/usr/bin/git"
    (bin_dir / "git").write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            from __future__ import annotations
            import json
            import os
            import subprocess
            import sys
            from pathlib import Path

            log_path = Path(os.environ["FAKE_GIT_LOG"])
            args = sys.argv[1:]
            entries = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
            entries.append(args)
            log_path.write_text(json.dumps(entries, indent=2) + "\\n", encoding="utf-8")
            if os.environ.get("FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL") == "1" and args == [
                "ls-remote", "--tags", "origin", "refs/tags/v0.0.0"
            ]:
                print("forced previous tag lookup failure", file=sys.stderr)
                raise SystemExit(44)
            if os.environ.get("FAKE_GIT_FETCH_TAG_FAIL") == "1" and args == [
                "fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"
            ]:
                print("forced tag fetch failure", file=sys.stderr)
                raise SystemExit(43)
            raise SystemExit(subprocess.run([{json.dumps(real_git)}, *args]).returncode)
            """
        ),
        encoding="utf-8",
    )
    (bin_dir / "git").chmod(0o755)


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


def _seed_missing_local_previous_tag_delta(tmp_path: Path) -> tuple[Path, Path]:
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
    return repo, bin_dir


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
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
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


def test_publish_release_fails_closed_when_previous_tag_fetch_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_FETCH_TAG_FAIL"] = "1"

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

    assert result.returncode == 1
    assert "release base ref fetch failed while computing unreleased paths" in result.stderr
    assert "tag_ref: refs/tags/v0.0.0" in result.stderr
    assert "command: git fetch --quiet origin refs/tags/v0.0.0:refs/tags/v0.0.0" in result.stderr
    assert "exit_code: 43" in result.stderr
    assert "forced tag fetch failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    fetch_command = ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"]
    fetch_index = git_log.index(fetch_command)
    assert ["ls-remote", "--tags", "origin", "refs/tags/v0.0.0"] in git_log
    assert fetch_command in git_log
    assert ["diff", "--name-only", "origin/main..HEAD"] not in git_log[fetch_index + 1 :]
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_previous_tag_fetch_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_FETCH_TAG_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "release base ref fetch failed while computing unreleased paths" in result.stderr
    assert "forced tag fetch failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


def test_publish_release_fails_closed_when_previous_tag_lookup_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL"] = "1"

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

    assert result.returncode == 1
    assert "release base ref lookup failed while computing unreleased paths" in result.stderr
    assert "tag_ref: refs/tags/v0.0.0" in result.stderr
    assert "command: git ls-remote --tags origin refs/tags/v0.0.0" in result.stderr
    assert "exit_code: 44" in result.stderr
    assert "forced previous tag lookup failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    lookup_command = ["ls-remote", "--tags", "origin", "refs/tags/v0.0.0"]
    lookup_index = git_log.index(lookup_command)
    assert lookup_command in git_log
    assert ["fetch", "--quiet", "origin", "refs/tags/v0.0.0:refs/tags/v0.0.0"] not in git_log
    assert ["diff", "--name-only", "origin/main..HEAD"] not in git_log[lookup_index + 1 :]
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_previous_tag_lookup_fails(tmp_path: Path) -> None:
    repo, bin_dir = _seed_missing_local_previous_tag_delta(tmp_path)
    _write_base_ref_failing_git(bin_dir)
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "release base ref lookup failed while computing unreleased paths" in result.stderr
    assert "forced previous tag lookup failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


def test_publish_release_fails_closed_when_release_diff_fails(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_real_host_release_config(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Configure release host proof"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_DIFF_NAME_ONLY_FAIL"] = "1"

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

    assert result.returncode == 1
    assert "release diff failed while computing unreleased paths" in result.stderr
    assert "command: git diff --name-only origin/main..HEAD" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced diff failure" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert any(entry[:2] == ["diff", "--name-only"] for entry in git_log)
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_release_diff_fails(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_real_host_release_config(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Configure release host proof"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GIT_DIFF_NAME_ONLY_FAIL"] = "1"

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "release diff failed while computing unreleased paths" in result.stderr
    assert "command: git diff --name-only origin/main..HEAD" in result.stderr
    assert "forced diff failure" in result.stderr
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


def test_publish_release_fails_closed_when_real_host_config_is_broken(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_broken_real_host_release_config(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Configure broken release host proof"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

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

    assert result.returncode == 1
    assert "release real-host proof probe failed" in result.stderr
    assert '"configuration_status": "broken"' in result.stderr
    assert "missing-release-surface" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["commit", "-m", "Release v0.0.1"] not in git_log
    assert ["tag", "v0.0.1"] not in git_log
    assert not any(entry and entry[0] == "push" for entry in git_log)
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_fails_closed_when_real_host_config_is_broken(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_broken_real_host_release_config(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Configure broken release host proof"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "release real-host proof probe failed" in result.stderr
    assert '"configuration_status": "broken"' in result.stderr
    assert "missing-release-surface" in result.stderr
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


def test_publish_release_fails_closed_when_real_host_builder_cannot_run(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_missing_surfaces_real_host_release_config(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Configure release host proof without surfaces"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    before_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

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

    assert result.returncode == 1
    assert "release real-host proof probe failed" in result.stderr
    assert "SurfaceError" in result.stderr
    assert "missing surfaces manifest" in result.stderr
    assert json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
        .stdout.strip()
        == before_head
    )
    assert subprocess.run(
        ["git", "tag", "--list", "v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == ""
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)


def test_publish_release_dry_run_allows_no_trigger_repo_without_surfaces(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    assert not (repo / ".agents" / "surfaces.json").exists()

    result = subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
        env=_publish_env(tmp_path, bin_dir),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["execute"] is False
    assert payload["target_version"] == "0.0.1"
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()


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
