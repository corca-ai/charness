#!/usr/bin/env python3
"""Advisory (#2a): nudge when a slice stages a new dated debug artifact that no
`rca-ledger.jsonl` event references.

The RCA-ledger append is prompt-only and deliberately non-gated (anti-gaming,
per the rca-conversion-ledger spec: schema validity is gated, the conversion
rate and the append itself are not). This advisory surfaces — at exit 0, never
blocking — the case where a debug artifact was added but no ledger event `ref`s
it, so the agent is reminded to record the RCA event. It is an advisory line in
the `run_slice_closeout.py --predict-commit` aggregate, NOT a promotable gate: it
has no failure path and no enforcement, by design.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

try:
    from scripts import rca_ledger_lib as lib
except ImportError:  # pragma: no cover - exercised only in the exported plugin tree
    import rca_ledger_lib as lib

DEBUG_DIR = "charness-artifacts/debug/"


def is_dated_debug_artifact(path: str) -> bool:
    """A dated debug artifact is a `charness-artifacts/debug/*.md` that is not the
    `latest.md` current pointer (the pointer mirrors a dated record at closeout,
    so it is not a distinct new artifact to link)."""
    norm = path.replace("\\", "/")
    if not norm.startswith(DEBUG_DIR) or not norm.endswith(".md"):
        return False
    return Path(norm).name != "latest.md"


def staged_added_paths(repo_root: Path) -> list[str]:
    """Paths newly *added* in the index. Added-only (not modified) keeps the nudge
    keyed to "a slice adds a new debug artifact" — dated artifacts are write-once."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def unlinked_debug_artifacts(repo_root: Path, changed_paths: Sequence[str]) -> list[str]:
    """Dated debug artifacts in `changed_paths` that no ledger event `ref`s."""
    candidates = [p.replace("\\", "/") for p in changed_paths if is_dated_debug_artifact(p)]
    if not candidates:
        return []
    ledger_path = lib.resolve_ledger_path(repo_root, None)
    refs = {
        str(event.get("ref")).replace("\\", "/")
        for event in lib.read_events(ledger_path)
        if event.get("ref")
    }
    return [path for path in candidates if path not in refs]


def advisory_lines(repo_root: Path, changed_paths: Sequence[str]) -> list[str]:
    """Advisory WARN lines for unlinked debug artifacts; empty when all are linked
    or none were added (silent path)."""
    unlinked = unlinked_debug_artifacts(repo_root, changed_paths)
    if not unlinked:
        return []
    lines = [
        "ADVISORY: debug artifact staged with no matching `rca-ledger.jsonl` `ref` "
        "- record an RCA event (`scripts/record_rca_event.py`) so the learning is "
        "captured. Advisory only; never blocks:",
    ]
    lines.extend(f"- {path}" for path in unlinked)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RCA-link advisory nudge (exit 0 always).")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Paths to check; defaults to git staged additions (--diff-filter=A).",
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    paths = args.paths if args.paths is not None else staged_added_paths(repo_root)
    for line in advisory_lines(repo_root, paths):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
