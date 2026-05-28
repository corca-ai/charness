from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

from .test_release_publish import _seed_publish_release_repo, _write_exec

ROOT = Path(__file__).resolve().parents[2]


def _publish_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    return env


def _run_publish(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            "skills/public/release/scripts/publish_release.py",
            "--repo-root",
            str(repo),
            "--part",
            "patch",
            "--close-issue",
            "44",
            "--critique-blocked",
            "synthetic-host-signal for legacy issue-closeout preflight test",
            "--execute",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _assert_stopped_before_mutation(repo: Path, tmp_path: Path, initial_head: str) -> None:
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.0.0"
    assert not (repo / ".quality-ran").exists()
    assert not (repo / "charness-artifacts" / "release" / "latest.md").exists()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True)
    assert head.stdout.strip() == initial_head
    tags = subprocess.run(["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True)
    assert tags.stdout.strip() == ""
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry and entry[0] in {"commit", "push"} for entry in git_log)
    assert ["tag", "v0.0.1"] not in git_log


def test_close_issue_preflight_fails_before_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    initial_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_GH_ISSUE_STATE"] = str(tmp_path / "issue-state.json")
    env["FAKE_GH_ISSUE_VIEW_FAIL"] = "1"
    Path(env["FAKE_GH_ISSUE_STATE"]).write_text(json.dumps({"44": "OPEN"}) + "\n", encoding="utf-8")

    result = _run_publish(repo, env)

    assert result.returncode == 1
    assert "release --close-issue preflight failed before mutation" in result.stderr
    _assert_stopped_before_mutation(repo, tmp_path, initial_head)
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["issue", "view", "44", "--repo", "example/demo", "--json", "number,state,url"] in gh_log
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log)
    assert not any(entry[:2] == ["issue", "close"] for entry in gh_log)


def test_close_issue_requires_github_repo_before_mutation(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _write_exec(
        bin_dir / "custom-release",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json, os, sys
            from pathlib import Path
            log = Path(os.environ["FAKE_RELEASE_BACKEND_LOG"])
            entries = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
            entries.append(sys.argv[1:])
            log.write_text(json.dumps(entries, indent=2) + "\\n", encoding="utf-8")
            raise SystemExit(1 if sys.argv[1:3] == ["release", "view"] else 0)
            """
        ),
    )
    adapter_path = repo / ".agents" / "release-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\nrelease_backend:\n"
        + "  id: custom-release\n"
        + "  commands:\n"
        + "    auth_check:\n"
        + "      - custom-release\n"
        + "      - auth\n"
        + "    release_view:\n"
        + "      - custom-release\n"
        + "      - release\n"
        + "      - view\n"
        + "      - '{tag}'\n"
        + "    release_create:\n"
        + "      - custom-release\n"
        + "      - release\n"
        + "      - create\n"
        + "      - '{tag}'\n"
        + "      - '--title'\n"
        + "      - '{title}'\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".agents/release-adapter.yaml"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Use custom release backend"], cwd=repo, check=True, capture_output=True, text=True)
    initial_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    env = _publish_env(tmp_path, bin_dir)
    env["FAKE_RELEASE_BACKEND_LOG"] = str(tmp_path / "release-backend-log.json")

    result = _run_publish(repo, env)

    assert result.returncode == 1
    assert "release --close-issue requires a GitHub repo before mutation" in result.stderr
    _assert_stopped_before_mutation(repo, tmp_path, initial_head)
    backend_log = json.loads((tmp_path / "release-backend-log.json").read_text(encoding="utf-8"))
    assert ["release", "view", "v0.0.1"] in backend_log
    assert ["release", "create", "v0.0.1", "--title", "v0.0.1"] not in backend_log
