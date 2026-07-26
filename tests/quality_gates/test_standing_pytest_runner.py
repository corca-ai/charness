from __future__ import annotations

import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace


def test_standing_pytest_command_uses_xdist_and_expands_globs(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "quality_gates").mkdir()
    (tmp_path / "tests" / "control_plane").mkdir()
    (tmp_path / "tests" / "charness_cli").mkdir()
    monkeypatch.setattr(runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"])
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    # Affinity is what the worker width reads, so a host-derived assertion must pin
    # BOTH: under `taskset -c 0-3` an affinity-blind patch left the real 4 showing
    # through and this test failed on a restricted run only (#446 in a new place).
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
        env={},
    )

    assert command[:6] == [sys.executable, "-m", "pytest", "-q", "-m", "not release_only"]
    assert "-n" in command
    assert "16" in command
    assert "tests/test_alpha.py" in command
    assert "tests/test_*.py" not in command
    assert "tests/charness_cli" in command


def test_standing_pytest_command_appends_extra_pytest_targets(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    monkeypatch.setattr(runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"])
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

    monkeypatch.setattr(runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"])
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    # Pin the host-derived worker width: choose_xdist_workers() is
    # min(cpu_count, 16), so an unpatched cpu_count makes this assertion pass
    # only on >=16-core hosts (the 4-core CI runner computed "-n 4", #446).
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)
    # Affinity is what the worker width reads, so a host-derived assertion must pin
    # BOTH: under `taskset -c 0-3` an affinity-blind patch left the real 4 showing
    # through and this test failed on a restricted run only (#446 in a new place).
    monkeypatch.setattr(runner.os, "sched_getaffinity", lambda _pid: set(range(36)))

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
        pytest_targets=["tests/focused.py::test_one", "tests/other.py"],
        env={},
    )

    assert command[-4:] == ["-n", "16", "tests/focused.py::test_one", "tests/other.py"]
    assert "tests/quality_gates" not in command


def test_standing_pytest_temp_root_stays_outside_repo(tmp_path: Path) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    temp_root = runner.default_temp_root(repo, {"HOME": str(tmp_path / "home")})

    assert "/charness/pytest-tmp/" in str(temp_root)
    runner.ensure_external_temp_root(repo, temp_root)


def test_standing_pytest_env_temp_root_and_inside_repo_rejection(tmp_path: Path) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    custom = tmp_path / "custom-temp"

    assert runner.default_temp_root(repo, {"PYTEST_DEBUG_TEMPROOT": str(custom)}) == custom
    try:
        runner.ensure_external_temp_root(repo, repo / ".pytest-tmp")
    except SystemExit as exc:
        assert "is inside the repo" in str(exc)
    else:
        raise AssertionError("expected SystemExit for repo-local pytest temp root")


def test_standing_pytest_default_basetemp_uses_user_and_time(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args=[], returncode=0, stdout="alice\n"),
    )
    monkeypatch.setattr(runner.time, "time_ns", lambda: 123)

    # The leaf is deliberately NOT "pytest-*" so nested pytest runs' numbered-dir
    # cleanup cannot target this lock-less explicit basetemp (see
    # test_default_basetemp_survives_nested_pytest_cleanup).
    assert runner.default_basetemp(repo, {"HOME": str(tmp_path / "home")}).name == "charness-run-123"
    assert "pytest-of-alice" in str(runner.default_basetemp(repo, {"HOME": str(tmp_path / "home")}))


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


def test_standing_pytest_choose_prefers_python_module(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.delenv("CHARNESS_STANDING_PYTEST_PYTHON", raising=False)
    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert runner.choose_pytest_command() == [sys.executable, "-m", "pytest"]
    assert runner.choose_pytest_command({"CHARNESS_STANDING_PYTEST_PYTHON": "python3"}) == ["python3", "-m", "pytest"]


def test_standing_pytest_xdist_probe_uses_importlib_without_subprocess(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    looked_up: list[str] = []

    def fake_find_spec(name: str) -> object | None:
        looked_up.append(name)
        return object() if name == "xdist" else None

    monkeypatch.setattr(runner.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("subprocess probe should not run")),
    )

    assert runner.has_xdist([sys.executable, "-m", "pytest"], {}) is True
    assert runner.has_xdist(["python3", "-m", "pytest"], {"CHARNESS_STANDING_PYTEST_PYTHON": "python3"}) is True
    assert looked_up == ["xdist", "xdist"]


def test_standing_pytest_xdist_probe_honors_disabled_plugin(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert runner.has_xdist(
        [sys.executable, "-m", "pytest"],
        {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    ) is False
    assert runner.has_xdist(
        [sys.executable, "-m", "pytest"],
        {"PYTEST_ADDOPTS": "-p no:xdist"},
    ) is False
    assert runner.has_xdist(
        [sys.executable, "-m", "pytest"],
        {"PYTEST_ADDOPTS": "-pno:xdist"},
    ) is False
    assert runner.has_xdist(["pytest"], {}) is False


def test_standing_pytest_xdist_disabled_option_falls_back_on_unbalanced_addopts(monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert runner.has_xdist(
        [sys.executable, "-m", "pytest"],
        {"PYTEST_ADDOPTS": "-p no:xdist 'unterminated"},
    ) is False


def test_standing_pytest_run_print_command_and_executes(tmp_path: Path, monkeypatch, capsys) -> None:
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
        )
    )
    assert printed == 0
    assert "python3 -m pytest -q" in capsys.readouterr().out

    basetemp.mkdir()
    captured: dict[str, object] = {}

    def fake_run(command, *, cwd, env, check):
        captured.update({"command": command, "cwd": cwd, "env": env, "check": check})
        return subprocess.CompletedProcess(command, returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
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
        )
    )

    assert rc == 0
    assert captured["cwd"] == repo.resolve()
    assert captured["env"]["CHARNESS_QUALITY_MODE"] == "full"
    assert not basetemp.exists()


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
    assert runner.main([
        "--repo-root",
        str(repo),
        "--pytest-target",
        "tests/replacement.py::test_one",
        "--print-expanded-targets",
    ]) == 0
    assert capsys.readouterr().out.strip() == "tests/replacement.py::test_one"
    assert runner.main([
        "--repo-root",
        str(repo),
        "--extra-pytest-target",
        "tests/focused.py::test_one",
        "--print-expanded-targets",
    ]) == 0
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


def test_install_update_self_validation_delegates_to_parallel_runner(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    source = Path(__file__).resolve().parents[2] / "scripts" / "self-validate-install-update.sh"
    script = scripts / source.name
    shutil.copy2(source, script)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    capture = tmp_path / "args.txt"
    fake_python = bin_dir / "python3"
    fake_python.write_text(
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > \"$CAPTURE_ARGS\"\n",
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
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"PYTEST_DEBUG_TEMPROOT": str(tmp_path / "temproot")}

    basetemp = runner.default_basetemp(repo, env)

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

    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"PYTEST_DEBUG_TEMPROOT": str(tmp_path / "temproot")}

    basetemp = runner.default_basetemp(repo, env)
    basetemp.mkdir(parents=True, mode=0o700)  # mimic pytest's explicit-basetemp mkdir (no lock file)
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

    lib_path = _Path(runner.__file__).resolve().parent.parent / "skills" / "public" / "quality" / "scripts" / "runtime_profile_lib.py"
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
