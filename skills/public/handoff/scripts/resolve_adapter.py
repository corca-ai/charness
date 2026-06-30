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




_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.simple_skill_adapter_lib")
load_simple_adapter = _scripts_simple_skill_adapter_lib_module.load_simple_adapter


def load_adapter(repo_root: Path) -> dict[str, object]:
    return load_simple_adapter(
        repo_root,
        skill_id="handoff",
        artifact_filename="handoff.md",
        default_output_dir="docs",
        artifact_class="rolling",
        missing_warnings=(
            "No handoff adapter found. Using default docs/handoff.md location.",
            "Create .agents/handoff-adapter.yaml to move the artifact path or record preset provenance.",
        ),
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="handoff resolve_adapter", repo_root_help="Repo root for resolving the handoff adapter")


if __name__ == "__main__":
    main()
