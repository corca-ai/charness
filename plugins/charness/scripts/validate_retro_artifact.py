#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
validate_sibling_followups = _scripts_artifact_validator_module.validate_sibling_followups

RETRO_ARTIFACT_PREFIX = "charness-artifacts/retro/"
GENERATED_DIGEST = "recent-lessons.md"
SIBLING_BOUNDARY_HEADINGS = (
    "## Context",
    "## Window",
    "## Evidence Summary",
    "## Waste",
    "## Critical Decisions",
    "## Trends vs Last Retro",
    "## Expert Counterfactuals",
    "## Next Improvements",
    "## Persisted",
)
SIBLING_SOURCE_REFERENCE = "skills/public/retro/references/waste-sibling-scan.md"


def _git_paths(repo_root: Path, args: list[str]) -> list[str]:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        message = (
            "retro artifact changed-path discovery failed; "
            f"command: {' '.join(command)}; exit_code: {result.returncode}"
        )
        if detail:
            message = f"{message}; output: {detail}"
        raise ValidationError(message)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_paths(repo_root: Path) -> list[str]:
    paths = set(_git_paths(repo_root, ["diff", "--name-only", "HEAD", "--"]))
    paths.update(_git_paths(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(paths)


def _is_session_artifact(relpath: str) -> bool:
    if not relpath.startswith(RETRO_ARTIFACT_PREFIX) or not relpath.endswith(".md"):
        return False
    tail = relpath[len(RETRO_ARTIFACT_PREFIX) :]
    if "/" in tail:  # skip history/ and other nested archives
        return False
    return tail != GENERATED_DIGEST


def candidate_paths(repo_root: Path, paths: list[str], *, all_artifacts: bool) -> list[Path]:
    if all_artifacts:
        return sorted(
            path
            for path in (repo_root / RETRO_ARTIFACT_PREFIX).glob("*.md")
            if path.name != GENERATED_DIGEST
        )
    candidates: list[Path] = []
    for relpath in paths:
        if _is_session_artifact(relpath):
            path = repo_root / relpath
            if path.is_file():
                candidates.append(path)
    return sorted(candidates)


def validate_retro_artifact(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    validate_sibling_followups(
        lines,
        boundary_headings=SIBLING_BOUNDARY_HEADINGS,
        source_reference=SIBLING_SOURCE_REFERENCE,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to changed paths.")
    parser.add_argument("--all", action="store_true", help="Validate every checked retro session artifact.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = [] if args.all else args.paths if args.paths is not None else changed_paths(repo_root)
    artifacts = candidate_paths(repo_root, paths, all_artifacts=args.all)
    for artifact in artifacts:
        validate_retro_artifact(artifact)
    print(f"Validated {len(artifacts)} retro artifact(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
