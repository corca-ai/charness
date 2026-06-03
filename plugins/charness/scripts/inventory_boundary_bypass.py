#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.inventory_boundary_bypass_lib")
find_boundary_bypass_candidates = _lib.find_boundary_bypass_candidates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Advisory inventory of boundary-bypass tests (subprocess tests of import-safe entrypoints)."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit the full payload as JSON")
    parser.add_argument(
        "--output", type=Path, default=None, help="Write the JSON payload to this path in addition to stdout."
    )
    args = parser.parse_args()

    payload = find_boundary_bypass_candidates(args.repo_root.resolve())
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json:
        print(rendered)
    else:
        s = payload["summary"]
        print(
            f"boundary-bypass inventory (advisory): {s['candidate_count']} candidates "
            f"({s['convertible_count']} clean-convertible, "
            f"{s['internal_boundary_count']} internally-spawning, "
            f"{s['keep_boundary_count']} likely keep-boundary) "
            f"across {s['scanned_test_files']} test files"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
