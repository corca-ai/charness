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




_scripts_adapter_init_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_init_lib")
base_adapter_items = _scripts_adapter_init_lib_module.base_adapter_items
run_init_adapter = _scripts_adapter_init_lib_module.run_init_adapter


def build_items(repo_name: str, _args: object) -> list[tuple[str, object]]:
    return [
        *base_adapter_items(repo_name, "charness-artifacts/release"),
        ("package_id", repo_name),
        ("packaging_manifest_path", f"packaging/{repo_name}.json"),
        ("checked_in_plugin_root", f"plugins/{repo_name}"),
        ("sync_command", "python3 scripts/sync_root_plugin_manifests.py --repo-root ."),
        ("quality_command", "./scripts/run-quality.sh"),
        ("update_instructions", []),
        ("real_host_required_surfaces", []),
        ("real_host_required_path_globs", []),
        ("real_host_checklist", []),
        ("requested_review_commands", []),
        (
            "review_unavailable_patterns",
            [
                "review unavailable",
                "requested review unavailable",
                "review gate unavailable",
                "review skipped because",
                "executor_variants",
                "no executor_variants",
            ],
        ),
        ("review_waiver_phrases", ["review waiver:", "explicit review waiver:", "requested review waiver:"]),
    ]


def main() -> None:
    output = run_init_adapter(default_output=Path(".agents/release-adapter.yaml"), build_items=build_items)
    sys.stdout.write(f"{output}\n")


if __name__ == "__main__":
    main()
