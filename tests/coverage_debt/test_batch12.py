"""Focused probes for the task-run git fallback and the brief-critique bootstrap.

The `except ImportError` fallback in `task_run_git.py` and the repo-root insert
in `task_run_brief_critique._load_repo_runtime_bootstrap` only execute when the
repo root is missing from `sys.path` at import time -- a shape the normal suite
never produces, so the changed-line gate reports those inserts uncovered.
These probes observe local owner behavior; the changed-line gate remains the
consumer of their coverage.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.module_eviction import evict_module, evict_new_modules
from tests.repo_bootstrap_marker import hide_repo_bootstrap_marker
from tests.script_loader import load_script_module


class _RefuseSubprocessGuardOnce:
    """Refuses the first `scripts.core.subprocess_guard` import, then stands down."""

    def __init__(self) -> None:
        self.fired = False

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "scripts.core.subprocess_guard" and not self.fired:
            self.fired = True
            raise ModuleNotFoundError(f"No module named {fullname!r}")
        return None


def test_task_run_git_flat_layout_fallback_inserts_repo_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The git fallback -- not the bootstrap -- inserts the root when both are starved."""
    import scripts.core.git_checkout  # noqa: F401
    import scripts.core.git_status_snapshot  # noqa: F401
    import scripts.task_run.task_run_contract  # noqa: F401
    import scripts.worktree.checkout_view  # noqa: F401

    root = Path(__file__).resolve().parents[2]
    refuser = _RefuseSubprocessGuardOnce()
    monkeypatch.setattr(sys, "meta_path", [refuser] + sys.meta_path)
    evict_module(monkeypatch, "scripts.core.subprocess_guard")
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(root)])
    hide_repo_bootstrap_marker(monkeypatch)
    before = set(sys.modules)
    try:
        module = load_script_module(
            "task_run_git_flat",
            root / "scripts/task_run/task_run_git.py",
        )

        assert refuser.fired
        assert module.run_process.__module__ == "scripts.core.subprocess_guard"
        # The bootstrap stood down, so only the fallback could have inserted this.
        assert sys.path[0] == str(root)
    finally:
        evict_new_modules(before)


def test_brief_critique_bootstrap_inserts_missing_repo_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The brief-critique bootstrap inserts the root when it is missing from `sys.path`."""
    from scripts.task_run import task_run_brief_critique

    root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(root)])
    assert str(root) not in sys.path

    task_run_brief_critique._load_repo_runtime_bootstrap()

    assert sys.path[0] == str(root)
