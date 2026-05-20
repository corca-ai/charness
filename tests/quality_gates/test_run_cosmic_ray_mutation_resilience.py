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


def test_dump_session_atomic_rename_on_success(tmp_path: Path) -> None:
    """Successful dump leaves dump_path populated and removes the .partial file."""
    session = tmp_path / "session.sqlite"
    dump_path = tmp_path / "dump.jsonl"

    def fake_run(cmd, cwd, check, stdout, text):
        stdout.write('[{"work": 1}, {"result": 2}]\n')
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    with patch.object(RCRM.subprocess, "run", side_effect=fake_run):
        rc = RCRM._dump_session(session, dump_path, tmp_path)

    assert rc == 0
    assert dump_path.is_file()
    assert not (tmp_path / "dump.jsonl.partial").exists()
    assert "work" in dump_path.read_text(encoding="utf-8")


def test_dump_session_leaves_partial_on_crash(tmp_path: Path) -> None:
    """A crashed dump must NOT overwrite dump_path; .partial stays around for forensics."""
    session = tmp_path / "session.sqlite"
    dump_path = tmp_path / "dump.jsonl"
    dump_path.write_text("previous-good-content\n", encoding="utf-8")

    def fake_run(cmd, cwd, check, stdout, text):
        stdout.write("oops-")  # partial stream
        return subprocess.CompletedProcess(args=cmd, returncode=3)

    with patch.object(RCRM.subprocess, "run", side_effect=fake_run):
        rc = RCRM._dump_session(session, dump_path, tmp_path)

    assert rc == 3
    # Atomic-rename semantics: a failed dump must NOT clobber dump_path.
    assert dump_path.read_text(encoding="utf-8") == "previous-good-content\n"
    assert (tmp_path / "dump.jsonl.partial").is_file()
