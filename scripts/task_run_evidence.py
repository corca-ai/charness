"""Completion evidence, candidate scope, and concurrent-parent classification."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from scripts.task_run_contract import FAIL, PASS
from scripts.task_run_git import (
    _collect_populations,
    _collect_populations_with_metadata,
    _git_output,
    _parse_nul_paths,
    _population_delta,
    _snapshot_payload,
)
from scripts.task_run_scope import (
    _generated_files,
    _paths_in_scopes,
    _refresh_scope_specs,
    _scope_result,
)


def _parent_progress(
    *,
    parent_root: Path,
    parent_before: Mapping[str, Sequence[str]],
    parent_before_head: str,
    specs: Sequence[Mapping[str, Any]],
    glob_matches: Callable[[Path, str], tuple[list[str], list[str]]] | None = None,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    parent_after = _collect_populations(parent_root)
    parent_after_head = _git_output(parent_root, "rev-parse", "HEAD").strip()
    committed = (
        _parse_nul_paths(
            _git_output(
                parent_root,
                "diff",
                "--no-renames",
                "--name-only",
                "-z",
                parent_before_head,
                parent_after_head,
                "--",
            )
        )
        if parent_before_head != parent_after_head
        else []
    )
    dirty_paths: list[str] = []
    dirty_delta: dict[str, dict[str, list[str]]] = {}
    for population in ("tracked", "untracked"):
        before = set(parent_before.get(population, ()))
        after = set(parent_after.get(population, ()))
        added = sorted(after - before)
        removed = sorted(before - after)
        dirty_delta[population] = {"added": added, "removed": removed}
        dirty_paths.extend(added)
        dirty_paths.extend(removed)

    ignored_before = set(parent_before.get("ignored", ()))
    ignored_after = set(parent_after.get("ignored", ()))
    ignored_delta = {
        "added": sorted(ignored_after - ignored_before),
        "removed": sorted(ignored_before - ignored_after),
        "paths": sorted(ignored_after),
    }
    changed = sorted(set(committed) | set(dirty_paths))
    refreshed = _refresh_scope_specs(parent_root, specs, glob_matches=glob_matches)
    overlap = _paths_in_scopes(changed, refreshed)
    classification = (
        "normal"
        if not changed
        else "writer-conflict"
        if overlap
        else "concurrent-parent-progress"
    )
    progress = {
        "classification": classification,
        "blocking": classification == "writer-conflict",
        "committed_paths": committed,
        "dirty": dirty_delta,
        "paths": changed,
        "overlap_paths": overlap,
        "ignored": ignored_delta,
        "before_head": parent_before_head,
        "after_head": parent_after_head,
    }
    return progress, parent_after


def _completion_evidence(
    *,
    target_path: Path,
    parent_root: Path,
    before_exec: Mapping[str, Sequence[str]],
    base_sha: str,
    scope_specs: Sequence[Mapping[str, Any]],
    require_change: bool,
    parent_before: Mapping[str, Sequence[str]],
    parent_before_head: str,
    target_head: str | None = None,
    glob_matches: Callable[[Path, str], tuple[list[str], list[str]]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    after_exec, observed_head, observed_branch = _collect_populations_with_metadata(target_path)
    populations = _population_delta(before_exec, after_exec)
    target_scope_specs = _refresh_scope_specs(
        target_path,
        scope_specs,
        glob_matches=glob_matches,
    )
    scope = _scope_result(
        target_path,
        base_sha,
        target_scope_specs,
        require_change,
        after_exec,
        target_head or observed_head,
        observed_branch,
    )
    parent_progress, parent_after = _parent_progress(
        parent_root=parent_root,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
        specs=scope_specs,
        glob_matches=glob_matches,
    )
    evidence = {
        "after_exec": _snapshot_payload(after_exec),
        "populations": populations,
        "generated_files": _generated_files(populations, target_scope_specs),
        "scope": scope,
        "parent": {
            "unchanged": parent_progress["classification"] == "normal",
            "before": _snapshot_payload(parent_before),
            "after": _snapshot_payload(parent_after),
            "progress": parent_progress,
            "verdict": FAIL if parent_progress["blocking"] else PASS,
        },
    }
    return evidence, scope, parent_progress
