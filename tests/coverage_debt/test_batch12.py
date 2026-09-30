"""Focused probe for the brief-critique repo-root bootstrap.

`task_run_brief_critique._load_repo_runtime_bootstrap` is the single owner of
repo-root insertion for that module: the `except ImportError` re-root
fallbacks that used to shadow it in sibling scripts are removed, and the
bootstrap insert only executes when the root is missing from `sys.path` -- a
shape the normal suite never produces, so the changed-line gate reports the
insert uncovered without this probe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


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
