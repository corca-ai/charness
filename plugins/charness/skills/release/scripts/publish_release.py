#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path


def _refuse_foreign_copy() -> None:
    """Refuse a drifted foreign copy before bump, sync, quality, tag, or publish.

    Two 2.11.2 publish attempts ran the whole pipeline from an installed copy
    before dying on an artifact the copy's own stale library had written. This
    is the same provenance check, moved to the seam the operator invokes.

    Non-claim: this cannot close that class. A copy old enough to write a bad
    artifact can be old enough to predate this function — which is exactly what
    happened, twice, on the incident above. It buys a fast, well-worded failure
    for copies that carry it, nothing more; the enforcement that does not depend
    on the caller's age is the target repo's own validators.
    """
    if "--prep-update-instructions" in sys.argv[1:]:
        # Documented as the read-only pre-critique affordance that needs neither a
        # clean worktree nor the critique gate; it mutates nothing provenance can
        # corrupt, and it is the first command an operator runs.
        return
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        return
    runpy.run_path(str(bootstrap))["refuse_foreign_entrypoint"](__file__)


def _load_sibling(module_name: str) -> object:
    module_path = Path(__file__).resolve().with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    _refuse_foreign_copy()
    _load_sibling("publish_release_cli").main()
