from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def github_repo_slug(repo_root: Path, backend: dict[str, Any], *, run) -> str | None:
    if backend.get("id", "gh") != "gh":
        return None
    result = run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        cwd=repo_root,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    url_result = run(["gh", "repo", "view", "--json", "url", "--jq", ".url"], cwd=repo_root, check=False)
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$", url_result.stdout.strip())
    return match.group(1) if match else None


def release_commit_body(payload: dict[str, Any], close_issues: list[int]) -> list[str]:
    if not close_issues:
        return []
    lines = [
        f"Release: {payload['tag_name']}",
        f"Quality: {payload['quality_command']}",
        "",
    ]
    lines.extend(f"Close #{number}." for number in close_issues)
    return lines


def issue_state(repo_root: Path, repo: str, number: int, *, run) -> dict[str, Any]:
    result = run(
        ["gh", "issue", "view", str(number), "--repo", repo, "--json", "number,state,url"],
        cwd=repo_root,
    )
    return json.loads(result.stdout)


def ensure_release_issues_closed(
    repo_root: Path,
    *,
    repo: str | None,
    issue_numbers: list[int],
    payload: dict[str, Any],
    run,
) -> None:
    if not issue_numbers:
        payload["issue_closeout"] = {"status": "not_requested", "issues": []}
        return
    if repo is None:
        raise SystemExit("release close issue verification needs a GitHub repo; pass --close-issue-repo")
    verified: list[dict[str, Any]] = []
    for number in issue_numbers:
        state_payload = issue_state(repo_root, repo, number, run=run)
        if state_payload.get("state") != "CLOSED":
            comment = "\n".join(
                [
                    f"Resolved by release `{payload['tag_name']}`.",
                    "",
                    f"- Release: {payload.get('release_url') or 'published release URL unavailable'}",
                    f"- Commit: `{payload.get('commit_sha')}`",
                    "- Auto-close carrier: direct release commit body.",
                    "- Manual close reason: issue remained open after push/release verification.",
                ]
            )
            run(["gh", "issue", "close", str(number), "--repo", repo, "--comment", comment], cwd=repo_root)
            state_payload = issue_state(repo_root, repo, number, run=run)
        if state_payload.get("state") != "CLOSED":
            raise SystemExit(f"release issue closeout failed: {repo}#{number} is still {state_payload.get('state')}")
        verified.append(state_payload)
    payload["issue_closeout"] = {"status": "verified", "repo": repo, "issues": verified}


def commit_issue_closeout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload["issue_closeout"],
    )
    run(["git", "add", artifact_relpath], cwd=repo_root)
    run(["git", "commit", "-m", f"Record release issue closeout for {payload['tag_name']}"], cwd=repo_root)
    run(["git", "push", remote, branch], cwd=repo_root)
    payload["issue_closeout_commit_sha"] = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
