#!/usr/bin/env python3
"""Reach an authoring-repo script from a path that resolves in BOTH layouts.

A repo-level script lives at `<repo>/scripts/X.py` in the authoring tree and at
`<plugin-root>/scripts/X.py` once exported. Those sit at DIFFERENT depths from a
skill package — three levels up versus two — so no single `$SKILL_DIR/../../../`
count reaches it in both. #477 was exactly that: a command correct here and
broken in every installed plugin, silently.

`$SKILL_DIR/../../shared/scripts/` is the one prefix at equal depth in both
layouts, because the exporter flattens `skills/<kind>/<skill>` to
`skills/<skill>` and the package-to-tier-root distance is the same either way.
So a thin shim here is reachable by one spelling, and the layout ambiguity is
resolved ONCE in code with tests instead of once per call site in prose.

This module is the shared half. Each shim is a few lines naming its target, so
adding one does not copy this resolution logic again.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

# The walk is BOUNDED. A shim sits at `<root>/<tier>/scripts/<name>`, so its
# target is three ancestors up in the authoring tree and two in the shipped one.
# An unbounded walk would keep climbing past the package into the consuming
# repo and eventually `/`, and then EXECUTE whatever `scripts/<name>.py` it
# found there -- a consumer plausibly owns a `validate_skills.py`, and running
# their file is worse than the FileNotFoundError this promises.
_MAX_ANCESTORS = 5
_TARGET_ROOTS = {"validate_skills.py": "tools", "plan_risk_interrupt.py": "scripts/gates_support"}


def locate(name: str, caller: Path) -> Path:
    """The nearest ancestor's ``scripts/<name>``, never the caller itself.

    Walking up from the CALLER lands on `<repo>/scripts/` in the authoring tree
    and `<plugin-root>/scripts/` in the shipped one without either depth being
    hard-coded. The self-skip is load-bearing: a shim named `X.py` living in
    `<tier>/scripts/` is itself an `<ancestor>/scripts/X.py`, so an unguarded
    walk finds itself and recurses until the interpreter dies.
    """
    origin = caller.resolve()
    target_root = _TARGET_ROOTS.get(name, "scripts")
    for ancestor in list(origin.parents)[:_MAX_ANCESTORS]:
        candidate = ancestor.joinpath(*target_root.split("/")) / name
        if candidate.is_file() and candidate.resolve() != origin:
            if target_root == "tools" and not (ancestor / "packaging" / "charness.json").is_file():
                # A consumer's own tools/<name> is not the authoring-repo script;
                # the walk must never execute a file the plugin does not own.
                continue
            return candidate
    raise FileNotFoundError(
        f"no ancestor of {origin} within {_MAX_ANCESTORS} levels contains {target_root}/{name}; "
        + (
            "the exported plugin does not carry the authoring repository's tools/ tree, "
            "so this entrypoint runs only from a charness source checkout"
            if target_root == "tools"
            else "this shim must ship alongside the authoring-repo script it fronts"
        )
    )


def run(name: str, caller: str) -> int:
    """Locate the target and run it AS `__main__`, exactly as a direct call would.

    Importing it and calling `main()` looks equivalent and is not: two of the
    three targets put their ERROR HANDLING in the `__main__` guard --
    `validate_skills.py` and `plan_risk_interrupt.py` both catch `ValidationError`
    there and print the reason to stderr. Calling `main()` from an import leaves
    that guard false, so a failing validation reaches the operator as a traceback
    with the actual reason buried at the bottom, on the one path
    `binary-preflight.md` step 5 exists to serve.

    `runpy` executes the guard, so the shim inherits whatever entry contract the
    target already has instead of re-implementing a per-target one. Its own
    directory goes on `sys.path` first because repo scripts use bare
    `from yaml_output import ...` imports that only resolve from there -- running
    one directly gets that for free; reaching it from here does not.

    SINGLE-SHOT PER PROCESS. `runpy` itself is re-entrant, but the targets are
    not: their module-level `import_repo_module` caches libraries in `sys.modules`
    under tree-independent keys (`scripts.gates_support.risk_interrupt_lib`, ...). A second call
    for the same target from the OTHER tree would re-run the entrypoint while
    silently reusing the first tree's libraries -- the resolved-to-the-wrong-tree
    class this shim exists to kill, one layer down. Every call site is
    `python3 <shim>`, i.e. a fresh process, which is what keeps that unreachable.
    """
    script_path = locate(name, Path(caller))
    script_dir = str(script_path.parent)
    for import_root in (script_dir, str(script_path.parent.parent)):
        if import_root not in sys.path:
            sys.path.insert(0, import_root)
    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(str(code), file=sys.stderr)
        return 1
    return 0
