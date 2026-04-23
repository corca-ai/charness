#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


class BootstrapRuntimeError(Exception):
    pass


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_command(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def expect_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        raise BootstrapRuntimeError(
            f"{context} failed with exit code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def load_contract(repo_root: Path, contract_path: Path | None = None) -> dict[str, object]:
    path = contract_path or (repo_root / "packaging" / "bootstrap-python.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BootstrapRuntimeError(f"missing bootstrap runtime contract `{path}`") from exc
    except json.JSONDecodeError as exc:
        raise BootstrapRuntimeError(f"invalid bootstrap runtime contract `{path}`: {exc}") from exc
    if not isinstance(data, dict):
        raise BootstrapRuntimeError(f"bootstrap runtime contract `{path}` must be a JSON object")
    return data


def validate_contract(contract: dict[str, object], contract_path: Path) -> dict[str, object]:
    if contract.get("schema_version") != 1:
        raise BootstrapRuntimeError(f"`{contract_path}` must declare `schema_version: 1`")
    python_section = contract.get("python")
    if not isinstance(python_section, dict):
        raise BootstrapRuntimeError(f"`{contract_path}` must declare a `python` object")
    min_version = python_section.get("min_version")
    if not isinstance(min_version, str) or not min_version:
        raise BootstrapRuntimeError(f"`{contract_path}` must declare `python.min_version`")
    runtime_dir = contract.get("runtime_dir")
    if not isinstance(runtime_dir, str) or not runtime_dir:
        raise BootstrapRuntimeError(f"`{contract_path}` must declare `runtime_dir`")
    requirements_file = contract.get("requirements_file")
    if not isinstance(requirements_file, str) or not requirements_file:
        raise BootstrapRuntimeError(f"`{contract_path}` must declare `requirements_file`")
    required_modules = contract.get("required_modules")
    if not isinstance(required_modules, list) or not required_modules:
        raise BootstrapRuntimeError(f"`{contract_path}` must declare a non-empty `required_modules` list")
    for index, module_name in enumerate(required_modules):
        if not isinstance(module_name, str) or not module_name:
            raise BootstrapRuntimeError(f"`{contract_path}` has invalid `required_modules[{index}]`")
    return {
        "min_version": min_version,
        "runtime_dir": runtime_dir,
        "requirements_file": requirements_file,
        "required_modules": required_modules,
    }


def python_in_runtime(runtime_dir: Path) -> Path:
    if os.name == "nt":
        return runtime_dir / "Scripts" / "python.cmd"
    return runtime_dir / "bin" / "python"


def site_packages_dir(runtime_dir: Path) -> Path:
    return runtime_dir / "site-packages"


def parse_min_version(value: str) -> tuple[int, int]:
    parts = value.split(".")
    if len(parts) < 2:
        raise BootstrapRuntimeError(f"invalid minimum Python version `{value}`")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise BootstrapRuntimeError(f"invalid minimum Python version `{value}`") from exc


def python_info(python_cmd: str) -> dict[str, object]:
    result = run_command(
        [
            python_cmd,
            "-c",
            (
                "import json, sys; "
                "print(json.dumps({'executable': sys.executable, 'version': list(sys.version_info[:3])}))"
            ),
        ]
    )
    expect_success(result, f"`{python_cmd}` interpreter probe")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise BootstrapRuntimeError(f"`{python_cmd}` interpreter probe returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise BootstrapRuntimeError(f"`{python_cmd}` interpreter probe returned an invalid payload")
    executable = payload.get("executable")
    version = payload.get("version")
    if not isinstance(executable, str) or not executable:
        raise BootstrapRuntimeError(f"`{python_cmd}` interpreter probe did not report an executable path")
    if not isinstance(version, list) or len(version) != 3 or not all(isinstance(part, int) for part in version):
        raise BootstrapRuntimeError(f"`{python_cmd}` interpreter probe did not report a valid version")
    return {"executable": executable, "version": tuple(version)}


def ensure_min_version(info: dict[str, object], minimum: tuple[int, int]) -> None:
    version = info["version"]
    assert isinstance(version, tuple)
    current = version[:2]
    if current < minimum:
        raise BootstrapRuntimeError(
            "charness bootstrap requires Python "
            f"{minimum[0]}.{minimum[1]}+ but `{info['executable']}` is "
            f"{version[0]}.{version[1]}.{version[2]}"
        )


def modules_available(python_path: Path, required_modules: list[str]) -> bool:
    if not python_path.exists():
        return False
    probe = (
        "import importlib.util, sys\n"
        f"modules = {required_modules!r}\n"
        "missing = [name for name in modules if importlib.util.find_spec(name) is None]\n"
        "sys.exit(0 if not missing else 1)\n"
    )
    result = run_command([str(python_path), "-c", probe])
    return result.returncode == 0


def pip_available(python_path: Path) -> bool:
    result = run_command([str(python_path), "-m", "pip", "--version"])
    return result.returncode == 0


def install_requirements(python_path: Path, requirements_path: Path, target_dir: Path) -> None:
    if not requirements_path.is_file():
        raise BootstrapRuntimeError(f"missing bootstrap requirements file `{requirements_path}`")
    if not pip_available(python_path):
        raise BootstrapRuntimeError(
            f"`{python_path}` does not provide `pip`; install Python with pip support and rerun `init.sh`"
        )
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    result = run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--target",
            str(target_dir),
            "-r",
            str(requirements_path),
        ]
    )
    expect_success(result, f"`{python_path}` bootstrap dependency install from `{requirements_path}`")


def write_launcher(launcher_path: Path, base_python: str, target_dir: Path) -> None:
    launcher_path.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        launcher_path.write_text(
            "\r\n".join(
                [
                    "@echo off",
                    f"set \"PYTHONPATH={target_dir};%PYTHONPATH%\"",
                    f"\"{base_python}\" %*",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        launcher_path.write_text(
            "\n".join(
                [
                    "#!/bin/sh",
                    f"PYTHONPATH={shlex.quote(str(target_dir))}${{PYTHONPATH:+:${{PYTHONPATH}}}}",
                    "export PYTHONPATH",
                    f"exec {shlex.quote(base_python)} \"$@\"",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    launcher_path.chmod(0o755)


def ensure_bootstrap_runtime(
    repo_root: Path,
    *,
    base_python: str,
    contract_path: Path | None = None,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    resolved_contract_path = contract_path.resolve() if contract_path is not None else (repo_root / "packaging" / "bootstrap-python.json")
    contract = validate_contract(load_contract(repo_root, resolved_contract_path), resolved_contract_path)
    info = python_info(base_python)
    minimum = parse_min_version(contract["min_version"])
    ensure_min_version(info, minimum)

    runtime_dir = repo_root / str(contract["runtime_dir"])
    python_path = python_in_runtime(runtime_dir)
    packages_dir = site_packages_dir(runtime_dir)
    requirements_path = repo_root / str(contract["requirements_file"])
    required_modules = [str(item) for item in contract["required_modules"]]
    base_python_path = Path(str(info["executable"]))

    created = False
    installed = False

    if not python_path.exists():
        created = True
        write_launcher(python_path, str(info["executable"]), packages_dir)

    if not modules_available(python_path, required_modules):
        write_launcher(python_path, str(info["executable"]), packages_dir)

    if not modules_available(python_path, required_modules) and not modules_available(base_python_path, required_modules):
        install_requirements(Path(str(info["executable"])), requirements_path, packages_dir)
        write_launcher(python_path, str(info["executable"]), packages_dir)
        installed = True

    if not modules_available(python_path, required_modules):
        raise BootstrapRuntimeError(
            f"bootstrap runtime `{python_path}` is still missing required modules {required_modules}"
        )

    return {
        "repo_root": str(repo_root),
        "base_python": str(info["executable"]),
        "base_version": list(info["version"]),
        "runtime_dir": str(runtime_dir),
        "python": str(python_path),
        "site_packages_dir": str(packages_dir),
        "requirements_file": str(requirements_path),
        "required_modules": required_modules,
        "created": created,
        "installed": installed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or reuse the repo-owned bootstrap Python runtime used by install/update flows."
    )
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    parser.add_argument("--base-python", default=sys.executable)
    parser.add_argument("--contract-path", type=Path)
    parser.add_argument("--print-python", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = ensure_bootstrap_runtime(
        args.repo_root,
        base_python=args.base_python,
        contract_path=args.contract_path,
    )
    if args.print_python:
        print(payload["python"])
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BootstrapRuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
