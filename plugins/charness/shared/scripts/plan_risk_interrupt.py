#!/usr/bin/env python3
"""Layout-independent entrypoint for the repo-level risk-interrupt planner (#477).

`impl` and `spec` used to invoke the planner as
``$SKILL_DIR/../../../scripts/plan_risk_interrupt.py``. Three levels up reaches
the repo root from ``skills/public/<skill>``, and OVERSHOOTS from
``plugins/<pkg>/skills/<skill>`` — where the exported scripts sit two levels up.
So the command resolved in the authoring tree and nowhere else, and because both
call sites ended in ``2>/dev/null || true`` it failed silently: the planner had
never run in any installed plugin.

No single ``../``-count fixes that, because the correct depth differs per layout.
``$SKILL_DIR/../../shared/scripts/`` is the one prefix that resolves *identically*
in both — the package-to-tier-root distance is the same in each — so the layout
ambiguity is resolved ONCE here, in code with a test, instead of twice in prose
across two SKILL.md files. A two-candidate probe in the fence was the obvious
alternative and is worse: one of its candidates must always fail, which is
indistinguishable from a real broken reference to `check_doc_links.py` and to
`inventory_skill_script_references.py`.

The ancestor walk is the repo's established shape for this (see
``skills/public/quality/scripts/inventory_brittle_source_guards.py``).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PLANNER_NAME = "plan_risk_interrupt.py"


def locate_planner(start: Path | None = None) -> Path:
    """The nearest ancestor's ``scripts/plan_risk_interrupt.py``.

    Walks up from this file, so it lands on ``<repo>/scripts/`` in the authoring
    tree and ``plugins/<pkg>/scripts/`` in the shipped one without either depth
    being hard-coded.
    """
    origin = (start or Path(__file__)).resolve()
    this_file = Path(__file__).resolve()
    for ancestor in origin.parents:
        candidate = ancestor / "scripts" / PLANNER_NAME
        # `skills/shared` + `scripts/<name>` IS this shim, so an unguarded walk
        # finds itself and recurses forever. Skip self rather than skip the
        # directory: the guard stays correct if the shim is ever relocated.
        if candidate.is_file() and candidate.resolve() != this_file:
            return candidate
    raise FileNotFoundError(
        f"no ancestor of {origin} contains scripts/{PLANNER_NAME}; "
        "this shim must ship alongside the repo-level planner"
    )


def load_planner(planner_path: Path):
    """Import the planner with its own directory importable.

    The planner does bare `from yaml_output import ...` / `from runtime_bootstrap
    import ...`, which only resolve when its OWN directory is on `sys.path`.
    Running it directly gets that for free; loading it from here does not.
    """
    planner_dir = str(planner_path.parent)
    if planner_dir not in sys.path:
        sys.path.insert(0, planner_dir)
    spec = importlib.util.spec_from_file_location("plan_risk_interrupt_entrypoint", planner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {planner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    return load_planner(locate_planner()).main()


if __name__ == "__main__":
    raise SystemExit(main())
