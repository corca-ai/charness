#!/usr/bin/env python3
"""Append one multi-session, proposal-only lesson graduation candidate."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper

ROOT = repo_root_from_script(__file__)
_register = import_repo_module(__file__, "scripts.contract_register_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"record contract proposal: {name} must be non-empty")
    return stripped


def append_proposal(
    *,
    repo_root: Path,
    proposal_id: str,
    lesson_id: str,
    source_retro: str,
    evidence_session_ids: list[str],
    target_path: str,
    target_heading: str,
    rationale: str,
    displacement_unit_ids: list[str],
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _register.contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    proposal = {
        "proposal_id": _nonblank(proposal_id, "proposal_id"),
        "lesson_id": _nonblank(lesson_id, "lesson_id"),
        "source_retro": _nonblank(source_retro, "source_retro"),
        "evidence_session_ids": [
            _nonblank(value, "evidence_session_id") for value in evidence_session_ids
        ],
        "target_path": _nonblank(target_path, "target_path"),
        "target_heading": _nonblank(target_heading, "target_heading"),
        "proposed_unit_id": _register.unit_id(target_path, target_heading),
        "rationale": _nonblank(rationale, "rationale"),
        "displacement_unit_ids": [
            _nonblank(value, "displacement_unit_id") for value in displacement_unit_ids
        ],
    }
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=payload,
        )
        candidate = copy.deepcopy(payload)
        candidate["graduation_proposals"].append(proposal)
        _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=candidate,
        )
        _writer.replace_payload(path, candidate)
    return proposal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--proposal-id", required=True)
    parser.add_argument("--lesson-id", required=True)
    parser.add_argument("--source-retro", required=True)
    parser.add_argument("--evidence-session-id", action="append", required=True)
    parser.add_argument("--target-path", choices=_register.UNIT_PATHS, required=True)
    parser.add_argument("--target-heading", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--displacement-unit-id", action="append", default=[])
    args = parser.parse_args(argv)
    proposal = append_proposal(
        repo_root=args.repo_root.resolve(),
        proposal_id=args.proposal_id,
        lesson_id=args.lesson_id,
        source_retro=args.source_retro,
        evidence_session_ids=args.evidence_session_id,
        target_path=args.target_path,
        target_heading=args.target_heading,
        rationale=args.rationale,
        displacement_unit_ids=args.displacement_unit_id,
    )
    print(json.dumps(proposal, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
