#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
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
_init_repo_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "init_repo_adapter")




_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.simple_skill_adapter_lib")
load_simple_adapter = _scripts_simple_skill_adapter_lib_module.load_simple_adapter


def load_adapter(repo_root: Path) -> dict[str, object]:
    payload = load_simple_adapter(
        repo_root,
        skill_id="init-repo",
        artifact_filename="latest.md",
        default_output_dir="charness-artifacts/init-repo",
        missing_warnings=(
            "No init-repo adapter found. Using default durable artifact location.",
            "Create .agents/init-repo-adapter.yaml to move the artifact path or record preset provenance.",
        ),
    )
    adapter_data, _adapter_path, _warnings = _init_repo_adapter_module.load_init_repo_adapter(repo_root)
    payload.setdefault("data", {})["skill_routing_mode"] = "compact"
    return payload


def main() -> None:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="init-repo resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    try:
        args = parser.parse_args()
        sys.stdout.write(json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
