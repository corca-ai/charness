#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_public_skill_dogfood_lib_module = import_repo_module(__file__, "scripts.public_skill_dogfood_lib")
DOGFOOD_PATH = _scripts_public_skill_dogfood_lib_module.DOGFOOD_PATH
_scripts_public_skill_dogfood_validation_lib_module = import_repo_module(__file__, "scripts.public_skill_dogfood_validation_lib")
ValidationError = _scripts_public_skill_dogfood_validation_lib_module.ValidationError
load_registry = _scripts_public_skill_dogfood_validation_lib_module.load_registry
validate_registry = _scripts_public_skill_dogfood_validation_lib_module.validate_registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry = validate_registry(load_registry(repo_root), repo_root)
    print(
        f"Validated public skill dogfood registry {DOGFOOD_PATH} "
        f"({len(registry['cases'])} cases, {len(registry['review_required_skills'])} required)."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
