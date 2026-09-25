#!/usr/bin/env python3
"""Claude PreToolUse(Bash) entry for the discard-worktree guard.

Thin entry: the rule tables and verdict live in
`scripts/hooks/host_hook_command_guards.py` (shared with the hook runner
`scripts/host_command_guard_hook.py`). A distinct basename per guard is
load-bearing: host-hook entry identity keys same-hook detection on the
script basename, so three guards sharing one script would uninstall each
other.
"""

from __future__ import annotations


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.host_command_guard_hook import main as _run_guard  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(_run_guard(["--guard", "discard-worktree"]))
