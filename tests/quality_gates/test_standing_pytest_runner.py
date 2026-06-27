from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


def test_standing_pytest_command_uses_xdist_and_expands_globs(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "quality_gates").mkdir()
    (tmp_path / "tests" / "control_plane").mkdir()
    (tmp_path / "tests" / "charness_cli").mkdir()
    monkeypatch.setattr(runner, "choose_pytest_command", lambda: [sys.executable, "-m", "pytest"])
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: True)
    monkeypatch.setattr(runner.os, "cpu_count", lambda: 36)

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
    monkeypatch.setattr(runner, "choose_pytest_command", lambda: [sys.executable, "-m", "pytest"])
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

    assert runner.default_basetemp(repo, {"HOME": str(tmp_path / "home")}).name == "pytest-123"
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

    monkeypatch.setattr(runner.importlib.util, "find_spec", lambda name: object())

    assert runner.choose_pytest_command() == [sys.executable, "-m", "pytest"]


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
    assert looked_up == ["xdist"]


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
