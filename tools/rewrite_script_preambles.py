#!/usr/bin/env python3
"""Normalize root-script imports so nested scripts work when run directly.

The repository deliberately supports both ``python3 scripts/name.py`` and
``python3 scripts/package/name.py``. Python only puts the executed file's
directory on ``sys.path``; this small, idempotent preamble walks upward to the
repository marker before using absolute ``scripts.`` imports.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

REPO_SCRIPT_SHIM = """def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()"""

_FUNCTION_ONLY_REPO_SCRIPT_SHIM = """def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()"""

_BARE_IMPORT = re.compile(r"^(?P<indent>\s*)from (?P<module>runtime_bootstrap|yaml_output) import\b")
_REPO_IMPORT = re.compile(
    r"^\s*from (?:scripts\.)?(?:runtime_bootstrap|yaml_output) import\b",
    re.MULTILINE,
)


def _rewrite_source(source: str) -> tuple[str, int]:
    if REPO_SCRIPT_SHIM in source and not _BARE_IMPORT.search(source):
        return source, 0
    source = source.replace(REPO_SCRIPT_SHIM, "").replace(
        _FUNCTION_ONLY_REPO_SCRIPT_SHIM, ""
    )
    lines = source.splitlines()
    has_repo_import = _REPO_IMPORT.search(source) is not None
    replacements = 0
    for index, line in enumerate(lines):
        match = _BARE_IMPORT.match(line)
        if match is None:
            continue
        lines[index] = line.replace(
            f"from {match.group('module')} import",
            f"from scripts.{match.group('module')} import",
            1,
        )
        replacements += 1
    if not has_repo_import:
        return source, replacements

    import_index = next(
        index
        for index, line in enumerate(lines)
        if _REPO_IMPORT.match(line)
    )
    while (
        import_index >= 2
        and lines[import_index - 1] == ""
        and lines[import_index - 2] == ""
    ):
        del lines[import_index - 1]
        import_index -= 1
    source = "\n".join(lines) + ("\n" if source.endswith("\n") else "")
    tree = ast.parse(source)
    insertion_index = import_index
    for node in tree.body:
        if node.lineno - 1 >= import_index:
            break
        if isinstance(node, ast.Expr) and node.value.__class__ is ast.Constant:
            if isinstance(node.value.value, str):
                continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            insertion_index = node.lineno - 1
            break
    while (
        insertion_index >= 2
        and lines[insertion_index - 1] == ""
        and lines[insertion_index - 2] == ""
    ):
        del lines[insertion_index - 1]
        insertion_index -= 1
    shim_lines = REPO_SCRIPT_SHIM.splitlines()
    while insertion_index and lines[insertion_index - 1] == "":
        del lines[insertion_index - 1]
        insertion_index -= 1
    lines[insertion_index:insertion_index] = ["", "", *shim_lines, ""]
    shim_end = insertion_index + len(shim_lines)
    for index in range(shim_end, len(lines)):
        line = lines[index]
        if line[:1].isspace() or not line.startswith(("import ", "from ")):
            continue
        if "# noqa" not in line:
            lines[index] = f"{line}  # noqa: E402"
        elif "E402" not in line:
            lines[index] = line.replace("# noqa:", "# noqa: E402,", 1)
    return "\n".join(lines) + ("\n" if source.endswith("\n") else ""), replacements


def rewrite_tree(repo_root: Path, *, check: bool = False) -> dict[str, object]:
    scripts_root = repo_root / "scripts"
    changed_paths: list[str] = []
    rewritten_imports = 0
    already_normalized = 0
    for path in sorted(scripts_root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        rewritten, replacements = _rewrite_source(source)
        if replacements == 0 and rewritten == source:
            continue
        if rewritten == source:
            already_normalized += 1
            continue
        changed_paths.append(path.relative_to(repo_root).as_posix())
        rewritten_imports += replacements
        if not check:
            path.write_text(rewritten, encoding="utf-8")
    return {
        "changed_files": len(changed_paths),
        "rewritten_imports": rewritten_imports,
        "already_normalized_files": already_normalized,
        "paths": changed_paths,
        "check_only": check,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check",
        action="store_true",
        help="report files that need rewriting without changing them",
    )
    args = parser.parse_args()
    payload = rewrite_tree(args.repo_root.resolve(), check=args.check)
    print(f"changed_files: {payload['changed_files']}")
    print(f"rewritten_imports: {payload['rewritten_imports']}")
    print(f"already_normalized_files: {payload['already_normalized_files']}")
    if payload["paths"]:
        print("paths:")
        for path in payload["paths"]:
            print(f"- {path}")
    return 1 if args.check and payload["changed_files"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
