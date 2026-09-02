from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts_dir = next(
        ancestor / "scripts"
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_scripts_dir) not in sys.path:
        sys.path.insert(0, str(_scripts_dir.parent))
    from scripts.core.subprocess_guard import run_process

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
_resolve_op = _load_local("issue_backend", "issue_runtime_backend").resolve_op

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
    result = run_process(
        ["git", "config", "--get", f"remote.{remote_name}.url"],
        cwd=repo_root,
        timeout_seconds=GIT_TIMEOUT_SECONDS,
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


def resolve_target(
    repo_root: Path, target: str | None, adapter_data: dict[str, Any]
) -> dict[str, Any]:
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
    result = run_process(argv, cwd=Path.cwd(), timeout_seconds=BACKEND_TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or result.stdout.strip() or f"{argv[0]} command failed"
        )
    return json.loads(result.stdout or "null")


GH_NEWEST_OPEN_ARGS = [
    "search",
    "issues",
    "--repo",
    "{repo}",
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


NEWEST_OPEN_PLACEHOLDERS: frozenset[str] = frozenset({"repo"})


def newest_open_issue(repo: str, backend: dict[str, Any] | None = None) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    # This used to re-derive the binary, the built-in `gh` default, the template
    # lookup, and the substitution itself -- the same rule `issue_backend.resolve_op` already
    # owned, in the SAME skill, minus its placeholder validation. Delegating gains that
    # validation: an adapter can no longer smuggle an unknown placeholder into this op.
    argv = _resolve_op(
        backend,
        "search_newest_open",
        GH_NEWEST_OPEN_ARGS,
        NEWEST_OPEN_PLACEHOLDERS,
        # `{repo}` is REQUIRED here, unlike handoff's `list_open`, and the difference is
        # deliberate: this op searches, and a search template that omits the repo returns
        # another repository's newest issue, which the caller then acts on as if it were this
        # one. A missing page size is a benign omission; a missing scope is a wrong answer.
        required=frozenset({"repo"}),
        repo=repo,
    )
    payload = _backend_json(argv)
    if isinstance(payload, dict) and "issues" in payload:
        payload = payload.get("issues")
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"No open issues found for {repo}")
    issue = payload[0]
    if not isinstance(issue, dict) or "number" not in issue:
        raise RuntimeError("issue search returned an unexpected payload")
    return issue
