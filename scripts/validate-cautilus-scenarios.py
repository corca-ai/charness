#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cautilus_scenarios_lib import REGISTRY_PATH, validate_registry
from scripts.public_skill_validation_lib import ValidationError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = validate_registry(repo_root)
    evaluator_skills = result["registry"]["profiles"]["evaluator-required"]["skills"]
    print(f"Validated cautilus scenario registry {REGISTRY_PATH} ({len(evaluator_skills)} evaluator-required skills).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
