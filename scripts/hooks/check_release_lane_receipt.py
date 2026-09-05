#!/usr/bin/env python3
"""Refuse a commit that touches scripts/, skills/, or docs/ without a release-lane receipt.

The commit hook otherwise admits any green the author chose to run; the release
lane is only forced at push. This checker looks at a cheap receipt, not the
lane: a passing ``run-quality.sh --full --release`` stamps
``.charness/quality/last-release-receipt.json`` with the index tree it verified.
A later commit of a different index is refused. ``Slice-reopen:`` in the commit
message is the explicit slice exception for that receipt; it does not skip the
cheap owners of staged files (``check_staged_cheap_owners.py`` in pre-commit).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

LAST_RECEIPT_RELATIVE = ".charness/quality/last-release-receipt.json"
SCOPED_PREFIXES = ("scripts/", "skills/", "docs/")
SLICE_REOPEN_RE = re.compile(r"(?im)^\s*Slice-reopen:")


def last_receipt_path(repo_root: Path) -> Path:
    return repo_root / LAST_RECEIPT_RELATIVE


def _git(repo_root: Path, *args: str) -> str | None:
    result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def staged_paths(repo_root: Path) -> list[str] | None:
    raw = _git(repo_root, "diff", "--cached", "--name-only", "-z")
    if raw is None:
        return None
    return [path for path in raw.split("\0") if path]


def scoped_staged_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if path.startswith(SCOPED_PREFIXES)]


def index_tree(repo_root: Path) -> str | None:
    return _git(repo_root, "write-tree")


def receipt_matches_index(receipt: dict[str, Any], tree: str) -> bool:
    details = receipt.get("details")
    if not isinstance(details, dict):
        return False
    return (
        receipt.get("surface") == "quality"
        and receipt.get("status") == "pass"
        and receipt.get("effective_exit_code") == 0
        and details.get("release") is True
        and details.get("full_queue") is True
        and details.get("index_tree") == tree
    )


def load_receipt(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def evaluate(
    *,
    repo_root: Path,
    commit_message: str,
    paths: list[str] | None,
    tree: str | None,
    receipt: dict[str, Any] | None,
) -> tuple[int, str]:
    if SLICE_REOPEN_RE.search(commit_message):
        return 0, "charness commit-msg: Slice-reopen: admitted without a release-lane receipt"
    if paths is None:
        return 2, "charness commit-msg: could not read staged paths"
    scoped = scoped_staged_paths(paths)
    if not scoped:
        return 0, ""
    if tree is None:
        return 2, "charness commit-msg: could not read the staged tree"
    if receipt is None or not receipt_matches_index(receipt, tree):
        listed = ", ".join(scoped[:8])
        extra = "" if len(scoped) <= 8 else f" (+{len(scoped) - 8} more)"
        return (
            2,
            "charness commit-msg: refusing commit touching "
            f"{listed}{extra} without a release-lane receipt for this staged tree. "
            "Run `./scripts/run-quality.sh --full --read-only --release`, or add a "
            "`Slice-reopen:` line to the commit message.",
        )
    return 0, "charness commit-msg: release-lane receipt matches the staged tree"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--commit-msg-file", type=Path, required=True)
    args = parser.parse_args(argv)
    repo_root = args.repo_root.expanduser().resolve()
    try:
        message = args.commit_msg_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"charness commit-msg: cannot read commit message: {exc}", file=sys.stderr)
        return 2
    code, text = evaluate(
        repo_root=repo_root,
        commit_message=message,
        paths=staged_paths(repo_root),
        tree=index_tree(repo_root),
        receipt=load_receipt(last_receipt_path(repo_root)),
    )
    if text:
        stream = sys.stdout if code == 0 else sys.stderr
        print(text, file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
