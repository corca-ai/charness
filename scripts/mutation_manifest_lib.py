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
        f"- Changed files excluded by coverage/mutation-line filters: {len(manifest.get('uncovered_changed_files', []))}",
        f"- Changed files excluded by selection budgets: {len(manifest.get('selection_excluded_changed_files', []))}",
        f"- Selected: {len(manifest['sample'])}/{manifest['max_files']}",
        f"- Test command: `{manifest.get('test_command') or '(not recorded)'}`",
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


def build_manifest_from_state(state: dict) -> dict:
    max_total, max_per_file, max_nodeids = state["workload_limits"]
    coverage_enabled = state["coverage_enabled"]
    mutation_line_coverage = state["mutation_line_coverage"]
    eligible = state["eligible"]
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
        "uncovered_changed_files": state["uncovered_changed_files"],
        "selection_excluded_changed_files": state["selection_excluded_changed_files"],
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
