from __future__ import annotations

from pathlib import Path
from typing import Any

import public_spec_quality_lib as qlib
from public_spec_adapter_policy import load_quality_adapter_data, load_repo_script_module
from public_spec_scan_lib import spec_inventory

_VENDORED_LIB = load_repo_script_module("vendored_path_lib")


def _vendored_prefixes(data: dict[str, Any]) -> list[str]:
    if _VENDORED_LIB is None:
        return []
    return _VENDORED_LIB.vendored_prefixes(data.get("vendored_paths"))


def _filter_vendored(repo_root: Path, paths: list[Path], prefixes: list[str]) -> list[Path]:
    if _VENDORED_LIB is None or not prefixes:
        return paths
    return _VENDORED_LIB.filter_vendored(repo_root, paths, prefixes)


def iter_public_specs(repo_root: Path) -> list[Path]:
    return qlib.visible_paths(repo_root, "*.spec.md")


def iter_smoke_like_tests(repo_root: Path) -> tuple[list[str], list[str]]:
    smoke_paths: set[str] = set()
    e2e_paths: set[str] = set()
    for path in qlib.visible_paths(repo_root, "*"):
        rel = path.relative_to(repo_root).as_posix()
        lowered = rel.lower()
        if "smoke" in lowered:
            smoke_paths.add(rel)
        if "e2e" in lowered or "end_to_end" in lowered:
            e2e_paths.add(rel)
    return sorted(smoke_paths), sorted(e2e_paths)


def duplicate_commands(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    duplicate_map: dict[str, list[str]] = {}
    for spec in specs:
        for command in spec["command_examples"]:
            duplicate_map.setdefault(command, []).append(spec["spec_path"])
    return [
        {"command": command, "spec_paths": sorted(paths)}
        for command, paths in sorted(duplicate_map.items())
        if len(set(paths)) >= 2
    ]


def inventory(repo_root: Path) -> dict[str, Any]:
    data = load_quality_adapter_data(repo_root)
    vendored = _vendored_prefixes(data)
    spec_paths = _filter_vendored(repo_root, iter_public_specs(repo_root), vendored)
    specs = [spec_inventory(repo_root, path, data) for path in spec_paths]
    duplicates = duplicate_commands(specs)
    smoke_paths, e2e_paths = iter_smoke_like_tests(repo_root)
    if vendored:
        smoke_paths = [path for path in smoke_paths if not _VENDORED_LIB.is_vendored_relative(path, vendored)]
        e2e_paths = [path for path in e2e_paths if not _VENDORED_LIB.is_vendored_relative(path, vendored)]
    runner_specs = sorted(spec["spec_path"] for spec in specs if "delegated_test_runner_proof" in spec["heuristics"])
    source_guard_spec_rows = qlib.source_guard_specs(specs)
    implementation_guard_spec_rows = qlib.implementation_guard_specs(specs)
    top_source_guard_specs = qlib.top_source_guard_specs(specs)
    recommendations = qlib.public_spec_recommendations(
        duplicates=duplicates,
        runner_specs=runner_specs,
        top_source_specs=top_source_guard_specs,
        smoke_paths=smoke_paths,
        e2e_paths=e2e_paths,
    )
    layering_heuristics = qlib.layering_heuristics(
        duplicates=duplicates,
        runner_specs=runner_specs,
        source_guard_spec_rows=source_guard_spec_rows,
        implementation_guard_spec_rows=implementation_guard_spec_rows,
        smoke_paths=smoke_paths,
        e2e_paths=e2e_paths,
    )
    summary = qlib.source_guard_summary(specs)
    return {
        "repo_root": str(repo_root),
        "summary": {
            "public_spec_count": len(specs),
            "flagged_spec_count": sum(1 for spec in specs if spec["heuristics"]),
            "duplicate_command_count": len(duplicates),
            **summary,
            "smoke_test_count": len(smoke_paths),
            "e2e_test_count": len(e2e_paths),
        },
        "public_specs": specs,
        "layering": {
            "duplicate_command_examples": duplicates,
            "smoke_test_paths": smoke_paths,
            "e2e_test_paths": e2e_paths,
            "delegated_runner_specs": runner_specs,
            "top_source_guard_specs": top_source_guard_specs,
            "heuristics": layering_heuristics,
            "review_prompts": qlib.REVIEW_PROMPTS,
            "recommendations": recommendations,
        },
    }
