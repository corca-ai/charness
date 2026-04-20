from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path


def _write_exec(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _make_release_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    return tmp_path / "repo", tmp_path / "remote.git", tmp_path / "bin"


def _prepare_release_tree(repo: Path, remote: Path, bin_dir: Path) -> None:
    repo.mkdir()
    remote.mkdir()
    bin_dir.mkdir()
    (repo / ".agents").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)


def _write_release_adapter(repo: Path) -> None:
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/release",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "package_id: demo",
                "packaging_manifest_path: packaging/demo.json",
                "checked_in_plugin_root: plugins/demo",
                "sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .",
                "quality_command: ./scripts/run-quality.sh",
                "update_instructions:",
                "- Run `demo update`.",
                "- Restart the host if the previous version is still visible.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {"manifest": {"version": "0.0.0"}},
                "claude": {"manifest": {"version": "0.0.0"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_fake_git(repo: Path, bin_dir: Path) -> None:
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    _write_exec(
        bin_dir / "git",
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
            raise SystemExit(subprocess.run([{json.dumps(shutil.which("git") or "/usr/bin/git")}, *args]).returncode)
            """
        ),
    )


def _write_sync_script(repo: Path) -> None:
    _write_exec(
        repo / "scripts" / "sync_root_plugin_manifests.py",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            from __future__ import annotations
            import argparse
            import json
            from pathlib import Path

            parser = argparse.ArgumentParser()
            parser.add_argument("--repo-root", type=Path, required=True)
            args = parser.parse_args()
            repo_root = args.repo_root.resolve()
            version = json.loads((repo_root / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"]
            for rel in (
                ".claude-plugin/marketplace.json",
                "plugins/demo/.claude-plugin/plugin.json",
                "plugins/demo/.codex-plugin/plugin.json",
            ):
                path = repo_root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"version": version}, indent=2) + "\\n", encoding="utf-8")
            agents_path = repo_root / ".agents" / "plugins" / "marketplace.json"
            agents_path.parent.mkdir(parents=True, exist_ok=True)
            agents_path.write_text(
                json.dumps({"plugins": [{"name": "demo", "source": {"path": "./plugins/demo"}}]}, indent=2) + "\\n",
                encoding="utf-8",
            )
            """
        ),
    )


def _write_quality_script(repo: Path) -> None:
    _write_exec(
        repo / "scripts" / "run-quality.sh",
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            printf 'quality ok\n' > .quality-ran
            """
        ),
    )


def _write_fake_gh(bin_dir: Path) -> None:
    _write_exec(
        bin_dir / "gh",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            from __future__ import annotations
            import json
            import os
            import sys
            from pathlib import Path

            log_path = Path(os.environ["FAKE_GH_LOG"])
            args = sys.argv[1:]
            entries = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
            entries.append(args)
            log_path.write_text(json.dumps(entries, indent=2) + "\\n", encoding="utf-8")

            if args == ["auth", "status"]:
                print("authenticated")
                raise SystemExit(0)
            if args[:2] == ["release", "view"]:
                raise SystemExit(1)
            if args[:2] == ["release", "create"]:
                tag = args[2]
                print(f"https://github.com/example/demo/releases/tag/{tag}")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
    )


def _init_repo_git(repo: Path, remote: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "codex-test@example.com"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo, check=True, capture_output=True, text=True)


def _seed_publish_release_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo, remote, bin_dir = _make_release_paths(tmp_path)
    _prepare_release_tree(repo, remote, bin_dir)
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)
    _write_release_adapter(repo)
    _write_fake_git(repo, bin_dir)
    _write_sync_script(repo)
    _write_quality_script(repo)
    _write_fake_gh(bin_dir)
    _init_repo_git(repo, remote)
    return repo, remote, bin_dir


def test_publish_release_bumps_pushes_tags_and_creates_release(tmp_path: Path) -> None:
    repo, remote, bin_dir = _seed_publish_release_repo(tmp_path)

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
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

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["previous_version"] == "0.0.0"
    assert payload["target_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert (repo / ".quality-ran").read_text(encoding="utf-8").strip() == "quality ok"
    assert (repo / "charness-artifacts" / "release" / "latest.md").is_file()
    assert subprocess.run(["git", "tag", "--list", "v0.0.1"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip() == "v0.0.1"
    remote_tags = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", "refs/tags/v0.0.1"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "refs/tags/v0.0.1" in remote_tags
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert ["auth", "status"] in gh_log
    assert ["release", "view", "v0.0.1"] in gh_log
    assert any(
        entry[:6] == ["release", "create", "v0.0.1", "--verify-tag", "--title", "v0.0.1"]
        for entry in gh_log
    )
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["push", "origin", "main", "v0.0.1"] in git_log
    assert ["push", "origin", "main"] not in git_log
    assert ["push", "origin", "v0.0.1"] not in git_log
    assert payload["release_url"] == "https://github.com/example/demo/releases/tag/v0.0.1"
    assert payload["public_release_verification"] == "not_checked"
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Release State" in artifact_text
    assert "public release surface verification: not checked by this helper" in artifact_text
    assert "## Public Release Verification" in artifact_text
    assert "Run `demo update`." in artifact_text
    assert "Restart the host if the previous version is still visible." in artifact_text
