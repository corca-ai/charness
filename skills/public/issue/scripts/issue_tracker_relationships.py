"""Real GitHub sub-issue relationship reads and verified mutations."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
BACKEND = _load_local("issue_backend", "issue_tracker_relationships_backend")
JSON_PAGES = _load_local("issue_json_pages", "issue_tracker_relationships_json")
OUTCOME = _load_local("issue_tracker_outcome")
run_backend = BACKEND.run_backend
resolve_op = BACKEND.resolve_op
require_exact_issue_identity = BACKEND.require_exact_issue_identity
_run_json = JSON_PAGES.run_json
_flatten_pages = JSON_PAGES.flatten_pages
unverified_mutation = OUTCOME.unverified_mutation

GH_LIST_SUB_ISSUES_DEFAULT = [
    "api",
    "--paginate",
    "--slurp",
    "repos/{repo}/issues/{number}/sub_issues",
]
GH_RESOLVE_ISSUE_ID_DEFAULT = ["api", "repos/{repo}/issues/{sub_issue_number}"]
GH_ADD_SUB_ISSUE_DEFAULT = [
    "api",
    "--method",
    "POST",
    "repos/{repo}/issues/{number}/sub_issues",
    "-F",
    "sub_issue_id={sub_issue_id}",
]
GH_REMOVE_SUB_ISSUE_DEFAULT = [
    "api",
    "--method",
    "DELETE",
    "repos/{repo}/issues/{number}/sub_issue",
    "-F",
    "sub_issue_id={sub_issue_id}",
]
LIST_SUB_ISSUES_PLACEHOLDERS = frozenset({"repo", "number"})
RESOLVE_ISSUE_ID_PLACEHOLDERS = frozenset({"repo", "sub_issue_number"})
MUTATE_SUB_ISSUE_PLACEHOLDERS = frozenset({"repo", "number", "sub_issue_id", "sub_issue_number"})


_parent_url_matches = _load_local("issue_tracker_discovery", "issue_tracker_relationships_discovery").parent_url_matches


def list_sub_issues(repo: str, number: int, *, backend: dict[str, Any]) -> dict[str, Any]:
    argv = resolve_op(
        backend,
        "list_sub_issues",
        GH_LIST_SUB_ISSUES_DEFAULT,
        LIST_SUB_ISSUES_PLACEHOLDERS,
        required=frozenset({"repo", "number"}),
        repo=repo,
        number=str(number),
    )
    rows = _flatten_pages(_run_json(argv, context="sub-issue readback"))
    children: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise RuntimeError(f"sub-issue readback row {index} is not an object")
        child_number = raw.get("number")
        if type(child_number) is not int or child_number <= 0:
            raise RuntimeError(f"sub-issue readback row {index} has no positive issue number")
        require_exact_issue_identity(
            raw,
            expected_repo=repo,
            expected_number=child_number,
            context=f"sub-issue readback row {index}",
        )
        if not _parent_url_matches(raw.get("parent_issue_url"), repo, number):
            raise RuntimeError(
                f"sub-issue readback row {index} did not prove parent {repo}#{number}"
            )
        if child_number in seen:
            raise RuntimeError(f"sub-issue readback repeated child #{child_number}")
        seen.add(child_number)
        state = raw.get("state")
        children.append(
            {
                "number": child_number,
                "title": raw.get("title"),
                "state": state.upper() if isinstance(state, str) else None,
                "url": raw.get("html_url") or raw.get("url"),
                "parent_issue_url": raw.get("parent_issue_url"),
            }
        )
    completed = sum(child["state"] == "CLOSED" for child in children)
    return {
        "ok": True,
        "status": "verified-read",
        "outcome": "verified-read",
        "mutation_invoked": False,
        "repo": repo,
        "parent_number": number,
        "count": len(children),
        "completed": completed,
        "open": len(children) - completed,
        "percent_completed": round((completed / len(children)) * 100) if children else 0,
        "children": children,
    }


def _resolve_issue_id(repo: str, sub_issue_number: int, backend: dict[str, Any]) -> int:
    argv = resolve_op(
        backend,
        "resolve_issue_id",
        GH_RESOLVE_ISSUE_ID_DEFAULT,
        RESOLVE_ISSUE_ID_PLACEHOLDERS,
        required=frozenset({"repo", "sub_issue_number"}),
        repo=repo,
        sub_issue_number=str(sub_issue_number),
    )
    payload = _run_json(argv, context="sub-issue identity readback")
    require_exact_issue_identity(
        payload,
        expected_repo=repo,
        expected_number=sub_issue_number,
        context="sub-issue identity readback",
    )
    issue_id = payload.get("id") if isinstance(payload, dict) else None
    if type(issue_id) is not int or issue_id <= 0:
        raise RuntimeError("sub-issue identity readback did not return a positive database id")
    return issue_id


def add_sub_issue(
    repo: str, number: int, sub_issue_number: int, *, backend: dict[str, Any]
) -> dict[str, Any]:
    before = list_sub_issues(repo, number, backend=backend)
    if any(child["number"] == sub_issue_number for child in before["children"]):
        return {
            "ok": True,
            "status": "already-linked",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "action": "already-linked",
            "mutation_performed": False,
            "repo": repo,
            "parent_number": number,
            "sub_issue_number": sub_issue_number,
            "readback": before,
        }
    issue_id = _resolve_issue_id(repo, sub_issue_number, backend)
    argv = resolve_op(
        backend,
        "add_sub_issue",
        GH_ADD_SUB_ISSUE_DEFAULT,
        MUTATE_SUB_ISSUE_PLACEHOLDERS,
        required=frozenset({"repo", "number", "sub_issue_id"}),
        repo=repo,
        number=str(number),
        sub_issue_id=str(issue_id),
        sub_issue_number=str(sub_issue_number),
    )
    result = run_backend(argv)
    if result.returncode != 0:
        return unverified_mutation(
            "add-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error=f"provider command failed: {result.stderr.strip()!r}",
            exit_code=result.returncode,
        )
    try:
        after = list_sub_issues(repo, number, backend=backend)
    except RuntimeError as exc:
        return unverified_mutation(
            "add-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error=str(exc),
        )
    if not any(child["number"] == sub_issue_number for child in after["children"]):
        return unverified_mutation(
            "add-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error="provider command succeeded but relationship readback is absent",
        )
    return {
        "ok": True,
        "status": "verified-write",
        "outcome": "verified-write",
        "mutation_invoked": True,
        "action": "linked",
        "mutation_performed": True,
        "repo": repo,
        "parent_number": number,
        "sub_issue_number": sub_issue_number,
        "sub_issue_id": issue_id,
        "readback": after,
    }


def remove_sub_issue(
    repo: str, number: int, sub_issue_number: int, *, backend: dict[str, Any]
) -> dict[str, Any]:
    before = list_sub_issues(repo, number, backend=backend)
    if not any(child["number"] == sub_issue_number for child in before["children"]):
        return {
            "ok": True,
            "status": "already-unlinked",
            "outcome": "verified-read",
            "mutation_invoked": False,
            "action": "already-unlinked",
            "mutation_performed": False,
            "repo": repo,
            "parent_number": number,
            "sub_issue_number": sub_issue_number,
            "readback": before,
        }
    issue_id = _resolve_issue_id(repo, sub_issue_number, backend)
    argv = resolve_op(
        backend,
        "remove_sub_issue",
        GH_REMOVE_SUB_ISSUE_DEFAULT,
        MUTATE_SUB_ISSUE_PLACEHOLDERS,
        required=frozenset({"repo", "number", "sub_issue_id"}),
        repo=repo,
        number=str(number),
        sub_issue_id=str(issue_id),
        sub_issue_number=str(sub_issue_number),
    )
    result = run_backend(argv)
    if result.returncode != 0:
        return unverified_mutation(
            "remove-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error=f"provider command failed: {result.stderr.strip()!r}",
            exit_code=result.returncode,
        )
    try:
        after = list_sub_issues(repo, number, backend=backend)
    except RuntimeError as exc:
        return unverified_mutation(
            "remove-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error=str(exc),
        )
    if any(child["number"] == sub_issue_number for child in after["children"]):
        return unverified_mutation(
            "remove-sub-issue",
            repo=repo,
            parent_number=number,
            sub_issue_number=sub_issue_number,
            before=before,
            error="provider command succeeded but relationship readback remains",
        )
    return {
        "ok": True,
        "status": "verified-write",
        "outcome": "verified-write",
        "mutation_invoked": True,
        "action": "unlinked",
        "mutation_performed": True,
        "repo": repo,
        "parent_number": number,
        "sub_issue_number": sub_issue_number,
        "sub_issue_id": issue_id,
        "readback": after,
    }
