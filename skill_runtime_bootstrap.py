from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_skill_runtime_bootstrap_module():
    module_path = Path(__file__).resolve().parent / "scripts" / "skill_runtime_bootstrap.py"
    spec = importlib.util.spec_from_file_location("scripts.skill_runtime_bootstrap", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load skill runtime bootstrap from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SKILL_RUNTIME_BOOTSTRAP = _load_skill_runtime_bootstrap_module()
arm_cli_timeout = _SKILL_RUNTIME_BOOTSTRAP.arm_cli_timeout
load_local_skill_module = _SKILL_RUNTIME_BOOTSTRAP.load_local_skill_module
load_repo_module_from_skill_script = _SKILL_RUNTIME_BOOTSTRAP.load_repo_module_from_skill_script
repo_root_from_skill_script = _SKILL_RUNTIME_BOOTSTRAP.repo_root_from_skill_script

__all__ = [
    "arm_cli_timeout",
    "load_local_skill_module",
    "load_repo_module_from_skill_script",
    "repo_root_from_skill_script",
]
