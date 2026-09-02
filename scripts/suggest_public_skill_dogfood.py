#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_public_skill_dogfood_lib_module = import_repo_module(
    __file__, "scripts.public_skill_dogfood_lib"
)
build_matrix = _scripts_public_skill_dogfood_lib_module.build_matrix
format_human = _scripts_public_skill_dogfood_lib_module.format_human
policy_applicability_report = _scripts_public_skill_dogfood_lib_module.policy_applicability_report
_scripts_public_skill_validation_lib_module = import_repo_module(
    __file__, "scripts.public_skill_validation_lib"
)
public_skill_ids = _scripts_public_skill_validation_lib_module.public_skill_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--skill-id", action="append", default=[])
    parser.add_argument(
        "--detail", action="store_true", help="Emit the full dogfood matrix payload as YAML."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if report := policy_applicability_report(repo_root):
        if args.detail:
            emit_yaml(report)
        else:
            print(format_human(report))
        return 0
    all_skill_ids = public_skill_ids(repo_root)
    requested = args.skill_id or all_skill_ids
    unknown = sorted(set(requested) - set(all_skill_ids))
    if unknown:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in unknown)
        print(f"Unknown public skill id(s): {rendered}", file=sys.stderr)
        return 1

    report = build_matrix(repo_root, requested)
    if args.detail:
        emit_yaml(report)
    else:
        print(format_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
