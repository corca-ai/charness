#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

ROOT = repo_root_from_script(__file__)
_register = import_repo_module(__file__, "scripts.contract_register_lib")
validate_contract_register = _register.validate_contract_register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = validate_contract_register(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
    )
    print(
        "Validated contract register: "
        f"{result['unit_count']} active units, "
        f"{result['retired_unit_count']} retired, "
        f"{result['citation_event_count']} citations, "
        f"{result['graduation_proposal_count']} proposals, "
        f"{result['applied_transition_count']} applied transitions."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
