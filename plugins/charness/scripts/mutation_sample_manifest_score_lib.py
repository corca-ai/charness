"""Sample-manifest checks for mutation score closeout."""

from __future__ import annotations

import json
from pathlib import Path

SCOPE_GAP_MANIFEST_SECTIONS = (
    ("changed_files_excluded_by_file_coverage", "File coverage floor"),
    ("changed_files_excluded_by_mutation_line_coverage", "Mutation-line coverage"),
    ("selection_excluded_changed_files", "Selection budget or nodeid"),
    ("workload_excluded_changed_files", "Workload budget"),
    ("uncovered_changed_files", "Compatibility union"),
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
    all_paths: set[str] = set()
    details: dict[str, list[str]] = {}
    for key, _heading in SCOPE_GAP_MANIFEST_SECTIONS:
        if key not in payload:
            continue
        value = payload[key]
        if not isinstance(value, list):
            issues.append(f"mutation sample manifest `{key}` must be a list of strings")
            continue
        invalid_values = [path for path in value if not isinstance(path, str)]
        if invalid_values:
            issues.append(f"mutation sample manifest `{key}` must be a list of strings")
            continue
        paths = sorted(set(value))
        if paths:
            details[key] = paths
            all_paths.update(paths)
    return sorted(all_paths), details, "; ".join(issues)


def changed_scope_gap_section_lines(paths: list[str], details: dict[str, list[str]]) -> list[str]:
    lines = ["", "## Changed Files Excluded Before Mutation", "", *[f"- `{path}`" for path in paths[:10]], ""]
    for key, heading in SCOPE_GAP_MANIFEST_SECTIONS:
        if detail_paths := details.get(key):
            lines.extend([f"### {heading}", "", *[f"- `{path}`" for path in detail_paths[:10]], ""])
    return lines
