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


def changed_line_scope_gap_targets(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> dict[str, list[dict[str, object]]]:
    """Exact changed-line targets that make the scope-gap blocker fire.

    Tracked files report changed lines that are also missing coverage. Untracked
    files report all changed lines because the test suite observed none of the
    file. The source text is included so manual targeted-mutant proof can bind
    to a numbered gate target before editing similar nearby code.
    """
    if not coverage_enabled or not base_sha:
        return {}
    targets: dict[str, list[dict[str, object]]] = {}
    for path in changed_before_coverage:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if not changed:
            continue
        if path not in statement_lines:
            target_lines = changed
        else:
            _executed, missing = statement_lines[path]
            target_lines = changed & missing
        if target_lines:
            entries = line_source_targets(repo_root, path, target_lines, ref=head_sha)
            if entries:
                targets[path] = entries
    return dict(sorted(targets.items()))


def classify_changed_sample_scope(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    eligible: list[str],
    coverage_eligible: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> tuple[list[str], list[str], list[str], list[str], list[str], dict[str, list[dict[str, object]]]]:
    changed = [path for path in changed_before_coverage if path in set(eligible)]
    (
        changed_files_excluded_by_file_coverage,
        changed_files_excluded_by_mutation_line_coverage,
        uncovered_changed_files,
    ) = classify_changed_file_exclusions(
        changed_before_coverage=changed_before_coverage,
        coverage_eligible=coverage_eligible,
        eligible=eligible,
        coverage_enabled=coverage_enabled,
    )
    changed_line_uncovered_changed_files = classify_changed_line_scope_gap(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=coverage_enabled,
    )
    changed_line_uncovered_changed_line_targets = changed_line_scope_gap_targets(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=coverage_enabled,
    )
    return (
        changed,
        changed_files_excluded_by_file_coverage,
        changed_files_excluded_by_mutation_line_coverage,
        uncovered_changed_files,
        changed_line_uncovered_changed_files,
        changed_line_uncovered_changed_line_targets,
    )


def line_source_targets(
    repo_root: Path,
    path: str,
    line_numbers: set[int],
    ref: str | None = None,
) -> list[dict[str, object]]:
    """Return deterministic ``line`` + ``source`` entries for repo-relative path."""
    source_lines = line_source_text(repo_root, path, ref)
    entries: list[dict[str, object]] = []
    for line_number in sorted(line_numbers):
        source = source_lines[line_number - 1].strip() if 1 <= line_number <= len(source_lines) else ""
        if not source:
            continue
        entries.append({"line": line_number, "source": source})
    return entries


def line_source_text(repo_root: Path, path: str, ref: str | None = None) -> list[str]:
    if ref:
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{path}"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return []
        return result.stdout.splitlines()
    source_path = repo_root / path
    try:
        return source_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


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
