#!/usr/bin/env python3
"""Append one cited lesson score without bypassing the ledger validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    repo_root_from_script,
    require_repo_local_helper,
)
from scripts.yaml_output import emit_yaml  # noqa: E402

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lessons.lesson_ledger_lib")
lesson_ledger_path = _ledger.lesson_ledger_path
replay_validated_ledger_payload = _ledger.replay_validated_ledger_payload
# The writer is the only way to append the current typed shape. The validator
# still preserves the historical scalar prefix and rejects a later scalar.
_outcome = import_repo_module(__file__, "scripts.lessons.lesson_score_outcome_lib")
_writer = import_repo_module(__file__, "scripts.lessons.lesson_ledger_writer_lib")
ledger_lock = _writer.ledger_lock
replace_payload = _writer.replace_payload


def _fail(message: str) -> None:
    raise ValueError(f"record lesson score: {message}")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        _fail(f"{name} must be a non-empty non-whitespace string")
    return stripped


def append_score(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
    event_id: str,
    lesson_id: str,
    source_retro: str,
    outcome: str,
    anchor: str,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    event_id = _nonblank(event_id, "event_id")
    lesson_id = _nonblank(lesson_id, "lesson_id")
    source_retro = _nonblank(source_retro, "source_retro")
    anchor = _nonblank(anchor, "anchor")
    if outcome not in _outcome.SCORE_OUTCOMES:
        # The refusal carries the QUESTIONS, not just the legal values: an author
        # picking between `read-but-not-applied` and `not-consulted` from the
        # slugs alone is guessing, and guessing is what collapses the split the
        # vocabulary exists to make.
        legal = "; ".join(
            f"`{value}` -- {_outcome.OUTCOME_QUESTIONS[value]}"
            for value in sorted(_outcome.SCORE_OUTCOMES)
        )
        _fail(f"outcome must be one of: {legal}")
    # Refused HERE rather than at replay, because this is where the author still
    # remembers the counterfactual. A refusal at gate time arrives after the
    # session that could have answered it is over.
    anchor_error = _outcome.anchor_shape_error(outcome, anchor)
    if anchor_error is not None:
        _fail(anchor_error)
    if not _outcome.canonical_retro_citation(source_retro):
        _fail(
            f"source_retro must be a repo-relative `{_outcome.RETRO_DIR}/<name>.md` path naming the "
            "retro that RECORDS this encounter -- this session's own retro, not the lesson's origin"
        )
    path = lesson_ledger_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing lesson ledger `{path.relative_to(repo_root)}`")
    with ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload, _migrated = _ledger.migrate_ledger_payload(payload)
        if _migrated:
            # One-way upgrade: keep the pre-upgrade bytes so the documented
            # rollback to the previous release stays true.
            _writer.preserve_pre_migration_copy(path)
        replayed = replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=payload,
        )
        if lesson_id not in replayed:
            _fail(f"lesson_id `{lesson_id}` is unseeded")
        candidate = copy.deepcopy(payload)
        event: dict[str, Any] = {
            "event_id": event_id,
            "source_retro": source_retro,
            "lesson_id": lesson_id,
            "outcome": outcome,
            "anchor": anchor,
        }
        candidate["score_events"].append(event)
        candidate["lessons"] = replayed
        lesson = candidate["lessons"][lesson_id]
        lesson["score_total"] += _outcome.valence(event)
        lesson["score_count"] += 1
        lesson["outcome_counts"][outcome] += 1
        replay_validated_ledger_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            path=path,
            payload=candidate,
        )
        replace_payload(path, candidate)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument(
        "--source-retro",
        required=True,
        help="repo-relative path of the retro RECORDING this encounter (this session's own retro)",
    )
    parser.add_argument(
        "--outcome",
        required=True,
        choices=sorted(_outcome.SCORE_OUTCOMES),
        help="; ".join(
            f"{value}: {question}" for value, question in sorted(_outcome.OUTCOME_QUESTIONS.items())
        ),
    )
    # Required, not optional: with magnitude gone there is no unanchored tier
    # left to fall back to. One fewer rule, one more obligation.
    parser.add_argument("--anchor", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    event = append_score(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        event_id=args.event_id,
        lesson_id=args.lesson_id,
        source_retro=args.source_retro,
        outcome=args.outcome,
        anchor=args.anchor,
    )
    # Receipt only; `append_score` already persisted the event in the JSON ledger.
    emit_yaml(event)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
