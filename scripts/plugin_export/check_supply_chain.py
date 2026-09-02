#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_supply_chain_lib_module = import_repo_module(
    __file__, "scripts.plugin_export.supply_chain_lib"
)
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
