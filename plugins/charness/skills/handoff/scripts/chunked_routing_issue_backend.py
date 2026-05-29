"""#249 provider-routing layer for the handoff chunker's issue source.

Split out of ``chunked_routing_issue_source.py`` to keep each module under the
repo's single-file length budget (the recent-lessons trap: a slice bundle
silently growing a module past the soft cap). This module owns ONLY provider
access — resolving an issue from the ``issue`` skill backend seam and listing
open issues — with no hardcoded provider literal beyond the ``gh`` default
template (mirroring ``issue_runtime``). The shape/union/dedup logic stays in
``chunked_routing_issue_source.py``.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

DEFAULT_ISSUE_LIMIT = 50

# gh default for listing open issues. Mirrors issue_runtime.GH_NEWEST_OPEN_ARGS:
# the only built-in provider literal; non-gh backends declare commands.list_open.
GH_LIST_OPEN_ARGS = [
    "issue", "list", "--repo", "{repo}", "--state", "open",
    "--limit", "{limit}", "--json", "number,title,labels,body",
]


def _load_issue_module(repo_root: Path, name: str):
    """Import a module from the ``issue`` skill's scripts dir (route reuse).

    Walks up to ``skills/public/issue/scripts/<name>.py``. Read/import across
    skills is allowed (the same pattern draft_goal_from_chunk uses to import
    the achieve goal-artifact lib); only file *mutation* across skills is gated.
    """
    here = Path(__file__).resolve()
    roots = [repo_root, *here.parents]
    for ancestor in roots:
        candidate = ancestor / "skills" / "public" / "issue" / "scripts" / f"{name}.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(f"issue_{name}", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"skills/public/issue/scripts/{name}.py not found")


def list_open_issues(
    repo: str,
    *,
    backend: dict[str, Any] | None = None,
    limit: int = DEFAULT_ISSUE_LIMIT,
    runner: Callable[[list[str]], Any] | None = None,
) -> list[dict[str, Any]]:
    """List open issues for ``repo`` via the resolved backend.

    ``runner`` (argv -> parsed JSON) defaults to issue_runtime._backend_json;
    tests inject a stub so no live provider call is made.
    """
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    binary = backend.get("binary") or backend.get("id") or "gh"
    commands = backend.get("commands") or {}
    template = commands.get("list_open")
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"issue_backend.id={backend.get('id')} did not declare "
                "commands.list_open; configure the adapter for this host."
            )
        template = GH_LIST_OPEN_ARGS
    argv = [binary] + [
        part.replace("{repo}", repo).replace("{limit}", str(limit))
        for part in template
    ]
    if runner is None:
        issue_runtime = _load_issue_module(Path.cwd(), "issue_runtime")
        runner = issue_runtime._backend_json
    payload = runner(argv)
    if isinstance(payload, dict) and "issues" in payload:
        payload = payload.get("issues")
    return list(payload) if isinstance(payload, list) else []
