"""Resilience tests for `scripts/run_cosmic_ray_mutation.py` (#183 follow-up).

The original #183 fix preserved partial dumps on `cosmic-ray exec` timeout. A
post-push critique pointed out that a non-zero exec exit (worker crash, etc.)
still bypassed the dump because the inner `subprocess.run` used `check=True`.
These tests pin the post-fix behavior: dump runs on timeout AND on crash, and
the caller still observes a non-zero return code in the crash case.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "run_cosmic_ray_mutation", ROOT / "scripts" / "run_cosmic_ray_mutation.py"
)
assert _spec is not None and _spec.loader is not None
RCRM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RCRM)


def test_exec_clean_completion_returns_zero_returncode(tmp_path: Path) -> None:
    config = tmp_path / "cosmic-ray.toml"
    session = tmp_path / "session.sqlite"
    config.touch()

    with patch.object(RCRM.subprocess, "run") as run_mock:
        run_mock.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        timed_out, returncode = RCRM._run_exec_with_timeout(config, session, tmp_path, 60)

    assert timed_out is False
    assert returncode == 0


def test_exec_timeout_returns_sentinel_returncode(tmp_path: Path) -> None:
    config = tmp_path / "cosmic-ray.toml"
    session = tmp_path / "session.sqlite"
    config.touch()

    with patch.object(RCRM.subprocess, "run") as run_mock:
        run_mock.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=60)
        timed_out, returncode = RCRM._run_exec_with_timeout(config, session, tmp_path, 60)

    assert timed_out is True
    assert returncode == -1


def test_exec_crash_returns_real_returncode_no_exception(tmp_path: Path) -> None:
    """A non-zero exec exit must NOT raise; caller decides whether to propagate."""
    config = tmp_path / "cosmic-ray.toml"
    session = tmp_path / "session.sqlite"
    config.touch()

    with patch.object(RCRM.subprocess, "run") as run_mock:
        run_mock.return_value = subprocess.CompletedProcess(args=[], returncode=2)
        timed_out, returncode = RCRM._run_exec_with_timeout(config, session, tmp_path, 60)

    assert timed_out is False
    assert returncode == 2
