#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_scripts_public_skill_dogfood_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.public_skill_dogfood_lib")
build_matrix = _scripts_public_skill_dogfood_lib_module.build_matrix
_scripts_public_skill_validation_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.public_skill_validation_lib")
public_skill_ids = _scripts_public_skill_validation_lib_module.public_skill_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root whose public skill dogfood matrix should be suggested")
    parser.add_argument("--skill-id", action="append", default=[], help="Public skill id to include in the matrix (repeatable; defaults to all)")
    parser.add_argument("--json", action="store_true", help="Emit the full dogfood matrix payload as JSON")
    return parser.parse_args()


def format_human(report: dict[str, object]) -> str:
    lines = ["Public skill consumer dogfood matrix:"]
    for row in report["matrix"]:
        assert isinstance(row, dict)
        lines.append(
            f"- `{row['skill_id']}`: prompt={row['prompt']} repo_shape={row['repo_shape']}"
        )
        artifact = row["expected_artifact"] or "none"
        lines.append(
            f"  expected_skill=`{row['expected_skill']}` artifact=`{artifact}` "
            f"tier=`{row['validation_tier']}` adapter=`{row['adapter_requirement']}`"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    all_skill_ids = public_skill_ids(repo_root)
    requested = args.skill_id or all_skill_ids
    unknown = sorted(set(requested) - set(all_skill_ids))
    if unknown:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in unknown)
        print(f"Unknown public skill id(s): {rendered}", file=sys.stderr)
        return 1

    report = build_matrix(repo_root, requested)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
