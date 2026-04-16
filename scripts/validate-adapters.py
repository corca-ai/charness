#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files


class ValidationError(Exception):
    pass


def expected_artifact_filename(skill_id: str) -> str:
    return current_artifact_filename(skill_id)


def validate_resolver(path: Path, root: Path) -> None:
    skill_id = path.parent.parent.name
    completed = subprocess.run(
        ["python3", str(path), "--repo-root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValidationError(f"{path}: exited with code {completed.returncode}: {completed.stderr.strip()}")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: did not emit valid JSON") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{path}: JSON output must be an object")
    if data.get("valid") is not True:
        raise ValidationError(f"{path}: expected `valid=true`, got {data.get('valid')!r}")

    expected_filename = expected_artifact_filename(skill_id)
    actual_filename = data.get("artifact_filename")
    if actual_filename is not None and actual_filename != expected_filename:
        raise ValidationError(
            f"{path}: expected artifact_filename `{expected_filename}`, got `{actual_filename}`"
        )

    artifact_path = data.get("artifact_path")
    if artifact_path is not None and not artifact_path.endswith(expected_filename):
        raise ValidationError(
            f"{path}: artifact_path must end with `{expected_filename}`, got `{artifact_path}`"
        )


def iter_resolvers(root: Path) -> list[Path]:
    return iter_matching_repo_files(root, ("skills/public/*/scripts/resolve_adapter.py",))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    resolvers = iter_resolvers(root)
    if not resolvers:
        print("No adapter resolvers found.")
        return 0

    for resolver in resolvers:
        validate_resolver(resolver, root)

    print(f"Validated {len(resolvers)} adapter resolvers.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
