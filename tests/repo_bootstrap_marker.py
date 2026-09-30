"""Defeat the repo-runtime bootstrap marker for one flat-layout probe.

Every script starts with `_load_repo_runtime_bootstrap()`, which inserts the
repo root when `<root>/scripts/adapter_lib.py` exists. That insert runs BEFORE
the `try: from scripts.core...` / `except ImportError:` fallback, so a probe
that loads a script by path always takes the fallback's `root already on path`
branch: the fallback's own `sys.path.insert` never executes and the
changed-line gate reports it uncovered.

Hiding the marker simulates the partial layout the fallback exists for (a tree
that carries `scripts/core/subprocess_guard.py` but no `scripts/adapter_lib.py`):
the bootstrap stands down, the `try` import fails, and the fallback insert --
the only inserter left -- becomes the line under test.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def hide_repo_bootstrap_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make `*/scripts/adapter_lib.py` read as missing until teardown."""
    real_is_file = Path.is_file

    def _is_file(self: Path) -> bool:
        if self.name == "adapter_lib.py" and self.parent.name == "scripts":
            return False
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", _is_file)
