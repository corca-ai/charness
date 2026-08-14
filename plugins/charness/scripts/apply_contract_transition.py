#!/usr/bin/env python3
"""Preview or apply one reviewed contract graduation or retirement transition."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_register = import_repo_module(__file__, "scripts.contract_register_lib")
_writer = import_repo_module(__file__, "scripts.lesson_ledger_writer_lib")


def _nonblank(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"apply contract transition: {name} must be non-empty")
    return stripped


def apply_transition(
    *,
    repo_root: Path,
    action: str,
    event_id: str,
    approval_ref: str,
    rationale: str,
    proposal_id: str | None,
    retired_unit_ids: list[str],
    successor_unit_ids: list[str],
    disposition: str | None,
    execute: bool,
) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _register.contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    event: dict[str, Any] = {
        "sequence": 0,
        "event_id": _nonblank(event_id, "event_id"),
        "action": action,
        "approval_ref": _nonblank(approval_ref, "approval_ref"),
        "rationale": _nonblank(rationale, "rationale"),
    }
    if action == "apply-graduation":
        if proposal_id is None or retired_unit_ids or successor_unit_ids or disposition is not None:
            raise ValueError("apply contract transition: graduation accepts only --proposal-id")
        event["proposal_id"] = _nonblank(proposal_id, "proposal_id")
    elif action == "retire":
        if proposal_id is not None:
            raise ValueError("apply contract transition: retirement does not accept --proposal-id")
        event["retired_unit_ids"] = retired_unit_ids
        event["successor_unit_ids"] = successor_unit_ids
        event["disposition"] = disposition
    else:
        raise ValueError("apply contract transition: unknown action")
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        current = _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=payload,
            require_live_match=False,
        )
        candidate = copy.deepcopy(payload)
        event["sequence"] = len(candidate["applied_transitions"]) + 1
        candidate["applied_transitions"].append(event)
        proposal_map = current["proposal_map"]
        expected_units, expected_retired, _applied = _register._replay_membership(
            candidate["seed_units"],
            candidate["applied_transitions"],
            proposal_map,
            budget=candidate["unit_budget"],
            repo_root=repo_root,
        )
        candidate["units"] = expected_units
        candidate["retired_units"] = expected_retired
        result = _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=candidate,
        )
        if execute:
            _writer.replace_payload(path, candidate)
    return {
        "kind": "charness.contract-transition",
        "event": event,
        "executed": execute,
        "unit_count": result["unit_count"],
        "retired_unit_count": result["retired_unit_count"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--action", choices=("apply-graduation", "retire"), required=True)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--approval-ref", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--proposal-id")
    parser.add_argument("--retired-unit-id", action="append", default=[])
    parser.add_argument("--successor-unit-id", action="append", default=[])
    parser.add_argument(
        "--disposition", choices=("successor-units", _register.NO_BINDING_BEHAVIOR)
    )
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    result = apply_transition(
        repo_root=args.repo_root.resolve(),
        action=args.action,
        event_id=args.event_id,
        approval_ref=args.approval_ref,
        rationale=args.rationale,
        proposal_id=args.proposal_id,
        retired_unit_ids=args.retired_unit_id,
        successor_unit_ids=args.successor_unit_id,
        disposition=args.disposition,
        execute=args.execute,
    )
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
