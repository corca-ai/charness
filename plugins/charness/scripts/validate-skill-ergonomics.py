#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import load_path_module


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parent.parent


def _helper_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "validate_skill_ergonomics.py",
        repo_root / "skills" / "quality" / "scripts" / "validate_skill_ergonomics.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "missing quality ergonomics helper; expected one of "
        "`skills/public/quality/scripts/validate_skill_ergonomics.py` or "
        "`skills/quality/scripts/validate_skill_ergonomics.py`"
    )


REPO_ROOT = _runtime_root()
HELPER_PATH = _helper_path(REPO_ROOT)
HELPER = load_path_module("validate_skill_ergonomics_entrypoint", HELPER_PATH)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = HELPER.evaluate(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(HELPER._format_human(report))
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
