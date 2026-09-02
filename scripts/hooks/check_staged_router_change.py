#!/usr/bin/env python3
"""Refuse a staged change to the repo's first-read instruction router.

The trap this gate closes: ``AGENTS.md`` is the file every session opens first,
and it is the file an agent is most tempted to edit while doing something else --
a rule it wants remembered, a lane note, a worktree policy. Each edit is
individually plausible, none is individually reviewed, and the accumulated result
is the "second operating manual" the router's own second sentence forbids. This
is not hypothetical: the router was edited twice without approval in a single
session, and the only observer was the operator reading a diff afterwards.

The rule this mechanizes already existed in prose and did not hold. Prose asking
an agent to stop is read by the same agent that decided not to.

Scope (the irreducible observables, per the north star's P3 exception): the
root-level router names the agent-host ecosystem actually defines --
``AGENTS.md`` and ``CLAUDE.md`` -- deduplicated by realpath, so this repo's
``CLAUDE.md -> AGENTS.md`` symlink reports as one router rather than two.

Blind class, stated because this repo requires it: this gate sees ONLY those two
root paths in the git index. It does not guard nested ``AGENTS.md`` files, the
host adapters under ``.agents/``, ``docs/``, or any skill contract; it does not
read the DIFF, so a whitespace-only touch refuses exactly like a rewrite; and it
cannot see an edit that is never staged. It is a stop-and-ask boundary, not a
content judgment and not a size ratchet.

Escape (the repo's existing env-var idiom, ``CHARNESS_ALLOW_STAGED_REVERSION`` /
``CHARNESS_ALLOW_PARTIAL_STAGE`` / ``CHARNESS_ALLOW_FOREIGN_HELPER``): pass
``--allow-router-change`` or set ``CHARNESS_ALLOW_ROUTER_CHANGE`` to a truthy
value. The escape exits clean and prints an explicit ``allowed`` line, so an
approved change is acknowledged rather than hidden behind a silent pass. The
escape is the operator's approval taking effect -- an agent that sets it without
having asked has bypassed the boundary, not satisfied it.

If git cannot enumerate the index (not a repository, dubious ownership, missing
git), the gate reports ``unestablished`` and exits non-zero: it never prints a
clean verdict over a scope it could not read.

Portable: pure git plumbing, no host-specific assumption.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from scripts.yaml_output import emit_yaml

try:
    from scripts.core.env_bypass import env_bypass_enabled
except ModuleNotFoundError:
    from env_bypass import env_bypass_enabled

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

_ENV_BYPASS = "CHARNESS_ALLOW_ROUTER_CHANGE"

# The root router names, not a policy list: these are the two filenames the
# Claude Code / Codex ecosystem reads as "the repository's instructions". A
# third name would be a new ecosystem fact, not a new rule.
ROUTER_NAMES = ("AGENTS.md", "CLAUDE.md")


def _staged_paths(repo_root: str) -> list[str]:
    """Repo-relative paths with staged changes, deletions and renames included.

    Raises ``RuntimeError`` when git cannot enumerate the index. An empty list
    from a failed git is indistinguishable from "nothing staged", so returning it
    would render a clean verdict over a scope this gate never read.
    """
    try:
        proc = run_process(
            ["git", "-C", repo_root, "diff", "--cached", "--name-only", "-z"],
            cwd=Path(repo_root),
            timeout_seconds=None,
        )
    except OSError as exc:  # git absent, repo_root unusable as cwd, ...
        raise RuntimeError(f"git diff --cached failed: {exc}") from exc
    if proc.returncode != 0:
        # First stderr line only: git appends a usage dump for some failures,
        # which would bury this gate's own message.
        reason = next((ln for ln in proc.stderr.splitlines() if ln.strip()), "")
        raise RuntimeError(
            reason.strip() or f"git diff --cached --name-only exited {proc.returncode}"
        )
    return [path for path in proc.stdout.split("\0") if path]


def _routers_among(repo_root: str, staged: set[str]) -> list[str]:
    """The staged router paths, collapsed to one entry per distinct router file.

    ``CLAUDE.md`` is a symlink to ``AGENTS.md`` here, so a content edit stages
    only ``AGENTS.md`` -- but a commit that also restages the link would
    otherwise report the same file twice and read as two separate router edits.
    Dedup is by realpath so the count answers "how many routers", not "how many
    index entries". A path staged for DELETION has no realpath to resolve, and is
    kept under its own name: removing the router is at least as much a
    stop-and-ask as editing it.
    """
    found: dict[str, str] = {}
    for name in ROUTER_NAMES:
        if name not in staged:
            continue
        absolute = os.path.join(repo_root, name)
        key = os.path.realpath(absolute) if os.path.lexists(absolute) else name
        found.setdefault(key, name)
    return sorted(found.values())


def staged_router_paths(repo_root: str) -> list[str]:
    """The staged routers, or ``[]`` when the index holds none."""
    return _routers_among(repo_root, set(_staged_paths(repo_root)))


def _bypassed(args: argparse.Namespace) -> bool:
    if getattr(args, "allow_router_change", False):
        return True
    return env_bypass_enabled(_ENV_BYPASS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Refuse a staged change to the first-read instruction router "
            "(AGENTS.md / CLAUDE.md) until the operator has approved it."
        )
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument(
        "--allow-router-change",
        action="store_true",
        help=(
            "Record the operator's approval for this router change and exit clean "
            f"(also honored via the {_ENV_BYPASS} env var)."
        ),
    )
    args = parser.parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)

    if _bypassed(args):
        emit_yaml(
            {
                "state": "allowed",
                "routers": [],
                "detail": (
                    "operator-approved router change (--allow-router-change / "
                    f"{_ENV_BYPASS}); no staged path was inspected"
                ),
            }
        )
        return 0

    try:
        staged = set(_staged_paths(repo_root))
    except RuntimeError as exc:
        emit_yaml(
            {
                "state": "unestablished",
                "routers": [],
                "error": str(exc),
                "detail": (
                    f"git could not read the index at {repo_root!r}, so no staged path "
                    "was inspected and no router verdict was reached."
                ),
                "remediation": (
                    "Fix the repository access (e.g. run from inside the repo, or "
                    "`git config --global --add safe.directory <path>` for a "
                    "dubious-ownership checkout) and re-run."
                ),
            }
        )
        return 1

    # Two different empty answers, kept apart on purpose. An index with nothing
    # staged gave this gate no scope at all -- saying "clean" there would be a
    # positive verdict over zero, the class this repo inventories. An index with
    # staged paths, none of them a router, is the sanctioned DISCOVERED-empty
    # pass: a real answer to a real question, and the case every ordinary commit
    # takes.
    if not staged:
        emit_yaml(
            {
                "state": "clean",
                "routers": [],
                "staged_paths_inspected": 0,
                "detail": (
                    f"nothing was checked: no path is staged at {repo_root!r}, so no "
                    "router verdict was established. A commit cannot reach this state; "
                    "git refuses an empty commit before the hook runs."
                ),
            }
        )
        return 0

    routers = _routers_among(repo_root, staged)
    if not routers:
        emit_yaml(
            {
                "state": "clean",
                "routers": [],
                "staged_paths_inspected": len(staged),
                "detail": (
                    f"inspected {len(staged)} staged path(s); none of them is "
                    f"{' or '.join(ROUTER_NAMES)}"
                ),
            }
        )
        return 0

    emit_yaml(
        {
            "state": "blocked",
            "routers": routers,
            # The whole point of the refusal is that the agent STOPS and ASKS, so
            # the message has to say that in words rather than name a flag and
            # leave "just set it" as the obvious next move.
            "detail": (
                f"this commit changes the first-read instruction router ({', '.join(routers)}). "
                "STOP and ask the operator to approve this change before committing it. "
                "The router routes to the document that owns each question; it is not a "
                "second operating manual, and content that belongs to an owner page "
                "should move there instead."
            ),
            "escape": (
                "Once the operator has approved the change, re-run with "
                f"--allow-router-change or set {_ENV_BYPASS}=1. Setting it without "
                "having asked bypasses the boundary rather than satisfying it."
            ),
        }
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
