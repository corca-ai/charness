#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_supply_chain_lib_module = import_repo_module(__file__, "scripts.supply_chain_lib")
ValidationError = _scripts_supply_chain_lib_module.ValidationError
collect_offline_findings = _scripts_supply_chain_lib_module.collect_offline_findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings = collect_offline_findings(repo_root)

    if not findings:
        print("No supported supply-chain surfaces detected.")
        return 0

    print("Validated supply-chain surfaces: " + ", ".join(findings))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
