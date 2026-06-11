"""agent-browser session I/O and post-close runtime-clean proof for web-fetch.

Split out of ``acquire_public_url.py`` so the acquire helper stays under the
skill-helper length gate and so the session/cleanup logic is independently
testable. Owns the ephemeral ``charness-gather-*`` session name, the render and
network recon calls, locating the runtime guard, and asserting the runtime is
clean after close.

The runtime guard ships at ``<repo>/scripts/agent_browser_runtime_guard.py`` in
the repo-root layout and at ``plugins/charness/scripts/...`` in the exported
plugin layout; the acquire helper sits at ``skills/support/web-fetch/scripts``
(repo-root) or ``plugins/charness/support/web-fetch/scripts`` (export), so a
single relative offset does not reach the guard in both. We therefore search the
caller's ``repo_root/scripts`` first, then every ancestor of the acquire script
for a ``scripts/agent_browser_runtime_guard.py`` sibling. When the guard cannot
be found anywhere, callers surface a fail-visible ``guard_unavailable`` signal
rather than reporting an unrun proof as a clean close.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Callable

GUARD_FILENAME = "agent_browser_runtime_guard.py"
GUARD_UNAVAILABLE = (
    "guard_unavailable:agent_browser_runtime_guard.py not reachable from repo_root/scripts "
    "or any bundled support layout; post-close runtime proof was not run"
)

RunCommand = Callable[..., tuple[str, str | None]]


def session_name(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"charness-gather-{digest}"


def run_browser_text(url: str, *, timeout: int, run_command: RunCommand) -> tuple[str, str | None, dict[str, object]]:
    session = session_name(url)
    details: dict[str, object] = {"session": session}
    for command in (
        ["agent-browser", "--session", session, "open", url],
        ["agent-browser", "--session", session, "wait", "1000"],
    ):
        _stdout, error = run_command(command, timeout=timeout)
        if error:
            return "", error, details
    text, error = run_command(["agent-browser", "--session", session, "get", "text", "body"], timeout=timeout)
    if error:
        return text, error, details
    return text, None, details


def run_browser_network(url: str, *, timeout: int, run_command: RunCommand) -> tuple[str, str | None, dict[str, object]]:
    session = session_name(url)
    requests_text, requests_error = run_command(
        ["agent-browser", "--session", session, "network", "requests", "--filter", "api|graphql|json"],
        timeout=timeout,
    )
    candidates = [line.strip() for line in requests_text.splitlines() if line.strip()][:20]
    details: dict[str, object] = {"session": session, "network_candidates": candidates}
    return requests_text, requests_error, details


def close_session(url: str, *, timeout: int, run_command: RunCommand) -> str | None:
    _stdout, error = run_command(["agent-browser", "--session", session_name(url), "close"], timeout=timeout)
    return error


def resolve_runtime_guard(script_dir: Path, repo_root: Path) -> Path | None:
    """Return the first reachable runtime-guard path, or None if none exists."""
    candidates = [repo_root / "scripts" / GUARD_FILENAME]
    candidates.extend(ancestor / "scripts" / GUARD_FILENAME for ancestor in script_dir.parents)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file():
            return candidate
    return None


def assert_runtime_clean(script_dir: Path, repo_root: Path, *, timeout: int, run_command: RunCommand) -> str | None:
    """Run the runtime guard; return an error/`guard_unavailable` string, else None.

    A missing guard is reported as ``guard_unavailable`` (fail-visible) instead of
    None, so exported/installed surfaces never read an unrun proof as clean.
    """
    guard = resolve_runtime_guard(script_dir, repo_root)
    if guard is None:
        return GUARD_UNAVAILABLE
    command = [sys.executable, str(guard), "--repo-root", str(repo_root), "--assert-no-orphans"]
    return run_command(command, timeout=timeout)[1]


def cleanup_orphans(script_dir: Path, repo_root: Path, *, timeout: int, run_command: RunCommand) -> str | None:
    guard = resolve_runtime_guard(script_dir, repo_root)
    if guard is None:
        return GUARD_UNAVAILABLE
    command = [sys.executable, str(guard), "--repo-root", str(repo_root), "--cleanup-orphans", "--execute"]
    return run_command(command, timeout=timeout)[1]
