#!/usr/bin/env python3
"""Edit-time issue-anchor scan for skill-package files.

Flags disallowed `#NNN`/issue anchors in the one file an author just edited,
before the package-wide commit-time validate_skill_ergonomics sweep round-trips.
Reuses the canonical rule (`ISSUE_ANCHOR_RE` + `is_allowed_issue_anchor_context`
in skill_text_quality_lib) so the per-file verdict matches the commit sweep
exactly. The sweep stays the backstop; this is the additive author-time surface.
Driven through `check_skill_surface_preflight.py --scan-issue-anchors`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime_bootstrap import load_path_module, repo_root_from_script

# The canonical anchor-rule lib ships beside this script, so resolve it from the
# script's own tree (not the scanned --repo-root) -- a seeded test repo or an
# installed bundle that scans elsewhere still finds the single source of truth.
LIB_ROOT = repo_root_from_script(__file__)


class IssueAnchorScanError(Exception):
    pass


def _load_text_quality_lib():
    candidates = (
        LIB_ROOT / "skills" / "public" / "quality" / "scripts" / "skill_text_quality_lib.py",
        LIB_ROOT / "skills" / "quality" / "scripts" / "skill_text_quality_lib.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return load_path_module("skill_text_quality_lib_scan", candidate)
    raise IssueAnchorScanError(
        "missing skill_text_quality_lib helper beside the preflight; expected one of "
        "`skills/public/quality/scripts/skill_text_quality_lib.py` or "
        "`skills/quality/scripts/skill_text_quality_lib.py`"
    )


def _scan_target(repo_root: Path, raw_path: str) -> Path:
    target = Path(raw_path)
    if not target.is_absolute():
        target = repo_root / target
    target = target.resolve()
    try:
        rel = target.relative_to(repo_root)
    except ValueError as exc:
        raise IssueAnchorScanError(f"{target} is outside repo root {repo_root}") from exc
    parts = rel.parts
    if len(parts) < 4 or parts[0] != "skills" or parts[1] not in {"public", "support"}:
        raise IssueAnchorScanError(
            f"{rel.as_posix()}: issue-anchor scan target must be a file under "
            "skills/public/<skill>/ or skills/support/<skill>/"
        )
    if not target.is_file():
        raise IssueAnchorScanError(f"{rel.as_posix()} is missing")
    return target


def scan_issue_anchors(repo_root: Path, paths: list[str]) -> dict[str, Any]:
    """Per-file verdict over the named skill-package files: a disallowed issue
    anchor blocks; an allowed context (version field, placeholder URL) passes."""
    tqlib = _load_text_quality_lib()
    checked: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for raw in paths:
        target = _scan_target(repo_root, raw)
        file_findings = tqlib.issue_anchor_findings_for_file(repo_root, target)
        checked.append({"path": target.relative_to(repo_root).as_posix(), "findings": len(file_findings)})
        findings.extend(file_findings)
    return {
        "status": "blocked" if findings else "ok",
        "blocked": sorted({finding["path"] for finding in findings}),
        "findings": findings,
        "checked": checked,
    }


def format_human(report: dict[str, Any]) -> str:
    lines = [f"skill-issue-anchor-scan: {report['status']}"]
    for row in report["checked"]:
        verdict = "BLOCK" if row["findings"] else "ok"
        lines.append(f"- {row['path']}: {row['findings']} anchor(s) [{verdict}]")
    for finding in report["findings"]:
        lines.append(f"  {finding['path']}:{finding['line']}: {finding['excerpt']}")
    if report["status"] == "blocked":
        lines.append(
            "Disallowed issue anchors (`#NNN`, `owner/repo#N`, `issues/N`) in a "
            "portable skill package. Keep issue provenance in the commit message and "
            "the goal/critique artifact, not the package, before the commit-time "
            "validate_skill_ergonomics sweep blocks it."
        )
    return "\n".join(lines)
