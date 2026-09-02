#!/usr/bin/env python3
"""PostToolUse edit-time guard: scan the just-edited skill-package file for
disallowed issue anchors.

Fired by the adapter-declared Claude PostToolUse(Edit|Write) hook installed via
`host_hook_skill_anchor_guard` — the host-specific firing lives in the adapter
and the host settings; this script and the scan it drives stay repo-owned and
portable. Fail-open by design: anything unexpected (no payload, non-skill
file, already-deleted file) exits 0 so the hook never interferes with ordinary
editing; a real finding exits 2 so the host surfaces the scan verdict at edit
time, before the commit-time validate_skill_ergonomics sweep (which stays the
backstop). Fail-open is not the same as fail-silent: when the file IS a live
skill-package file but the scan cannot render a verdict over it (missing
`skill_text_quality_lib` rule library, broken bundle), the guard exits 1 with
the reason on stderr — the host's non-blocking hook-error channel — rather than
reporting a clean verdict it never established.
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


def repo_relpath(repo_root: Path, raw: str) -> str | None:
    """The repo-relative path for any edited file inside this repo, else None.

    Resolution is the shared `path_portability_lib.resolve_within_repo`; only the
    disposition is local. That module exists precisely because three callers had
    each grown their own copy of this core.
    """

    portability = import_repo_module(__file__, "scripts.core.path_portability_lib")
    return portability.resolve_within_repo(repo_root, raw)


def _emit_dup_ratchet_advisory(repo_root: Path, raw_path: str) -> None:
    """Print the dup-ratchet edit-time advisory, and never do anything else.

    Fail-open and fail-quiet in every direction: this rides on an edit-time hook,
    so an advisory that raised would break ordinary editing over a signal that is
    explicitly non-blocking.
    """

    try:
        rel = repo_relpath(repo_root, raw_path)
        if rel is None:
            return
        advisory = import_repo_module(__file__, "scripts.dup_ratchet_edit_advisory")
        message = advisory.advise_for_edited_file(repo_root, rel)
        if not message:
            return
        # `hookSpecificOutput.additionalContext` on STDOUT, not stderr. This
        # guard's contract is that the host branches on exit 0 (silent) vs 2
        # (surface findings), and the advisory is exit 0 by construction — so
        # stderr would compute the message correctly and then throw it away,
        # which is the exact "rule that cannot fire where it was written" class
        # this advisory was built during. The retired session-routing path used
        # this channel to put text in front of the agent while exiting 0.
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": message,
                    }
                },
                ensure_ascii=False,
            )
        )
    except Exception:  # noqa: BLE001 - an advisory must never break an edit
        return


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
    # Edit-time dup-ratchet advisory (#474), carried on this already-installed
    # PostToolUse hook rather than a second intent: it needs exactly the same
    # firing (any Edit/Write, the path just edited) and a parallel hook would be
    # more machinery for the same event. Strictly advisory — it never changes
    # this guard's exit code, so a dup-ratchet signal can never block an edit
    # that the anchor scan would have allowed.
    _emit_dup_ratchet_advisory(repo_root, raw_path)
    rel = skill_package_relpath(repo_root, raw_path)
    if rel is None:
        return 0
    if not (repo_root / rel).is_file():
        # Edited file already gone (rename/delete after the edit): nothing to
        # scan, and nothing was claimed about it.
        return 0
    scan = import_repo_module(__file__, "scripts.skill_issue_anchor_scan")
    try:
        report = scan.scan_issue_anchors(repo_root, [rel])
    except scan.IssueAnchorScanError as exc:
        # The target is a live skill-package file, so the scan was supposed to
        # render a verdict over it and could not. Stay non-blocking (this is an
        # additive edit-time guard; the commit sweep is the backstop) but say so
        # loudly instead of exiting 0 like a clean scan.
        print(
            f"skill-issue-anchor-scan: unestablished — could not scan {rel}: {exc}",
            file=sys.stderr,
        )
        return 1
    if report["status"] != "blocked":
        return 0
    print(scan.format_human(report), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
