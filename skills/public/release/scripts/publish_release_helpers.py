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
    update_instructions: list[str],
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
        f"Advanced `{package_id}` toward release `{target_version}` through the repo-owned release helper.",
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
        "",
        "## Release State",
        "",
        "- local release mutation: complete",
        "- branch/tag push: complete",
    ]
    if release_url:
        lines.append(f"- GitHub release record: created ({release_url})")
    else:
        lines.append("- GitHub release record: not created by this helper run")
    lines.extend(
        [
            "- public release surface verification: not checked by this helper",
            "",
            "## Public Release Verification",
            "",
        ]
    )
    if real_host_payload.get("required"):
        lines.append(
            "- This slice still requires configured public/real-host verification before the release is fully closed."
        )
        lines.extend(["", "## Real-Host Proof", "", "- Release-time real-host proof is required for this slice."])
        lines.extend(f"- {item}" for item in real_host_payload.get("checklist", []))
    else:
        lines.append(
            "- No configured public/real-host verification trigger matched this slice, but async publication repos should still keep workflow/public checks explicit."
        )
        lines.extend(
            ["", "## Real-Host Proof", "", "- No configured release-time real-host proof trigger matched this slice."]
        )
    user_update_steps = update_instructions or [
        "Document the operator-facing refresh path before calling the release fully closed.",
    ]
    lines.extend(
        [
            "",
            "## User Update Steps",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in user_update_steps)
    lines.append("")
    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    return str(artifact_path.relative_to(repo_root))
