from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from .support import load_cli_module, pin_state_home

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_RUNTIME_PATH = ROOT / "scripts" / "core" / "bootstrap_runtime.py"
CHARNESS_PATH = ROOT / "charness"
INIT_SH_PATH = ROOT / "init.sh"


def load_module(module_name: str, path: Path):
    return load_cli_module(module_name, path)


def copy_bootstrap_contract(repo_root: Path) -> None:
    packaging_dir = repo_root / "packaging"
    packaging_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "packaging" / "bootstrap-python.json", packaging_dir / "bootstrap-python.json")
    shutil.copy2(
        ROOT / "packaging" / "bootstrap-requirements.txt",
        packaging_dir / "bootstrap-requirements.txt",
    )


def completed(command: list[str], *, returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def external_bootstrap_dir(monkeypatch, tmp_path: Path) -> Path:
    runtime_root = tmp_path / "external-runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)
    return runtime_root / "bootstrap-python"


def test_bootstrap_runtime_creates_runtime_and_installs_requirements(tmp_path: Path, monkeypatch) -> None:
    module = load_module("bootstrap_runtime_test_create", BOOTSTRAP_RUNTIME_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    runtime_dir = external_bootstrap_dir(monkeypatch, tmp_path)
    runtime_python = runtime_dir / ("Scripts/python.cmd" if os.name == "nt" else "bin/python")
    commands: list[list[str]] = []
    requirements_installed = {"value": False}
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging', 'yaml']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

    def fake_run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        if command[:2] == ["python", "-c"]:
            return completed(
                command,
                stdout='{"executable": "/usr/bin/python", "version": [3, 11, 9]}\n',
            )
        if command == ["/usr/bin/python", "-c", module_probe]:
            return completed(command, returncode=1)
        if command == [str(runtime_python), "-c", module_probe]:
            return completed(command, returncode=0 if requirements_installed["value"] else 1)
        if command == ["/usr/bin/python", "-m", "pip", "--version"]:
            return completed(command)
        if command == [
            "/usr/bin/python",
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--target",
            str(runtime_dir / "site-packages"),
            "-r",
            str(repo_root / "packaging" / "bootstrap-requirements.txt"),
        ]:
            requirements_installed["value"] = True
            return completed(command)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_command", fake_run)

    payload = module.ensure_bootstrap_runtime(repo_root, base_python="python")

    assert payload["created"] is True
    assert payload["installed"] is True
    assert payload["python"] == str(runtime_python)
    assert any(command[1:4] == ["-m", "pip", "install"] for command in commands)


def test_bootstrap_runtime_repairs_stale_launcher_when_base_has_modules(tmp_path: Path, monkeypatch) -> None:
    module = load_module("bootstrap_runtime_test_repair_stale_launcher", BOOTSTRAP_RUNTIME_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    runtime_python = external_bootstrap_dir(monkeypatch, tmp_path) / (
        "Scripts/python.cmd" if os.name == "nt" else "bin/python"
    )
    runtime_python.parent.mkdir(parents=True, exist_ok=True)
    runtime_python.write_text("# stale launcher\n", encoding="utf-8")
    commands: list[list[str]] = []
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging', 'yaml']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

    def fake_run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        if command[:2] == ["python", "-c"]:
            return completed(
                command,
                stdout='{"executable": "/usr/bin/current-python", "version": [3, 11, 9]}\n',
            )
        if command == [str(runtime_python), "-c", module_probe]:
            content = runtime_python.read_text(encoding="utf-8")
            return completed(command, returncode=0 if "/usr/bin/current-python" in content else 1)
        if command == ["/usr/bin/current-python", "-c", module_probe]:
            return completed(command)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_command", fake_run)

    payload = module.ensure_bootstrap_runtime(repo_root, base_python="python")

    assert payload["created"] is False
    assert payload["installed"] is False
    assert payload["python"] == str(runtime_python)
    assert "/usr/bin/current-python" in runtime_python.read_text(encoding="utf-8")
    assert not any(command[1:4] == ["-m", "pip", "install"] for command in commands)


def test_bootstrap_runtime_reuses_existing_runtime_when_modules_are_present(tmp_path: Path, monkeypatch) -> None:
    module = load_module("bootstrap_runtime_test_reuse", BOOTSTRAP_RUNTIME_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    runtime_python = external_bootstrap_dir(monkeypatch, tmp_path) / (
        "Scripts/python.cmd" if os.name == "nt" else "bin/python"
    )
    runtime_python.parent.mkdir(parents=True, exist_ok=True)
    runtime_python.write_text("", encoding="utf-8")
    commands: list[list[str]] = []
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging', 'yaml']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

    def fake_run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        if command[:2] == ["python", "-c"]:
            return completed(
                command,
                stdout='{"executable": "/usr/bin/python", "version": [3, 11, 9]}\n',
            )
        if command == [str(runtime_python), "-c", module_probe]:
            return completed(command)
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run_command", fake_run)

    payload = module.ensure_bootstrap_runtime(repo_root, base_python="python")

    assert payload["created"] is False
    assert payload["installed"] is False
    assert payload["python"] == str(runtime_python)
    assert not any(command[1:4] == ["-m", "pip", "install"] for command in commands)


def test_charness_invokes_repo_scripts_with_bootstrap_runtime(monkeypatch, tmp_path: Path) -> None:
    module = load_module("charness_bootstrap_runtime_test", CHARNESS_PATH)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    external_bootstrap_dir(monkeypatch, tmp_path)
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        if command[:2] == [sys.executable, "scripts/core/bootstrap_runtime.py"]:
            return completed(command, stdout="/tmp/charness-bootstrap/bin/python\n")
        if command == ["/tmp/charness-bootstrap/bin/python", "scripts/example.py", "--flag"]:
            return completed(command, stdout="ok\n")
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run", fake_run)
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    result = module.invoke_repo_script(repo_root, "scripts/example.py", "--flag")

    assert result == "ok"
    assert commands[0][:2] == [sys.executable, "scripts/core/bootstrap_runtime.py"]
    assert commands[1][0] == "/tmp/charness-bootstrap/bin/python"


def test_resolve_repo_python_reuses_healthy_launcher_without_bootstrap(monkeypatch, tmp_path: Path) -> None:
    module = load_module("charness_bootstrap_fast_path_healthy", CHARNESS_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    launcher = external_bootstrap_dir(monkeypatch, tmp_path) / (
        "Scripts/python.cmd" if os.name == "nt" else "bin/python"
    )
    launcher.parent.mkdir(parents=True)
    launcher.write_text("healthy launcher\n", encoding="utf-8")
    commands: list[list[str]] = []
    isolated_envs: list[dict[str, str] | None] = []

    def fake_run(
        command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        isolated_envs.append(env)
        assert command[0] == str(launcher)
        return completed(command)

    monkeypatch.setattr(module, "run", fake_run)
    monkeypatch.setenv("PYTHONPATH", "/foreign/runtime")
    monkeypatch.setenv("PYTHONHOME", "/foreign/home")
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    assert module.resolve_repo_python(repo_root) == str(launcher)
    assert len(commands) == 1
    assert isolated_envs == [env for env in isolated_envs if env and "PYTHONPATH" not in env and "PYTHONHOME" not in env]


def test_resolve_repo_python_bootstraps_when_launcher_is_absent(monkeypatch, tmp_path: Path) -> None:
    module = load_module("charness_bootstrap_fast_path_absent", CHARNESS_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    external_bootstrap_dir(monkeypatch, tmp_path)
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env
        commands.append(command)
        assert command[:2] == [sys.executable, "scripts/core/bootstrap_runtime.py"]
        return completed(command, stdout="/tmp/repaired/bin/python\n")

    monkeypatch.setattr(module, "run", fake_run)
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    assert module.resolve_repo_python(repo_root) == "/tmp/repaired/bin/python"
    assert len(commands) == 1


@pytest.mark.parametrize(
    ("field_path", "invalid_value"),
    [
        pytest.param(("schema_version",), 2, id="schema-version-unsupported"),
        pytest.param(("python", "min_version"), None, id="min-version-wrong-type"),
        pytest.param(("python", "min_version"), "3", id="min-version-too-short"),
        pytest.param(("python", "min_version"), "three.ten", id="min-version-not-numeric"),
        pytest.param(("runtime_dir",), "", id="runtime-dir-empty"),
        pytest.param(("requirements_file",), None, id="requirements-file-wrong-type"),
        pytest.param(("required_modules",), [], id="required-modules-empty"),
    ],
)
def test_resolve_repo_python_leaves_malformed_contracts_to_bootstrap(
    monkeypatch,
    tmp_path: Path,
    field_path: tuple[str, ...],
    invalid_value: object,
) -> None:
    module_name = "charness_bootstrap_fast_path_malformed_" + "_".join(field_path)
    module = load_module(module_name, CHARNESS_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    launcher = external_bootstrap_dir(monkeypatch, tmp_path) / (
        "Scripts/python.cmd" if os.name == "nt" else "bin/python"
    )
    launcher.parent.mkdir(parents=True)
    launcher.write_text("healthy launcher\n", encoding="utf-8")
    contract_path = repo_root / "packaging" / "bootstrap-python.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    target = contract
    for key in field_path[:-1]:
        target = target[key]
        assert isinstance(target, dict)
    target[field_path[-1]] = invalid_value
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env
        commands.append(command)
        assert command[:2] == [sys.executable, "scripts/core/bootstrap_runtime.py"]
        return completed(command, stdout="/tmp/repaired/bin/python\n")

    monkeypatch.setattr(module, "run", fake_run)
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    assert module.resolve_repo_python(repo_root) == "/tmp/repaired/bin/python"
    assert len(commands) == 1


@pytest.mark.parametrize(
    ("launcher_content", "requires_version_guard"),
    [
        pytest.param("stale launcher\n", False, id="probe-nonzero"),
        pytest.param("old launcher\n", True, id="python-too-old"),
    ],
)
def test_resolve_repo_python_bootstraps_when_launcher_probe_fails(
    monkeypatch,
    tmp_path: Path,
    launcher_content: str,
    requires_version_guard: bool,
) -> None:
    module = load_module(
        f"charness_bootstrap_fast_path_unhealthy_{requires_version_guard}",
        CHARNESS_PATH,
    )
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    launcher = external_bootstrap_dir(monkeypatch, tmp_path) / (
        "Scripts/python.cmd" if os.name == "nt" else "bin/python"
    )
    launcher.parent.mkdir(parents=True)
    launcher.write_text(launcher_content, encoding="utf-8")
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env
        commands.append(command)
        if command[0] == str(launcher):
            if requires_version_guard:
                assert "sys.version_info[:2] < minimum" in command[2]
            return completed(command, returncode=1)
        assert command[:2] == [sys.executable, "scripts/core/bootstrap_runtime.py"]
        return completed(command, stdout="/tmp/repaired/bin/python\n")

    monkeypatch.setattr(module, "run", fake_run)
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    assert module.resolve_repo_python(repo_root) == "/tmp/repaired/bin/python"
    assert [command[0] for command in commands] == [str(launcher), sys.executable]


@pytest.mark.skipif(os.name == "nt", reason="POSIX execute permissions provide the real probe failure")
def test_resolve_repo_python_bootstraps_when_launcher_is_not_executable(
    tmp_path: Path, monkeypatch
) -> None:
    module = load_module("charness_bootstrap_fast_path_non_executable", CHARNESS_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    launcher = external_bootstrap_dir(monkeypatch, tmp_path) / "bin" / "python"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("not executable\n", encoding="utf-8")
    launcher.chmod(0o644)
    bootstrap_script = repo_root / "scripts" / "core" / "bootstrap_runtime.py"
    bootstrap_script.parent.mkdir(parents=True)
    bootstrap_script.write_text("print('/tmp/repaired/bin/python')\n", encoding="utf-8")
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    assert module.resolve_repo_python(repo_root) == "/tmp/repaired/bin/python"


@pytest.mark.boundary_contract(
    reason="init.sh must bootstrap an exported checkout through a clean PATH"
)
def test_init_sh_falls_back_to_python_when_python3_is_missing(tmp_path: Path) -> None:
    fixture_repo = tmp_path / "fixture-repo"
    (fixture_repo / "scripts").mkdir(parents=True)
    (fixture_repo / "packaging").mkdir(parents=True)
    (fixture_repo / "scripts" / "core").mkdir(parents=True, exist_ok=True)
    (fixture_repo / "scripts" / "core").mkdir(parents=True, exist_ok=True)
    (fixture_repo / "scripts" / "core" / "bootstrap_runtime.py").write_text("# fixture\n", encoding="utf-8")
    (fixture_repo / "charness").write_text("# fixture\n", encoding="utf-8")
    init_copy = tmp_path / "init.sh"
    init_copy.write_text(INIT_SH_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    init_copy.chmod(0o755)

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    for name, target in {"mkdir": "/bin/mkdir", "dirname": "/usr/bin/dirname"}.items():
        wrapper = fake_bin / name
        wrapper.write_text(f"#!/bin/sh\nexec {target} \"$@\"\n", encoding="utf-8")
        wrapper.chmod(0o755)
    bootstrap_python = fake_bin / "bootstrap-python"
    bootstrap_log = tmp_path / "bootstrap.log"
    bootstrap_python.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$@\" > {bootstrap_log}\n"
        "exit 0\n",
        encoding="utf-8",
    )
    bootstrap_python.chmod(0o755)

    python_log = tmp_path / "python.log"
    fake_python = fake_bin / "python"
    fake_python.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$@\" >> {python_log}\n"
        "if [ \"$1\" = scripts/core/bootstrap_runtime.py ]; then\n"
        f"  printf '%s\\n' '{bootstrap_python}'\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    fake_git = fake_bin / "git"
    fake_git.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = clone ]; then\n"
        f"  /bin/cp -R {fixture_repo} \"$3\"\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake_git.chmod(0o755)

    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    pin_state_home(env, Path(env["HOME"]))
    env["PATH"] = str(fake_bin)
    result = subprocess.run(
        ["/bin/bash", str(init_copy)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "scripts/core/bootstrap_runtime.py" in python_log.read_text(encoding="utf-8")
    assert bootstrap_log.read_text(encoding="utf-8").splitlines()[:2] == ["./charness", "init"]
