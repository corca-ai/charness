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


_scripts_adapter_init_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
base_adapter_items = _scripts_adapter_init_lib_module.base_adapter_items
run_init_adapter = _scripts_adapter_init_lib_module.run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return [
        *base_adapter_items(repo_name, "charness-artifacts/hotl"),
        ("surfaces", []),
        ("proof_commands", []),
    ]


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/hotl-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
