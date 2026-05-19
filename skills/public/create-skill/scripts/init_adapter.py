#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_adapter_init_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
base_adapter_items = _adapter_init_lib.base_adapter_items
run_init_adapter = _adapter_init_lib.run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    items = base_adapter_items(repo_name, "charness-artifacts/create-skill")
    items.extend(
        [
            ("implementation_identity_terms", ["canonical implementation", "shared implementation"]),
            ("placement_terms", ["host-facing registration", "trigger surface", "alias"]),
            ("intentional_fork_signals", ["behavior difference", "data isolation", "independent lifecycle"]),
            (
                "topology_verification_hints",
                [
                    "State whether the skill implementation is shared or intentionally forked before completion.",
                    "State which repo-local placements point at the canonical implementation when the repo exposes that topology.",
                ],
            ),
        ]
    )
    return items


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/create-skill-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
