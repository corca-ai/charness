"""Sample-manifest checks for mutation score closeout."""

from __future__ import annotations

import json
from pathlib import Path

# Sections that make the mutation signal untrustworthy for the change and so
# block recovery: the change's own lines were left test-uncovered. This arm is
# computed over ALL eligible changed files in range, independent of sampling,
# so it keeps blocking real coverage gaps even for files the budgets dropped.
SCOPE_GAP_BLOCKING_SECTIONS = (
    ("changed_line_uncovered_changed_files", "Uncovered changed lines"),
)

# Capacity-class drops of changed files (cumulative selection/nodeid budgets,
# workload budgets). Advisory, not blocking: a dropped file's changed lines
# already passed the blocking uncovered arm above, so the drop is a sampling
# capacity limit, not a coverage gap — the same class #341 made advisory for
# the per-file cap. Completes the premerge-gate spec's deferred follow-up
# (`follow-up:mutation-selection-budget-setup-libs`): before this, any push
# changing more eligible files than `max_files` guaranteed a red scheduled
# run whose auto-issue a later empty-diff run closed without re-proof.
SCOPE_GAP_CAPACITY_ADVISORY_SECTIONS = (
    ("selection_excluded_changed_files", "Selection budget or nodeid (advisory: capacity, not coverage)"),
    ("workload_excluded_changed_files", "Workload budget (advisory: capacity, not coverage)"),
)

# Whole-file selection diagnostics. A touched file failing the whole-file
# coverage floor or whole-file mutation-line filter is recorded for triage but
# does NOT block on its own: a well-tested change must not be failed because of
# unrelated, pre-existing untested lines elsewhere in the same file. The
# changed-line blocker above still catches genuinely untested changes.
SCOPE_GAP_ADVISORY_KEYS = (
    "changed_files_excluded_by_file_coverage",
    "changed_files_excluded_by_mutation_line_coverage",
    # A changed file dropped purely because its own covered-mutable-line workload
    # exceeds the per-file mutation budget is a capacity limit, not a coverage gap
    # (its changed lines' coverage is verified by the changed-line arm). It is
    # surfaced for triage but never blocks recovery (#341).
    "changed_files_excluded_by_per_file_budget",
    "uncovered_changed_files",
)
CHANGED_LINE_TARGETS_KEY = "changed_line_uncovered_changed_line_targets"


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

    details: dict[str, list[str]] = {}
    blocking_paths, changed_line_paths = _collect_scope_gap_sections(read_section, details)
    if target_lines := read_changed_line_target_section(payload, issues):
        details[CHANGED_LINE_TARGETS_KEY] = target_lines
    target_paths = {line.split(":", 1)[0] for line in details.get(CHANGED_LINE_TARGETS_KEY, [])}
    missing_target_paths = sorted(set(changed_line_paths) - target_paths)
    if missing_target_paths:
        issues.append(
            "mutation sample manifest changed-line blockers missing exact proof targets for "
            + ", ".join(missing_target_paths)
        )
    # Advisory keys are still type-validated so a malformed manifest fails
    # closed, but their paths never enter the blocking set.
    for key in SCOPE_GAP_ADVISORY_KEYS:
        read_section(key)
    return sorted(blocking_paths), details, "; ".join(issues)


def _collect_scope_gap_sections(read_section, details: dict[str, list[str]]) -> tuple[set[str], list[str]]:
    """Fill ``details`` from the blocking and capacity-advisory sections.

    Capacity-class sections stay out of the blocking set but keep their
    detail lists so the summary still names the dropped files for triage."""
    blocking_paths: set[str] = set()
    changed_line_paths: list[str] = []
    for key, _heading in SCOPE_GAP_BLOCKING_SECTIONS:
        paths = read_section(key)
        if paths:
            details[key] = paths
            blocking_paths.update(paths)
            if key == "changed_line_uncovered_changed_files":
                changed_line_paths = paths
    for key, _heading in SCOPE_GAP_CAPACITY_ADVISORY_SECTIONS:
        paths = read_section(key)
        if paths:
            details[key] = paths
    return blocking_paths, changed_line_paths


def read_changed_line_target_section(payload: dict, issues: list[str]) -> list[str]:
    value = payload.get(CHANGED_LINE_TARGETS_KEY)
    if value is None:
        return []
    if not isinstance(value, dict):
        issues.append(f"mutation sample manifest `{CHANGED_LINE_TARGETS_KEY}` must be an object")
        return []
    lines: list[str] = []
    for path in sorted(value):
        entries = value[path]
        if not isinstance(path, str) or not isinstance(entries, list):
            issues.append(
                f"mutation sample manifest `{CHANGED_LINE_TARGETS_KEY}` must map paths to lists"
            )
            return []
        target_lines = _target_lines_for_path(path, entries, issues)
        if not target_lines and issues:
            return []
        lines.extend(target_lines)
    return lines


def _target_lines_for_path(path: str, entries: list[object], issues: list[str]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append(
                f"mutation sample manifest `{CHANGED_LINE_TARGETS_KEY}` entries must be objects"
            )
            return []
        line = entry.get("line")
        source = entry.get("source", "")
        if not isinstance(line, int) or not isinstance(source, str):
            issues.append(
                f"mutation sample manifest `{CHANGED_LINE_TARGETS_KEY}` entries need integer line and string source"
            )
            return []
        lines.append(f"{path}:{line}" + (f" {source}" if source else ""))
    return lines


def changed_scope_gap_section_lines(paths: list[str], details: dict[str, list[str]]) -> list[str]:
    lines = ["", "## Changed Files Excluded Before Mutation", ""]
    if paths:
        lines.extend([*[f"- `{path}`" for path in paths[:10]], ""])
    for key, heading in (*SCOPE_GAP_BLOCKING_SECTIONS, *SCOPE_GAP_CAPACITY_ADVISORY_SECTIONS):
        if detail_paths := details.get(key):
            lines.extend([f"### {heading}", "", *[f"- `{path}`" for path in detail_paths[:10]], ""])
    if target_lines := details.get(CHANGED_LINE_TARGETS_KEY):
        lines.extend(
            [
                "### Changed-line proof targets",
                "",
                *[f"- `{line}`" for line in target_lines[:10]],
                "",
            ]
        )
    return lines
