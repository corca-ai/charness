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


def _is_script(stem: str) -> bool:
    """A name resolves only if `scripts/<stem>.py` is really there."""
    return bool(stem) and stem.isidentifier() and (SCRIPTS / f"{stem}.py").is_file()


def _from_string(value: str) -> set[str]:
    """Modules named by a STRING rather than an import statement.

    Two live spellings: `import_repo_module(__file__, "scripts.x")` and
    `spec_from_file_location(..., Path(__file__).with_name("x.py"))`.

    `_is_script` rejects the runtime-composed case: the literal prefix in
    `"scripts." + name` splits to `["scripts", ""]`, which put an EMPTY module
    name in the closure -- harmless downstream (no `scripts/.py` exists) but a
    garbage entry that would mask a real miss in any caller inspecting this set.
    """
    parts = value.split(".")
    if len(parts) == 2 and parts[0] == "scripts" and _is_script(parts[1]):
        return {parts[1]}
    # The `.py` suffix, rather than any bare word, is what keeps a script whose
    # stem is ordinary English (`support`, `quality`) out of every closure.
    if value.endswith(".py") and _is_script(value.removesuffix(".py")):
        return {value.removesuffix(".py")}
    return set()


def _from_import(node: ast.Import) -> set[str]:
    """`import scripts.x` and the bare flat `import x` nine scripts/ modules use."""
    found: set[str] = set()
    for alias in node.names:
        parts = alias.name.split(".")
        if len(parts) == 2 and parts[0] == "scripts" and _is_script(parts[1]):
            found.add(parts[1])
        elif len(parts) == 1 and _is_script(parts[0]):
            found.add(parts[0])
    return found


def _from_import_from(node: ast.ImportFrom) -> set[str]:
    """`from scripts.x import y`, `from scripts import x`, and the dual-path fallback.

    The `from scripts import x` case is the one that bit: the NAMES carry the
    modules there, not the module path, so reading only `node.module` (just
    `"scripts"`) returned nothing for six modules including `task_run.py`.
    """
    if node.level or not node.module:
        return set()
    parts = node.module.split(".")
    if parts == ["scripts"]:
        return {alias.name for alias in node.names if _is_script(alias.name)}
    if len(parts) == 2 and parts[0] == "scripts" and _is_script(parts[1]):
        return {parts[1]}
    # The portable `except ModuleNotFoundError: from x import y` fallback, which is
    # why resolution asks "does the file exist" rather than matching a prefix.
    if len(parts) == 1 and _is_script(parts[0]):
        return {parts[0]}
    return set()


def _referenced(source: str) -> set[str]:
    """Module stems this source imports that resolve to a `scripts/*.py` file.

    Covers every spelling this repo actually uses -- see the three helpers above.
    The dynamic string form is not optional: `build_retro_lesson_selection_index.py`
    reaches `recent_lessons_lib` only that way, so a closure built from static
    imports alone is short by four files and the fixture still dies at import,
    which is the failure this helper exists to make impossible.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found |= _from_string(node.value)
        elif isinstance(node, ast.Import):
            found |= _from_import(node)
        elif isinstance(node, ast.ImportFrom):
            found |= _from_import_from(node)
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
