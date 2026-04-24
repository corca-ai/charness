from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_RUNTIME_PATH = ROOT / "scripts" / "bootstrap_runtime.py"
CHARNESS_PATH = ROOT / "charness"
INIT_SH_PATH = ROOT / "init.sh"


def load_module(module_name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(module_name, str(path))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_bootstrap_runtime_creates_runtime_and_installs_requirements(tmp_path: Path, monkeypatch) -> None:
    module = load_module("bootstrap_runtime_test_create", BOOTSTRAP_RUNTIME_PATH)
    repo_root = tmp_path / "repo"
    copy_bootstrap_contract(repo_root)
    runtime_python = repo_root / ".charness" / "bootstrap-python" / ("Scripts/python.cmd" if os.name == "nt" else "bin/python")
    commands: list[list[str]] = []
    requirements_installed = {"value": False}
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

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
            str(repo_root / ".charness" / "bootstrap-python" / "site-packages"),
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
    runtime_python = repo_root / ".charness" / "bootstrap-python" / ("Scripts/python.cmd" if os.name == "nt" else "bin/python")
    runtime_python.parent.mkdir(parents=True, exist_ok=True)
    runtime_python.write_text("# stale launcher\n", encoding="utf-8")
    commands: list[list[str]] = []
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

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
    runtime_python = repo_root / ".charness" / "bootstrap-python" / ("Scripts/python.cmd" if os.name == "nt" else "bin/python")
    runtime_python.parent.mkdir(parents=True, exist_ok=True)
    runtime_python.write_text("", encoding="utf-8")
    commands: list[list[str]] = []
    module_probe = "import importlib, sys\nmodules = ['jsonschema', 'packaging']\nmissing = []\nfor name in modules:\n    try:\n        importlib.import_module(name)\n    except Exception:\n        missing.append(name)\nsys.exit(0 if not missing else 1)\n"

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
    commands: list[list[str]] = []

    def fake_run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        del cwd
        commands.append(command)
        if command[:2] == [sys.executable, "scripts/bootstrap_runtime.py"]:
            return completed(command, stdout="/tmp/charness-bootstrap/bin/python\n")
        if command == ["/tmp/charness-bootstrap/bin/python", "scripts/example.py", "--flag"]:
            return completed(command, stdout="ok\n")
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module, "run", fake_run)
    module._BOOTSTRAP_PYTHON_CACHE.clear()

    result = module.invoke_repo_script(repo_root, "scripts/example.py", "--flag")

    assert result == "ok"
    assert commands[0][:2] == [sys.executable, "scripts/bootstrap_runtime.py"]
    assert commands[1][0] == "/tmp/charness-bootstrap/bin/python"


def test_init_sh_falls_back_to_python_when_python3_is_missing(tmp_path: Path) -> None:
    fixture_repo = tmp_path / "fixture-repo"
    (fixture_repo / "scripts").mkdir(parents=True)
    (fixture_repo / "packaging").mkdir(parents=True)
    (fixture_repo / "scripts" / "bootstrap_runtime.py").write_text("# fixture\n", encoding="utf-8")
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
        "if [ \"$1\" = scripts/bootstrap_runtime.py ]; then\n"
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
    assert "scripts/bootstrap_runtime.py" in python_log.read_text(encoding="utf-8")
    assert bootstrap_log.read_text(encoding="utf-8").splitlines()[:2] == ["./charness", "init"]
