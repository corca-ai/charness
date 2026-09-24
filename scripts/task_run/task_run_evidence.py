"""Completion evidence, candidate scope, and concurrent-parent classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.task_run.task_run_contract import FAIL, PASS, TaskRunError  # noqa: E402
from scripts.task_run.task_run_git import (  # noqa: E402
    _collect_populations_with_metadata,
    _git_output,
    _parse_nul_paths,
    _population_delta,
    _snapshot_payload,
)
from scripts.task_run.task_run_scope import (  # noqa: E402
    _generated_files,
    _paths_in_scopes,
    _refresh_scope_specs,
    _scope_result,
)


def _persist_full_report(
    delivery: Mapping[str, Any], report_path: Path
) -> dict[str, Any]:
    """Write the complete delivered report beside its task-run result."""
    source = delivery.get("log")
    raw: bytes | None = None
    if isinstance(source, (str, Path)):
        try:
            raw = Path(source).read_bytes()
        except OSError:
            raw = None
    if raw is None:
        text = delivery.get("text")
        if isinstance(text, str):
            raw = text.encode("utf-8")
    try:
        if raw is None:
            return {
                "path": str(report_path),
                "bytes": None,
                "complete": None,
            }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_bytes(raw)
        expected = delivery.get("bytes")
        complete = (
            len(raw) == expected
            if isinstance(expected, int) and not isinstance(expected, bool)
            else not bool(delivery.get("truncated"))
        )
        complete = complete and report_path.stat().st_size == len(raw)
        return {
            "path": str(report_path),
            "bytes": len(raw),
            "complete": complete,
            **({"error": "source report was clipped before persistence"} if not complete else {}),
        }
    except OSError as exc:
        return {
            "path": str(report_path),
            "bytes": None,
            "complete": False,
            "error": str(exc),
        }


def _write_full_report(
    delivery: dict[str, Any], report_path: Path
) -> None:
    delivery["full_report"] = _persist_full_report(delivery, report_path)


def _short_summary(
    *,
    branch: object,
    head: object,
    verdict: object,
    decisions: object,
) -> dict[str, Any]:
    """Return the three fields the integrator needs before opening the report."""
    return {
        "branch_head": {"branch": branch, "head": head},
        "verdict": verdict,
        "decisions_needing_confirmation": decisions if isinstance(decisions, list) else [],
    }


def _render_short_summary(summary: Mapping[str, Any]) -> str:
    return json.dumps(dict(summary), ensure_ascii=False, separators=(",", ":"))


def _attach_short_summary(
    payload: dict[str, Any], delivery: dict[str, Any]
) -> None:
    payload["summary"] = _short_summary(
        branch=payload.get("target_branch"),
        head=payload.get("target_sha"),
        verdict=payload.get("result_kind"),
        decisions=payload.get(
            "decisions_needing_confirmation", payload.get("review_required", [])
        ),
    )
    delivery["text"] = _render_short_summary(payload["summary"])


def _report_delivery_blockers(
    delivery: Mapping[str, Any], *, report_only: bool
) -> list[str]:
    blockers: list[str] = []
    full_report = delivery.get("full_report")
    if isinstance(full_report, Mapping) and full_report.get("error"):
        blockers.append(f"full report could not be saved: {full_report['error']}")
    if not report_only:
        return blockers
    delivered_text = delivery.get("text")
    if delivery.get("status") != "delivered" or not str(delivered_text or "").strip():
        blockers.append("report-only task delivered no report: the lane must produce a full report")
        return blockers
    report_complete = isinstance(full_report, Mapping) and full_report.get("complete") is True
    if delivery.get("truncated") and not report_complete:
        blockers.append(
            "report-only task result was truncated: the full report file is incomplete"
        )
    return blockers


def _parent_progress(
    *,
    parent_root: Path,
    parent_before: Mapping[str, Sequence[str]],
    parent_before_head: str,
    specs: Sequence[Mapping[str, Any]],
    glob_matches: Callable[[Path, str], tuple[list[str], list[str]]] | None = None,
    report_only: bool = False,
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    parent_after, parent_after_head, _ = _collect_populations_with_metadata(parent_root)
    if parent_after_head is None:
        raise TaskRunError("parent Git status did not report a valid HEAD")
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
    if report_only:
        # A report-only lane carries no write candidate, so scoped parent
        # movement cannot collide with it (#827). Overlap stays recorded in
        # `overlap_paths` with the before/after HEADs, but never blocks.
        classification = "normal" if not changed else "concurrent-parent-progress"
    else:
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
    report_only: bool = False,
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
        report_only=report_only,
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
