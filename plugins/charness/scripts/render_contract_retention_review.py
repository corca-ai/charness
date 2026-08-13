#!/usr/bin/env python3
"""Render non-authorizing contract retention evidence from the checked register."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script, require_repo_local_helper

ROOT = repo_root_from_script(__file__)
_register = import_repo_module(__file__, "scripts.contract_register_lib")


def build_retention_review(repo_root: Path) -> dict[str, Any]:
    require_repo_local_helper(__file__, repo_root)
    output_dir = repo_root / "charness-artifacts/retro"
    path = _register.contract_register_path(output_dir)
    result = _register.validate_contract_register(
        repo_root=repo_root,
        output_dir=output_dir,
        summary_path=output_dir / "recent-lessons.md",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    citations = Counter(event["unit_id"] for event in payload["citation_events"])
    catches = Counter(event["unit_id"] for event in payload["catch_events"])
    retired = {unit["unit_id"]: unit for unit in payload["retired_units"]}
    units = [*payload["units"], *payload["retired_units"]]
    rows = [
        {
            "unit_id": unit["unit_id"],
            "membership": "retired" if unit["unit_id"] in retired else "active",
            "citation_count": citations[unit["unit_id"]],
            "catch_count": catches[unit["unit_id"]],
            "signal": "observed" if citations[unit["unit_id"]] or catches[unit["unit_id"]] else "none-observed",
            "retired_by": retired.get(unit["unit_id"], {}).get("retired_by"),
        }
        for unit in sorted(units, key=lambda item: item["unit_id"])
    ]
    return {
        "kind": "charness.contract-retention-review",
        "schema_version": 1,
        "verdict": "non-authorizing-evidence-only",
        "catch_mapping_status": "unavailable" if not payload["catch_events"] else "declared",
        "staleness_status": "not-calibrated",
        "unit_count": result["unit_count"],
        "retired_unit_count": result["retired_unit_count"],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    print(json.dumps(build_retention_review(args.repo_root.resolve()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
