#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
validate_sibling_followups = _scripts_artifact_validator_module.validate_sibling_followups

# Shared single source of the disposition-form grammar (#329); imported same-root
# so the session-retro `## Next Improvements` floor never forks achieve parsing.
disposition_form = import_repo_module(__file__, "scripts.disposition_form")

NEXT_IMPROVEMENTS_HEADING = "## Next Improvements"
DISPOSITION_FORM_REFERENCE = "skills/public/achieve/references/goal-artifact.md (#329 disposition-form floor)"
_DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\b")

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


def _retro_date(lines: list[str]) -> date | None:
    """Parse the retro's ``Date: YYYY-MM-DD`` line; ``None`` when absent/malformed."""
    for line in lines[:5]:
        match = _DATE_LINE.match(line.strip())
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
    return None


def _date_from_filename(path: Path) -> date | None:
    """The leading ``YYYY-MM-DD`` of the retro filename, ``None`` when absent."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _retro_observed_date(path: Path, lines: list[str]) -> date | None:
    """The retro's effective date for grandfathering: the in-body ``Date:`` line,
    else the leading ``YYYY-MM-DD`` of the filename. Many frozen historical retros
    predate the ``Date:`` header convention but are still dated by filename, so the
    filename fallback keeps them grandfathered (Goodhart Non-Goal). Only a retro
    with neither falls through to ``None`` -> fail-closed enforcement, which also
    blocks dodging the floor by stripping the date line of a current-dated file."""
    return _retro_date(lines) or _date_from_filename(path)


def _next_improvements_body(lines: list[str]) -> str:
    """Return the ``## Next Improvements`` section body (heading excluded), from
    its heading to the next ``## `` heading or EOF. Empty string when absent."""
    start = None
    for index, line in enumerate(lines):
        if line.strip() == NEXT_IMPROVEMENTS_HEADING:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def validate_disposition_forms(lines: list[str], observed_date: date | None) -> None:
    """Fail when an in-scope retro's ``## Next Improvements`` carries a disposition
    line in an invalid form (#329). Grandfathered for retros dated before the
    form rule date; form/enum only — substance stays the reviewer's job."""
    if not disposition_form.is_form_enforced(observed_date):
        return
    invalid = disposition_form.invalid_dispositions(_next_improvements_body(lines))
    if not invalid:
        return
    offenders = "; ".join(f"`{entry['marker']}: {entry['value'][:80]}`" for entry in invalid)
    raise ValidationError(
        f"`{NEXT_IMPROVEMENTS_HEADING}` has {len(invalid)} disposition line(s) in an invalid form "
        f"(offenders: {offenders}); each disposition must be one of "
        f"{disposition_form.VALID_FORM_SUMMARY} — a bare `memory`/prose-only disposition is rejected. "
        f"See {DISPOSITION_FORM_REFERENCE}."
    )


def validate_retro_artifact(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    validate_sibling_followups(
        lines,
        boundary_headings=SIBLING_BOUNDARY_HEADINGS,
        source_reference=SIBLING_SOURCE_REFERENCE,
    )
    validate_disposition_forms(lines, _retro_observed_date(path, lines))


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
