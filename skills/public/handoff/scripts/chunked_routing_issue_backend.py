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


# Why the most recent state resolution could not be built. Swallowing the owner's precise
# message left a broken `view_state` template indistinguishable from an unauthenticated
# tracker, forever. Read by the staleness layer's diagnostic, mirroring
# LAST_ISSUE_SOURCE_DIAGNOSTIC on the listing half.
LAST_STATE_RESOLUTION_DIAGNOSTIC: str | None = None

_MEMOIZED_ISSUE_MODULES: dict[str, Any] = {}


def _memoized_issue_module(name: str):
    """Load an `issue` skill module once per process, by name."""
    if name not in _MEMOIZED_ISSUE_MODULES:
        _MEMOIZED_ISSUE_MODULES[name] = _load_issue_module(Path.cwd(), name)
    return _MEMOIZED_ISSUE_MODULES[name]


def _issue_backend_owner():
    """The `issue` skill's backend owner, loaded once.

    Memoized because `chunked_routing_staleness.resolve_issue_states` calls one state lookup
    per cited issue number, inside a CLI that arms a timeout, and `parse_handoff_entries`
    already carries a comment warning that the skill loaders do not cache. Reading and
    exec'ing the module per issue would put that cost back.

    A first version memoized only this loader while `_default_runner` still exec'd
    `issue_runtime` per call on the same path, so the docstring claimed a broader cost fix than
    shipped. Both are memoized now, by the same helper.
    """
    return _memoized_issue_module("issue_backend")


VIEW_STATE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number"})
LIST_OPEN_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "limit"})
# Which placeholders a template MUST spell, chosen per op rather than set to all-or-nothing.
# All-of-them invalidated adapter templates that were valid before (a host whose binary
# carries the repo declares no `{repo}`; one that pages internally declares no `{limit}`).
# NONE of them was worse: `{number}` is IDENTITY-bearing, and a `view_state` template that
# omits it resolves to a listing, whose first row is then read as the state of whichever issue
# was asked about -- reporting a live backlog citation as CLOSED, silently, with
# `issue_states_checked: true`. That is the manufactured stale verdict this module exists to
# refuse, so it is a loud error instead.
VIEW_STATE_REQUIRED: frozenset[str] = frozenset({"number"})
LIST_OPEN_REQUIRED: frozenset[str] = frozenset()


def _resolve_command(
    backend: dict[str, Any] | None,
    command_key: str,
    gh_default: list[str],
    allowed: frozenset[str],
    required: frozenset[str],
    **subs: str,
) -> tuple[list[str] | None, str]:
    """Build the argv for one backend command, or report why it cannot be built.

    Returns ``(argv, backend_id)``; ``argv`` is None when a non-``gh`` backend declared no
    template for ``command_key``. RAISES for an adapter or caller error — an unknown or
    missing-required placeholder, or no usable binary — because those are configuration bugs
    rather than absences. ``list_open_issues`` lets them propagate to its own diagnostic;
    ``issue_state`` catches them, because its contract is UNKNOWN and its callers have no
    handler. Callers decide what that means -- listing treats it as a
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
    # `required` is chosen PER OP by the caller, and both extremes were wrong. Equating it with
    # `allowed` invalidated adapter templates that were valid before (a host paging internally
    # declares no `{limit}`); setting it to nothing let a `view_state` template omit the
    # identity-bearing `{number}` and resolve to a listing, whose first row was then read as the
    # asked-about issue's state. See VIEW_STATE_REQUIRED / LIST_OPEN_REQUIRED above for what each
    # op requires and why. The allowlist always refuses an UNKNOWN placeholder.
    argv = _issue_backend_owner().try_resolve_op(
        backend, command_key, gh_default, allowed, required, **subs
    )
    return argv, backend_id


def _default_runner(runner: Callable[[list[str]], Any] | None) -> Callable[[list[str]], Any]:
    if runner is not None:
        return runner
    return _memoized_issue_module("issue_runtime")._backend_json


def issue_state(
    repo: str,
    number: int,
    *,
    backend: dict[str, Any] | None = None,
    runner: Callable[[list[str]], Any] | None = None,
) -> str | None:
    """Return one issue's state string (e.g. ``OPEN``/``CLOSED``), or None.

    None means UNKNOWN, not open: a provider error, a missing/renumbered issue, a backend
    that declared no ``commands.view_state`` template, an adapter template this backend
    cannot render, a payload naming a different issue than the one asked about, or the
    ``issue`` skill's backend module being absent from the install. Callers must report
    unknown as unknown — guessing "closed" here would manufacture the very stale-verdict this
    facts-only path refuses to emit. ``LAST_STATE_RESOLUTION_DIAGNOSTIC`` carries the reason
    for the resolution failures, because "template is broken" and "tracker is unreachable"
    are different problems and read identically once the message is dropped.
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
            VIEW_STATE_REQUIRED, repo=repo, number=str(number),
        )
    except Exception as exc:  # noqa: BLE001 - see LAST_STATE_RESOLUTION_DIAGNOSTIC below
        # `except Exception`, not `except RuntimeError`. A first version of this guard named
        # only the owner's own refusals and a bounded round found two escapes it did not
        # cover: `_load_issue_module` raises ImportError on a partially-synced install (a
        # shape this very slice created, since handoff now needs `issue_backend.py` present),
        # and the owner's `part.format(...)` raises KeyError/ValueError for an adapter template
        # containing a brace that is not a placeholder -- a jq reshape, which this repo's own
        # backend reference documents. Both aborted the whole pickup. Matching the breadth of
        # the runner guard three lines below is the point: this function's contract is UNKNOWN.
        global LAST_STATE_RESOLUTION_DIAGNOSTIC
        LAST_STATE_RESOLUTION_DIAGNOSTIC = f"{type(exc).__name__}: {exc}"
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
    # If the payload says WHICH issue it describes, it must be the one asked about. Requiring
    # `{number}` in the template is the primary guard; this is the second, because a template
    # can still resolve to a listing whose first row is a different issue, and reporting that
    # row's state here is how a live citation becomes a CLOSED verdict.
    reported = payload.get("number")
    if isinstance(reported, int) and reported != number:
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
        LIST_OPEN_REQUIRED, repo=repo, limit=str(limit),
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
