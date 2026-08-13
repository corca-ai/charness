#!/usr/bin/env python3
"""Preview or apply the deterministic contract-register v1 to v2 migration."""

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


def migration_candidate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("kind") != _register.KIND:
        raise ValueError("contract register migration: expected a contract register object")
    if payload.get("schema_version") == _register.SCHEMA_VERSION:
        return copy.deepcopy(payload)
    if payload.get("schema_version") != 1:
        raise ValueError("contract register migration: only schema version 1 can migrate")
    if payload.get("graduation_proposals"):
        raise ValueError(
            "contract register migration: schema-v1 proposals need explicit evidence sessions"
        )
    candidate = copy.deepcopy(payload)
    candidate["schema_version"] = _register.SCHEMA_VERSION
    candidate["seed_units"] = copy.deepcopy(candidate["units"])
    candidate["retired_units"] = []
    candidate["applied_transitions"] = []
    return candidate


def migrate(*, repo_root: Path, execute: bool) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _register.contract_register_path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(f"missing contract register `{path.relative_to(repo_root)}`")
    with _writer.ledger_lock(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate = migration_candidate(payload)
        result = _register.replay_validated_contract_register_payload(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=output_dir / "recent-lessons.md",
            path=path,
            payload=candidate,
        )
        changed = candidate != payload
        if execute and changed:
            _writer.replace_payload(path, candidate)
    return {
        "kind": "charness.contract-register-migration",
        "from_schema_version": payload.get("schema_version"),
        "to_schema_version": candidate["schema_version"],
        "changed": changed,
        "executed": execute,
        "unit_count": result["unit_count"],
        "unit_budget": candidate["unit_budget"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(migrate(repo_root=args.repo_root.resolve(), execute=args.execute), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
