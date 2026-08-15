from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType


def repo_root_from_script(script_file: str | Path) -> Path:
    override = os.environ.get("CHARNESS_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()
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


def skill_script(repo_root: Path, skill: str, name: str) -> Path:
    """A script inside a skill package, in the dev tree OR in the collapsed export.

    `skills/public/<skill>/scripts/` in this repo; `skills/<skill>/scripts/` once
    exported, because the export collapses the `public` segment. Every caller that
    reaches into another skill's scripts needs both spellings, and each one had
    grown its own copy of this four-line search with its own error string.
    """
    for candidate in (
        repo_root / "skills" / "public" / skill / "scripts" / name,
        repo_root / "skills" / skill / "scripts" / name,
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"{skill} script {name} not found under {repo_root}")


def arm_cli_timeout(
    *,
    label: str,
    default_seconds: int = 10,
):
    module = import_repo_module(__file__, "scripts.script_timeout")
    return module.arm_cli_timeout(label=label, default_seconds=default_seconds)


def require_repo_local_helper(script_file: str | Path, repo_root: str | Path, **kwargs) -> dict:
    """Refuse a write helper that belongs to a different, drifted charness tree.

    Lazily loaded from the running script's own tree, like ``arm_cli_timeout``, so
    the guard is always the copy that shipped with the helper being guarded.
    """

    module = import_repo_module(__file__, "scripts.helper_provenance_lib")
    return module.require_repo_local_helper(script_file, repo_root, **kwargs)
