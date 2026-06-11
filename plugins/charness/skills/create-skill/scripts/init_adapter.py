#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_BOOTSTRAP_ROOT = next(
    (ancestor for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()),
    None,
)
if _BOOTSTRAP_ROOT is None:
    raise ImportError("skill_runtime_bootstrap.py not found")
sys.path.insert(0, str(_BOOTSTRAP_ROOT))

import skill_runtime_bootstrap as SKILL_RUNTIME  # noqa: E402

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
