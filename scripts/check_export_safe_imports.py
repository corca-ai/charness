#!/usr/bin/env python3
"""Reject dev-tree-only imports that break after plugin export.

Plugin export collapses `skills/public/<skill>/` to `skills/<skill>/` without
rewriting Python import statements. A top-level import of the form
`from skills.public.<skill>.scripts.X import Y` resolves in the dev tree but
fails with `ModuleNotFoundError: No module named 'skills.public'` once the
same file runs from the exported plugin tree.

Detect and reject those imports in source files that get copied into the
exported plugin tree (`scripts/`, `skills/public/*/scripts/`,
`skills/support/*/scripts/`).
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
REMEDIATION = (
    "Import the sibling module by name after adding the resolver directory "
    "to sys.path at runtime (see scripts/record_quality_runtime.py for the "
    "`_RESOLVER_DIR` pattern that works in both the dev tree and the "
    "exported plugin tree)."
)


class ValidationError(Exception):
    pass


def iter_python_targets(root: Path) -> list[Path]:
    return iter_matching_repo_files(
        root,
        (
            "scripts/*.py",
            "skills/public/*/scripts/*.py",
            "skills/support/*/scripts/*.py",
        ),
    )


def _is_forbidden(module: str | None) -> bool:
    if not module:
        return False
    return module == FORBIDDEN_PREFIX or module.startswith(FORBIDDEN_PREFIX + ".")


def validate_imports(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
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
    args = parser.parse_args()

    root = args.repo_root.resolve()
    targets = iter_python_targets(root)
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
