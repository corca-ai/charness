#!/usr/bin/env python3

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

PACKAGE_MANAGER_KEYS = ("npm", "cargo", "go")


def _run_command(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def detect_binary_name(manifest: dict[str, Any]) -> str | None:
    detect = manifest.get("checks", {}).get("detect", {})
    commands = detect.get("commands", [])
    if not isinstance(commands, list) or not commands:
        return None
    first = commands[0]
    if not isinstance(first, str):
        return None
    parts = shlex.split(first)
    if not parts:
        return None
    return parts[0]


def detect_package_manager_prefixes() -> dict[str, str]:
    prefixes: dict[str, str] = {}
    npm_prefix = _run_command(["npm", "prefix", "-g"])
    if npm_prefix:
        prefixes["npm"] = npm_prefix
    cargo_home = os.environ.get("CARGO_HOME")
    if cargo_home:
        prefixes["cargo"] = str(Path(cargo_home).expanduser().resolve())
    else:
        default_cargo_home = Path.home() / ".cargo"
        if default_cargo_home.exists():
            prefixes["cargo"] = str(default_cargo_home.resolve())
    gopath = os.environ.get("GOPATH") or _run_command(["go", "env", "GOPATH"])
    if gopath:
        prefixes["go"] = str(Path(gopath).expanduser().resolve())
    elif (Path.home() / "go").exists():
        prefixes["go"] = str((Path.home() / "go").resolve())
    return prefixes


def _path_matches_manager(binary_path: Path, resolved_path: Path, manager: str, prefix: Path) -> bool:
    candidates = [binary_path, resolved_path]
    if manager == "npm":
        expected_roots = [prefix / "bin", prefix / "lib" / "node_modules"]
    elif manager == "cargo":
        expected_roots = [prefix / "bin"]
    elif manager == "go":
        expected_roots = [prefix / "bin"]
    else:
        expected_roots = [prefix]
    for candidate in candidates:
        for root in expected_roots:
            try:
                candidate.relative_to(root)
                return True
            except ValueError:
                continue
    return False


def detect_install_provenance(manifest: dict[str, Any]) -> dict[str, Any]:
    binary_name = detect_binary_name(manifest)
    if binary_name is None:
        return {
            "checked_at": None,
            "binary_name": None,
            "status": "unknown",
            "install_method": "unknown",
            "binary_path": None,
            "resolved_path": None,
            "package_name": None,
            "package_manager_prefix": None,
            "available_package_managers": [],
            "update_supported": False,
        }

    available_prefixes = detect_package_manager_prefixes()
    binary_path_string = shutil.which(binary_name)
    if binary_path_string is None:
        return {
            "checked_at": None,
            "binary_name": binary_name,
            "status": "missing",
            "install_method": "missing",
            "binary_path": None,
            "resolved_path": None,
            "package_name": None,
            "package_manager_prefix": None,
            "available_package_managers": sorted(available_prefixes.keys()),
            "update_supported": False,
        }

    binary_path = Path(binary_path_string).expanduser()
    resolved_path = binary_path.resolve(strict=False)
    package_managers = manifest.get("package_managers", {})
    for manager in PACKAGE_MANAGER_KEYS:
        prefix_string = available_prefixes.get(manager)
        if prefix_string is None:
            continue
        prefix = Path(prefix_string).expanduser().resolve(strict=False)
        if not _path_matches_manager(binary_path, resolved_path, manager, prefix):
            continue
        package_name = None
        if isinstance(package_managers, dict):
            manager_meta = package_managers.get(manager)
            if isinstance(manager_meta, dict):
                candidate = manager_meta.get("package_name")
                if isinstance(candidate, str):
                    package_name = candidate
        return {
            "checked_at": None,
            "binary_name": binary_name,
            "status": "detected",
            "install_method": manager,
            "binary_path": str(binary_path),
            "resolved_path": str(resolved_path),
            "package_name": package_name,
            "package_manager_prefix": str(prefix),
            "available_package_managers": sorted(available_prefixes.keys()),
            "update_supported": package_name is not None,
        }

    return {
        "checked_at": None,
        "binary_name": binary_name,
        "status": "detected",
        "install_method": "path",
        "binary_path": str(binary_path),
        "resolved_path": str(resolved_path),
        "package_name": None,
        "package_manager_prefix": None,
        "available_package_managers": sorted(available_prefixes.keys()),
        "update_supported": False,
    }


def package_manager_update_action(manifest: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any] | None:
    if provenance.get("status") != "detected":
        return None
    manager = provenance.get("install_method")
    if not isinstance(manager, str):
        return None
    package_managers = manifest.get("package_managers", {})
    if not isinstance(package_managers, dict):
        return None
    manager_meta = package_managers.get(manager)
    if not isinstance(manager_meta, dict):
        return None
    package_name = manager_meta.get("package_name")
    if not isinstance(package_name, str) or not package_name:
        return None
    if manager == "npm":
        commands = [f"npm install -g {package_name}@latest"]
    elif manager == "cargo":
        commands = [f"cargo install {package_name} --force"]
    elif manager == "go":
        commands = [f"go install {package_name}@latest"]
    else:
        return None
    notes = manager_meta.get("notes", [])
    return {
        "mode": "package_manager",
        "package_manager": manager,
        "package_name": package_name,
        "commands": commands,
        "notes": notes if isinstance(notes, list) else [],
    }
