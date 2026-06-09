#!/usr/bin/env python3
"""PostToolUse edit-time guard: scan the just-edited skill-package file for
disallowed issue anchors.

Fired by the adapter-declared Claude PostToolUse(Edit|Write) hook installed via
`host_hook_skill_anchor_guard` — the host-specific firing lives in the adapter
and the host settings; this script and the scan it drives stay repo-owned and
portable. Fail-open by design: anything unexpected (no payload, non-skill
file, scan error) exits 0 so the hook never interferes with ordinary editing;
a real finding exits 2 so the host surfaces the scan verdict at edit time,
before the commit-time validate_skill_ergonomics sweep (which stays the
backstop).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def edited_file_path(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    return raw if isinstance(raw, str) and raw else None


def skill_package_relpath(repo_root: Path, raw: str) -> str | None:
    """The repo-relative path when `raw` names a file inside this repo's
    skills/public/<skill>/ or skills/support/<skill>/ trees, else None (the
    guard stays silent for every other repo and path — consumer-inert)."""
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    try:
        rel = path.resolve().relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "skills" and parts[1] in {"public", "support"}:
        return rel.as_posix()
    return None


def main(argv: list[str] | None = None, stdin: Any = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="claude", help="Installing host (parity with the hook command; unused).")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    stream = stdin if stdin is not None else sys.stdin
    try:
        payload = json.loads(stream.read() or "{}")
    except (OSError, ValueError):
        return 0
    raw_path = edited_file_path(payload)
    if raw_path is None:
        return 0
    rel = skill_package_relpath(repo_root, raw_path)
    if rel is None:
        return 0
    scan = import_repo_module(__file__, "scripts.skill_issue_anchor_scan")
    try:
        report = scan.scan_issue_anchors(repo_root, [rel])
    except scan.IssueAnchorScanError:
        return 0
    if report["status"] != "blocked":
        return 0
    print(scan.format_human(report), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
