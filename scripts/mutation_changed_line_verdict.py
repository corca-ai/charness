"""Shared changed-line verdict assembly for the mutation gate."""

from __future__ import annotations

from collections.abc import Mapping

from scripts.mutation_changed_files_lib import (
    changed_line_numbers_for_paths,
    changed_line_scope_gap_targets,
    classify_changed_line_scope_gap,
)


def changed_line_scope_verdict(scope: dict) -> tuple[list[str], dict, dict[str, set[int]]]:
    """Classify a scope and build exact targets from one range diff."""
    changed_lines = changed_line_numbers_for_paths(
        scope["repo_root"], scope["base_sha"], scope["head_sha"], scope["changed_before_coverage"]
    )
    blocking = classify_changed_line_scope_gap(**scope, _changed_lines=changed_lines)
    targets = changed_line_scope_gap_targets(**scope, _changed_lines=changed_lines)
    return blocking, targets, changed_lines


def blocking_details(
    blocking: list[str],
    statement_lines: Mapping[str, tuple[set[int], set[int]]],
    changed_lines: Mapping[str, set[int]],
) -> dict[str, object]:
    """Describe missing lines for each blocked file without another Git query."""
    details: dict[str, object] = {}
    for path in blocking:
        changed = changed_lines.get(path, set())
        if path not in statement_lines:
            details[path] = (
                "file not tracked by the test suite (untested, or exercised only where coverage "
                "was never attributed -- see subprocess_coverage_advisory, and its _scope "
                "sibling, which says what was examined when the advisory itself is empty) "
                "-> covers as 0%"
            )
        else:
            _executed, missing = statement_lines[path]
            details[path] = {"changed_and_missing": sorted(changed & missing)}
    return details
