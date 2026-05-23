"""Changed-file classification for mutation scope-gap reporting.

Selection predicates (whole-file coverage floor, whole-file mutation-line) stay
in `mutation_sampling_lib`; this module answers the change-set question only.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def changed_line_numbers(repo_root: Path, base_sha: str, head_sha: str, path: str) -> set[int]:
    """New-file line numbers changed for `path` over base..head.

    `--no-renames` makes a renamed-and-modified file read as a full addition so a
    rename never silently empties the set; the blocker then fails closed on it.
    """
    if not base_sha:
        return set()
    head = head_sha or "HEAD"
    command = ["git", "diff", "-U0", "--no-renames", f"{base_sha}..{head}", "--", path]
    result = subprocess.run(command, cwd=repo_root, check=True, text=True, capture_output=True)
    lines: set[int] = set()
    for match in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", result.stdout, re.MULTILINE):
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        lines.update(range(start, start + count))
    return lines


def classify_changed_line_scope_gap(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> list[str]:
    """Changed pool files whose changed lines are not test-covered (the blocker).

    Judges the change, not the whole file: a file blocks only if its changed
    lines include uncovered statements, or the suite never tracked the file.
    Pre-existing untested lines elsewhere in a touched file do not block.
    """
    if not coverage_enabled or not base_sha:
        return []
    gaps: list[str] = []
    for path in changed_before_coverage:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if not changed:
            continue
        if path not in statement_lines:
            gaps.append(path)
            continue
        _executed, missing = statement_lines[path]
        if changed & missing:
            gaps.append(path)
    return sorted(gaps)


def classify_changed_file_exclusions(
    *,
    changed_before_coverage: list[str],
    coverage_eligible: list[str],
    eligible: list[str],
    coverage_enabled: bool,
) -> tuple[list[str], list[str], list[str]]:
    """Advisory whole-file selection exclusions, split by which filter dropped them."""
    if not coverage_enabled:
        return [], [], []
    coverage_eligible_set = set(coverage_eligible)
    eligible_set = set(eligible)
    file_coverage_excluded = [
        path for path in changed_before_coverage if path not in coverage_eligible_set
    ]
    mutation_line_excluded = [
        path
        for path in changed_before_coverage
        if path in coverage_eligible_set and path not in eligible_set
    ]
    return (
        file_coverage_excluded,
        mutation_line_excluded,
        file_coverage_excluded + mutation_line_excluded,
    )
