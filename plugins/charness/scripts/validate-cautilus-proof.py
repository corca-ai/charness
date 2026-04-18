#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
ARTIFACT_PATH = Path("charness-artifacts/cautilus/latest.md")
MAX_ARTIFACT_LINES = 120
PROMPT_AFFECTING_PATTERNS = (
    "AGENTS.md",
    ".agents/*-adapter.yaml",
    ".agents/cautilus-adapters/*.yaml",
    "skills/public/*/SKILL.md",
    "skills/public/*/references/**",
    "skills/support/*/SKILL.md",
    "skills/support/*/references/**",
)
REQUIRED_SECTIONS = (
    "## Trigger",
    "## Validation Goal",
    "## Prompt Surfaces",
    "## Commands Run",
    "## Outcome",
    "## Follow-ups",
)
OPTIONAL_SECTIONS = ("## A/B Compare",)
RECOMMENDATION_PREFIX = "- recommendation: "
GOAL_PREFIX = "- goal: "
VALID_GOALS = {"preserve", "improve"}
INSTRUCTION_SURFACE_COMMAND = "cautilus instruction-surface test --repo-root ."
A_B_REQUIRED_SNIPPETS = (
    "baseline_ref:",
    "cautilus workspace prepare-compare",
    "cautilus mode evaluate",
)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
find_index = _scripts_artifact_validator_module.find_index
read_lines = _scripts_artifact_validator_module.read_lines
validate_date_line = _scripts_artifact_validator_module.validate_date_line
validate_exact_h2_sections = _scripts_artifact_validator_module.validate_exact_h2_sections
validate_max_lines = _scripts_artifact_validator_module.validate_max_lines
validate_nonempty_sections = _scripts_artifact_validator_module.validate_nonempty_sections
_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
normalize_repo_path = _scripts_surfaces_lib_module.normalize_repo_path


def path_matches_patterns(path: str, patterns: tuple[str, ...]) -> bool:
    normalized = normalize_repo_path(path)
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def section_lines(lines: list[str], heading: str) -> list[str]:
    headings = list(REQUIRED_SECTIONS) + list(OPTIONAL_SECTIONS)
    start = find_index(lines, heading) + 1
    end = len(lines)
    for candidate in headings:
        if candidate == heading:
            continue
        try:
            index = find_index(lines, candidate)
        except ValidationError:
            continue
        if index > start:
            end = min(end, index)
    return [line.strip() for line in lines[start:end] if line.strip()]


def prompt_affecting_paths(changed_paths: list[str]) -> list[str]:
    return [path for path in changed_paths if path_matches_patterns(path, PROMPT_AFFECTING_PATTERNS)]


def validate_title(lines: list[str]) -> None:
    if not lines or lines[0].strip() != "# Cautilus Dogfood":
        raise ValidationError("cautilus proof artifact must start with `# Cautilus Dogfood`")


def validate_validation_goal(lines: list[str]) -> str:
    values = [line[len(GOAL_PREFIX) :].strip(" `") for line in section_lines(lines, "## Validation Goal") if line.startswith(GOAL_PREFIX)]
    if len(values) != 1 or values[0] not in VALID_GOALS:
        raise ValidationError("`## Validation Goal` must contain exactly one `- goal: preserve|improve` line")
    return values[0]


def validate_prompt_surfaces(lines: list[str], changed_prompt_paths: list[str]) -> None:
    prompt_lines = section_lines(lines, "## Prompt Surfaces")
    missing = [path for path in changed_prompt_paths if not any(path in line for line in prompt_lines)]
    if missing:
        rendered = ", ".join(f"`{path}`" for path in missing)
        raise ValidationError(
            "`## Prompt Surfaces` must list every prompt-affecting changed path; missing "
            + rendered
        )


def validate_commands_run(lines: list[str], goal: str) -> None:
    command_lines = section_lines(lines, "## Commands Run")
    if not any(INSTRUCTION_SURFACE_COMMAND in line for line in command_lines):
        raise ValidationError(
            "`## Commands Run` must include `cautilus instruction-surface test --repo-root .`"
        )
    if goal != "improve":
        return
    try:
        compare_lines = section_lines(lines, "## A/B Compare")
    except ValidationError as exc:
        raise ValidationError("`## A/B Compare` is required when `goal: improve`") from exc
    for snippet in A_B_REQUIRED_SNIPPETS:
        if not any(snippet in line for line in compare_lines):
            raise ValidationError(
                "`## A/B Compare` must record baseline ref plus compare commands; missing "
                f"`{snippet}`"
            )


def validate_outcome(lines: list[str]) -> None:
    outcome_lines = section_lines(lines, "## Outcome")
    if not any(line.startswith(RECOMMENDATION_PREFIX) for line in outcome_lines):
        raise ValidationError("`## Outcome` must include a `- recommendation: ...` line")


def validate_cautilus_proof(repo_root: Path, changed_paths: list[str]) -> str:
    changed_prompt_paths = prompt_affecting_paths(changed_paths)
    if not changed_prompt_paths:
        return "no prompt-affecting changes detected"

    artifact_repo_path = ARTIFACT_PATH.as_posix()
    if artifact_repo_path not in changed_paths:
        raise ValidationError(
            "prompt-affecting changes require refreshing "
            f"`{artifact_repo_path}` in the same slice"
        )

    lines = read_lines(repo_root / ARTIFACT_PATH)
    validate_title(lines)
    validate_max_lines(lines, max_lines=MAX_ARTIFACT_LINES, artifact_label="cautilus proof artifact")
    validate_date_line(lines)
    validate_exact_h2_sections(lines, REQUIRED_SECTIONS, optional_sections=OPTIONAL_SECTIONS)
    validate_nonempty_sections(lines, REQUIRED_SECTIONS)
    goal = validate_validation_goal(lines)
    validate_prompt_surfaces(lines, changed_prompt_paths)
    validate_commands_run(lines, goal)
    validate_outcome(lines)
    return f"validated prompt-affecting cautilus proof for {len(changed_prompt_paths)} changed path(s)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    changed_paths = [normalize_repo_path(path) for path in args.paths] if args.paths else collect_changed_paths(repo_root)
    message = validate_cautilus_proof(repo_root, changed_paths)
    print(message)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
