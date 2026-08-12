#!/usr/bin/env python3
"""Append one declared deterministic preview session to the lesson ledger."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lesson_ledger_lib")
_preview = import_repo_module(__file__, "scripts.lesson_selection_preview_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")


def _nonblank(value: str, name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"record lesson session: {name} must be a non-empty non-whitespace string")
    return value


def append_session(
    *, repo_root: Path, output_dir: Path, summary_path: Path, session_id: str, seed: str
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    session_id, seed = _nonblank(session_id, "session_id"), _nonblank(seed, "seed")
    path = _ledger.lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=payload,
        )
        preview = _preview.build_lesson_selection_preview(
            repo_root=repo_root, output_dir=output_dir, summary_path=summary_path, seed=seed
        )
        lesson_ids = [item["lesson_id"] for item in preview["items"]]
        if not lesson_ids:
            raise ValueError("record lesson session: preview selected no eligible lessons")
        snapshot: dict[str, Any] = {
            "kind": preview["kind"],
            "schema_version": preview["schema_version"],
            "selection_policy_version": _preview.SELECTION_POLICY_VERSION,
            "seed": seed,
            "eligible_count": preview["eligible_count"],
            "bucket_counts": preview["bucket_counts"],
            "lesson_ids": lesson_ids,
        }
        event = {
            "session_id": session_id,
            "snapshot": snapshot,
            "snapshot_sha256": _ledger.snapshot_sha256(snapshot),
        }
        candidate = copy.deepcopy(payload)
        candidate["session_events"].append(event)
        _ledger.replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=candidate,
        )
        _writer.replace_payload(path, candidate)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--seed", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    print(
        json.dumps(
            append_session(
                repo_root=root,
                output_dir=root / "charness-artifacts/retro",
                summary_path=root / "charness-artifacts/retro/recent-lessons.md",
                session_id=args.session_id,
                seed=args.seed,
            ),
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
