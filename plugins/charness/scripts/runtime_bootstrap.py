from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def repo_root_from_script(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parent.parent


def import_repo_module(script_file: str | Path, module_name: str) -> ModuleType:
    repo_root = repo_root_from_script(script_file)
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)
    return importlib.import_module(module_name)


def load_path_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec for {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
