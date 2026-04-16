#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_cautilus_scenarios_lib_module = import_repo_module(__file__, "scripts.cautilus_scenarios_lib")
REGISTRY_PATH = _scripts_cautilus_scenarios_lib_module.REGISTRY_PATH
validate_registry = _scripts_cautilus_scenarios_lib_module.validate_registry
_scripts_public_skill_validation_lib_module = import_repo_module(__file__, "scripts.public_skill_validation_lib")
ValidationError = _scripts_public_skill_validation_lib_module.ValidationError


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
