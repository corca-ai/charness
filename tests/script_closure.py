"""Derive the `scripts/` files a fixture repo must carry, instead of listing them.

A fixture that installs a repo-owned script into a synthetic tree has to install
everything that script imports, or the script dies at import inside the fixture.
Every such fixture in this repo spelled that closure out as a literal tuple of
filenames, and a literal closure is a RESTATEMENT of the import graph with
nothing binding it to the graph it restates. It drifts the moment anyone adds a
module-level import, and the only thing that observes the drift is an unrelated
test failing with `ModuleNotFoundError`.

That has now happened at least twice:

* `classify_push_diff.py` began importing `emit_yaml`, and
  `test_prepush_runtime_regime` had to gain `yaml_output.py` by hand (its own
  comment records the incident).
* `helper_provenance_lib.py` began importing `env_bypass`, and
  `test_retro_persistence` broke.

Computing the closure removes the restatement. Over-inclusion is safe here (an
unused file in a fixture costs a copy); under-inclusion is the failure mode, so
this walks the WHOLE module rather than only module-scope imports -- a
function-level `from scripts.x import y` is just as fatal when the fixture runs
that function.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _referenced(source: str) -> set[str]:
    """Module stems this source imports that resolve to a `scripts/*.py` file.

    Recognises the four spellings this repo actually uses: `import scripts.x`,
    `from scripts.x import y`, the portable dual-path fallback `from x import y`
    that scripts use under `except ModuleNotFoundError`, and the DYNAMIC form
    `import_repo_module(__file__, "scripts.x")`. The dual-path one is why the
    check is "does `scripts/<stem>.py` exist" rather than a prefix match.

    The dynamic form is not optional: `build_retro_lesson_selection_index.py`
    reaches `recent_lessons_lib` only that way, so a closure built from static
    imports alone is short by four files and the fixture still dies at import --
    which is the failure this helper exists to make impossible.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            parts = node.value.split(".")
            if len(parts) == 2 and parts[0] == "scripts":
                found.add(parts[1])
            elif node.value.endswith(".py") and (SCRIPTS / node.value).is_file():
                # `spec_from_file_location(..., Path(__file__).with_name("x.py"))`
                # -- how `classify_push_diff.py` reaches its own lib. Matching on
                # the `.py` suffix rather than on any bare word keeps this from
                # dragging in a script whose stem is an ordinary English string.
                found.add(node.value.removesuffix(".py"))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if len(parts) == 2 and parts[0] == "scripts":
                    found.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            parts = node.module.split(".")
            if len(parts) == 2 and parts[0] == "scripts":
                found.add(parts[1])
            elif len(parts) == 1 and (SCRIPTS / f"{parts[0]}.py").is_file():
                found.add(parts[0])
    return found


def script_import_closure(*entry_names: str) -> tuple[str, ...]:
    """Every `scripts/*.py` filename reachable from ``entry_names`` by import.

    Returns the entries themselves plus the transitive closure, sorted, so a
    fixture can install exactly what the scripts need without restating it.
    """
    pending = [name.removesuffix(".py") for name in entry_names]
    seen: set[str] = set()
    while pending:
        stem = pending.pop()
        if stem in seen:
            continue
        path = SCRIPTS / f"{stem}.py"
        if not path.is_file():
            # Not a `scripts/` module (stdlib, third party, or a typo in the
            # caller's entry list). Silently skipping a genuine typo would hand
            # back a closure that is short by everything the missing entry
            # imports, so an explicitly named entry must exist.
            if stem in {n.removesuffix(".py") for n in entry_names}:
                raise FileNotFoundError(f"scripts/{stem}.py does not exist")
            continue
        seen.add(stem)
        pending.extend(_referenced(path.read_text(encoding="utf-8")))
    return tuple(sorted(f"{stem}.py" for stem in seen))
