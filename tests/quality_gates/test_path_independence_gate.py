"""Unit tests for the PATH-independence gate script itself."""

from __future__ import annotations

from pathlib import Path

from tests.script_main import load_script_module

from .support import ROOT

SCRIPT = ROOT / "scripts" / "gates" / "check_path_independence.py"


def _gate():
    return load_script_module("check_path_independence_for_test", SCRIPT)


def test_gate_pins_interpreter_and_strips_path(tmp_path: Path, monkeypatch) -> None:
    """The child runner keeps this interpreter; only PATH is minimal."""
    from types import SimpleNamespace

    surface = tmp_path / "tests" / "charness_cli"
    surface.mkdir(parents=True)
    (surface / "test_task_run_probe.py").write_text("x = 1\n", encoding="utf-8")
    module = _gate()
    captured: dict[str, object] = {}

    def fake_phase(command: list[str], **kwargs: object):
        captured["args"] = command
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=3)

    monkeypatch.setattr(module, "run_monitored_phase", fake_phase)
    monkeypatch.setattr(
        module.sys, "argv", ["check_path_independence.py", "--repo-root", str(tmp_path)]
    )
    assert module.main() == 3

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["cwd"] == tmp_path.resolve()
    assert kwargs["timeout_seconds"] is None
    assert kwargs["capture"] is False
    env = kwargs["env"]
    assert isinstance(env, dict)
    assert env["PATH"] == module.MINIMAL_PATH
    assert env["CHARNESS_STANDING_PYTEST_PYTHON"] == module.sys.executable
    args = captured["args"]
    assert isinstance(args, list)
    assert args[0] == module.sys.executable
    assert args[1] == "scripts/gates_support/run_standing_pytest.py"
    assert "--pytest-target" in args
    assert "tests/charness_cli/test_task_run_probe.py" in args


def test_gate_skips_repos_without_surface(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A repo without the surface reports the skip instead of failing."""
    module = _gate()
    monkeypatch.setattr(
        module.sys, "argv", ["check_path_independence.py", "--repo-root", str(tmp_path)]
    )
    assert module.main() == 0
    assert "nothing to check" in capsys.readouterr().out


def test_gate_entry_point_reports_skip_as_main(tmp_path: Path) -> None:
    """Running the script as __main__ covers the entry guard end to end."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "nothing to check" in result.stdout
