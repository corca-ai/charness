from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_local(
    module_name: str, alias: str | None = None, *, caller_file: str | Path
) -> ModuleType:
    module_path = Path(caller_file).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(alias or module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sibling_loader(caller_file: str | Path):
    def _load_local(module_name: str, alias: str | None = None) -> ModuleType:
        return load_local(module_name, alias, caller_file=caller_file)

    return _load_local


def load_achieve(name: str, alias: str, *, caller_file: str | Path) -> ModuleType:
    """Load a canonical Achieve script by walking up to the nearest `achieve/scripts/`.

    The issue skill consumes Achieve's binding and pickup contracts without a
    package import, so the export layout (flattened or not) decides the path.
    """
    here = Path(caller_file).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "achieve" / "scripts" / f"{name}.py"
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(alias, candidate)
        if spec is None or spec.loader is None:
            raise ImportError(f"unable to load canonical Achieve module {candidate}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"canonical Achieve module {name!r} was not found")
