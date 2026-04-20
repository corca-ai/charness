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
arm_cli_timeout = _RUNTIME_BOOTSTRAP.arm_cli_timeout
import_repo_module = _RUNTIME_BOOTSTRAP.import_repo_module
load_path_module = _RUNTIME_BOOTSTRAP.load_path_module
repo_root_from_script = _RUNTIME_BOOTSTRAP.repo_root_from_script

__all__ = ["arm_cli_timeout", "import_repo_module", "load_path_module", "repo_root_from_script"]
