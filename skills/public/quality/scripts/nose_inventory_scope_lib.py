"""Scope resolution and payload contract for the nose clone inventory."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path
from typing import Any, Callable

DEFAULT_PATHS = ("scripts", "skills/public", "skills/support")
WRITE_BASELINE_TOP = 1_000_000

def _adapter_inventory_paths(
    repo_root: Path, load_repo_module: Callable[[str, str], Any], script_path: str
) -> tuple[list[str] | None, list[str], list[str]]:
    """Read optional consumer-owned scope without hard-coding it in the skill."""
    try:
        adapter_module = load_repo_module(script_path, "scripts.adapters.quality_adapter_lib")
        payload = adapter_module.load_quality_adapter_permissive(repo_root)
    except (ImportError, RuntimeError, OSError) as exc:
        return None, [], [f"quality adapter scope unavailable; using defaults: {exc}"]
    if not isinstance(payload, dict):
        return None, [], ["quality adapter scope unavailable; using defaults: invalid payload"]
    errors = [str(error) for error in payload.get("errors", []) if str(error)]
    data = payload.get("data", {})
    values = data.get("nose_inventory_paths", []) if isinstance(data, dict) else []
    configured = list(values) if isinstance(values, list) and values else None
    if errors:
        return configured, errors, []
    return configured, [], []


def scope_fields(
    requested_paths: list[str], scanned_paths: list[str], missing_paths: list[str], scope_status: str
) -> dict[str, Any]:
    scope = {
        "paths": list(scanned_paths),
        "requested_paths": list(requested_paths),
        "scanned_paths": list(scanned_paths),
        "missing_paths": list(missing_paths),
        "scope_status": scope_status,
    }
    return {
        "paths": list(requested_paths),
        "requested_paths": list(requested_paths),
        "scanned_paths": list(scanned_paths),
        "missing_paths": list(missing_paths),
        "scope_status": scope_status,
        "scope": scope,
    }


def resolve_scope(repo_root: Path, requested_paths: list[str]) -> tuple[list[str], list[str], str]:
    scanned: list[str] = []
    missing: list[str] = []
    for value in requested_paths:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        (scanned if candidate.is_dir() else missing).append(value)
    status = "scanned" if scanned and not missing else "partial" if scanned else "inapplicable"
    return scanned, missing, status


def _representative_command(report: Any, nose_bin: str, roots: list[str], args: argparse.Namespace) -> str:
    """Render the one multi-root query used by the scope resolver."""
    return shlex.join(
        report.build_query_command(
            nose_bin,
            roots or ["."],
            mode=args.mode,
            min_size=args.min_size,
            top=args.top,
            sort=args.sort,
            exclude=list(args.exclude or []),
            ignore_file=args.ignore_file,
        )
    )


def payload_for_args(
    args: argparse.Namespace,
    *,
    baseline: Any,
    report: Any,
    fingerprint: Any,
    load_repo_module: Callable[[str, str], Any],
    script_path: str,
    resolve_nose_bin: Callable[[], str | None],
    interpretation: dict[str, str],
) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    configured, adapter_errors, adapter_notes = _adapter_inventory_paths(repo_root, load_repo_module, script_path)
    if args.path:
        roots = [str(path) for path in args.path]
        adapter_errors = []
        adapter_notes = []
    else:
        roots = [str(path) for path in (configured or DEFAULT_PATHS)]
    scanned_paths, missing_paths, scope_status = resolve_scope(repo_root, roots)
    excludes = list(args.exclude or [])
    ignore_file = args.ignore_file
    baseline_path = baseline.resolve_baseline(
        write_baseline=args.write_baseline, baseline=args.baseline, repo_root=repo_root
    )
    if adapter_errors:
        scope = scope_fields(roots, scanned_paths, missing_paths, "error")
        return {
            "status": "error", "advisory": True, "repo_root": str(repo_root), **scope,
            "excludes": excludes, "ignore_file": ignore_file, "baseline": baseline_path,
            "ranking": {}, "command": "", "exit_code": 1, "tool_version": "",
            "family_count": 0, "families": [], "stderr": "; ".join(adapter_errors),
            "notes": ["quality adapter scope is invalid; inventory not run.", *adapter_notes],
        }
    nose_bin = resolve_nose_bin()
    if nose_bin is None:
        scope = scope_fields(roots, scanned_paths, missing_paths, "missing-tool")
        return {
            "status": "missing", "advisory": True, "repo_root": str(repo_root), **scope,
            "excludes": excludes, "ignore_file": ignore_file, "baseline": baseline_path,
            "ranking": {}, "command": "", "exit_code": 3, "tool_version": "",
            "family_count": 0, "families": [],
            "notes": [
                "nose is missing; install per integrations/tools/nose.json to run the clone-family advisory.",
                "nose is now required (>=0.13.3): document near-duplicate review runs through inventory_doc_duplicates.py (Markdown families), not a difflib fallback.",
                *adapter_notes,
            ],
        }
    if not scanned_paths:
        scope = scope_fields(roots, scanned_paths, missing_paths, "inapplicable")
        return {
            "status": "inapplicable", "advisory": True, "repo_root": str(repo_root), **scope,
            "excludes": excludes, "ignore_file": ignore_file, "baseline": baseline_path,
            "ranking": {}, "command": "", "exit_code": 3,
            "tool_version": report.resolve_tool_version(nose_bin), "family_count": 0,
            "families": [], "stderr": "",
            "notes": [
                "nose clone inventory inapplicable; no requested scan root exists.",
                "Configure nose_inventory_paths or pass --path for this repository's source roots.",
                *adapter_notes,
            ],
        }
    if args.write_baseline and scope_status != "scanned":
        scope = scope_fields(roots, scanned_paths, missing_paths, scope_status)
        return {
            "status": "error", "advisory": True, "repo_root": str(repo_root), **scope,
            "excludes": excludes, "ignore_file": ignore_file, "baseline": baseline_path,
            "ranking": {}, "command": "", "exit_code": 1,
            "tool_version": report.resolve_tool_version(nose_bin), "family_count": 0,
            "families": [], "stderr": "",
            "notes": ["baseline not written because the requested scope is incomplete."],
        }
    scan_top = WRITE_BASELINE_TOP if args.write_baseline else args.top
    collected = report.collect_families(
        repo_root,
        nose_bin,
        scanned_paths,
        mode=args.mode,
        min_size=args.min_size,
        top=scan_top,
        sort=args.sort,
        exclude=excludes,
        ignore_file=ignore_file,
    )
    command = _representative_command(report, nose_bin, scanned_paths, args)
    families = collected["families"]
    if args.write_baseline:
        if collected["status"] == "error":
            scope = scope_fields(roots, scanned_paths, missing_paths, "error")
            return {
                "status": "error", "advisory": True, "repo_root": str(repo_root), **scope,
                "baseline": baseline_path, "command": command, "excludes": excludes,
                "ignore_file": ignore_file, "ranking": {}, "exit_code": collected["exit_code"],
                "tool_version": collected.get("tool_version", ""), "family_count": 0,
                "families": [], "stderr": collected["stderr"],
                "notes": ["nose query errored; baseline not written. Review manually."],
            }
        fingerprints = {family.get("family_fingerprint") for family in families}
        written = baseline.write_baseline_payload(
            repo_root,
            baseline_path,
            {fp for fp in fingerprints if fp},
            roots,
            tool_version=collected.get("tool_version", ""),
            algo_version=fingerprint.FINGERPRINT_ALGO_VERSION,
        )
        return {**scope_fields(roots, scanned_paths, missing_paths, "scanned"), **written}
    if collected["status"] == "error":
        scope = scope_fields(roots, scanned_paths, missing_paths, "error")
        return {
            "status": "error", "advisory": True, "repo_root": str(repo_root), **scope,
            "excludes": excludes, "ignore_file": ignore_file, "baseline": baseline_path,
            "ranking": {}, "command": command, "exit_code": collected["exit_code"],
            "tool_version": collected.get("tool_version", ""), "family_count": 0,
            "families": [], "stderr": collected["stderr"],
            "notes": ["nose inventory error; review manually."],
        }
    baseline_ids = baseline.load_baseline_ids(repo_root, baseline_path)
    drift = [family for family in families if baseline_ids is None or family.get("family_fingerprint") not in baseline_ids]
    summaries = [report.family_summary(family) for family in drift]
    skew = (
        report.tool_version_skew(
            baseline.load_baseline_tool_version(repo_root, baseline_path), collected.get("tool_version", "")
        )
        if baseline_ids is not None
        else None
    )
    notes = [
        "nose findings are refactoring candidates, not standing quality failures.",
        "Review only extractable non-bootstrap families before changing code; do not chase every reported family.",
        "Map each reviewed family to a structural response (machine-owned consistency for intentional duplication, owned extraction, generated-surface ownership, or design review) per the quality inventory-dispatch reference.",
        "Never treat total_dup_lines as a reduction target or a cross-scanner-version trend; re-baseline per scanner version.",
    ]
    if skew:
        notes.insert(0, f"WARNING: {skew}")
    scope = scope_fields(roots, scanned_paths, missing_paths, scope_status)
    return {
        "status": "findings" if summaries else "clean", "advisory": True,
        "repo_root": str(repo_root), **scope, "excludes": excludes, "ignore_file": ignore_file,
        "baseline": baseline_path if baseline_ids is not None else None,
        "ranking": collected.get("ranking", {}), "command": command,
        "exit_code": collected["exit_code"], "tool_version": collected.get("tool_version", ""),
        "version_skew": skew, "family_count": len(summaries),
        "total_dup_lines": sum(int(summary.get("dup_lines") or 0) for summary in summaries),
        "families": summaries, "stderr": collected["stderr"],
        "interpretation": dict(interpretation), "notes": notes,
    }


def cli_exit_code_for_payload(payload: dict[str, Any]) -> int:
    if payload.get("status") == "error":
        return 1
    if payload.get("status") in {"missing", "inapplicable"}:
        return 3
    if payload.get("scope_status") == "partial":
        return 4
    return 0
