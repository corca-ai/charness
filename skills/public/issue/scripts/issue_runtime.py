from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

REMOTE_PATTERNS = (
    re.compile(r"^git@[^:]+:(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"),
    re.compile(r"^ssh://git@[^/]+/(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"),
    re.compile(r"^https?://[^/]+/(?P<owner>[^/]+)/(?P<repo>.+?)(?:\.git)?$"),
)


def parse_remote_url(value: str) -> tuple[str, str] | None:
    cleaned = value.strip()
    for pattern in REMOTE_PATTERNS:
        match = pattern.match(cleaned)
        if match:
            repo = match.group("repo")
            if repo.endswith(".git"):
                repo = repo[:-4]
            return match.group("owner"), repo
    return None


def git_remote_url(repo_root: Path, remote_name: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", f"remote.{remote_name}.url"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def resolve_target(repo_root: Path, target: str | None, adapter_data: dict[str, Any]) -> dict[str, Any]:
    default_org = str(adapter_data["default_org"])
    remote_name = str(adapter_data["remote_name"])
    source = "argument"
    if target and target.strip():
        cleaned = target.strip().removeprefix("https://github.com/").removeprefix("http://github.com/")
        cleaned = cleaned[:-4] if cleaned.endswith(".git") else cleaned
        parts = [part for part in cleaned.split("/") if part]
        if len(parts) == 1:
            owner, repo = default_org, parts[0]
            source = "argument-default-org"
        elif len(parts) == 2:
            owner, repo = parts
        else:
            raise ValueError("target must be empty, repo, or org/repo")
    else:
        remote_url = git_remote_url(repo_root, remote_name)
        parsed = parse_remote_url(remote_url) if remote_url else None
        if parsed is not None:
            owner, repo = parsed
            source = f"git-remote:{remote_name}"
        else:
            owner, repo = default_org, repo_root.name
            source = "cwd-default-org"
    return {"owner": owner, "repo": repo, "full_name": f"{owner}/{repo}", "source": source}


def parse_selector(selector: str | None) -> list[int] | None:
    if selector is None or not selector.strip():
        return None
    cleaned = selector.strip()
    if re.fullmatch(r"\d+", cleaned):
        return [int(cleaned)]
    match = re.fullmatch(r"(\d+)-(\d+)", cleaned)
    if not match:
        raise ValueError("selector must be a number or inclusive start-end range")
    start, end = int(match.group(1)), int(match.group(2))
    if end < start:
        raise ValueError("selector range end must be greater than or equal to start")
    return list(range(start, end + 1))


def split_resolve_args(values: list[str]) -> tuple[str | None, str | None]:
    if len(values) > 2:
        raise ValueError("issue resolve accepts at most repo and selector arguments")
    if not values:
        return None, None
    if len(values) == 1:
        value = values[0]
        if parse_selector(value) is not None:
            return None, value
        return value, None
    target, selector = values
    if parse_selector(target) is not None:
        raise ValueError("when two arguments are provided, the first must be a repo target")
    parse_selector(selector)
    return target, selector


def gh_json(args: list[str]) -> Any:
    result = subprocess.run(["gh", *args], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh command failed")
    return json.loads(result.stdout or "null")


def newest_open_issue(repo: str) -> dict[str, Any]:
    payload = gh_json(
        [
            "search",
            "issues",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "1",
            "--json",
            "number,title,createdAt,url,state",
            "--sort",
            "created",
            "--order",
            "desc",
        ]
    )
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"No open issues found for {repo}")
    issue = payload[0]
    if not isinstance(issue, dict) or "number" not in issue:
        raise RuntimeError("GitHub issue search returned an unexpected payload")
    return issue
