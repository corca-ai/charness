"""Standalone-copy bootstrap sync: root fallback copies match the canonicals (#873).

The root `charness` entry must run without a source tree on `sys.path`
(installed standalone copy), so it carries verbatim fallback copies of the
bootstrap closure. The canonical homes are `scripts/cli/bootstrap.py`,
`scripts/cli/bootstrap_state.py`, and `scripts/cli/bootstrap_probe.py`
(self-release probe split out of bootstrap_state). This test fails the build
the moment the two sides drift apart -- like the `bool_env` table contract,
the duplication is deliberate and load-bearing.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRY = REPO_ROOT / "charness"
BOOTSTRAP = REPO_ROOT / "scripts" / "cli" / "bootstrap.py"
BOOTSTRAP_STATE = REPO_ROOT / "scripts" / "cli" / "bootstrap_state.py"
BOOTSTRAP_PROBE = REPO_ROOT / "scripts" / "cli" / "bootstrap_probe.py"

# Entry-bound names: computed from `__file__` per file, values intentionally
# differ (entry roots vs tree roots). Everything else must match literally.
ENTRY_BOUND = {"EMBEDDED_REPO_ROOT", "SCRIPT_PATH", "_CLI_TREE_ROOT"}


def _fallback_block() -> tuple[set[str], dict[str, ast.AST]]:
    tree = ast.parse(ENTRY.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        imports = [
            item
            for item in node.body
            if isinstance(item, ast.ImportFrom) and item.module == "scripts.cli.bootstrap"
        ]
        if len(imports) != 1 or len(imports[0].names) < 10:
            continue
        names = {alias.asname or alias.name for alias in imports[0].names}
        copies = {}
        for item in node.handlers[0].body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                copies[item.name] = item
        return names, copies
    raise AssertionError("fallback try/except block not found in root entry")


def _canonical_defs(path: Path) -> tuple[dict[str, ast.AST], dict[str, object]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defs = {}
    consts = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] = node
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id not in ENTRY_BOUND:
                try:
                    consts[target.id] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
            and node.target.id not in ENTRY_BOUND
        ):
            try:
                consts[node.target.id] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                pass
    return defs, consts


def _entry_consts() -> dict[str, object]:
    tree = ast.parse(ENTRY.read_text(encoding="utf-8"))
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id not in ENTRY_BOUND:
                try:
                    consts[target.id] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
            and node.target.id not in ENTRY_BOUND
        ):
            try:
                consts[node.target.id] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                pass
    return consts


def _unindent_copy(node: ast.AST) -> ast.AST:
    """Reverse the writer's +4 indent on bundled copies (exact inverse).

    The generator indents every non-blank line of a fallback copy by four
    spaces to nest it under `except ImportError:`. Multi-line string
    literals therefore carry four extra spaces per continuation line in the
    root entry. Removing exactly those spaces restores the canonical text;
    anything else is real drift and must fail below.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            lines = child.value.split("\n")
            if len(lines) < 2:
                continue
            # Exact inverse of the writer's per-line +4 indent (blank source
            # lines stay blank; column-0 continuations inside one source line
            # are identical on both sides).
            child.value = "\n".join(
                [lines[0]] + [line[4:] if line.startswith("    ") else line for line in lines[1:]]
            )
    return node


def _state_names() -> set[str]:
    tree = ast.parse(ENTRY.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for item in node.body:
            if isinstance(item, ast.ImportFrom) and item.module == "scripts.cli.bootstrap_state":
                return {alias.asname or alias.name for alias in item.names}
    raise AssertionError("bootstrap_state import not found in root entry")


def test_fallback_copies_match_canonical_defs() -> None:
    names, copies = _fallback_block()
    boot_defs, _ = _canonical_defs(BOOTSTRAP)
    state_defs, _ = _canonical_defs(BOOTSTRAP_STATE)
    probe_defs, _ = _canonical_defs(BOOTSTRAP_PROBE)
    state_names = _state_names()
    canonical = dict(boot_defs)
    canonical.update(state_defs)
    canonical.update(probe_defs)
    assert names | state_names == set(copies), (
        "fallback import list and bundled copies disagree: "
        f"{sorted(set(copies) ^ (names | state_names))}"
    )
    missing = (names | state_names) - set(canonical)
    assert not missing, f"fallback names without canonical def: {sorted(missing)}"
    for name in sorted(names | state_names):
        assert ast.dump(_unindent_copy(copies[name])) == ast.dump(canonical[name]), (
            f"fallback copy of {name!r} drifted from scripts/cli canonical"
        )


def test_shared_literal_consts_match() -> None:
    _, boot_consts = _canonical_defs(BOOTSTRAP)
    entry_consts = _entry_consts()
    assert boot_consts, "no literal consts found in bootstrap.py"
    for name, value in sorted(boot_consts.items()):
        assert name in entry_consts, f"{name!r} missing from root entry"
        assert entry_consts[name] == value, f"const {name!r} drifted between entry and bootstrap"
