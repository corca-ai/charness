#!/usr/bin/env python3
"""Declare, render, and receipt one deterministic lesson session."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from runtime_bootstrap import import_repo_module, repo_root_from_script

ROOT = repo_root_from_script(__file__)
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
_session = import_repo_module(__file__, "scripts.record_lesson_session")
_boundary = import_repo_module(__file__, "scripts.lesson_session_boundary")


def open_session(
    *,
    repo_root: Path,
    session_id: str,
    seed: str,
    stdout: BinaryIO,
    emitted_at: str | None = None,
    worker_mode: bool = False,
) -> dict[str, object]:
    if worker_mode:
        raise _boundary.LessonSessionBoundaryError(
            "worker mode cannot open or mutate the parent lesson ledger; inherit a parent bundle"
        )
    _continuity.validate_session_id(session_id)
    output_dir = repo_root / "charness-artifacts/retro"
    event, preview = _session.declare_session(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=output_dir / "recent-lessons.md",
        session_id=session_id,
        seed=seed,
    )
    rendered = _continuity.render_preview_bytes(preview)
    bundle = _continuity.bundle_path(output_dir, event["session_id"])
    _continuity.write_bundle(bundle, rendered)
    written = 0
    while written < len(rendered):
        progress = stdout.write(rendered[written:])
        if type(progress) is not int or progress <= 0 or progress > len(rendered) - written:
            raise OSError("lesson session stdout made no valid write progress")
        written += progress
    stdout.flush()
    timestamp = emitted_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    receipt = _continuity.build_receipt(
        session_id=event["session_id"],
        snapshot_sha256=event["snapshot_sha256"],
        stdout_bytes=rendered,
        emitted_at=timestamp,
    )
    path = _continuity.receipt_path(output_dir, event["session_id"])
    _continuity.write_receipt(path, receipt)
    return {
        "session": event,
        "bundle_path": str(bundle.relative_to(repo_root)),
        "receipt_path": str(path.relative_to(repo_root)),
        "receipt": receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--seed", required=True)
    parser.add_argument(
        "--parent-bundle",
        type=Path,
        help="worker mode: inherit this parent bundle without opening the global ledger",
    )
    parser.add_argument("--lane-id", help="worker mode lane identifier")
    parser.add_argument("--owner-id", help="worker mode owner identifier")
    parser.add_argument("--lane-receipt", type=Path, help="worker mode write-once lane receipt")
    parser.add_argument(
        "--worker-mode",
        action="store_true",
        help="refuse global lesson writes; requires --parent-bundle inheritance",
    )
    args = parser.parse_args()
    if args.worker_mode and args.parent_bundle is None:
        parser.error("--worker-mode requires --parent-bundle")
    if args.parent_bundle is not None:
        if not args.lane_id or not args.owner_id:
            parser.error("--parent-bundle requires --lane-id and --owner-id")
        try:
            context, lane_receipt = _boundary.inherit_worker_session(
                args.repo_root.resolve(),
                bundle_path=args.parent_bundle,
                lane_id=args.lane_id,
                owner_id=args.owner_id,
                session_id=args.session_id,
                receipt_path=args.lane_receipt,
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(
            f"worker inherited parent lesson session {context.session_id}; lane receipt at "
            f"{lane_receipt.relative_to(args.repo_root.resolve())}",
            file=sys.stderr,
        )
        return 0
    result = open_session(
        repo_root=args.repo_root.resolve(),
        session_id=args.session_id,
        seed=args.seed,
        stdout=sys.stdout.buffer,
    )
    # STDERR, never stdout: the receipt binds `stdout_sha256`/`stdout_byte_count` to the
    # rendered lesson bytes, and the bundle is validated by re-reading the file and
    # comparing against them. One extra line on stdout would make every receipt this
    # command writes fail its own digest check -- the surface would announce the bundle
    # by breaking it.
    #
    # Announced at all because #617 asks the COMMAND to reference the file by session id,
    # and it did not: `open_session` has always returned `bundle_path` and `main` dropped
    # it, so an agent that ran the CLI had no way to learn where the frozen bytes went --
    # which is the reread path the whole issue exists to provide after compaction.
    print(
        f"lesson session {args.session_id}: frozen lesson bundle at {result['bundle_path']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BrokenPipeError, FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
