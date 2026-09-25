#!/usr/bin/env python3
"""Reprint the active Goal Run pointer after a host compaction (#871).

A host SessionStart hook scoped to `compact`: after compaction the
orchestrator resumes from this pointer (pickup line, ledger path, status
command) instead of memory. Outside the checkout, with no active run, or
for any other session source, it prints nothing and exits 0.

Copied-entry invariant: a copied hook script builds its world with zero
sibling imports, so the marker walk and the state path below are inline
here. `STATE_RELATIVE` mirrors
`scripts.hooks.host_hook_install_lib.HOST_HOOKS_STATE_RELATIVE`; the
active entry is written by
`scripts.hooks.host_hook_goal_reinject_install.record_active_goal_run`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

COMPACT_SOURCE = "compact"
DEFAULT_STATUS_COMMAND = "charness task status"
# Mirrors install_lib.HOST_HOOKS_STATE_RELATIVE (see module docstring).
STATE_RELATIVE = Path(".charness") / "host-hooks" / "state.json"
ACTIVE_KEY = "goal-reinject:active"


def repo_root_for(cwd: str | None) -> Path | None:
    """Enclosing repository of the hook's working directory, else None."""
    if not cwd:
        return None
    try:
        here = Path(cwd).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
    for candidate in (here, *here.parents):
        try:
            if (candidate / ".git").exists() or (candidate / ".agents").is_dir():
                return candidate
        except OSError:
            continue
    return None


def _valid_entry(entry: Any) -> dict[str, Any] | None:
    if not isinstance(entry, Mapping):
        return None
    number = entry.get("number")
    ledger = entry.get("ledger_path")
    status_command = entry.get("status_command", DEFAULT_STATUS_COMMAND)
    if (
        not isinstance(number, int)
        or isinstance(number, bool)
        or number <= 0
        or not isinstance(ledger, str)
        or not ledger.strip()
        or not isinstance(status_command, str)
        or not status_command.strip()
    ):
        return None
    return {
        "number": number,
        "ledger_path": ledger.strip(),
        "status_command": status_command.strip(),
    }


def pointer_for(repo_root: Path) -> str | None:
    """The re-injection pointer for an active Goal Run, else None."""
    try:
        raw = (repo_root / STATE_RELATIVE).read_text(encoding="utf-8")
        state = json.loads(raw)
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    entry = _valid_entry(state.get(ACTIVE_KEY))
    if entry is None:
        return None
    return (
        f"/goal #{entry['number']}\n"
        f"ledger: {entry['ledger_path']}\n"
        f"status: {entry['status_command']}"
    )


def decide(payload: Any) -> tuple[int, str]:
    """Evaluate a SessionStart payload; (exit code, stdout message)."""
    try:
        if not isinstance(payload, Mapping):
            return 0, ""
        if payload.get("source", "compact") != COMPACT_SOURCE:
            return 0, ""
        repo_root = repo_root_for(payload.get("cwd"))
        if repo_root is None:
            return 0, ""
        pointer = pointer_for(repo_root)
        return 0, pointer or ""
    except Exception:  # noqa: BLE001 - a pointer hook never breaks startup
        return 0, ""


def main(argv: list[str] | None = None) -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else None
    except (OSError, ValueError):
        return 0
    code, message = decide(payload)
    if message:
        print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
