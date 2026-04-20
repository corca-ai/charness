from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_runtime_bootstrap_module() -> ModuleType:
    module_path = Path(__file__).resolve().parent / "runtime_bootstrap.py"
    spec = importlib.util.spec_from_file_location("scripts.runtime_bootstrap", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load runtime bootstrap from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RUNTIME_BOOTSTRAP = _load_runtime_bootstrap_module()
arm_cli_timeout = _RUNTIME_BOOTSTRAP.arm_cli_timeout
load_path_module = _RUNTIME_BOOTSTRAP.load_path_module


def repo_root_from_skill_script(script_file: str | Path) -> Path:
    script_path = Path(script_file).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


def _ensure_repo_root_on_syspath(repo_root: Path) -> None:
    import sys

    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)


def load_repo_module_from_skill_script(script_file: str | Path, module_name: str) -> ModuleType:
    repo_root = repo_root_from_skill_script(script_file)
    _ensure_repo_root_on_syspath(repo_root)
    import importlib

    return importlib.import_module(module_name)


def load_local_skill_module(
    script_file: str | Path,
    module_name: str,
    *,
    file_name: str | None = None,
) -> ModuleType:
    repo_root = repo_root_from_skill_script(script_file)
    _ensure_repo_root_on_syspath(repo_root)
    script_path = Path(script_file).resolve()
    local_path = script_path.parent / (file_name or f"{module_name}.py")
    module_id = f"{script_path.stem}_{module_name}".replace("-", "_")
    return load_path_module(module_id, local_path)
