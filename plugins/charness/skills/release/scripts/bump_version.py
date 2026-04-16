#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-[0-9A-Za-z.-]+)?$")


def parse_version(version: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if match is None:
        raise SystemExit(f"Unsupported version format: {version}")
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


def bump_part(version: str, part: str) -> str:
    major, minor, patch = parse_version(version)
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "major":
        return f"{major + 1}.0.0"
    raise SystemExit(f"Unsupported bump part: {part}")


def write_packaging_version(manifest_path: Path, new_version: str) -> str:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_version = data["version"]
    data["version"] = new_version
    data["claude"]["manifest"]["version"] = new_version
    data["codex"]["manifest"]["version"] = new_version
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return old_version


def run_sync(repo_root: Path, command: str) -> None:
    result = subprocess.run(command, cwd=repo_root, shell=True, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"sync_command failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--part", choices=("patch", "minor", "major"))
    group.add_argument("--set-version")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    data = adapter["data"]
    manifest_path = repo_root / data["packaging_manifest_path"]
    if not manifest_path.is_file():
        raise SystemExit(f"Packaging manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_version = manifest["version"]
    target_version = args.set_version or bump_part(current_version, args.part)
    old_version = write_packaging_version(manifest_path, target_version)
    run_sync(repo_root, data["sync_command"])

    print(
        json.dumps(
            {
                "package_id": data["package_id"],
                "old_version": old_version,
                "new_version": target_version,
                "packaging_manifest_path": str(manifest_path),
                "sync_command": data["sync_command"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
