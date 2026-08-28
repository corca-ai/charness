from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_runtime_bootstrap_module():
    module_path = Path(__file__).resolve().parent / "scripts" / "runtime_bootstrap.py"
    spec = importlib.util.spec_from_file_location("scripts.runtime_bootstrap", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load runtime bootstrap from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RUNTIME_BOOTSTRAP = _load_runtime_bootstrap_module()
MANAGED_RUNTIME_PATH_KEYS = _RUNTIME_BOOTSTRAP.MANAGED_RUNTIME_PATH_KEYS
arm_cli_timeout = _RUNTIME_BOOTSTRAP.arm_cli_timeout
configure_runtime_environment = _RUNTIME_BOOTSTRAP.configure_runtime_environment
runtime_root = _RUNTIME_BOOTSTRAP.runtime_root
import_repo_module = _RUNTIME_BOOTSTRAP.import_repo_module
load_path_module = _RUNTIME_BOOTSTRAP.load_path_module
repo_root_from_script = _RUNTIME_BOOTSTRAP.repo_root_from_script
RuntimeEnvironmentError = _RUNTIME_BOOTSTRAP.RuntimeEnvironmentError
skill_script = _RUNTIME_BOOTSTRAP.skill_script
require_repo_local_helper = _RUNTIME_BOOTSTRAP.require_repo_local_helper
native_core_path = _RUNTIME_BOOTSTRAP.native_core_path

__all__ = [
    "MANAGED_RUNTIME_PATH_KEYS",
    "arm_cli_timeout",
    "configure_runtime_environment",
    "runtime_root",
    "import_repo_module",
    "load_path_module",
    "repo_root_from_script",
    "RuntimeEnvironmentError",
    "require_repo_local_helper",
    "skill_script",
    "native_core_path",
]
