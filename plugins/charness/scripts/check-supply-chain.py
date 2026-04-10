#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


class ValidationError(Exception):
    pass


JS_LOCKFILES = {
    "npm": ("package-lock.json",),
    "pnpm": ("pnpm-lock.yaml",),
    "yarn": ("yarn.lock",),
    "bun": ("bun.lock", "bun.lockb"),
}
JS_DEPENDENCY_KEYS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
PACKAGE_MANAGER_RE = re.compile(r"^(?P<name>[a-z0-9._-]+)@")


def load_package_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: top-level JSON value must be an object")
    return data


def package_has_dependencies(data: dict[str, object]) -> bool:
    for key in JS_DEPENDENCY_KEYS:
        value = data.get(key)
        if isinstance(value, dict) and value:
            return True
    return False


def parse_package_manager(package_manager: object) -> str | None:
    if not isinstance(package_manager, str):
        return None
    match = PACKAGE_MANAGER_RE.match(package_manager)
    if not match:
        return None
    return match.group("name")


def existing_js_lockfiles(repo_root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for manager, filenames in JS_LOCKFILES.items():
        for filename in filenames:
            path = repo_root / filename
            if path.exists():
                found[manager] = path
                break
    return found


def detect_declared_python_dependencies(pyproject_path: Path) -> bool:
    contents = pyproject_path.read_text(encoding="utf-8")
    if tomllib is not None:
        try:
            data = tomllib.loads(contents)
        except tomllib.TOMLDecodeError as exc:
            raise ValidationError(f"{pyproject_path}: invalid TOML: {exc}") from exc
        project = data.get("project")
        if isinstance(project, dict):
            dependencies = project.get("dependencies")
            if isinstance(dependencies, list) and dependencies:
                return True
            optional = project.get("optional-dependencies")
            if isinstance(optional, dict) and any(isinstance(value, list) and value for value in optional.values()):
                return True
        dependency_groups = data.get("dependency-groups")
        if isinstance(dependency_groups, dict) and any(
            isinstance(value, list) and value for value in dependency_groups.values()
        ):
            return True
        tool = data.get("tool")
        if isinstance(tool, dict):
            poetry = tool.get("poetry")
            if isinstance(poetry, dict):
                dependencies = poetry.get("dependencies")
                if isinstance(dependencies, dict):
                    non_python_keys = [key for key in dependencies if key != "python"]
                    if non_python_keys:
                        return True
    return bool(
        re.search(r"(?m)^\s*dependencies\s*=\s*\[\s*\S", contents)
        or re.search(r"(?m)^\s*\[project\.optional-dependencies\]\s*$", contents)
        or re.search(r"(?m)^\s*\[dependency-groups\]\s*$", contents)
        or re.search(r"(?m)^\s*\[tool\.poetry\.dependencies\]\s*$", contents)
    )


def validate_javascript_surface(repo_root: Path, findings: list[str]) -> None:
    package_json = repo_root / "package.json"
    found_lockfiles = existing_js_lockfiles(repo_root)
    if not package_json.exists():
        if found_lockfiles:
            rendered = ", ".join(sorted(path.name for path in found_lockfiles.values()))
            raise ValidationError(
                f"found JavaScript lockfile(s) without package.json: {rendered}; keep manifests and lockfiles aligned"
            )
        return

    data = load_package_json(package_json)
    has_dependencies = package_has_dependencies(data)
    declared_manager = parse_package_manager(data.get("packageManager"))
    if len(found_lockfiles) > 1:
        rendered = ", ".join(sorted(path.name for path in found_lockfiles.values()))
        raise ValidationError(f"multiple JavaScript lockfiles present ({rendered}); keep one package manager surface")

    manager = declared_manager
    if manager is None and found_lockfiles:
        manager = next(iter(found_lockfiles))
    if manager in JS_LOCKFILES:
        if not found_lockfiles.get(manager):
            expected = " or ".join(JS_LOCKFILES[manager])
            raise ValidationError(f"packageManager declares `{manager}` but `{expected}` is missing")
        findings.append(f"{manager}:{found_lockfiles[manager].name}")
        return

    if declared_manager is not None and declared_manager not in JS_LOCKFILES:
        findings.append(f"js:{declared_manager}:unsupported-manager")
        return

    if has_dependencies and not found_lockfiles:
        raise ValidationError(
            "package.json declares dependencies but no lockfile is checked in; add package-lock.json, pnpm-lock.yaml, yarn.lock, or bun.lockb"
        )
    if found_lockfiles:
        inferred_manager, lockfile_path = next(iter(found_lockfiles.items()))
        findings.append(f"{inferred_manager}:{lockfile_path.name}")
    elif package_json.exists():
        findings.append("js:manifest-only")


def validate_python_surface(repo_root: Path, findings: list[str]) -> None:
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return

    has_dependencies = detect_declared_python_dependencies(pyproject)
    uv_lock = repo_root / "uv.lock"
    if has_dependencies and not uv_lock.exists():
        raise ValidationError(
            "pyproject.toml declares Python dependencies but uv.lock is missing; check in the lockfile or keep the project dependency-free"
        )

    if has_dependencies:
        findings.append("uv:uv.lock")
    else:
        findings.append("python:manifest-only")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings: list[str] = []

    validate_javascript_surface(repo_root, findings)
    validate_python_surface(repo_root, findings)

    if not findings:
        print("No supported supply-chain surfaces detected.")
        return 0

    print("Validated supply-chain surfaces: " + ", ".join(findings))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
