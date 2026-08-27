from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BACKEND = _load_local("issue_backend", "issue_read_backend")
_run_backend = _BACKEND.run_backend
_resolve_op = _BACKEND.resolve_op
_require_exact_issue_identity = _BACKEND.require_exact_issue_identity

GH_READ_DEFAULT = [
    "issue",
    "view",
    "--repo",
    "{repo}",
    "{number}",
    "--comments",
    "--json",
    "{json_fields}",
]

READ_FIELDS = "number,title,body,comments,labels,state,url,author,createdAt,updatedAt"
GOAL_RUN_READ_FIELDS = f"{READ_FIELDS},subIssuesSummary"
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})


def normalise_sub_issues_summary(issue: dict[str, Any]) -> dict[str, int] | None:
    """Return the optional provider count without treating it as the cursor."""
    raw = issue.get("subIssuesSummary")
    if not isinstance(raw, dict):
        return None
    total = raw.get("total")
    completed = raw.get("completed")
    percent = raw.get("percentCompleted")
    if type(total) is not int or total < 0 or type(completed) is not int or completed < 0:
        return None
    if completed > total:
        return None
    summary = {"total": total, "completed": completed, "open": total - completed}
    if type(percent) is int and 0 <= percent <= 100:
        summary["percent_completed"] = percent
    return summary


def read_issue_with_comments(
    repo: str,
    number: int,
    *,
    backend: dict[str, Any] | None = None,
    include_sub_issues_summary: bool = False,
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    # The extra field is a cheap native GitHub read, but is not part of the
    # generic issue-reader contract.  Keep custom/host-mediated adapters
    # compatible until they explicitly expose an equivalent field.
    json_fields = (
        GOAL_RUN_READ_FIELDS
        if include_sub_issues_summary and backend.get("id", "gh") == "gh" and not backend.get("commands")
        else READ_FIELDS
    )
    argv = _resolve_op(
        backend,
        "view",
        GH_READ_DEFAULT,
        VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number", "json_fields"}),
        repo=repo,
        number=str(number),
        json_fields=json_fields,
    )
    result = _run_backend(argv)
    if result.returncode != 0:
        raise RuntimeError(f"issue read failed: exit={result.returncode} stderr={result.stderr.strip()!r}")
    try:
        issue = json.loads(result.stdout)
    except Exception as exc:
        raise RuntimeError(f"issue read returned invalid JSON: {exc}") from exc
    comments = issue.get("comments") if isinstance(issue, dict) else None
    if not isinstance(comments, list):
        raise RuntimeError("issue read did not return a comments list; retry with comments included")
    _require_exact_issue_identity(
        issue,
        expected_repo=repo,
        expected_number=number,
        context="issue read",
    )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "read_argv": argv,
        "comments_read": True,
        "comment_count": len(comments),
        "issue": issue,
    }
