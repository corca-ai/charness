from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_local(module_name: str, alias: str | None = None):
    module_path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(alias or module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BACKEND = _load_local("issue_backend", "issue_read_backend")
_run_backend = _BACKEND.run_backend
_resolve_op = _BACKEND.resolve_op

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
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})


def read_issue_with_comments(repo: str, number: int, *, backend: dict[str, Any] | None = None) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    argv = _resolve_op(
        backend,
        "view",
        GH_READ_DEFAULT,
        VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number", "json_fields"}),
        repo=repo,
        number=str(number),
        json_fields=READ_FIELDS,
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
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "read_argv": argv,
        "comments_read": True,
        "comment_count": len(comments),
        "issue": issue,
    }
