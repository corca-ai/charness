"""Sample-manifest checks for mutation score closeout."""

from __future__ import annotations

import json
from pathlib import Path

# Sections that make the mutation signal untrustworthy for the change and so
# block recovery: the change's own lines were left uncovered, or eligible
# changed files were dropped by selection/workload budgets before mutation.
SCOPE_GAP_BLOCKING_SECTIONS = (
    ("changed_line_uncovered_changed_files", "Uncovered changed lines"),
    ("selection_excluded_changed_files", "Selection budget or nodeid"),
    ("workload_excluded_changed_files", "Workload budget"),
)

# Whole-file selection diagnostics. A touched file failing the whole-file
# coverage floor or whole-file mutation-line filter is recorded for triage but
# does NOT block on its own: a well-tested change must not be failed because of
# unrelated, pre-existing untested lines elsewhere in the same file. The
# changed-line blocker above still catches genuinely untested changes.
SCOPE_GAP_ADVISORY_KEYS = (
    "changed_files_excluded_by_file_coverage",
    "changed_files_excluded_by_mutation_line_coverage",
    "uncovered_changed_files",
)


def sample_manifest_scope_gap_details(
    manifest_path: Path,
) -> tuple[list[str], dict[str, list[str]], str]:
    if not manifest_path.is_file():
        return [], {}, f"mutation sample manifest not found at {manifest_path}"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [], {}, f"could not read mutation sample manifest at {manifest_path}: {exc}"
    if not isinstance(payload, dict):
        return [], {}, "mutation sample manifest root must be an object"
    issues: list[str] = []
    if "base_sha" not in payload:
        issues.append("mutation sample manifest missing `base_sha`; changed-file proof state is unknown")
    elif payload["base_sha"] is not None and (
        not isinstance(payload["base_sha"], str) or not payload["base_sha"].strip()
    ):
        issues.append(
            "mutation sample manifest `base_sha` must be a non-empty string or null"
        )

    def read_section(key: str) -> list[str] | None:
        if key not in payload:
            return None
        value = payload[key]
        if not isinstance(value, list) or any(not isinstance(path, str) for path in value):
            issues.append(f"mutation sample manifest `{key}` must be a list of strings")
            return None
        return sorted(set(value))

    blocking_paths: set[str] = set()
    details: dict[str, list[str]] = {}
    for key, _heading in SCOPE_GAP_BLOCKING_SECTIONS:
        paths = read_section(key)
        if paths:
            details[key] = paths
            blocking_paths.update(paths)
    # Advisory keys are still type-validated so a malformed manifest fails
    # closed, but their paths never enter the blocking set.
    for key in SCOPE_GAP_ADVISORY_KEYS:
        read_section(key)
    return sorted(blocking_paths), details, "; ".join(issues)


def changed_scope_gap_section_lines(paths: list[str], details: dict[str, list[str]]) -> list[str]:
    lines = ["", "## Changed Files Excluded Before Mutation", "", *[f"- `{path}`" for path in paths[:10]], ""]
    for key, heading in SCOPE_GAP_BLOCKING_SECTIONS:
        if detail_paths := details.get(key):
            lines.extend([f"### {heading}", "", *[f"- `{path}`" for path in detail_paths[:10]], ""])
    return lines
