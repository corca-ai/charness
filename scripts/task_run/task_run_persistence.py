"""Persisted-data-loss lens for lane candidates (#830).

A lane that drops a persistence structure (or an unscoped delete) while
keeping every gate green reads as a success until someone re-reads the
diff. The lens scans the candidate diff for those shapes and records a
typed blocker, so the receipt separates data-loss risk from clean work.
It is best-effort and documented as such: the blocker names what the
lens saw, never a proof that the diff is safe.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Mapping

#: Lines matching these block the lane, added or removed: the candidate
#: introduces or executes a destructive persistence statement with no
#: replacement in the same diff. Kept to statement keywords that are
#: rarely part of legitimate application diffs.
_DROP_RE = re.compile(r"(?i)^\s*(DROP\s+(TABLE|COLUMN|INDEX|SCHEMA|DATABASE)|TRUNCATE\s+TABLE)\b")
_UNSCOPED_DELETE_RE = re.compile(r"(?i)^\s*DELETE\s+FROM\s+\S+\s*;?\s*$")

#: Added lines matching these are advisory: an empty substitute where the
#: same file also loses lines, or a note deferring the replacement.
_EMPTY_SUB_RE = re.compile(r"(?i)^\s*(return\s+(\[\]|\{\}|None)|[\w.]+\s*=\s*(\[\]|\{\}))\s*(#.*)?$")
_DEFERRED_RE = re.compile(r"(?i)(deferr|follow[\s-]?up|until\s+\S+|placeholder)")


def scan_persistence_risks(
    worktree: Path,
    base_sha: str,
    changed_paths: list[str],
    *,
    git: Callable[..., Any],
) -> dict[str, Any]:
    """Flag data-loss shapes in the candidate diff; never fail the lane itself."""
    if not changed_paths:
        return {"findings": [], "blocking": False}
    # The lane branch commit lands after completion (the changed-line gate
    # persists the validated candidate), so at scan time the work may still
    # be uncommitted: diff the worktree against the base, not HEAD.
    # Fail closed: an unreadable diff blocks rather than shipping silent loss.
    try:
        diff = git(worktree, "diff", base_sha, "--", *changed_paths)
    except Exception:  # noqa: BLE001 - an unreadable diff blocks, never ships silent loss
        return {
            "findings": [
                {"path": "", "shape": "candidate-diff-unreadable", "detail": "git diff failed"}
            ],
            "blocking": True,
            "error": "candidate diff unreadable",
        }
    if diff.returncode != 0:
        return {
            "findings": [
                {"path": "", "shape": "candidate-diff-unreadable", "detail": "git diff failed"}
            ],
            "blocking": True,
            "error": "candidate diff unreadable",
        }
    findings: list[dict[str, Any]] = []
    path = ""
    removed = False
    for line in diff.stdout.splitlines():
        if line.startswith("+++ "):
            path = line[6:].removeprefix("b/")
            removed = False
        elif line.startswith("--- "):
            continue
        elif line.startswith("-"):
            removed = True
            body = line[1:]
            if _DROP_RE.search(body):
                findings.append(
                    {
                        "path": path,
                        "shape": "dropped-persistence-structure",
                        "detail": body.strip()[:120],
                    }
                )
            elif _UNSCOPED_DELETE_RE.search(body):
                findings.append(
                    {"path": path, "shape": "unscoped-delete", "detail": body.strip()[:120]}
                )
        elif line.startswith("+"):
            body = line[1:]
            if _DROP_RE.search(body):
                findings.append(
                    {
                        "path": path,
                        "shape": "dropped-persistence-structure",
                        "detail": body.strip()[:120],
                    }
                )
            elif _UNSCOPED_DELETE_RE.search(body):
                findings.append(
                    {"path": path, "shape": "unscoped-delete", "detail": body.strip()[:120]}
                )
            elif _EMPTY_SUB_RE.match(body) and removed:
                findings.append(
                    {"path": path, "shape": "empty-substitution", "detail": body.strip()[:120]}
                )
            elif _DEFERRED_RE.search(body):
                findings.append(
                    {
                        "path": path,
                        "shape": "deferred-replacement-note",
                        "detail": body.strip()[:120],
                    }
                )
    blocking = any(
        finding["shape"] in ("dropped-persistence-structure", "unscoped-delete")
        for finding in findings
    )
    return {"findings": findings, "blocking": blocking}


def persistence_blockers(persistence: Mapping[str, Any] | dict[str, Any] | None) -> list[str]:
    """Blocker text for a blocking lens result, empty when the lens is quiet."""
    if not isinstance(persistence, Mapping) or not persistence.get("blocking"):
        return []
    findings = persistence.get("findings")
    shapes = sorted(
        {finding.get("shape", "unknown") for finding in findings if isinstance(finding, dict)}
        if isinstance(findings, list)
        else set()
    )
    return [
        "persisted data path removed or substituted "
        f"({', '.join(shapes)}); restore the data path or land its replacement before merge"
    ]
