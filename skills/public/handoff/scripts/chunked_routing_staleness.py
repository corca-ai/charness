"""Resolvable-ness facts for chunked-routing backlog entries.

A backlog entry is planned against long after it was written. Its cited paths
may have moved and its cited issues may have been closed, and nothing in the
pipeline used to say so — staleness surfaced only when a reviewer or the agent
happened to open the cited file, i.e. *after* a slice plan existed.

This module answers two narrow, checkable questions per entry:

- which ``referenced_paths`` no longer exist under the repo root, and
- which ``referenced_issues`` the tracker reports as not-open.

Boundaries it keeps:

- **Facts only, never a verdict.** Nothing here drops, deprioritizes, or
  rewrites an entry. An entry whose paths moved may still be real work; that
  judgment stays with the agent reading the packet.
- **Unknown is not stale.** A tracker that cannot be reached, a backend with no
  state command, or a number the provider does not recognize yields UNKNOWN, and
  unknown numbers are never reported as closed.
- **No line-level claims.** Whether a cited ``file:line`` still points at the
  same code is judgment, not a check; only existence is tested.
- **No new provider literal.** Issue state routes through the same backend seam
  as the open-issue listing.
"""
from __future__ import annotations

import importlib.util
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside chunked_routing_staleness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_backend = _load_sibling("chunked_routing_issue_backend")


def missing_paths(repo_root: Path | None, referenced_paths: Sequence[str]) -> tuple[str, ...]:
    """Cited paths that do not resolve under ``repo_root``, in citation order.

    Directories count as existing: a backlog line legitimately names a surface
    (``skills/public/handoff/``) rather than a file. A path that escapes the repo
    root is ignored rather than reported — the chunker has no basis to call an
    out-of-tree reference stale, and reporting one would be a false positive on
    every entry citing an upstream URL fragment normalized into path shape.
    """
    if repo_root is None:
        return ()
    root = repo_root.resolve()
    missing: list[str] = []
    for referenced in referenced_paths:
        try:
            candidate = (root / referenced).resolve()
            if root != candidate and root not in candidate.parents:
                continue
            exists = candidate.exists()
        except (RuntimeError, OSError, ValueError):
            # A symlink loop or an unrepresentable name is UNKNOWN, not missing:
            # resolving it is our failure, and reporting it as a stale citation
            # would be a verdict we cannot support.
            continue
        if not exists:
            missing.append(referenced)
    return tuple(missing)


def resolve_issue_states(
    repo: str,
    numbers: Iterable[int],
    *,
    known_open: Iterable[int] = (),
    backend: dict[str, Any] | None = None,
    runner: Callable[[list[str]], Any] | None = None,
) -> dict[int, str]:
    """Map each cited issue number to a state string, reusing known-open ones.

    ``known_open`` is the set already proven open by the open-issue listing this
    run performed, so those cost nothing; the caller must pass it explicitly.
    Only the remainder — the suspected-stale set — costs one provider call each.
    Unresolvable numbers map to ``"UNKNOWN"``.
    """
    open_set = set(known_open)
    states: dict[int, str] = {}
    for number in dict.fromkeys(numbers):
        if number in open_set:
            states[number] = "OPEN"
            continue
        state = _backend.issue_state(repo, number, backend=backend, runner=runner)
        states[number] = state or "UNKNOWN"
    return states


# Closed is an ALLOW-LIST, not "anything that is not OPEN". Trackers disagree
# about their open vocabulary -- GitLab says `opened`, Linear says `started` /
# `unstarted` / `backlog`, Jira says `In Progress` -- and treating an unrecognized
# state as closed would report a live issue as stale, which is the one verdict
# this facts-only path must never manufacture. An unrecognized state is UNKNOWN.
CLOSED_STATES = frozenset({"CLOSED", "COMPLETED", "DONE", "MERGED", "RESOLVED"})


def closed_issues(referenced_issues: Sequence[int], states: dict[int, str]) -> tuple[int, ...]:
    """Cited issues the tracker positively reports as closed."""
    return tuple(
        number for number in referenced_issues if states.get(number, "UNKNOWN") in CLOSED_STATES
    )


def unresolved_issues(referenced_issues: Sequence[int], states: dict[int, str] | None) -> tuple[int, ...]:
    """Cited issues whose state the tracker did not answer for, when it was asked.

    Reported per entry, not only as a global ratio: a reader inspecting ONE
    backlog line cannot consult a run-level count, and an entry whose issues all
    failed to resolve otherwise renders exactly like an entry whose issues are
    all open.
    """
    if states is None:
        return ()
    return tuple(number for number in referenced_issues if states.get(number, "UNKNOWN") == "UNKNOWN")


def annotate_entries(
    entries: Sequence[Any],
    *,
    repo_root: Path | None,
    issue_states: dict[int, str] | None = None,
) -> list[Any]:
    """Return entries with ``missing_paths`` / ``closed_issues`` filled in.

    ``issue_states`` of None means the issue check did not run (offline pickup);
    entries keep an empty ``closed_issues``, which the caller reports as
    not-checked rather than as "nothing is stale".
    """
    states = issue_states or {}
    return [
        replace(
            entry,
            missing_paths=missing_paths(repo_root, entry.referenced_paths),
            closed_issues=closed_issues(entry.referenced_issues, states),
            unresolved_issues=unresolved_issues(entry.referenced_issues, issue_states),
        )
        for entry in entries
    ]


def staleness_summary(
    entries: Sequence[Any],
    *,
    paths_checked: bool,
    issue_states_checked: bool,
    diagnostic: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Top-level report of what was checked and how much did not resolve.

    ``*_checked`` is reported separately from the counts on purpose: zero
    missing paths and "paths were never checked" are the same empty tuples on
    the entries, and a reader who cannot tell them apart draws the more
    comfortable conclusion.
    """
    return {
        "paths_checked": paths_checked,
        "issue_states_checked": issue_states_checked,
        "entries_with_missing_paths": sum(1 for entry in entries if entry.missing_paths),
        "entries_with_closed_issues": sum(1 for entry in entries if entry.closed_issues),
        "missing_path_count": sum(len(entry.missing_paths) for entry in entries),
        "closed_issue_count": sum(len(entry.closed_issues) for entry in entries),
        # A run where 19 of 20 lookups failed and one came back CLOSED would
        # otherwise report `issue_states_checked: true, closed_issue_count: 1`
        # and read as a clean check. The unresolved count is what makes a
        # PARTIAL check legible as partial.
        "unresolved_issue_count": sum(len(entry.unresolved_issues) for entry in entries),
        "diagnostic": diagnostic,
    }


def resolve_states_for_repo(
    repo_root: Path,
    numbers: list[int],
    *,
    known_open: tuple[int, ...] = (),
    runner: Callable[[list[str]], Any] | None = None,
) -> tuple[dict[int, str], dict[str, Any] | None]:
    """Resolve cited issue numbers to states through the same backend seam.

    Returns ``(states, diagnostic)``. On any resolution failure the states map is
    empty and the diagnostic says why — the caller then reports the issue check
    as NOT RUN rather than reporting nothing-is-closed, because those two must
    never look alike to a reader deciding whether to trust a backlog line.
    """
    if not numbers:
        return {}, None
    source = _load_sibling("chunked_routing_issue_source")
    config = source.load_issue_source_config(repo_root)
    if not config["enabled"]:
        return {}, {"stage": "issue_source_disabled", "provider_attempted": False}
    stage = "load_issue_modules"
    try:
        issue_resolver = _backend._load_issue_module(repo_root, "resolve_adapter")
        issue_runtime = _backend._load_issue_module(repo_root, "issue_runtime")
        stage = "load_issue_adapter"
        adapter_data = issue_resolver.load_adapter(repo_root).get("data", {})
        backend = adapter_data.get("issue_backend") or {"id": "gh", "binary": "gh", "commands": None}
        stage = "resolve_target"
        repo_full = issue_runtime.resolve_target(repo_root, config["repo"], adapter_data)["full_name"]
        run = runner if runner is not None else issue_runtime._backend_json
    except Exception as exc:
        return {}, {
            "stage": stage,
            "provider_attempted": False,
            "type": type(exc).__name__,
            "message": str(exc),
        }
    # `known_open` is passed IN, never read back off the issue-source module: the
    # skill loaders build a fresh module object per import, so the instance this
    # function would reach is not the one the listing mutated, and the reuse
    # would silently be dead -- turning a free lookup into one provider call per
    # cited issue.
    open_set = set(known_open)
    states = resolve_issue_states(
        repo_full,
        numbers,
        known_open=open_set,
        backend=backend,
        runner=run,
    )
    # A provider that is reachable-looking but answers nothing (no auth, wrong
    # repo, offline) resolves EVERY looked-up number to UNKNOWN. Returning that
    # as a successful check would render as "checked, nothing closed" — the one
    # reading this whole path exists to prevent. Report it as not-run instead.
    looked_up = [number for number in states if number not in open_set]
    if looked_up and all(states[number] == "UNKNOWN" for number in looked_up):
        return {}, {
            "stage": "issue_state_lookup",
            "provider_attempted": True,
            "message": f"no state resolved for any of {len(looked_up)} cited issue(s)",
        }
    return states, None
