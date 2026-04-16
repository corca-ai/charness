#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "debug" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "debug" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("debug resolve_adapter.py not found")


_debug_resolve_adapter = load_path_module("debug_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _debug_resolve_adapter.load_adapter
_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_date_line = _scripts_artifact_validator_module.validate_date_line
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
validate_max_lines = _scripts_artifact_validator_module.validate_max_lines
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
validate_title = _scripts_artifact_validator_module.validate_title

MAX_ARTIFACT_LINES = 140
REQUIRED_SECTIONS = (
    "## Problem",
    "## Correct Behavior",
    "## Observed Facts",
    "## Reproduction",
    "## Candidate Causes",
    "## Hypothesis",
    "## Verification",
    "## Root Cause",
    "## Prevention",
)
OPTIONAL_SECTIONS = (
    "## Related Prior Incidents",
)


def validate_candidate_causes(lines: list[str]) -> None:
    start = find_index(lines, "## Candidate Causes") + 1
    end = find_index(lines, "## Hypothesis")
    bullets = [line.strip() for line in lines[start:end] if line.strip().startswith("- ")]
    if len(bullets) < 3:
        raise ValidationError("`## Candidate Causes` must list at least three plausible causes")


def validate_debug_artifact(path: Path) -> None:
    lines = read_lines(path)
    validate_title(
        lines,
        title_predicate=lambda line: line.startswith("# ") and "debug" in line.lower(),
        error_message="debug artifact must start with a `# ... Debug ...` heading",
    )
    validate_date_line(lines)
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="debug artifact")
    validate_exact_h2_sections(lines, REQUIRED_SECTIONS, optional_sections=OPTIONAL_SECTIONS)
    validate_nonempty_sections(lines, REQUIRED_SECTIONS)
    validate_candidate_causes(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    output_dir = repo_root / adapter["data"]["output_dir"]
    if not output_dir.is_dir():
        print(f"No debug output directory at {output_dir.relative_to(repo_root)}.", file=sys.stderr)
        return 1
    artifacts = sorted(output_dir.glob("*.md"))
    if not artifacts:
        print(f"No debug artifacts found in {output_dir.relative_to(repo_root)}.", file=sys.stderr)
        return 1
    for artifact_path in artifacts:
        validate_debug_artifact(artifact_path)
        print(f"Validated debug artifact {artifact_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
