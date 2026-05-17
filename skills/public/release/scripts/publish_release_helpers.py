from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"tag"})
RELEASE_CREATE_PLACEHOLDERS: frozenset[str] = frozenset({"tag", "title"})
AUTH_CHECK_PLACEHOLDERS: frozenset[str] = frozenset()

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")

OP_PLACEHOLDERS: dict[str, frozenset[str]] = {
    "release_view": RELEASE_VIEW_PLACEHOLDERS,
    "release_create": RELEASE_CREATE_PLACEHOLDERS,
    "auth_check": AUTH_CHECK_PLACEHOLDERS,
}


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


def backend_command(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    **subs: str,
) -> list[str]:
    allowed = OP_PLACEHOLDERS.get(op)
    if allowed is None:
        raise SystemExit(
            f"backend_command({op}): unknown op; declare a placeholder allowlist in OP_PLACEHOLDERS"
        )
    extra_subs = sorted(set(subs) - allowed)
    if extra_subs:
        raise SystemExit(
            f"backend_command({op}): caller passed placeholders {extra_subs!r} "
            f"not in op's allowlist {sorted(allowed)!r}"
        )
    commands = backend.get("commands") or {}
    template = commands.get(op)
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise SystemExit(
                f"release_backend `{backend.get('id')}` did not declare a `{op}` command template"
            )
        template = default
    used = {match for part in template for match in _PLACEHOLDER_RE.findall(part)}
    unknown = sorted(used - allowed)
    if unknown:
        raise SystemExit(
            f"backend_command({op}): adapter template uses unknown placeholders {unknown!r}; "
            f"allowed for {op}: {sorted(allowed)!r}"
        )
    return [part.format(**subs) if subs and "{" in part else part for part in template]


def release_exists(repo_root: Path, tag_name: str, backend: dict[str, Any] | None = None) -> bool:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    command = backend_command(backend, "release_view", ["gh", "release", "view", "{tag}"], tag=tag_name)
    return run(command, cwd=repo_root, check=False).returncode == 0


def changed_paths(repo_root: Path) -> list[str]:
    return [line[3:] for line in git_status(repo_root) if len(line) >= 4]


def unreleased_paths(repo_root: Path, *, remote: str, branch: str) -> list[str]:
    result = run(
        ["git", "diff", "--name-only", f"{remote}/{branch}..HEAD"],
        cwd=repo_root,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def issue_closeout_lines(issue_closeout: dict[str, Any] | None) -> list[str]:
    lines = ["", "## Issue Closeout", ""]
    if issue_closeout is None:
        return lines + ["- Issue closeout verification: pending or not requested."]
    if issue_closeout.get("status") != "verified":
        return lines + [f"- Issue closeout verification: `{issue_closeout.get('status')}`."]
    lines.append(f"- Issue closeout verification: `{issue_closeout.get('status')}`.")
    if repo := issue_closeout.get("repo"):
        lines.append(f"- GitHub repo: `{repo}`")
    for issue in issue_closeout.get("issues", []):
        lines.append(f"- Issue #{issue.get('number')}: `{issue.get('state')}` ({issue.get('url')})")
    return lines


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
    fresh_checkout_payload: dict[str, Any] | None = None,
    issue_closeout: dict[str, Any] | None = None,
    quality_status: str = "passed before publish",
    tag_name: str | None = None,
) -> str:
    artifact_dir = repo_root / output_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "latest.md"
    resolved_tag = tag_name or f"v{target_version}"
    artifact_relpath = str(artifact_path.relative_to(repo_root))
    lines = [
        "# Release Surface Check",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        "",
        "## Scope",
        "",
        f"Advanced `{package_id}` toward release `{target_version}` (tag `{resolved_tag}`) through the repo-owned release helper.",
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
        f"- `{quality_command}` {quality_status}.",
        "- `current_release.py` reported no version drift across packaging and generated install surfaces.",
        "- one git push carried both the release branch update and the tag from the release helper.",
        "",
        "## Release State",
        "",
        "- local release mutation: complete",
        "- branch/tag push: complete",
    ]
    if release_url:
        lines.append(
            f"- GitHub release record: target URL `{release_url}`; creation runs after the branch/tag push"
        )
    else:
        lines.append("- GitHub release record: not created by this helper run")
    lines.extend(
        [
            "- public release surface verification: not checked by this helper",
            f"- audit narrative: durable record written to `{artifact_relpath}` and committed with this slice",
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
    lines.extend(["", "## Fresh Checkout Probes", ""])
    if fresh_checkout_payload is None:
        lines.append("- Fresh-checkout probe status: pending release-helper execution.")
    elif fresh_checkout_payload.get("status") == "not_configured":
        lines.append("- No repo-declared fresh checkout probes were configured for this release.")
    else:
        lines.append(f"- Fresh-checkout probe status: {fresh_checkout_payload.get('status')}.")
        for command in fresh_checkout_payload.get("fresh_checkout_probes", []):
            lines.append(f"- `{command}`")
    lines.extend(issue_closeout_lines(issue_closeout))
    user_update_steps = update_instructions or ["Document the operator-facing refresh path before calling the release fully closed."]
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
