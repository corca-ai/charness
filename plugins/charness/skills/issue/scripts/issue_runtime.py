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
GIT_TIMEOUT_SECONDS = 10
BACKEND_TIMEOUT_SECONDS = 60


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
        timeout=GIT_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def parse_target(value: str, default_org: str, *, source_prefix: str) -> tuple[str, str, str]:
    cleaned = value.strip().removeprefix("https://github.com/").removeprefix("http://github.com/")
    cleaned = cleaned[:-4] if cleaned.endswith(".git") else cleaned
    parts = [part for part in cleaned.split("/") if part]
    if len(parts) == 1:
        return default_org, parts[0], f"{source_prefix}-default-org"
    if len(parts) == 2:
        owner, repo = parts
        return owner, repo, source_prefix
    raise ValueError("target must be empty, repo, or org/repo")


def resolve_target(repo_root: Path, target: str | None, adapter_data: dict[str, Any]) -> dict[str, Any]:
    default_org = str(adapter_data["default_org"])
    remote_name = str(adapter_data["remote_name"])
    if target and target.strip():
        owner, repo, source = parse_target(target, default_org, source_prefix="argument")
    else:
        remote_url = git_remote_url(repo_root, remote_name)
        parsed = parse_remote_url(remote_url) if remote_url else None
        if parsed is not None:
            owner, repo = parsed
            source = f"git-remote:{remote_name}"
        elif adapter_data.get("default_repo"):
            owner, repo, source = parse_target(
                str(adapter_data["default_repo"]),
                default_org,
                source_prefix="adapter-default-repo",
            )
        else:
            owner, repo = default_org, repo_root.name
            source = "cwd-default-org"
    return {"owner": owner, "repo": repo, "full_name": f"{owner}/{repo}", "source": source}


def parse_selector(selector: str | None) -> list[int] | None:
    if selector is None or not selector.strip():
        return None
    cleaned = selector.strip()
    if re.fullmatch(r"\d+", cleaned):
        number = int(cleaned)
        if number < 1:
            raise ValueError("selector issue number must be a positive integer")
        return [number]
    match = re.fullmatch(r"(\d+)-(\d+)", cleaned)
    if not match:
        raise ValueError("selector must be a number or inclusive start-end range")
    start, end = int(match.group(1)), int(match.group(2))
    if start < 1:
        raise ValueError("selector range start must be a positive integer")
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
        if is_selector(value):
            return None, value
        return value, None
    target, selector = values
    if is_selector(target):
        raise ValueError("when two arguments are provided, the first must be a repo target")
    parse_selector(selector)
    return target, selector


def is_selector(value: str) -> bool:
    try:
        return parse_selector(value) is not None
    except ValueError:
        return False


def _backend_json(argv: list[str]) -> Any:
    try:
        result = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{argv[0]} command timed out after {BACKEND_TIMEOUT_SECONDS}s") from exc
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{argv[0]} command failed")
    return json.loads(result.stdout or "null")


GH_NEWEST_OPEN_ARGS = [
    "search", "issues", "--repo", "{repo}", "--state", "open", "--limit", "1",
    "--json", "number,title,createdAt,url,state", "--sort", "created", "--order", "desc",
]


def newest_open_issue(repo: str, backend: dict[str, Any] | None = None) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    binary = backend.get("binary") or backend.get("id") or "gh"
    commands = backend.get("commands") or {}
    template = commands.get("search_newest_open")
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"issue_backend.id={backend.get('id')} did not declare commands.search_newest_open; "
                "configure the adapter or pass an explicit selector."
            )
        template = GH_NEWEST_OPEN_ARGS
    argv = [binary] + [part.replace("{repo}", repo) for part in template]
    payload = _backend_json(argv)
    if isinstance(payload, dict) and "issues" in payload:
        payload = payload.get("issues")
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"No open issues found for {repo}")
    issue = payload[0]
    if not isinstance(issue, dict) or "number" not in issue:
        raise RuntimeError("issue search returned an unexpected payload")
    return issue
