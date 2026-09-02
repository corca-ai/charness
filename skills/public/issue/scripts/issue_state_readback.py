#!/usr/bin/env python3
"""Reading an issue's live state from the backend, for closeout verification.

Split out of `issue_verify_closeout` on a real seam: that file decides whether a
closeout is honest, and this one only fetches the fact it decides against. Two
consumers now need it -- the expected-state readback and the consolidation
destination readback -- and the verifier was at its length ceiling, which is the
wrong thing for a proof surface to be spending on a subprocess wrapper.

Every failure here RAISES rather than returning a degraded payload. A state read that
did not happen must never be indistinguishable from a state read that came back
clean; the callers turn the raise into a typed refusal.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.core import subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:
    _scripts_dir = next(
        (
            ancestor / "scripts"
            for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
            if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
        ),
        None,
    )
    if _scripts_dir is None:
        raise
    sys.path.insert(0, str(_scripts_dir.parent))
    import scripts.core.subprocess_guard as _subprocess_guard
    from scripts.core.subprocess_guard import run_process

subprocess = _subprocess_guard.subprocess

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
_ISSUE_CLOSE = None


def _issue_close():
    """The op templates and timeout, loaded LAZILY.

    At module scope this was a cycle: `issue_close` now performs a destination
    readback before it mutates GitHub, so it imports this module, which imported it
    back. Deferring to first call breaks the cycle without moving constants that
    belong with the close ops.
    """
    global _ISSUE_CLOSE
    if _ISSUE_CLOSE is None:
        _ISSUE_CLOSE = _load_local("issue_close", "issue_state_readback_issue_close")
    return _ISSUE_CLOSE


def view_issue_state(
    repo_root: Path,
    *,
    repo: str,
    number: int,
    backend: dict[str, Any],
    json_fields: str = "number,state,url",
) -> dict[str, Any]:
    commands = backend.get("commands") or {}
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "closeout state verification requires backend commands.view; "
            "carrier text alone is not issue closeout"
        )
    argv = _issue_close()._resolve_op(
        backend,
        "view",
        _issue_close().GH_VIEW_DEFAULT,
        _issue_close().VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number"}),
        repo=repo,
        number=str(number),
        json_fields=json_fields,
    )
    try:
        result = run_process(
            argv, cwd=repo_root, timeout_seconds=_issue_close().BACKEND_TIMEOUT_SECONDS
        )
    except OSError as exc:
        raise RuntimeError(f"issue state verification command failed to start: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(
            f"issue state verification failed for {repo}#{number}: "
            f"exit={result.returncode} stderr={result.stderr.strip()!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        raise RuntimeError(f"issue state verification returned invalid JSON: {exc}") from exc
    return payload
