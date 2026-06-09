"""Manifest helpers for the repo-owned mutation sampling workflow."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.mutation_sampling_lib import mutation_workload, test_nodeid_count


def display_path(repo_root: Path, path: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def write_manifest(manifest: dict, manifest_json: Path, manifest_md: Path) -> None:
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        "# Mutation Sample",
        "",
        f"- Base SHA: `{manifest['base_sha'] or '(none)'}`",
        f"- Head SHA: `{manifest['head_sha'] or '(unknown)'}`",
        f"- Seed: `{manifest['seed']}`",
        f"- Mutation pool files: {manifest.get('all_eligible_count', manifest['eligible_count'])}",
        f"- Mutation pools: {', '.join(_pool_summary(manifest).splitlines()) or 'n/a'}",
        f"- Eligible files after coverage/mutation-line filters: {manifest['eligible_count']}",
        f"- Covered eligible files: {manifest.get('covered_eligible_count', 'n/a')}",
        f"- File coverage floor: {manifest.get('min_file_coverage', 'n/a')}",
        f"- Eligible files after mutation-line filter: {manifest.get('mutation_line_eligible_count', 'n/a')}",
        f"- Executable mutant budget: {manifest.get('max_executable_mutants', 'n/a')}",
        f"- Per-file executable mutant budget: {manifest.get('max_executable_mutants_per_file', 'n/a')}",
        f"- Selected executable mutants: {manifest.get('selected_executable_mutants', 'n/a')}",
        f"- Test nodeid budget: {manifest.get('max_test_nodeids', 'n/a')}",
        f"- Selected test nodeids: {manifest.get('sample_test_nodeid_count', 'n/a')}",
        f"- Changed pool files: {len(manifest.get('changed_files_before_coverage', manifest['changed_files']))}",
        f"- Changed eligible files after coverage/mutation-line filters: {len(manifest['changed_files'])}",
        f"- Changed files with uncovered changed lines (blocking): {len(manifest.get('changed_line_uncovered_changed_files', []))}",
        f"- Changed-line proof targets: {_changed_line_target_count(manifest)}",
        f"- Changed files excluded by coverage/mutation-line filters (advisory union): {len(manifest.get('uncovered_changed_files', []))}",
        f"- Changed files excluded by file coverage floor: {len(manifest.get('changed_files_excluded_by_file_coverage', []))}",
        f"- Changed files excluded by mutation-line coverage: {len(manifest.get('changed_files_excluded_by_mutation_line_coverage', []))}",
        f"- Changed files excluded by selection budgets: {len(manifest.get('selection_excluded_changed_files', []))}",
        f"- Changed files excluded by per-file mutation budget (advisory): {len(manifest.get('changed_files_excluded_by_per_file_budget', []))}",
        f"- Selected: {len(manifest['sample'])}/{manifest['max_files']}",
        f"- Test command: `{manifest.get('test_command') or '(not recorded)'}`",
        "",
        "## Changed files with uncovered changed lines (blocking)",
        "",
        *(
            [f"- `{path}`" for path in manifest.get("changed_line_uncovered_changed_files", [])]
            or ["(none)"]
        ),
        "",
        "## Changed-line proof targets",
        "",
        *(_changed_line_target_lines(manifest) or ["(none)"]),
        "",
        "## Changed files excluded by file coverage (advisory)",
        "",
        *(
            [f"- `{path}`" for path in manifest.get("changed_files_excluded_by_file_coverage", [])]
            or ["(none)"]
        ),
        "",
        "## Changed files excluded by mutation-line coverage",
        "",
        *(
            [
                f"- `{path}`"
                for path in manifest.get("changed_files_excluded_by_mutation_line_coverage", [])
            ]
            or ["(none)"]
        ),
        "",
        "## Changed files excluded by per-file mutation budget (advisory, non-blocking)",
        "",
        *(
            [f"- `{path}`" for path in manifest.get("changed_files_excluded_by_per_file_budget", [])]
            or ["(none)"]
        ),
        "",
        "## Changed sample",
        "",
        *([f"- `{path}`" for path in manifest["changed_sample"]] or ["(none)"]),
        "",
        "## Fill sample",
        "",
        *([f"- `{path}`" for path in manifest["fill_sample"]] or ["(none)"]),
        "",
    ]
    manifest_md.parent.mkdir(parents=True, exist_ok=True)
    manifest_md.write_text("\n".join(md_lines), encoding="utf-8")


def split_per_file_budget_exclusions(
    selection_excluded_changed_files: list[str],
    *,
    mutation_line_coverage: dict[str, dict[str, int]],
    coverage_enabled: bool,
    max_executable_mutants_per_file: int,
) -> tuple[list[str], list[str]]:
    """Separate per-file-workload-cap drops from genuine selection-contention drops.

    A changed file whose own covered-mutable-line workload exceeds the per-file
    budget can never be selected as a mutation target (``select_budgeted_sample``
    checks the per-file cap first). That drop is a workload-CAPACITY limit, not a
    coverage/proof gap: the changed lines' coverage is verified independently by the
    changed-line arm, which still blocks any uncovered changed line. Reclassifying it
    out of the blocking ``selection_excluded_changed_files`` bucket into a non-blocking
    advisory bucket stops a module split that produced an oversized (but well-covered)
    changed file from blocking the gate forever (#341). The per-file budget is unchanged.
    """
    if not (coverage_enabled and max_executable_mutants_per_file):
        return selection_excluded_changed_files, []
    per_file_budget_excluded = [
        path
        for path in selection_excluded_changed_files
        if mutation_workload(path, mutation_line_coverage) > max_executable_mutants_per_file
    ]
    if not per_file_budget_excluded:
        return selection_excluded_changed_files, []
    capped = set(per_file_budget_excluded)
    remaining = [path for path in selection_excluded_changed_files if path not in capped]
    return remaining, per_file_budget_excluded


def build_manifest_from_state(state: dict) -> dict:
    max_total, max_per_file, max_nodeids = state["workload_limits"]
    coverage_enabled = state["coverage_enabled"]
    mutation_line_coverage = state["mutation_line_coverage"]
    eligible = state["eligible"]
    selection_excluded_changed_files, changed_files_excluded_by_per_file_budget = (
        split_per_file_budget_exclusions(
            state["selection_excluded_changed_files"],
            mutation_line_coverage=mutation_line_coverage,
            coverage_enabled=coverage_enabled,
            max_executable_mutants_per_file=max_per_file,
        )
    )
    return {
        "seed": state["seed"],
        "base_sha": state["base_sha"],
        "head_sha": state["head_sha"],
        "max_files": state["max_files"],
        "changed_quota": state["changed_quota"],
        "eligible_count": len(eligible),
        "all_eligible_count": len(state["all_eligible"]),
        "coverage_enabled": coverage_enabled,
        "coverage_json": display_path(state["repo_root"], state["coverage_json"]),
        "coverage_command": state["test_command"],
        "test_command": state["mutation_test_command"],
        "min_file_coverage": state["min_file_coverage"] if coverage_enabled else 0.0,
        "mutation_line_coverage": mutation_line_coverage,
        "mutation_line_eligible_count": _mutation_line_eligible_count(mutation_line_coverage),
        "eligible_executable_mutants": sum(
            mutation_workload(path, mutation_line_coverage) for path in eligible
        ),
        "max_executable_mutants": max_total,
        "max_executable_mutants_per_file": max_per_file,
        "max_test_nodeids": max_nodeids,
        "selected_executable_mutants": state["selected_executable_mutants"],
        "sample_test_nodeid_count": test_nodeid_count(
            state["repo_root"],
            state["sample"],
            state["line_contexts"],
            coverage_enabled=coverage_enabled,
        ),
        "covered_eligible_count": len(eligible) if coverage_enabled else None,
        "uncovered_eligible_count": len(state["all_eligible"]) - len(eligible)
        if coverage_enabled
        else None,
        "changed_files_before_coverage": state["changed_before_coverage"],
        "changed_files_excluded_by_file_coverage": state[
            "changed_files_excluded_by_file_coverage"
        ],
        "changed_files_excluded_by_mutation_line_coverage": state[
            "changed_files_excluded_by_mutation_line_coverage"
        ],
        "uncovered_changed_files": state["uncovered_changed_files"],
        "changed_line_uncovered_changed_files": state["changed_line_uncovered_changed_files"],
        "changed_line_uncovered_changed_line_targets": state.get(
            "changed_line_uncovered_changed_line_targets", {}
        ),
        "selection_excluded_changed_files": selection_excluded_changed_files,
        "changed_files_excluded_by_per_file_budget": changed_files_excluded_by_per_file_budget,
        "selection_excluded_fill_files": state["selection_excluded_fill_files"],
        "changed_files": state["changed"],
        "changed_sample": state["changed_sample"],
        "fill_sample": state["fill_sample"],
        "sample": state["sample"],
        "pools": _build_pool_manifest(state),
    }


def _mutation_line_eligible_count(mutation_line_coverage: dict[str, dict[str, int]]) -> int:
    return sum(
        1
        for stats in mutation_line_coverage.values()
        if int(stats.get("mutable", 0)) > 0 and int(stats.get("uncovered", 0)) == 0
    )


def _changed_line_target_count(manifest: dict) -> int:
    targets = manifest.get("changed_line_uncovered_changed_line_targets", {})
    if not isinstance(targets, dict):
        return 0
    return sum(len(entries) for entries in targets.values() if isinstance(entries, list))


def _changed_line_target_lines(manifest: dict) -> list[str]:
    targets = manifest.get("changed_line_uncovered_changed_line_targets", {})
    if not isinstance(targets, dict):
        return []
    lines: list[str] = []
    for path in sorted(targets):
        entries = targets[path]
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            line = entry.get("line")
            source = str(entry.get("source") or "")
            if not isinstance(line, int):
                continue
            suffix = f" `{source}`" if source else ""
            lines.append(f"- `{path}:{line}`{suffix}")
    return lines


def _build_pool_manifest(state: dict) -> dict[str, dict[str, int]]:
    pool_for_path = state.get("pool_for_path")
    if not callable(pool_for_path):
        return {}
    buckets: dict[str, dict[str, int]] = {}
    for key, paths in (
        ("all_eligible", state["all_eligible"]),
        ("eligible", state["eligible"]),
        ("sample", state["sample"]),
    ):
        for path in paths:
            pool = pool_for_path(path)
            bucket = buckets.setdefault(pool, {"all_eligible": 0, "eligible": 0, "sample": 0})
            bucket[key] += 1
    return dict(sorted(buckets.items()))


def _pool_summary(manifest: dict) -> str:
    pools = manifest.get("pools") or {}
    if not isinstance(pools, dict):
        return ""
    lines = []
    for pool, counts in sorted(pools.items()):
        if not isinstance(counts, dict):
            continue
        lines.append(
            f"{pool} {counts.get('sample', 0)}/{counts.get('eligible', 0)} "
            f"selected ({counts.get('all_eligible', 0)} pool)"
        )
    return "\n".join(lines)
