from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if check and result.returncode != 0:
        rendered = " ".join(command)
        raise SystemExit(
            f"command failed: {rendered}\n"
            f"exit_code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return result


def run_shell(command: str, *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise SystemExit(
            f"command failed: {command}\n"
            f"exit_code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return result


def git_status(repo_root: Path) -> list[str]:
    result = run(["git", "status", "--short"], cwd=repo_root)
    return [line for line in result.stdout.splitlines() if line.strip()]


def current_branch(repo_root: Path) -> str:
    branch = run(["git", "branch", "--show-current"], cwd=repo_root).stdout.strip()
    if not branch:
        raise SystemExit("publish_release requires a named branch; detached HEAD is not supported")
    return branch


def tag_exists(repo_root: Path, tag_name: str, *, remote: str) -> dict[str, bool]:
    local = run(["git", "tag", "--list", tag_name], cwd=repo_root).stdout.strip() == tag_name
    remote_result = run(["git", "ls-remote", "--tags", remote, f"refs/tags/{tag_name}"], cwd=repo_root)
    return {"local": local, "remote": bool(remote_result.stdout.strip())}


def release_exists(repo_root: Path, tag_name: str) -> bool:
    return run(["gh", "release", "view", tag_name], cwd=repo_root, check=False).returncode == 0


def changed_paths(repo_root: Path) -> list[str]:
    return [line[3:] for line in git_status(repo_root) if len(line) >= 4]


def write_release_artifact(
    repo_root: Path,
    *,
    output_dir: str,
    package_id: str,
    previous_version: str,
    target_version: str,
    remote: str,
    branch: str,
    quality_command: str,
    release_url: str | None,
    real_host_payload: dict[str, Any],
) -> str:
    artifact_dir = repo_root / output_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "latest.md"
    lines = [
        "# Release Surface Check",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        "",
        "## Scope",
        "",
        f"Published `{package_id}` release `{target_version}` through the repo-owned release helper.",
        "",
        "## Current Version",
        "",
        f"- previous version: `{previous_version}`",
        f"- target version: `{target_version}`",
        f"- git branch: `{branch}`",
        f"- git remote: `{remote}`",
        "",
        "## Verification",
        "",
        f"- `{quality_command}` passed before publish.",
        "- `current_release.py` reported no version drift across packaging and generated install surfaces.",
        "- one git push carried both the release branch update and the tag from the release helper.",
    ]
    if release_url:
        lines.append(f"- GitHub release created: {release_url}")
    if real_host_payload.get("required"):
        lines.extend(["", "## Real-Host Proof", "", "- Release-time real-host proof is required for this slice."])
        lines.extend(f"- {item}" for item in real_host_payload.get("checklist", []))
    else:
        lines.extend(["", "## Real-Host Proof", "", "- No configured release-time real-host proof trigger matched this slice."])
    lines.extend(
        [
            "",
            "## User Update Steps",
            "",
            "- Run `charness update` after pulling the published release.",
            "- Refresh Claude or Codex plugin state if the host cache still shows the previous version.",
            "",
        ]
    )
    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    return str(artifact_path.relative_to(repo_root))
