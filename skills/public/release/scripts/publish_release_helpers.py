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
COMMAND_TIMEOUT_SECONDS = 1800


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {COMMAND_TIMEOUT_SECONDS}s",
        )
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
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            executable="/bin/bash",
            check=False,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {COMMAND_TIMEOUT_SECONDS}s",
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


def create_release(repo_root: Path, backend: dict[str, Any], *, tag_name: str, title: str, notes_file: Path | None):
    release_command = backend_command(
        backend,
        "release_create",
        ["gh", "release", "create", "{tag}", "--verify-tag", "--title", "{title}"],
        tag=tag_name,
        title=title,
    )
    release_command.extend(["--notes-file", str(notes_file.resolve())] if notes_file else ["--generate-notes"])
    return run(release_command, cwd=repo_root)


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
        lines.append(f"  - carrier: `{issue.get('carrier')}`")
        lines.append(f"  - manual fallback used: `{issue.get('manual_fallback_used')}`")
    return lines


def release_record_lines(release_url: str | None, public_release_verification: str) -> list[str]:
    if release_url and public_release_verification == "verified":
        return [f"- GitHub release record: verified URL `{release_url}`"]
    if release_url:
        return [f"- GitHub release record: target URL `{release_url}`; creation runs after the branch/tag push"]
    return ["- GitHub release record: not created by this helper run"]


def release_push_lines(public_release_verification: str) -> list[str]:
    lines = ["- initial release push carried the release branch update and tag from the release helper."]
    if public_release_verification == "verified":
        lines.append("- post-publish artifact push recorded the verified public release state on the release branch.")
    return lines


def review_proof_lines(review_proof: str | None) -> list[str]:
    if review_proof:
        return ["", "## Review Proof", "", f"- Review proof: `{review_proof}`."]
    return ["", "## Review Status", "", "- Review proof: not recorded in this helper invocation."]


def post_publish_proof_lines(resolved_tag: str, public_release_verification: str) -> list[str]:
    if public_release_verification != "verified":
        return []
    return ["", "## Post-Publish Proof", "", f"- Public release check: `gh release view {resolved_tag}`."]


def public_release_verification_lines(public_release_verification: str, release_url: str | None) -> list[str]:
    lines = ["", "## Public Release Verification", ""]
    if public_release_verification == "verified":
        lines.append("- GitHub release publication: verified by the release backend.")
    elif release_url:
        lines.append("- GitHub release publication: expected after branch/tag push; not verified yet.")
    else:
        lines.append("- GitHub release publication: not created by this helper run.")
    return lines


def amend_fresh_checkout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    fresh_checkout_payload: dict[str, Any],
    release_url: str | None,
    artifact_relpath: str,
    tag_name: str,
    notes_file: Path | None,
    run_narrative_audit,
    run_command=run,
) -> None:
    write_artifact(fresh_checkout_payload=fresh_checkout_payload, release_url=release_url)
    run_narrative_audit(repo_root, target_tag=tag_name, notes_file=notes_file)
    run_command(["git", "add", artifact_relpath], cwd=repo_root)
    run_command(["git", "commit", "--amend", "--no-edit"], cwd=repo_root)


def commit_post_publish_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run_command=run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload.get("issue_closeout"),
    )
    diff_result = run_command(["git", "diff", "--quiet", "--", artifact_relpath], cwd=repo_root, check=False)
    if diff_result.returncode == 0:
        return
    run_command(["git", "add", artifact_relpath], cwd=repo_root)
    run_command(["git", "commit", "-m", f"Record release verification for {payload['tag_name']}"], cwd=repo_root)
    run_command(["git", "push", remote, branch], cwd=repo_root)
    payload["post_publish_artifact_commit_sha"] = run_command(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()


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
    public_release_verification: str = "not checked by this helper",
    review_proof: str | None = None,
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
        *release_push_lines(public_release_verification),
        "",
        "## Release State",
        "",
        "- local release mutation: complete",
        "- branch/tag push: complete",
    ]
    lines.extend(release_record_lines(release_url, public_release_verification))
    lines.extend(
        [
            f"- public release surface verification: {public_release_verification}",
            f"- audit narrative: durable record written to `{artifact_relpath}` and committed with this slice",
        ]
    )
    lines.extend(public_release_verification_lines(public_release_verification, release_url))
    lines.extend(["", "## Real-Host Verification", ""])
    if real_host_payload.get("required"):
        lines.append(
            "- This slice still requires configured real-host verification before the release is fully closed."
        )
        lines.extend(["", "## Real-Host Proof", "", "- Release-time real-host proof is required for this slice."])
        lines.extend(f"- {item}" for item in real_host_payload.get("checklist", []))
    else:
        lines.append("- No configured release-time real-host verification trigger matched this slice.")
        lines.extend(
            ["", "## Real-Host Proof", "", "- No configured release-time real-host proof trigger matched this slice."]
        )
    lines.extend(review_proof_lines(review_proof))
    lines.extend(post_publish_proof_lines(resolved_tag, public_release_verification))
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
