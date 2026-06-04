from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISH_SCRIPT = "skills/public/release/scripts/publish_release.py"
REVIEW_GATE_SCRIPT = "skills/public/release/scripts/check_requested_review_gate.py"


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
            if os.environ.get("FAKE_GIT_DIFF_NAME_ONLY_FAIL") == "1" and args[:2] == ["diff", "--name-only"]:
                print("forced diff failure", file=sys.stderr)
                raise SystemExit(42)
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
            if args == ["repo", "view", "--json", "url", "--jq", ".url"]:
                print("https://github.com/example/demo")
                raise SystemExit(0)
            if args == ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]:
                print("example/demo")
                raise SystemExit(0)
            if args[:2] == ["release", "view"]:
                state_path = Path(os.environ["FAKE_GH_RELEASE_STATE"])
                state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
                raise SystemExit(0 if args[2] in state else 1)
            if args[:2] == ["release", "create"]:
                tag = args[2]
                state_path = Path(os.environ["FAKE_GH_RELEASE_STATE"])
                state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
                if tag not in state and os.environ.get("FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW") != "1":
                    state.append(tag)
                state_path.write_text(json.dumps(state, indent=2) + "\\n", encoding="utf-8")
                print(f"https://github.com/example/demo/releases/tag/{tag}")
                raise SystemExit(0)
            if args[:2] == ["issue", "view"]:
                if os.environ.get("FAKE_GH_ISSUE_VIEW_FAIL") == "1":
                    print("issue view failed", file=sys.stderr)
                    raise SystemExit(1)
                state_path = Path(os.environ["FAKE_GH_ISSUE_STATE"])
                state = json.loads(state_path.read_text(encoding="utf-8"))
                number = args[2]
                print(json.dumps({
                    "number": int(number),
                    "state": state.get(number, "OPEN"),
                    "url": f"https://github.com/example/demo/issues/{number}",
                }))
                raise SystemExit(0)
            if args[:2] == ["issue", "close"]:
                state_path = Path(os.environ["FAKE_GH_ISSUE_STATE"])
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state[args[2]] = "CLOSED"
                state_path.write_text(json.dumps(state, indent=2) + "\\n", encoding="utf-8")
                print(f"closed issue {args[2]}")
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
    )


def _setup_git(repo: Path, remote: Path) -> None:
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
    _setup_git(repo, remote)
    return repo, remote, bin_dir


def _release_env(tmp_path: Path, bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["FAKE_GH_LOG"] = str(tmp_path / "gh-log.json")
    env["FAKE_GIT_LOG"] = str(tmp_path / "git-log.json")
    env["FAKE_GH_RELEASE_STATE"] = str(tmp_path / "release-state.json")
    return env


def _run_publish(repo: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", PUBLISH_SCRIPT, "--repo-root", str(repo), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_publish_patch(repo: Path, env: dict[str, str], *extra: str) -> subprocess.CompletedProcess[str]:
    # The release critique gate refuses publish unless one of
    # --critique-artifact / --critique-blocked is supplied. Tests that already
    # pass a critique flag are honored; tests that target a downstream failure
    # get a synthetic blocked-skip injected so they still reach their assertion.
    has_critique_flag = any(arg in ("--critique-artifact", "--critique-blocked") for arg in extra)
    extras = list(extra)
    if not has_critique_flag:
        extras.extend([
            "--critique-blocked",
            "synthetic-test-harness does not spawn real critique subagents",
        ])
    return _run_publish(repo, env, "--part", "patch", *extras, "--execute")


def _run_review_gate(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", REVIEW_GATE_SCRIPT, "--repo-root", str(repo), *extra],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
