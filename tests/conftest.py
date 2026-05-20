from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest_plugins = ["tests.repo_copy", "tests.quality_gates.support", "tests.charness_cli.support"]

_REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _disable_plugin_fallback_manifests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return
    guard = _REPO_ROOT / "scripts" / "agent_browser_runtime_guard.py"
    if not guard.is_file():
        return
    cleanup = [sys.executable, str(guard), "--repo-root", str(_REPO_ROOT), "--cleanup-orphans", "--execute"]
    inspect = [sys.executable, str(guard), "--repo-root", str(_REPO_ROOT), "--assert-no-orphans"]
    deadline = time.monotonic() + 10
    while True:
        try:
            subprocess.run(cleanup, check=False, capture_output=True, timeout=30)
            result = subprocess.run(inspect, check=False, capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return
        if result.returncode == 0 or time.monotonic() >= deadline:
            return
        time.sleep(1)
