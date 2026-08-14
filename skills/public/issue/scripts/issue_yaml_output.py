"""One YAML output seam for the `issue` skill's own stdout.

`issue_tool.py` and `issue_create.py` each grew their own copy of this ancestor
walk during the 2026-08-14 `--json` removal (dup-ratchet families
`38ca1411ca1c9fba` / `87beac73bcb6c911`). Two copies of a loader is one copy too
many when both answer the same question, and the second copy is what pushed
`issue_tool.py` past its code-line cap.

Deliberately NOT routed through `skill_runtime_bootstrap`: `issue_tool.py` loads
that lazily so its read-only subcommands stay usable from an installed copy, and
a module-level hard dependency here would undo that for both callers.

The walk resolves `scripts/yaml_output.py` in the authoring tree and
`plugins/<package>/scripts/yaml_output.py` in an installed one, so the same file
works from either. It converts only THIS skill's own stdout: every `--json`
handed to the `gh` backend, and every `json.loads` of the backend's reply, lives
in `issue_backend.py` / `issue_create_verify.py` and is untouched -- `gh`'s flag
is a third-party native API, not this repo's output contract.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any, Callable


def _load_yaml_output() -> dict[str, Any]:
    helper = next(
        (
            ancestor / "scripts" / "yaml_output.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "yaml_output.py").is_file()
        ),
        None,
    )
    if helper is None:
        raise ImportError("scripts/yaml_output.py not found")
    return runpy.run_path(str(helper))


_YAML_OUTPUT = _load_yaml_output()
render_yaml: Callable[[Any], str] = _YAML_OUTPUT["render_yaml"]
emit_yaml: Callable[[Any], None] = _YAML_OUTPUT["emit_yaml"]

__all__ = ["emit_yaml", "render_yaml"]
