from __future__ import annotations

import os
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest_plugins = ["tests.repo_copy", "tests.quality_gates.support", "tests.charness_cli.support"]

_REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _confine_git_discovery_to_pytest_temp(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    # Stop git repo discovery from escaping the pytest temp tree into an ambient
    # ancestor .git (e.g. a dotfiles repo above $TMPDIR). Otherwise the
    # fail-closed-outside-git fixtures can non-deterministically find an ancestor
    # repo depending on where the (xdist) basetemp lands. See issue #225.
    ceiling = str(tmp_path_factory.getbasetemp().resolve().parent)
    previous = os.environ.get("GIT_CEILING_DIRECTORIES")
    os.environ["GIT_CEILING_DIRECTORIES"] = ceiling if not previous else f"{ceiling}:{previous}"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("GIT_CEILING_DIRECTORIES", None)
        else:
            os.environ["GIT_CEILING_DIRECTORIES"] = previous


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
