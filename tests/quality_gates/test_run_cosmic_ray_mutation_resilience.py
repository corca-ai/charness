"""Resilience tests for `scripts/run_cosmic_ray_mutation.py` (#183 follow-up).

The original #183 fix preserved partial dumps on `cosmic-ray exec` timeout. A
post-push critique pointed out that a non-zero exec exit (worker crash, etc.)
still bypassed the dump because the inner `subprocess.run` used `check=True`.
These tests pin the post-fix behavior: dump runs on timeout AND on crash, and
the caller still observes a non-zero return code in the crash case.
"""

from __future__ import annotations

import importlib.util
import signal
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
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


# --- #262: defensive module-path restore on exit/interrupt ------------------
#
# Cosmic Ray restores a mutated source only BETWEEN work units, so a kill
# mid-unit (external `timeout`/signal, the internal exec timeout, or a worker
# crash) leaves the in-progress mutant applied in the working tree. These tests
# pin the defensive restore: read the config's module-path, then `git checkout`
# those files on every exec outcome (try/finally) and on SIGINT/SIGTERM.


def _write_config(tmp_path: Path, body: str) -> Path:
    config = tmp_path / "cosmic-ray.toml"
    config.write_text(dedent(body), encoding="utf-8")
    return config


def test_read_module_paths_parses_list(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        """\
        [cosmic-ray]
        module-path = ["scripts/a.py", "scripts/b.py"]
        """,
    )
    assert RCRM._read_module_paths(config, tmp_path) == [
        tmp_path / "scripts/a.py",
        tmp_path / "scripts/b.py",
    ]


def test_read_module_paths_accepts_single_string(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        """\
        [cosmic-ray]
        module-path = "scripts/only.py"
        """,
    )
    assert RCRM._read_module_paths(config, tmp_path) == [tmp_path / "scripts/only.py"]


def test_read_module_paths_empty_when_key_absent(tmp_path: Path) -> None:
    config = _write_config(tmp_path, "[cosmic-ray]\ntimeout = 1.0\n")
    assert RCRM._read_module_paths(config, tmp_path) == []


def test_read_module_paths_empty_when_unparseable(tmp_path: Path) -> None:
    # A malformed config must degrade to a no-op restore, never crash the run;
    # Cosmic Ray itself surfaces a genuinely broken config downstream.
    config = _write_config(tmp_path, "module-path = [unclosed\n")
    assert RCRM._read_module_paths(config, tmp_path) == []


def test_restore_module_paths_reverts_mutated_file(tmp_path: Path) -> None:
    """The core #262 reproduction: a module-path file left mutated mid-run is
    reverted to its committed content by the defensive restore."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    target = tmp_path / "scripts" / "mod.py"
    target.parent.mkdir(parents=True)
    target.write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=tmp_path, check=True)

    # Simulate Cosmic Ray leaving the file mutated after a mid-unit kill.
    target.write_text("x = 99  # MUTANT\n", encoding="utf-8")
    assert target.read_text(encoding="utf-8") != "x = 1\n"

    RCRM._restore_module_paths([target], tmp_path)

    assert target.read_text(encoding="utf-8") == "x = 1\n"


def test_restore_module_paths_noop_on_empty(tmp_path: Path) -> None:
    with patch.object(RCRM.subprocess, "run") as run_mock:
        RCRM._restore_module_paths([], tmp_path)
    run_mock.assert_not_called()


def test_restore_module_paths_best_effort_when_git_missing(tmp_path: Path) -> None:
    # git absent → log and skip, never raise (so a working run is not broken).
    with patch.object(RCRM.subprocess, "run", side_effect=FileNotFoundError):
        RCRM._restore_module_paths([tmp_path / "mod.py"], tmp_path)


def test_restore_module_paths_continues_past_one_file_failure(tmp_path: Path) -> None:
    attempted: list[str] = []

    def fake_run(cmd, cwd, check, capture_output, text):  # noqa: ANN001
        attempted.append(cmd[-1])
        rc = 1 if cmd[-1].endswith("a.py") else 0
        return subprocess.CompletedProcess(args=cmd, returncode=rc, stderr="boom")

    with patch.object(RCRM.subprocess, "run", side_effect=fake_run):
        RCRM._restore_module_paths([tmp_path / "a.py", tmp_path / "b.py"], tmp_path)

    # One file failing does not abort the rest.
    assert attempted == [str(tmp_path / "a.py"), str(tmp_path / "b.py")]


def test_build_restore_handler_restores_then_reraises(tmp_path: Path) -> None:
    module_paths = [tmp_path / "mod.py"]
    handler = RCRM._build_restore_handler(module_paths, tmp_path)
    with (
        patch.object(RCRM, "_restore_module_paths") as restore_mock,
        patch.object(RCRM.signal, "signal") as signal_mock,
        patch.object(RCRM.os, "kill") as kill_mock,
        patch.object(RCRM.os, "getpid", return_value=4321),
    ):
        handler(signal.SIGTERM, None)

    # Restore first, then reset to default disposition and re-raise so the
    # wrapper still dies with 128+signum instead of swallowing the signal.
    restore_mock.assert_called_once_with(module_paths, tmp_path)
    signal_mock.assert_called_once_with(signal.SIGTERM, signal.SIG_DFL)
    kill_mock.assert_called_once_with(4321, signal.SIGTERM)


def test_install_and_restore_signal_handlers_round_trip() -> None:
    def sentinel(signum, frame):  # noqa: ANN001
        return None

    previous = RCRM._install_restore_handlers(sentinel)
    try:
        assert signal.getsignal(signal.SIGINT) is sentinel
        assert signal.getsignal(signal.SIGTERM) is sentinel
        assert set(previous) == {signal.SIGINT, signal.SIGTERM}
    finally:
        RCRM._restore_signal_handlers(previous)

    assert signal.getsignal(signal.SIGINT) is previous[signal.SIGINT]
    assert signal.getsignal(signal.SIGTERM) is previous[signal.SIGTERM]


def _full_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "cosmic-ray.toml").write_text(
        '[cosmic-ray]\nmodule-path = ["mod.py"]\n', encoding="utf-8"
    )
    return repo


def test_main_full_restores_after_clean_exec(tmp_path: Path) -> None:
    repo = _full_repo(tmp_path)
    argv = ["run_cosmic_ray_mutation.py", "--repo-root", str(repo), "--mode", "full"]
    with (
        patch.object(sys, "argv", argv),
        patch.object(RCRM, "run"),
        patch.object(RCRM, "_run_exec_with_timeout", return_value=(False, 0)),
        patch.object(RCRM, "_dump_session", return_value=0),
        patch.object(RCRM, "_restore_module_paths") as restore_mock,
    ):
        rc = RCRM.main()

    assert rc == 0
    restore_mock.assert_called_once()


def test_main_full_restores_even_on_exec_crash(tmp_path: Path) -> None:
    repo = _full_repo(tmp_path)
    argv = ["run_cosmic_ray_mutation.py", "--repo-root", str(repo), "--mode", "full"]
    with (
        patch.object(sys, "argv", argv),
        patch.object(RCRM, "run"),
        patch.object(RCRM, "_run_exec_with_timeout", return_value=(False, 2)),
        patch.object(RCRM, "_dump_session", return_value=0),
        patch.object(RCRM, "_restore_module_paths") as restore_mock,
    ):
        rc = RCRM.main()

    # Original exec failure is preserved AND the finally restore still ran.
    assert rc == 2
    restore_mock.assert_called_once()


def test_main_full_restores_even_on_timeout(tmp_path: Path) -> None:
    repo = _full_repo(tmp_path)
    argv = ["run_cosmic_ray_mutation.py", "--repo-root", str(repo), "--mode", "full"]
    with (
        patch.object(sys, "argv", argv),
        patch.object(RCRM, "run"),
        patch.object(RCRM, "_run_exec_with_timeout", return_value=(True, -1)),
        patch.object(RCRM, "_dump_session", return_value=0),
        patch.object(RCRM, "_write_timeout_marker") as marker_mock,
        patch.object(RCRM, "_restore_module_paths") as restore_mock,
    ):
        rc = RCRM.main()

    assert rc == 0
    marker_mock.assert_called_once()
    restore_mock.assert_called_once()


def test_main_dry_run_does_not_restore(tmp_path: Path) -> None:
    repo = _full_repo(tmp_path)
    argv = ["run_cosmic_ray_mutation.py", "--repo-root", str(repo), "--mode", "dry-run"]
    with (
        patch.object(sys, "argv", argv),
        patch.object(RCRM, "run"),
        patch.object(RCRM, "_restore_module_paths") as restore_mock,
    ):
        rc = RCRM.main()

    # No exec means no mutation, so dry-run must not touch the working tree.
    assert rc == 0
    restore_mock.assert_not_called()
