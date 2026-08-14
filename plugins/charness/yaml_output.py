"""Repo-root shim for ``scripts/yaml_output.py``.

Same shape, and the same reason, as the sibling ``runtime_bootstrap.py`` shim.

The 2026-08-14 ``--json`` removal put ``from yaml_output import emit_yaml`` into ~96
files under ``scripts/``. That bare spelling resolves only while ``scripts/`` itself is
``sys.path[0]`` -- true when the file is RUN as a script, false when the same file is
IMPORTED as ``scripts.<name>`` with the repo root on the path, which is how skill
helpers and the CLI reach them (``import_repo_module``,
``load_repo_module_from_skill_script``).

Measured before this shim existed: 79 of those 96 modules raised
``ModuleNotFoundError: No module named 'yaml_output'`` when package-imported. Two of
them were reached that way in production and took real commands down with a traceback
and no payload -- ``resolve_quality_artifact.py --help`` and ``issue_tool.py
close-with-comment``. The failure is silent at authoring time because every one of
those modules works perfectly when run directly.

Fixing it here keeps ONE import spelling across the migrated files instead of 79 local
workarounds, and matches the convention the repo already chose for the bootstrap.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_yaml_output_module():
    module_path = Path(__file__).resolve().parent / "scripts" / "yaml_output.py"
    spec = importlib.util.spec_from_file_location("scripts.yaml_output", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load yaml output helper from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_YAML_OUTPUT = _load_yaml_output_module()
emit_yaml = _YAML_OUTPUT.emit_yaml
render_yaml = _YAML_OUTPUT.render_yaml

__all__ = ["emit_yaml", "render_yaml"]
