#!/usr/bin/env python3
"""Reject dev-tree-only imports and asset paths that break after plugin export.

Plugin export collapses `skills/public/<skill>/` to `skills/<skill>/` without
rewriting Python import statements. A top-level import of the form
`from skills.public.<skill>.scripts.X import Y` resolves in the dev tree but
fails with `ModuleNotFoundError: No module named 'skills.public'` once the
same file runs from the exported plugin tree.

The same collapse breaks *filesystem* paths, and more quietly: a template or
asset resolved as `REPO_ROOT / "skills" / "public" / ...` points at a path that
does not exist in the exported tree, and there is no ModuleNotFoundError to
announce it -- it surfaces as a FileNotFoundError in a consumer repo, or not at
all until someone runs the delivered artifact. `propose_mutation_testing.py`
shipped that way through eight releases: its workflow template was unreachable
from the only copy any consumer installs.

Detect and reject both forms in source files that get copied into the
exported plugin tree (`scripts/`, `skills/public/*/scripts/`,
`skills/support/*/scripts/`, `skills/shared/scripts/`).
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _scripts_repo_file_listing_module.iter_matching_repo_files

FORBIDDEN_PREFIX = "skills.public"
PATH_REMEDIATION = (
    "Resolve the asset relative to the script instead: "
    '`Path(__file__).resolve().parent / \"<asset-dir>\"`. The asset directory is '
    "copied beside the script by the plugin export, so that form holds in both "
    "the dev tree and the exported plugin tree."
)
REMEDIATION = (
    "Import the sibling module by name after adding the resolver directory "
    "to sys.path at runtime (see scripts/record_quality_runtime.py for the "
    "`_RESOLVER_DIR` pattern that works in both the dev tree and the "
    "exported plugin tree)."
)


class ValidationError(Exception):
    pass


def iter_python_targets(root: Path, *, require_git: bool = False) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (
            "scripts/*.py",
            "skills/public/*/scripts/*.py",
            "skills/support/*/scripts/*.py",
            "skills/shared/scripts/*.py",
        ),
        require_git=require_git,
    )


def _is_forbidden(module: str | None) -> bool:
    if not module:
        return False
    return module == FORBIDDEN_PREFIX or module.startswith(FORBIDDEN_PREFIX + ".")


def _binop_base(node: ast.AST) -> ast.AST:
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        node = node.left
    return node


def _chain_root_name(node: ast.AST) -> ast.AST:
    """Strip attribute access and calls off a chain base to reach the name it starts at.

    `REPO_ROOT.resolve()`, `REPO_ROOT.parent`, and `REPO_ROOT.resolve().parent` are
    all the module's own root, and all three used to escape the detector: unwrapping
    one `Call` layer to its `func` leaves an `ast.Attribute`, not the `ast.Name` the
    check demanded. `Path(x)` still stops at `Path`, so wrapping an operator-supplied
    root stays out of scope.
    """
    while True:
        if isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Attribute):
            node = node.value
        else:
            return node


def _is_export_rooted(node: ast.AST) -> bool:
    """True when a `/` chain is rooted at the module's own REPO_ROOT.

    That root is derived from the script's location, so after export it points
    into the plugin tree -- where `skills/public/` does not exist. A chain rooted
    at an operator-supplied `repo_root` argument is a different thing entirely: it
    scans whatever repo the caller named, and maintainer tools legitimately walk
    `skills/public/` there. Only the first form is a delivery bug.
    """
    base = _chain_root_name(_binop_base(node))
    return isinstance(base, ast.Name) and base.id == "REPO_ROOT"


def _forbidden_path_literal(node: ast.AST) -> str | None:
    """Return the offending literal when an expression builds a `skills/public` path
    rooted at the script's own tree.

    Two spellings reach the same broken place: the segment form
    `REPO_ROOT / "skills" / "public" / ...` and the string form
    `REPO_ROOT / "skills/public/..."`.
    """
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
        return None
    if not _is_export_rooted(node):
        return None
    right = node.right
    if isinstance(right, ast.Constant) and isinstance(right.value, str):
        text = right.value.replace("\\", "/")
        if text == "skills/public" or text.startswith("skills/public/"):
            return right.value
    left = node.left
    if (
        isinstance(left, ast.BinOp)
        and isinstance(left.op, ast.Div)
        and isinstance(left.right, ast.Constant)
        and left.right.value == "skills"
        and isinstance(right, ast.Constant)
        and right.value == "public"
    ):
        return 'skills" / "public'
    return None


def _probes_both_layouts(tree: ast.AST) -> bool:
    """True when the module also builds the exported (`skills/<id>/`) form.

    A file that lists both layouts as candidates -- `resolve_artifact_path.py`
    tries four paths and takes the first that `is_file()` -- is doing the right
    thing, not the broken thing: the dev-tree entry is a fallback, not the only
    destination. Whole-file rather than per-expression because the two candidates
    are frequently built in separate statements, and the cost of being wrong here
    is a missed warning in a file that already demonstrates awareness of the
    collapse, not a shipped break.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        if not _is_export_rooted(node):
            continue
        left, right = node.left, node.right
        is_public_segment = isinstance(right, ast.Constant) and right.value == "public"
        if (
            isinstance(left, ast.BinOp)
            and isinstance(left.right, ast.Constant)
            and left.right.value == "skills"
            and not is_public_segment
        ):
            return True
    return False


def validate_asset_paths(path: Path, tree: ast.AST) -> None:
    if _probes_both_layouts(tree):
        return
    for node in ast.walk(tree):
        literal = _forbidden_path_literal(node)
        if literal is None:
            continue
        raise ValidationError(
            f"{path}:{node.lineno}: the path `{literal}` is dev-tree only; plugin "
            f"export collapses `skills/public/<skill>/` to `skills/<skill>/`, so this "
            f"resolves to a nonexistent path in the delivered copy. {PATH_REMEDIATION}"
        )


def validate_imports(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    validate_asset_paths(path, tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and _is_forbidden(node.module):
            raise ValidationError(
                f"{path}:{node.lineno}: `from {node.module} import ...` "
                f"is dev-tree only and breaks after plugin export. {REMEDIATION}"
            )
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden(alias.name):
                    raise ValidationError(
                        f"{path}:{node.lineno}: `import {alias.name}` is "
                        f"dev-tree only and breaks after plugin export. "
                        f"{REMEDIATION}"
                    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    targets = iter_python_targets(root, require_git=args.require_git_file_listing)
    if not targets:
        # Zero files scanned is an unestablished scope, not a clean one: it reads
        # identically to a full pass while proving nothing about the export surface.
        print(
            f"no export-surface Python files found under {root}; nothing was validated. "
            "Check --repo-root (and --require-git-file-listing if the listing came back empty).",
            file=sys.stderr,
        )
        return 1
    for path in targets:
        try:
            validate_imports(path)
        except SyntaxError as exc:
            raise ValidationError(f"{path}: {exc}") from exc

    print(f"Validated export-safe imports for {len(targets)} file(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
