from __future__ import annotations

import os
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_standing_pytest_command_uses_xdist_and_expands_globs(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "quality_gates").mkdir()
    (tmp_path / "tests" / "control_plane").mkdir()
    (tmp_path / "tests" / "charness_cli").mkdir()
    monkeypatch.setattr(
        runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"]
    )
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    # Affinity is what the worker width reads, so a host-derived assertion must pin
    # BOTH: under `taskset -c 0-3` an affinity-blind patch left the real 4 showing
    # through and this test failed on a restricted run only (#446 in a new place).
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))
    # Same rule for the scheduling chunk: it is suppressed below xdist 3.2, so an
    # unpinned assertion would pass here and fail on an older-xdist host only.
    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 8, 0))

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
        env={},
    )

    # Both full-lane markers, in ONE expression: `slow_corpus` rides the same switch as
    # `release_only` so the two cannot drift into a lane that runs neither (#668).
    assert command[:6] == [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-m",
        "not release_only and not slow_corpus",
    ]
    assert "-n" in command
    assert "16" in command
    assert ["--maxschedchunk", "1"] == command[
        command.index("--maxschedchunk") : command.index("--maxschedchunk") + 2
    ]
    assert "tests/test_alpha.py" in command
    assert "tests/test_*.py" not in command
    assert "tests/charness_cli" in command


def test_standing_pytest_command_appends_extra_pytest_targets(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    monkeypatch.setattr(
        runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"]
    )
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: False)

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
        extra_pytest_targets=["tests/focused.py::test_one"],
        env={},
    )

    assert command[-1] == "tests/focused.py::test_one"
    assert "tests/test_alpha.py" in command


def test_standing_pytest_command_replaces_targets_without_losing_xdist(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(
        runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"]
    )
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    # Pin the host-derived worker width: choose_xdist_workers() is
    # min(cpu_count, 16), so an unpatched cpu_count makes this assertion pass
    # only on >=16-core hosts (the 4-core CI runner computed "-n 4", #446).
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    # Affinity is what the worker width reads, so a host-derived assertion must pin
    # BOTH: under `taskset -c 0-3` an affinity-blind patch left the real 4 showing
    # through and this test failed on a restricted run only (#446 in a new place).
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))
    # Same rule for the scheduling chunk: it is suppressed below xdist 3.2, so an
    # unpinned assertion would pass here and fail on an older-xdist host only.
    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 8, 0))

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
        pytest_targets=["tests/focused.py::test_one", "tests/other.py"],
        env={},
    )

    assert command[-6:] == [
        "-n",
        "16",
        "--maxschedchunk",
        "1",
        "tests/focused.py::test_one",
        "tests/other.py",
    ]
    assert "tests/quality_gates" not in command


def test_standing_pytest_temp_root_stays_outside_repo(tmp_path: Path) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    temp_root = basetemp_lib.default_temp_root(repo, {"HOME": str(tmp_path / "home")})

    assert "/charness/pytest-tmp/" in str(temp_root)
    basetemp_lib.ensure_external_temp_root(repo, temp_root)


def test_standing_pytest_env_temp_root_and_inside_repo_rejection(tmp_path: Path) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    custom = tmp_path / "custom-temp"

    assert basetemp_lib.default_temp_root(repo, {"PYTEST_DEBUG_TEMPROOT": str(custom)}) == custom
    try:
        basetemp_lib.ensure_external_temp_root(repo, repo / ".pytest-tmp")
    except SystemExit as exc:
        assert "is inside the repo" in str(exc)
    else:
        raise AssertionError("expected SystemExit for repo-local pytest temp root")


def test_runtime_bootstrap_routes_tool_outputs_outside_repo(tmp_path: Path, monkeypatch) -> None:
    from scripts.runtime_bootstrap import configure_runtime_environment

    repo = tmp_path / "repo"
    repo.mkdir()
    external = tmp_path / "runtime"
    env = {
        "CHARNESS_RUNTIME_ROOT": str(external),
        "PYTHONPYCACHEPREFIX": str(repo / "pycache"),
        "TMPDIR": str(repo / "tmp"),
        "PYTEST_DEBUG_TEMPROOT": str(repo / "pytest-tmp"),
        "CHARNESS_PYTEST_CACHE_DIR": str(repo / "pytest-cache"),
        "RUFF_CACHE_DIR": str(repo / ".ruff_cache"),
        "COVERAGE_FILE": str(repo / ".coverage"),
    }

    configured = configure_runtime_environment(repo, env)

    for key in (
        "PYTHONPYCACHEPREFIX",
        "TMPDIR",
        "PYTEST_DEBUG_TEMPROOT",
        "CHARNESS_PYTEST_CACHE_DIR",
        "RUFF_CACHE_DIR",
        "COVERAGE_FILE",
    ):
        path = Path(configured[key])
        if key == "COVERAGE_FILE":
            path = path.parent
        assert repo.resolve() not in path.resolve().parents
        assert path.exists()
    assert Path(configured["CHARNESS_RUNTIME_ROOT"]).is_dir()

    monkeypatch.setattr("scripts.run_standing_pytest.has_xdist", lambda *args, **kwargs: False)
    from scripts import run_standing_pytest as runner

    command = runner.build_pytest_command(
        repo,
        basetemp=external / "basetemp",
        include_release_only=True,
        pytest_targets=["tests/one.py"],
        env=env,
    )
    assert command[command.index("-o") + 1] == f"cache_dir={external / 'pytest-cache'}"


def test_runtime_bootstrap_rejects_explicit_repo_local_runtime_root(tmp_path: Path) -> None:
    from scripts.runtime_bootstrap import RuntimeEnvironmentError, configure_runtime_environment

    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(RuntimeEnvironmentError, match="must be outside the repository"):
        configure_runtime_environment(repo, {"CHARNESS_RUNTIME_ROOT": str(repo / "runtime")})


def test_standing_pytest_default_basetemp_uses_user_and_time(tmp_path: Path, monkeypatch) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        basetemp_lib,
        "run_process",
        lambda command, **kwargs: subprocess.CompletedProcess(
            args=command, returncode=0, stdout="alice\n", stderr=""
        ),
    )
    monkeypatch.setattr(basetemp_lib.time, "time_ns", lambda: 123)

    # The leaf is deliberately NOT "pytest-*" so nested pytest runs' numbered-dir
    # cleanup cannot target this lock-less explicit basetemp (see
    # test_default_basetemp_survives_nested_pytest_cleanup).
    assert (
        basetemp_lib.default_basetemp(repo, {"HOME": str(tmp_path / "home")}).name
        == "charness-run-123"
    )
    assert "pytest-of-alice" in str(
        basetemp_lib.default_basetemp(repo, {"HOME": str(tmp_path / "home")})
    )


def test_standing_pytest_command_probes_and_serial_fallback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: None)

    assert runner.choose_pytest_command() == ["pytest"]
    assert runner.has_xdist(["pytest"]) is False
    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path / "base",
        include_release_only=True,
    )

    assert command[:3] == ["pytest", "-q", "--basetemp"]
    assert "-m" not in command
    # The serial path must not carry the xdist-only flag: `--maxschedchunk` is
    # registered by the xdist plugin, so a plain pytest exits 4 on it before
    # collecting. This is the exact outcome the version floor and the `has_xdist`
    # nesting exist to prevent, and it had no assertion anywhere until now.
    assert "--maxschedchunk" not in command
    assert "pytest-xdist is not active" in capsys.readouterr().err


def test_standing_pytest_worker_cap_and_override(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.os, "cpu_count", lambda: 64)
    # Affinity is what the worker width reads, so a host-derived assertion must pin
    # BOTH: under `taskset -c 0-3` an affinity-blind patch left the real 4 showing
    # through and this test failed on a restricted run only (#446 in a new place).
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(64)))

    assert runner.choose_xdist_workers({}) == "16"
    assert runner.choose_xdist_workers({"CHARNESS_PYTEST_WORKERS": "8"}) == "8"
    assert runner.choose_xdist_workers({"CHARNESS_PYTEST_WORKERS": "auto"}) == "auto"

    try:
        runner.choose_xdist_workers({"CHARNESS_PYTEST_WORKERS": "0"})
    except SystemExit as exc:
        assert "must be >= 1" in str(exc)
    else:
        raise AssertionError("expected SystemExit for invalid worker count")

    try:
        runner.choose_xdist_workers({"CHARNESS_PYTEST_WORKERS": "many"})
    except SystemExit as exc:
        assert "positive integer" in str(exc)
    else:
        raise AssertionError("expected SystemExit for non-numeric worker count")


def test_standing_pytest_sched_chunk_defaults_to_one_and_honors_overrides(monkeypatch) -> None:
    """`--dist load` pre-assigns each worker a CONSECUTIVE chunk before any timing.

    Pinned as literals, not as a restatement of `choose_sched_chunk`'s own expression:
    "1" is what an operator's command line actually carries, and the suppression
    branches are the ones that keep an unknown flag from aborting the run.

    Every suppression case also pins the REASON string, because a suppressed flag puts
    the suite back on the slow path where this repo's runtime bars go red having
    regressed nothing -- the reason is the only thing that makes that red diagnosable.
    """
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 8, 0))

    assert runner.choose_sched_chunk({}) == ("1", None)
    assert runner.choose_sched_chunk({"CHARNESS_PYTEST_SCHED_CHUNK": "4"}) == ("4", None)
    assert runner.choose_sched_chunk({"CHARNESS_PYTEST_SCHED_CHUNK": "off"}) == (
        None,
        "CHARNESS_PYTEST_SCHED_CHUNK=off",
    )
    # An operator who already tuned it wins; ours would land later and silently beat it.
    assert runner.choose_sched_chunk({"PYTEST_ADDOPTS": "--maxschedchunk=10"}) == (
        None,
        "PYTEST_ADDOPTS already sets --maxschedchunk",
    )
    # The deference must DISCRIMINATE, not just fire. Without this line, widening the
    # check to `if env.get("PYTEST_ADDOPTS")` still passes -- and PYTEST_ADDOPTS is
    # routinely set for unrelated reasons (CI reporters, `-p no:cacheprovider`), so
    # that mutant would silently revert this optimization on exactly those hosts.
    assert runner.choose_sched_chunk({"PYTEST_ADDOPTS": "-p no:cacheprovider"}) == ("1", None)
    # Explicit override beats the addopts deference; the two are checked in that order.
    assert runner.choose_sched_chunk(
        {"CHARNESS_PYTEST_SCHED_CHUNK": "2", "PYTEST_ADDOPTS": "--maxschedchunk=10"}
    ) == ("2", None)

    for bad, expected in (("0", "must be >= 1"), ("some", "positive integer")):
        try:
            runner.choose_sched_chunk({"CHARNESS_PYTEST_SCHED_CHUNK": bad})
        except SystemExit as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"expected SystemExit for sched chunk {bad!r}")


def test_standing_pytest_sched_chunk_suppressed_below_xdist_floor(monkeypatch) -> None:
    """Below xdist 3.2 `--maxschedchunk` is an unknown option and pytest exits 4.

    A scheduling tweak must never be why the suite cannot start -- the same rule
    `usable_cpu_count` follows for affinity refusal.

    3.1 is pinned as a literal because it is REACHABLE, not decorative:
    `packaging/mutation-requirements.txt` allows `pytest-xdist>=3,<4`, so a supported
    environment can hold a version that predates the flag. The floor was first written
    as 2.3 from a guess and would have passed the flag to 3.0 and 3.1.
    """
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 1, 0))
    assert runner.choose_sched_chunk({}) == (None, "pytest-xdist 3.1.0 is below 3.2")

    # Unknown version reads as "cannot tell", which must suppress rather than assume.
    monkeypatch.setattr(runner, "xdist_version", lambda: ())
    assert runner.choose_sched_chunk({}) == (None, "pytest-xdist unknown is below 3.2")

    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 2))
    assert runner.choose_sched_chunk({}) == ("1", None)


def test_standing_pytest_warns_on_stderr_when_scheduling_is_suppressed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A suppressed flag is not a neutral fallback -- it reds runtime bars.

    `run-quality-full`'s bar is sized for the scheduled regime and sits BELOW this
    repo's own recorded pre-flag basis, so an involuntary suppression (old xdist, an
    unrelated PYTEST_ADDOPTS tuning) surfaces to the operator as "exceeded its budget"
    with nothing regressed. Without this warning there is no pointer from that red back
    to its cause, which is why the `has_xdist` branch already prints the analogue.
    """
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(
        runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"]
    )
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))
    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 1, 0))

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path / "base",
        include_release_only=False,
        pytest_targets=["tests/focused.py"],
        env={},
    )

    assert "--maxschedchunk" not in command
    stderr = capsys.readouterr().err
    assert "pytest-xdist 3.1.0 is below 3.2" in stderr
    assert "runtime budgets" in stderr

    # The applied path must stay quiet; a warning on every normal run is noise that
    # trains the operator to ignore the one run where it matters.
    monkeypatch.setattr(runner, "xdist_version", lambda: (3, 8, 0))
    runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path / "base",
        include_release_only=False,
        pytest_targets=["tests/focused.py"],
        env={},
    )
    assert capsys.readouterr().err == ""


def test_standing_pytest_xdist_version_parses_without_packaging_shadow(monkeypatch) -> None:
    """`pythonpath = ["."]` puts the repo's own `packaging/` dir ahead of the library."""
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.metadata, "version", lambda name: "3.8.0")
    assert runner.xdist_version() == (3, 8, 0)

    monkeypatch.setattr(runner.importlib.metadata, "version", lambda name: "3.9.0rc1")
    assert runner.xdist_version() == (3, 9, 0)

    def missing(name: str) -> str:
        raise runner.importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(runner.importlib.metadata, "version", missing)
    assert runner.xdist_version() == ()


def test_standing_pytest_choose_prefers_python_module(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.delenv("CHARNESS_STANDING_PYTEST_PYTHON", raising=False)
    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert runner.choose_pytest_command() == [sys.executable, "-m", "pytest"]
    assert runner.choose_pytest_command({"CHARNESS_STANDING_PYTEST_PYTHON": "python3"}) == [
        "python3",
        "-m",
        "pytest",
    ]


def test_standing_pytest_xdist_probe_uses_importlib_without_subprocess(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    looked_up: list[str] = []

    def fake_find_spec(name: str) -> object | None:
        looked_up.append(name)
        return object() if name == "xdist" else None

    monkeypatch.setattr(runner.importlib.util, "find_spec", fake_find_spec)
    # This used to patch `runner.subprocess.run` to explode. S6 moved the last
    # subprocess user (the `id -un` read in `default_basetemp`) into
    # `standing_pytest_basetemp`, so the runner no longer imports subprocess at
    # all -- a STRONGER guarantee than a patched-and-exploding probe, and the one
    # worth asserting: the module cannot shell out because it has no way to.
    assert not hasattr(runner, "subprocess"), (
        "the runner re-acquired a subprocess import; the xdist probe must stay an "
        "importlib metadata read, never a spawned process"
    )

    assert runner.has_xdist([sys.executable, "-m", "pytest"], {}) is True
    assert (
        runner.has_xdist(
            ["python3", "-m", "pytest"], {"CHARNESS_STANDING_PYTEST_PYTHON": "python3"}
        )
        is True
    )
    assert looked_up == ["xdist", "xdist"]


def test_standing_pytest_xdist_probe_honors_disabled_plugin(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert (
        runner.has_xdist(
            [sys.executable, "-m", "pytest"],
            {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        )
        is False
    )
    assert (
        runner.has_xdist(
            [sys.executable, "-m", "pytest"],
            {"PYTEST_ADDOPTS": "-p no:xdist"},
        )
        is False
    )
    assert (
        runner.has_xdist(
            [sys.executable, "-m", "pytest"],
            {"PYTEST_ADDOPTS": "-pno:xdist"},
        )
        is False
    )
    assert runner.has_xdist(["pytest"], {}) is False


def test_standing_pytest_xdist_disabled_option_falls_back_on_unbalanced_addopts(
    monkeypatch,
) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert (
        runner.has_xdist(
            [sys.executable, "-m", "pytest"],
            {"PYTEST_ADDOPTS": "-p no:xdist 'unterminated"},
        )
        is False
    )


def test_standing_pytest_run_print_command_and_executes(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    basetemp = tmp_path / "base"
    monkeypatch.setattr(
        runner,
        "build_pytest_command",
        lambda *args, **kwargs: ["python3", "-m", "pytest", "-q"],
    )

    printed = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=basetemp,
            include_release_only=False,
            mode="read-only",
            print_command=True,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )
    assert printed == 0
    assert "python3 -m pytest -q" in capsys.readouterr().out

    basetemp.mkdir()
    captured: dict[str, object] = {}

    def fake_phase(command, **kwargs):
        captured.update({"command": command, **kwargs})
        return SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        )

    # The seam moved from `subprocess.run` to the monitored primitive (SC11). The
    # assertions below are unchanged in substance -- same command, cwd, and env
    # reach the child -- which is the point: converting the runner must not change
    # what it runs.
    monkeypatch.setattr(runner, "run_monitored_phase", fake_phase)
    rc = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=basetemp,
            include_release_only=False,
            mode="full",
            print_command=False,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )

    assert rc == 0
    assert captured["cwd"] == repo.resolve()
    assert captured["env"]["CHARNESS_QUALITY_MODE"] == "full"
    assert not basetemp.exists()


def test_failed_basetemp_prune_keeps_newest_three_and_skips_active(
    tmp_path: Path,
) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    parent = tmp_path / "pytest-of-alice"
    parent.mkdir()
    roots = [parent / f"charness-run-{index}" for index in range(1, 7)]
    for index, path in enumerate(roots, start=1):
        path.mkdir()
        os.utime(path, ns=(index, index))
        basetemp_lib._mark_basetemp(path, basetemp_lib._FAILED_BASETEMP_MARKER)
        os.utime(path / basetemp_lib._FAILED_BASETEMP_MARKER, ns=(index, index))
    unrelated = parent / "pytest-1"
    unrelated.mkdir()
    current = parent / "charness-run-7"

    with basetemp_lib._hold_basetemp_lock(roots[0]):
        removed = basetemp_lib.prune_failed_basetemps(parent, current_failed=current, keep=3)

    assert {path.name for path in removed} == {"charness-run-2", "charness-run-3", "charness-run-4"}
    assert roots[0].is_dir()
    assert roots[4].is_dir() and roots[5].is_dir()
    assert unrelated.is_dir()


def test_failed_standing_run_prunes_only_default_owned_roots(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    parent = tmp_path / "pytest-of-alice"
    parent.mkdir()
    for index in range(1, 5):
        path = parent / f"charness-run-{index}"
        path.mkdir()
        os.utime(path, ns=(index, index))
        basetemp_lib._mark_basetemp(path, basetemp_lib._FAILED_BASETEMP_MARKER)
        os.utime(path / basetemp_lib._FAILED_BASETEMP_MARKER, ns=(index, index))
    current = parent / "charness-run-5"
    monkeypatch.setattr(runner, "default_basetemp", lambda repo_root: current)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *args, **kwargs: ["pytest"])

    def fail(command, **kwargs):
        current.mkdir()
        return SimpleNamespace(
            returncode=1, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        )

    monkeypatch.setattr(runner, "run_monitored_phase", fail)
    rc = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=None,
            include_release_only=False,
            mode="read-only",
            print_command=False,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )

    assert rc == 1
    assert sorted(path.name for path in parent.iterdir() if path.is_dir()) == [
        "charness-run-3",
        "charness-run-4",
        "charness-run-5",
    ]


def test_custom_basetemp_failure_does_not_prune_its_parent(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    parent = tmp_path / "operator-owned"
    parent.mkdir()
    sibling = parent / "charness-run-1"
    sibling.mkdir()
    custom = parent / "custom"
    monkeypatch.setattr(runner, "build_pytest_command", lambda *args, **kwargs: ["pytest"])
    monkeypatch.setattr(
        runner,
        "run_monitored_phase",
        lambda command, **kwargs: SimpleNamespace(
            returncode=1, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        ),
    )

    rc = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=custom,
            include_release_only=False,
            mode="read-only",
            print_command=False,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )

    assert rc == 1
    assert sibling.is_dir()


def test_success_keeps_three_prior_failures_without_reserving_a_current_slot(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_standing_pytest as runner
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    parent = tmp_path / "pytest-of-alice"
    parent.mkdir()
    failures = [parent / f"charness-run-{index}" for index in range(1, 5)]
    for index, path in enumerate(failures, start=1):
        path.mkdir()
        basetemp_lib._mark_basetemp(path, basetemp_lib._FAILED_BASETEMP_MARKER)
        marker = path / basetemp_lib._FAILED_BASETEMP_MARKER
        os.utime(marker, ns=(index, index))
    current = parent / "charness-run-5"
    current.mkdir()
    monkeypatch.setattr(runner, "default_basetemp", lambda repo_root: current)
    monkeypatch.setattr(runner, "build_pytest_command", lambda *args, **kwargs: ["pytest"])
    monkeypatch.setattr(
        runner,
        "run_monitored_phase",
        lambda command, **kwargs: SimpleNamespace(
            returncode=0, timed_out=False, elapsed_seconds=1.0, stdout="", stderr=""
        ),
    )

    rc = runner.run_standing_pytest(
        SimpleNamespace(
            repo_root=repo,
            basetemp=None,
            include_release_only=False,
            mode="read-only",
            print_command=False,
            keep_basetemp=False,
            pytest_target=[],
            extra_pytest_target=[],
            timeout_seconds=None,
        )
    )

    assert rc == 0
    assert not current.exists()
    assert sorted(path.name for path in parent.iterdir() if path.is_dir()) == [
        "charness-run-2",
        "charness-run-3",
        "charness-run-4",
    ]


def test_explicitly_kept_success_and_unmarked_legacy_roots_are_never_failure_candidates(
    tmp_path: Path,
) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    parent = tmp_path / "pytest-of-alice"
    parent.mkdir()
    kept = parent / "charness-run-1"
    kept.mkdir()
    basetemp_lib._mark_basetemp(kept, basetemp_lib._KEPT_BASETEMP_MARKER)
    legacy = parent / "charness-run-2"
    legacy.mkdir()
    failures = [parent / f"charness-run-{index}" for index in range(3, 7)]
    for index, path in enumerate(failures, start=3):
        path.mkdir()
        basetemp_lib._mark_basetemp(path, basetemp_lib._FAILED_BASETEMP_MARKER)
        marker = path / basetemp_lib._FAILED_BASETEMP_MARKER
        os.utime(marker, ns=(index, index))

    basetemp_lib.prune_failed_basetemps(parent, current_failed=None, keep=3)

    assert kept.is_dir() and legacy.is_dir()
    assert not failures[0].exists()
    assert all(path.is_dir() for path in failures[1:])


def test_failed_basetemp_keep_override_defaults_safely_on_invalid_values(
    monkeypatch, capsys
) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    assert basetemp_lib._failed_basetemp_keep({"CHARNESS_PYTEST_FAILED_BASETEMP_KEEP": "5"}) == 5
    for raw in ("0", "-1", "not-a-number"):
        assert (
            basetemp_lib._failed_basetemp_keep({"CHARNESS_PYTEST_FAILED_BASETEMP_KEEP": raw})
            == basetemp_lib.FAILED_BASETEMP_KEEP
        )
        assert "expected a positive integer" in capsys.readouterr().err


def test_standing_pytest_main_print_modes(tmp_path: Path, monkeypatch, capsys) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(runner, "expand_targets", lambda repo_root: ["tests/demo.py"])
    monkeypatch.setattr(runner, "default_temp_root", lambda repo_root: tmp_path / "temp")
    monkeypatch.setattr(runner, "ensure_external_temp_root", lambda repo_root, temp_root: None)
    monkeypatch.setattr(runner, "run_standing_pytest", lambda args: 7)

    assert runner.main(["--repo-root", str(repo), "--print-targets"]) == 0
    assert "tests/quality_gates" in capsys.readouterr().out
    assert runner.main(["--repo-root", str(repo), "--print-expanded-targets"]) == 0
    assert "tests/demo.py" in capsys.readouterr().out
    assert (
        runner.main(
            [
                "--repo-root",
                str(repo),
                "--pytest-target",
                "tests/replacement.py::test_one",
                "--print-expanded-targets",
            ]
        )
        == 0
    )
    assert capsys.readouterr().out.strip() == "tests/replacement.py::test_one"
    assert (
        runner.main(
            [
                "--repo-root",
                str(repo),
                "--extra-pytest-target",
                "tests/focused.py::test_one",
                "--print-expanded-targets",
            ]
        )
        == 0
    )
    assert "tests/focused.py::test_one" in capsys.readouterr().out
    assert runner.main(["--repo-root", str(repo), "--print-temp-root"]) == 0
    assert str(tmp_path / "temp") in capsys.readouterr().out
    assert runner.main(["--repo-root", str(repo)]) == 7


def test_standing_pytest_script_entrypoint_print_targets(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["run_standing_pytest.py", "--print-targets"])

    try:
        runpy.run_path("scripts/run_standing_pytest.py", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("expected SystemExit from script entrypoint")

    assert "tests/quality_gates" in capsys.readouterr().out


@pytest.mark.boundary_contract(
    reason="prove the install-update shell entrypoint delegates to the real standing runner executable"
)
def test_install_update_self_validation_delegates_to_parallel_runner(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    source = Path(__file__).resolve().parents[2] / "scripts" / "self-validate-install-update.sh"
    script = scripts / source.name
    shutil.copy2(source, script)
    # The gate sources the shared export-copy guard; without it the run dies on a
    # missing file rather than on the delegation this test is about.
    shutil.copy2(source.parent / "exported-copy-guard.sh", scripts / "exported-copy-guard.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    capture = tmp_path / "args.txt"
    fake_python = bin_dir / "python3"
    fake_python.write_text(
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$CAPTURE_ARGS"\n',
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    env = {
        "PATH": f"{bin_dir}:{Path('/usr/bin')}:{Path('/bin')}",
        "CAPTURE_ARGS": str(capture),
    }
    result = subprocess.run(
        ["bash", str(script)], cwd=repo, env=env, check=False, capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    assert capture.read_text(encoding="utf-8").splitlines() == [
        "scripts/run_standing_pytest.py",
        "--repo-root",
        str(repo),
        "--mode",
        "read-only",
        "--include-release-only",
        "--pytest-target",
        "tests/charness_cli/test_managed_install.py",
        "--pytest-target",
        "tests/charness_cli/test_codex_cache_refresh.py",
        "--pytest-target",
        "tests/charness_cli/test_update_propagation.py",
    ]


def test_default_basetemp_leaf_is_not_a_pytest_cleanup_candidate(tmp_path: Path) -> None:
    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"PYTEST_DEBUG_TEMPROOT": str(tmp_path / "temproot")}

    basetemp = basetemp_lib.default_basetemp(repo, env)

    # The basetemp shares its pytest-of-<user> parent with nested pytest runs'
    # numbered dirs; a "pytest-" leaf would be an unlocked deletion candidate for
    # their cleanup glob (prefix="pytest-").
    assert not basetemp.name.startswith("pytest-")
    assert basetemp.parent.name.startswith("pytest-of-")


def test_default_basetemp_survives_nested_pytest_cleanup(tmp_path: Path) -> None:
    # Regression for the mid-run temp-tree deletion race: a nested pytest run that
    # shares the pytest-of-<user> rootdir (via inherited PYTEST_DEBUG_TEMPROOT) runs
    # make_numbered_dir_with_cleanup at process exit, which renames+removes unlocked
    # "pytest-*" dirs. pytest's explicit --basetemp branch creates the standing
    # runner's basetemp WITHOUT a cleanup lock, so it must not carry a "pytest-*"
    # name or a nested run's cleanup would delete it (and every live xdist worker's
    # popen-gw* subdir) mid-run.
    from _pytest.pathlib import (  # noqa: PLC0415
        LOCK_TIMEOUT,
        cleanup_numbered_dir,
        make_numbered_dir_with_cleanup,
    )

    from scripts import standing_pytest_basetemp as basetemp_lib

    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"PYTEST_DEBUG_TEMPROOT": str(tmp_path / "temproot")}

    basetemp = basetemp_lib.default_basetemp(repo, env)
    basetemp.mkdir(
        parents=True, mode=0o700
    )  # mimic pytest's explicit-basetemp mkdir (no lock file)
    (basetemp / "popen-gw0").mkdir()  # a live xdist worker temp dir

    rootdir = basetemp.parent
    for _ in range(6):  # nested default-scheme pytest runs create higher-numbered locked dirs
        make_numbered_dir_with_cleanup(
            root=rootdir, prefix="pytest-", keep=3, lock_timeout=LOCK_TIMEOUT, mode=0o700
        )
    # a nested run's exit-time cleanup sweep of the shared rootdir (treat every lock as dead)
    cleanup_numbered_dir(
        root=rootdir, prefix="pytest-", keep=3, consider_lock_dead_if_created_before=time.time() + 1
    )

    assert basetemp.exists()
    assert (basetemp / "popen-gw0").exists()


def test_xdist_worker_width_keys_on_affinity_not_total_cpus(monkeypatch) -> None:
    """Oversubscription is a measured, not theoretical, speed loss.

    `choose_xdist_workers` used `os.cpu_count()`, so a run under `taskset -c 0-3`,
    a cpuset, or a container CPU limit on a 36-core box spawned 16 workers onto 4
    usable CPUs. Measured on this repo's suite: 94.2s at 16 workers vs 64.1s at 4 —
    the oversubscription cost 32% of wall time and ~76s of CPU.

    This is the same root cause as the runtime-profile bug fixed alongside it, in a
    second caller: `os.cpu_count()` answers "how many CPUs does the box have", never
    "how many may this process use".
    """
    from scripts import run_standing_pytest as runner

    # cpu_count says 36 and affinity says 4: the divergence IS the test.
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(4)))

    assert runner.choose_xdist_workers({}) == "4"

    # An unrestricted run on the same box still uses the cap, so the fix costs
    # nothing where affinity is not narrowed.
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))
    assert runner.choose_xdist_workers({}) == "16"

    # An explicit operator override still wins over either derivation.
    assert runner.choose_xdist_workers({"CHARNESS_PYTEST_WORKERS": "8"}) == "8"


def test_affinity_readers_stay_in_parity_across_their_two_owners(monkeypatch) -> None:
    """The dup-review entry that accepts this duplication needs a binding, not a promise.

    `run_standing_pytest.usable_cpu_count` and the quality skill's
    `runtime_profile_lib.usable_cpu_count` are deliberately separate (a process-width
    tuning number vs a writer/reader profile-id contract; routing the runner through
    the skill broke a coverage-instrumented child with ModuleNotFoundError). The repo
    accepts that copy as `intentional` in dup-review.json id 86638e4edc955d3f — and the
    precedent it follows (89d83f450e19e19b) is accepted BECAUSE a test binds the copies
    so semantic drift fails instead of diverging silently. This is that test.

    The `OSError` arm matters most: it was a shipped v2.10.0 known limitation, fixed in
    v2.11.0, and re-introduced here as a second untested copy. Narrowing it back to
    `AttributeError` would take the whole standing pytest gate down on a seccomp host.
    """
    import importlib.util
    from pathlib import Path as _Path

    from scripts import run_standing_pytest as runner

    lib_path = (
        _Path(runner.__file__).resolve().parent.parent
        / "skills"
        / "public"
        / "quality"
        / "scripts"
        / "runtime_profile_lib.py"
    )
    spec = importlib.util.spec_from_file_location("parity_runtime_profile_lib", lib_path)
    assert spec is not None and spec.loader is not None
    profile_lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profile_lib)

    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    monkeypatch.setattr(profile_lib.os, "cpu_count", lambda: 36)

    for affinity in (1, 4, 36):
        monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid, n=affinity: set(range(n)))
        assert runner.usable_cpu_count() == profile_lib.usable_cpu_count() == affinity

    def refuse(_pid: int) -> set[int]:
        raise OSError(1, "Operation not permitted")

    monkeypatch.setattr(runner.os, "sched_getaffinity", refuse)
    assert runner.usable_cpu_count() == profile_lib.usable_cpu_count() == 36

    # Neither reader may return a width that would make xdist spawn nothing.
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set())
    assert runner.usable_cpu_count() == profile_lib.usable_cpu_count() == 1
    assert int(runner.choose_xdist_workers({})) >= 1
