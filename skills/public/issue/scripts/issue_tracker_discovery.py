"""Managed Work Item discovery and source-bound expected child sets."""

from __future__ import annotations

import hashlib
import json
import re
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_tracker_discovery_backend")
JSON_PAGES = _load_local("issue_json_pages", "issue_tracker_discovery_json")
resolve_op = BACKEND.resolve_op
require_exact_issue_identity = BACKEND.require_exact_issue_identity
_run_json = JSON_PAGES.run_json
_flatten_pages = JSON_PAGES.flatten_pages

GH_DISCOVER_MANAGED_ISSUES_DEFAULT = [
    "api",
    "--paginate",
    "--slurp",
    "repos/{repo}/issues?state=all&per_page=100",
]
DISCOVER_MANAGED_ISSUES_PLACEHOLDERS = frozenset({"repo"})
WORK_ITEM_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._:/-]{0,127}$")
WORK_ITEM_KEY_PREFIX = "<!-- charness-work-item-key: "


def parent_url_matches(value: Any, repo: str, number: int) -> bool:
    """True when a provider parent URL names exactly this repo and issue number."""
    if not isinstance(value, str):
        return False
    normalized = value.rstrip("/").lower()
    repo_lower = repo.lower()
    return normalized.endswith(f"/repos/{repo_lower}/issues/{number}") or normalized.endswith(
        f"/{repo_lower}/issues/{number}"
    )


def work_item_key_marker(work_item_key: str) -> str:
    if not WORK_ITEM_KEY_RE.fullmatch(work_item_key):
        raise RuntimeError("work item key must match [a-z0-9][a-z0-9._:/-]{0,127}")
    return f"{WORK_ITEM_KEY_PREFIX}{work_item_key} -->"


def load_expected_child_set(path: Path, *, repo: str, parent_number: int) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"expected child set file not found: {path}")
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"expected child set is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("expected child set must be a JSON object")
    allowed = {"kind", "repo", "parent_number", "children", "source"}
    extras = sorted(set(payload) - allowed)
    if extras:
        raise RuntimeError(f"expected child set contains unknown fields: {extras!r}")
    if payload.get("kind") != "charness.expected-sub-issue-set/v1":
        raise RuntimeError("expected child set kind must be charness.expected-sub-issue-set/v1")
    if payload.get("repo") != repo or payload.get("parent_number") != parent_number:
        raise RuntimeError(
            "expected child set target does not match the requested repository and parent"
        )
    children = payload.get("children")
    if not isinstance(children, list) or any(
        type(number) is not int or number <= 0 for number in children
    ):
        raise RuntimeError("expected child set children must be positive issue-number integers")
    if len(children) != len(set(children)):
        raise RuntimeError("expected child set contains duplicate issue numbers")
    return {
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "kind": payload["kind"],
        "repo": repo,
        "parent_number": parent_number,
        "children": sorted(children),
        "source": payload.get("source"),
    }


def discover_managed_issues(
    repo: str,
    work_item_key: str,
    *,
    backend: dict[str, Any],
    parent_number: int | None = None,
) -> dict[str, Any]:
    """Find issues carrying one Work Item marker.

    A Work Item key is scoped to its Goal Run parent, not to the repository:
    consecutive runs legitimately reuse slice names such as ``integrated-closeout``.
    When ``parent_number`` is given, an issue whose provider parent link names a
    DIFFERENT parent is reported under ``foreign_parent`` and never counted as a
    match. An issue with no parent link stays a match, because a child created
    by an interrupted run is unlinked until ``add-child`` runs and must still be
    rediscoverable.
    """
    marker = work_item_key_marker(work_item_key)
    argv = resolve_op(
        backend,
        "discover_managed_issues",
        GH_DISCOVER_MANAGED_ISSUES_DEFAULT,
        DISCOVER_MANAGED_ISSUES_PLACEHOLDERS,
        required=frozenset({"repo"}),
        repo=repo,
    )
    rows = _flatten_pages(_run_json(argv, context="managed issue discovery"))
    matches: list[dict[str, Any]] = []
    foreign_parent: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise RuntimeError(f"managed issue discovery row {index} is not an object")
        if raw.get("pull_request") is not None:
            continue
        body = raw.get("body")
        if not isinstance(body, str) or marker not in body:
            continue
        issue_number = raw.get("number")
        if type(issue_number) is not int or issue_number <= 0:
            raise RuntimeError(f"managed issue discovery row {index} has no positive issue number")
        require_exact_issue_identity(
            raw,
            expected_repo=repo,
            expected_number=issue_number,
            context=f"managed issue discovery row {index}",
        )
        parent_issue_url = raw.get("parent_issue_url")
        match = {
            "number": issue_number,
            "title": raw.get("title"),
            "body": body,
            "state": str(raw.get("state") or "").upper() or None,
            "url": raw.get("html_url") or raw.get("url"),
            "parent_issue_url": parent_issue_url if isinstance(parent_issue_url, str) else None,
        }
        if (
            parent_number is not None
            and match["parent_issue_url"] is not None
            and not parent_url_matches(match["parent_issue_url"], repo, parent_number)
        ):
            foreign_parent.append(match)
            continue
        matches.append(match)
    return {
        "ok": True,
        "status": "verified-read",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "repo": repo,
        "work_item_key": work_item_key,
        "marker": marker,
        "parent_number": parent_number,
        "count": len(matches),
        "matches": matches,
        "foreign_parent": foreign_parent,
    }


def _exact_reusable_match(
    discovery: dict[str, Any], *, title: str, body_text: str
) -> dict[str, Any] | None:
    matches = discovery["matches"]
    if len(matches) != 1:
        return None
    match = matches[0]
    if match["title"] != title or match["body"] != body_text:
        return None
    return match
