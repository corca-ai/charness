"""The `parents[N]` sites are correct in BOTH trees only by an arithmetic cancellation.

A skill script spells its sibling packages by counting directory levels:

    Path(__file__).resolve().parents[3] / "shared" / "scripts" / "run_plan_envelope.py"

In the authoring tree that script lives at `skills/<kind>/<skill>/scripts/x.py`,
so `parents[3]` is `skills/` and the target is `skills/shared/scripts/`. In an
installed tree `export_plugin.py` FLATTENS the kind level away and adds a package
level, giving `plugins/<pkg>/skills/<skill>/scripts/x.py` — so `parents[3]` is
`plugins/<pkg>/` and the target is `plugins/<pkg>/shared/scripts/`. Both correct,
for two different reasons, because the level the exporter removes and the level it
adds cancel exactly.

Nothing at any call site says so. Each one reads like a plain relative walk, and a
reviewer checking it against one tree confirms it and moves on. One change to the
exporter's skill-tier layout turns every one of them into an unreachable-file
instance at once — the class #477/#478/#479 are about — with no gate to notice.

This is that gate. It states the invariant as an executable claim rather than a
comment, so a layout change fails loudly here instead of silently in a consumer's
tree. It deliberately does NOT assert what the layout should be: the exporter is
free to change, and this test is the thing that will tell you what it broke.

Revisit trigger: any change to `export_plugin.py`'s skill-tier layout, or a new
`parents[N]` site in a skill script. Either should arrive with this test updated
in the same commit — if it goes red and the fix is "bump the number", that is the
whole class recurring and the call sites need a shared helper instead.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from .support import ROOT

PARENTS_INDEX_RE = re.compile(r"parents\[(\d+)\]")


def iter_skill_scripts(tree: Path) -> list[Path]:
    return sorted(p for p in tree.rglob("scripts/*.py") if "__pycache__" not in p.parts)


def iter_parents_sites(script: Path) -> list[tuple[int, int]]:
    """`(lineno, index)` for every `parents[<int>]` in the file."""
    return [
        (lineno, int(match.group(1)))
        for lineno, line in enumerate(script.read_text(encoding="utf-8").splitlines(), start=1)
        for match in PARENTS_INDEX_RE.finditer(line)
    ]


def resolved_ancestor(script: Path, index: int) -> Path | None:
    parents = script.resolve().parents
    return parents[index] if index < len(parents) else None


AUTHORING_TREE = ROOT / "skills"
def test_both_trees_are_present_so_this_test_can_mean_anything(exported_plugin_tree: Path) -> None:
    """Without both trees the comparison below is vacuous, and would pass silently."""
    assert AUTHORING_TREE.is_dir(), "authoring skill tree missing"
    assert (exported_plugin_tree / "skills").is_dir(), "exported skill tree missing"
    assert iter_skill_scripts(AUTHORING_TREE), "no authoring skill scripts found"


def test_every_parents_site_resolves_inside_its_own_tree_root(exported_plugin_tree: Path) -> None:
    """A `parents[N]` that climbs out of its own tree is unreachable for that tree's reader.

    Authoring scripts must stay at or under the repo root; installed scripts must
    stay at or under `plugins/<pkg>/`, because that is all a consumer installed.
    This is the assertion that catches an off-by-one in either direction.
    """
    failures: list[str] = []
    installed_tree = exported_plugin_tree / "skills"
    for tree, boundary in ((AUTHORING_TREE, ROOT), (installed_tree, exported_plugin_tree)):
        for script in iter_skill_scripts(tree):
            for lineno, index in iter_parents_sites(script):
                ancestor = resolved_ancestor(script, index)
                if ancestor is None:
                    failures.append(f"{script.relative_to(ROOT)}:{lineno}: parents[{index}] is out of range")
                    continue
                if not ancestor.is_relative_to(boundary.resolve()):
                    failures.append(
                        f"{script.relative_to(ROOT)}:{lineno}: parents[{index}] resolves to "
                        f"{ancestor} which escapes {boundary.relative_to(ROOT) if boundary != ROOT else '<repo root>'}"
                    )
    assert not failures, "\n".join(failures)


def test_the_cancellation_holds_for_every_mirrored_skill_script(exported_plugin_tree: Path) -> None:
    """The same `parents[N]` index must appear at the same line in both copies of a script.

    That equality IS the cancellation: the exporter changes the path depth but not
    the source, so if the index is right in one tree it is right in the other only
    while the added and removed levels cancel. If the exporter's layout changes,
    the indices stay equal (same source) while one tree's resolution goes wrong —
    which the previous test catches. Together they pin both halves.
    """
    installed_tree = exported_plugin_tree / "skills"
    mismatches: list[str] = []
    for authored in iter_skill_scripts(AUTHORING_TREE):
        relative = authored.relative_to(AUTHORING_TREE)
        # `skills/<kind>/<skill>/...` flattens to `skills/<skill>/...`
        installed = installed_tree.joinpath(*relative.parts[1:])
        if not installed.is_file():
            continue
        if iter_parents_sites(authored) != iter_parents_sites(installed):
            mismatches.append(f"{authored.relative_to(ROOT)} vs {installed.relative_to(ROOT)}")
    assert not mismatches, "mirror drift in parents[N] sites:\n" + "\n".join(mismatches)


def test_at_least_one_real_cancellation_site_is_covered() -> None:
    """Guards the two tests above from passing on an empty population.

    A sweep that finds nothing reports a clean result indistinguishable from a
    sweep whose ruler was broken — the exact failure this goal exists to close.
    """
    covered = [
        (script, lineno, index)
        for script in iter_skill_scripts(AUTHORING_TREE)
        for lineno, index in iter_parents_sites(script)
        if index >= 2
    ]
    assert len(covered) >= 8, f"expected the known parents[2]/parents[3] family; found {len(covered)}"


def test_skill_runtime_bootstrap_has_no_level_counting_fallback() -> None:
    """The eleventh site: a `parents[4]` fallback that was dead AND wrong in the mirror.

    Asserted against the AST, not the source text. The first version of this test
    grepped the function's source and went red on the *docstring* that explains the
    removal — a proxy passing for the thing, which is precisely the failure mode
    this file exists to catch one level down.
    """
    source = (ROOT / "scripts" / "skill_runtime_bootstrap.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "repo_root_from_skill_script"
    )
    level_counting = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "parents"
    ]
    assert not level_counting, "repo_root_from_skill_script indexes `.parents` again"
    assert any(
        isinstance(node, ast.Constant) and node.value == "adapter_lib.py" for node in ast.walk(function)
    ), "the marker-based ancestor walk is gone"


def test_the_removed_fallback_refuses_instead_of_guessing() -> None:
    """A script with no marker ancestor gets an explicit error, not an off-by-one root."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_skill_runtime_bootstrap_probe", ROOT / "scripts" / "skill_runtime_bootstrap.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(RuntimeError, match="cannot resolve a tree root"):
        module.repo_root_from_skill_script(Path("/nonexistent/a/b/c/d/e/x.py"))
