#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_setup_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "setup_adapter")




_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.simple_skill_adapter_lib")
load_simple_adapter = _scripts_simple_skill_adapter_lib_module.load_simple_adapter


def load_adapter(repo_root: Path) -> dict[str, object]:
    payload = load_simple_adapter(
        repo_root,
        skill_id="setup",
        artifact_filename="latest.md",
        default_output_dir="charness-artifacts/setup",
        artifact_class="current",
        missing_warnings=(
            "No setup adapter found. Using default durable artifact location.",
            "Create .agents/setup-adapter.yaml to move the artifact path or record preset provenance.",
        ),
    )
    adapter_data, _adapter_path, _warnings = _setup_adapter_module.load_setup_adapter(repo_root)
    payload.setdefault("data", {})["skill_routing_mode"] = "compact"
    return payload


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="setup resolve_adapter", repo_root_help="Repo root whose setup adapter should be resolved")


if __name__ == "__main__":
    main()
