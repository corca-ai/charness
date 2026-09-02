"""Path selection and filesystem boundary checks for reviewed inputs."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


def _load_changed_path_owner():
    """Load the tree's surface owner even when this file is loaded by path."""
    script_path = Path(__file__).resolve()
    root = next(
        (ancestor for ancestor in script_path.parents if (ancestor / "scripts" / "adapter_lib.py").is_file()),
        None,
    )
    if root is None:
        raise ImportError(f"Unable to resolve repository root from {script_path}")
    sibling = root / "scripts" / "adapters" / "surfaces_lib.py"
    canonical = "scripts.adapters.surfaces_lib"
    loaded = sys.modules.get(canonical)
    if loaded is not None and Path(getattr(loaded, "__file__", "")).resolve() == sibling:
        return loaded
    try:
        spec = importlib.util.find_spec(canonical)
    except (ImportError, ValueError):
        spec = None
    if spec is not None and spec.origin and Path(spec.origin).resolve() == sibling:
        return importlib.import_module(canonical)
    spec = importlib.util.spec_from_file_location("charness_surfaces_lib", sibling)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load changed-path owner from {sibling}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


changed_path_owner = _load_changed_path_owner()


def auto_paths(repo_root: Path, changed_ref: str | None) -> list[str]:
    """Delegate changed-path selection to the surface module's single owner."""
    try:
        if changed_ref:
            return changed_path_owner.collect_changed_paths_for_ref(repo_root, changed_ref)
        return changed_path_owner.collect_changed_paths(repo_root)
    except changed_path_owner.SurfaceError as exc:
        raise ValueError(str(exc)) from exc


def lexical_path(path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root")
    return relative


def checked_path(repo_root: Path, path: str) -> Path:
    relative = lexical_path(path)
    candidate = repo_root.resolve() / relative
    if candidate.is_symlink():
        raise ValueError(
            f"reviewed path `{path}` is a symlink; declare the target file explicitly"
        )
    resolved_for_boundary = candidate.resolve()
    try:
        resolved_for_boundary.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"reviewed path `{path}` resolves outside repo root") from exc
    return candidate
