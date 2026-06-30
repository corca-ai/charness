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


def run_adapter_cli(
    resolve, *, label: str, repo_root_help: str, description: str | None = None
) -> None:
    """Shared CLI driver for skill adapter resolvers (resolve_adapter/review_adapter mains).

    Reproduces, verbatim, the main() tail every simple resolver duplicated: arm the
    CLI timeout, parse a required ``--repo-root``, then emit sorted-keys JSON of
    ``resolve(repo_root)``. The per-skill ``resolve`` callable, label, help text, and
    optional parser ``description`` stay local in each script; only this invariant
    driver is shared. ``description`` defaults to ``None`` -- the argparse default --
    so callers that did not set one are byte-identical, including ``--help``. It lives
    beside ``arm_cli_timeout`` -- already called by every resolver main via
    SKILL_RUNTIME -- so sharing it adds no dependency the resolvers did not carry.
    """
    import argparse
    import json
    import sys

    cancel_timeout = arm_cli_timeout(label=label)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--repo-root", type=Path, required=True, help=repo_root_help)
    try:
        args = parser.parse_args()
        sys.stdout.write(
            json.dumps(resolve(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
    finally:
        cancel_timeout()


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
