"""Provider-routing layer for the handoff chunker's issue source.

Split out of ``chunked_routing_issue_source.py`` to keep each module under the
repo's single-file length budget (the recent-lessons trap: a slice bundle
silently growing a module past the soft cap). This module owns ONLY provider
access — resolving an issue from the ``issue`` skill backend seam and listing
open issues — with no hardcoded provider literal beyond the ``gh`` default
template. Rendering a template into argv belongs to the ``issue`` skill's backend owner,
which this module delegates to. The shape/union/dedup logic stays in
``chunked_routing_issue_source.py``.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

DEFAULT_ISSUE_LIMIT = 50

# gh default for listing open issues: the only built-in provider literal here; non-gh
# backends declare commands.list_open. The RULE that renders it lives in the issue skill's
# backend owner, so this is data, not a second implementation to keep in sync by hand.
GH_LIST_OPEN_ARGS = [
    "issue", "list", "--repo", "{repo}", "--state", "open",
    "--limit", "{limit}", "--json", "number,title,labels,body",
]

# gh default for reading ONE issue's state. Per-issue rather than a second
# `--state all` listing on purpose: a listing is bounded by {limit} and returns
# the newest issues, so the old closed number a stale backlog line cites is
# exactly the one a listing would miss. Callers ask only about numbers the open
# listing did not already account for, so the call count stays small.
GH_VIEW_STATE_ARGS = [
    "issue", "view", "{number}", "--repo", "{repo}", "--json", "number,state",
]


def _issue_module_candidates(repo_root: Path, name: str) -> list[Path]:
    package_root, installed_first = _package_root(Path(__file__).resolve())
    rels = [
        Path("skills/issue/scripts") / f"{name}.py",
        Path("skills/public/issue/scripts") / f"{name}.py",
    ]
    if not installed_first:
        rels.reverse()
    return [package_root / rel for rel in rels]


def _package_root(script_path: Path) -> tuple[Path, bool]:
    parts = script_path.parts
    for index in range(len(parts) - 3):
        if parts[index:index + 4] == ("skills", "public", "handoff", "scripts"):
            return Path(*parts[:index]), False
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == ("skills", "handoff", "scripts"):
            return Path(*parts[:index]), True
    raise ImportError(f"cannot resolve handoff package root for {script_path}")


def _load_issue_module(repo_root: Path, name: str):
    """Import a module from the ``issue`` skill's scripts dir (route reuse).

    Supports both the source-tree layout (``skills/public/issue``) and the
    installed plugin layout (``skills/issue``). Read/import across skills is
    allowed; only file *mutation* across skills is gated.
    """
    for candidate in _issue_module_candidates(repo_root, name):
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(f"issue_{name}", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(
        f"issue skill script {name}.py not found in source-tree "
        "skills/public/issue/scripts or installed skills/issue/scripts layout"
    )


_ISSUE_BACKEND_OWNER: Any | None = None


def _issue_backend_owner():
    """The `issue` skill's backend owner, loaded once.

    Memoized because `chunked_routing_staleness.resolve_issue_states` calls one state lookup
    per cited issue number, inside a CLI that arms a timeout, and `parse_handoff_entries`
    already carries a comment warning that the skill loaders do not cache. Reading and
    exec'ing the module per issue would put that cost back.
    """
    global _ISSUE_BACKEND_OWNER
    if _ISSUE_BACKEND_OWNER is None:
        _ISSUE_BACKEND_OWNER = _load_issue_module(Path.cwd(), "issue_backend")
    return _ISSUE_BACKEND_OWNER


VIEW_STATE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number"})
LIST_OPEN_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "limit"})


def _resolve_command(
    backend: dict[str, Any] | None, command_key: str, gh_default: list[str], allowed: frozenset[str], **subs: str
) -> tuple[list[str] | None, str]:
    """Build the argv for one backend command, or report why it cannot be built.

    Returns ``(argv, backend_id)``; ``argv`` is None when a non-``gh`` backend declared no
    template for ``command_key``. Callers decide what that means -- listing treats it as a
    configuration error, a state lookup treats it as UNKNOWN -- but neither re-derives the
    binary, template, and substitution rules, which is the part that must stay identical
    across commands.

    Those rules are no longer derived HERE either. This delegates to
    ``issue_backend.try_resolve_op``, the contractual owner of tracker access, through the
    same ``_load_issue_module`` route reuse this module already used for the runner. The copy
    that used to live here shared an expression with ``issue_runtime`` verbatim and neither
    had the owner's placeholder validation; both now do. The None-instead-of-raise answer this
    module needs is the owner's ``try_resolve_op`` entry point rather than a second
    implementation of the shared part.
    """
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    backend_id = backend.get("id", "gh")
    # `required` is deliberately EMPTY, not `allowed`. Equating them would make every
    # placeholder mandatory and invalidate adapter templates that were valid before: a host
    # whose `issue list` pages internally declares no `{limit}`, and one whose binary carries
    # the repo declares no `{repo}`. The allowlist still refuses an UNKNOWN placeholder, which
    # is the validation worth gaining; requiring all of them is a narrowing nobody asked for.
    argv = _issue_backend_owner().try_resolve_op(
        backend, command_key, gh_default, allowed, frozenset(), **subs
    )
    return argv, backend_id


def _default_runner(runner: Callable[[list[str]], Any] | None) -> Callable[[list[str]], Any]:
    if runner is not None:
        return runner
    return _load_issue_module(Path.cwd(), "issue_runtime")._backend_json


def issue_state(
    repo: str,
    number: int,
    *,
    backend: dict[str, Any] | None = None,
    runner: Callable[[list[str]], Any] | None = None,
) -> str | None:
    """Return one issue's state string (e.g. ``OPEN``/``CLOSED``), or None.

    None means UNKNOWN, not open: a provider error, a missing/renumbered issue,
    or a backend that declared no ``commands.view_state`` template. Callers must
    report unknown as unknown — guessing "closed" here would manufacture the very
    stale-verdict this facts-only path refuses to emit.
    """
    # Inside the try, not outside it. Delegating to the owner introduced raising paths this
    # function never had -- an adapter template with an unknown placeholder, or a backend with
    # no usable binary -- and `issue_state`'s callers have no handler anywhere up to an
    # `except`-less `main()`, so one misconfigured adapter key would abort the whole pickup
    # instead of reporting one issue as UNKNOWN. UNKNOWN is what this surface promises and what
    # it must keep promising; guessing OPEN or CLOSED here is the stale verdict it refuses.
    try:
        argv, _ = _resolve_command(
            backend, "view_state", GH_VIEW_STATE_ARGS, VIEW_STATE_PLACEHOLDERS,
            repo=repo, number=str(number),
        )
    except RuntimeError:
        return None
    if argv is None:
        return None
    try:
        payload = _default_runner(runner)(argv)
    except Exception:
        return None
    if isinstance(payload, list):
        payload = payload[0] if payload else None
    if not isinstance(payload, dict):
        return None
    state = payload.get("state")
    return state.strip().upper() if isinstance(state, str) and state.strip() else None


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
    argv, backend_id = _resolve_command(
        backend, "list_open", GH_LIST_OPEN_ARGS, LIST_OPEN_PLACEHOLDERS,
        repo=repo, limit=str(limit),
    )
    if argv is None:
        raise RuntimeError(
            f"issue_backend.id={backend_id} did not declare "
            "commands.list_open; configure the adapter for this host."
        )
    payload = _default_runner(runner)(argv)
    if isinstance(payload, dict):
        if "issues" not in payload or not isinstance(payload["issues"], list):
            raise RuntimeError("issue backend returned an object without list field `issues`")
        payload = payload["issues"]
    if not isinstance(payload, list):
        raise RuntimeError("issue backend returned non-list JSON payload")
    return list(payload)
