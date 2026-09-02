#!/usr/bin/env python3

from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_setup_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "setup_adapter")
_inspect_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.setup.setup_inspect_lib")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to inspect")
    parser.add_argument(
        "--expect-plan-identity",
        help="Refuse when the current read-only inspection does not match an approved plan identity",
    )
    args = parser.parse_args()
    payload = _inspect_lib.build_setup_inspection_payload(
        args.repo_root.resolve(),
        load_setup_adapter=_setup_adapter_module.load_setup_adapter,
        prose_wrap_state=_setup_adapter_module.prose_wrap_state,
        surface_overrides=_setup_adapter_module.surface_overrides,
        operating_surface_profile=_setup_adapter_module.operating_surface_profile,
    )
    if args.expect_plan_identity and payload["approval_plan"]["identity"] != args.expect_plan_identity:
        yaml_output.emit_yaml(
            {
                "status": "plan-changed",
                "expected_plan_identity": args.expect_plan_identity,
                "actual_plan_identity": payload["approval_plan"]["identity"],
            }
        )
        return 2
    yaml_output.emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
